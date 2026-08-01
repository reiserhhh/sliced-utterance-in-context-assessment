#!/usr/bin/env python3
"""M4-D Leg 7: realization averaging -- the direct R^(-1/2) falsification test
of the Leg-4b "floor = per-realization variance" interpretation.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 7 -- realization averaging", 2026-08-02 loop cycle 2, commit 79d35e6,
BEFORE this run). All floor machinery is IMPORTED from
scripts/run_suica_m4_d_dleg_floor_leg4.py (the validated 4b protocol:
oracle-forced route, e_d_paired, analytic D_true with unit check), the
two-stage construction from scripts/run_suica_m4_d_two_stage_leg5.py, and the
chunked-foreground pattern from Leg 6. Nothing there is reimplemented.

THE TEST. Leg 4b's interpretation of the ~.39 D-leg floor is "the creation
derivative's PER-REALIZATION VARIANCE plus non-vanishing regularization
bias". That interpretation makes a sharp falsifiable prediction: averaging D
estimates across INDEPENDENT REALIZATIONS of the same law must reduce the
floor as R^(-1/2) -- exactly what more events within one realization (4b) and
richer excitation within one realization (Leg 6) could not do. If the floor
is instead estimator-family bias or a world-identifiability limit, it is
R-invariant and the interpretation DIES.

REALIZATION MECHANISM (the 4b frozen-world trick, now at fixed budget).
generate_m4_chart_ecology_world draws the LAW (condition panels + oracle
basis at seed+1_009; mechanism parameters at seed+17_021) from seed-offset
RNG streams that never touch the path panels; each path panel draws from its
own stream at seed + view_index*10_000_019 + role_index*1_000_003. Leg 4b's
non-1x panels were fresh path realizations because changing spec.events
shifts path RNG consumption while the law streams are untouched. Leg 7 makes
the realization index EXPLICIT: realization r keeps the law streams
bit-identical and offsets only the path-panel seeds by r*1_000_000_007
(realization 0 = offset 0 = the exact battery panels). Faithfulness is
gated, not assumed, per world-rep BEFORE any fresh realization is consumed:
(i) the reassembled law (oracle basis all roles + all 8 author-parameter
arrays) must be bit-identical to the battery truth; (ii) the reassembled
realization-0 calibration/selection panels must reproduce the battery panels
VALUE-EXACTLY on all 8 panel fields (both views); (iii) the realization-0
floor rows must match Leg 4's persisted 1x rows (<= 1e-9, flags/routes
exactly equal) -- the registered "R=1 must match the persisted floors"
assert -- before any R > 1 work runs on that world-rep.

FLOOR ARMS (registered): R in {1, 2, 4, 8} independent path realizations per
world-rep under the IDENTICAL law, event budget FIXED at 1x per realization
(120 events). D estimated PER REALIZATION at the oracle-forced route (4b
protocol: route frozen at the 1x oracle stack's V2-selected model, chart and
both bases frozen at V2 1x, V2 estimator semantics, no selection anywhere),
then REALIZATION-AVERAGED:
- PRIMARY method 'avg': simple mean of the R D-estimates on each side;
- SECONDARY method 'joint': one pooled V2 hazard fit over the R panels
  (calibration+selection of all R realizations stacked); at R=1 the two
  methods coincide by construction (identical rows persisted for both).
e_d_paired(R) = ||D_disc_avg(R) - D_orc_avg(R)|| / ||D_orc_avg(R)|| (the
program-standard paired error; at R=1 it IS Leg 4b's 1x e_d_paired
bit-exactly). Companions per row: e_d_true, e_orc_true (vs the analytic
generator-law derivative, unit-checked), e_d_frozen and orc drift vs the
frozen 1x oracle stack D, reference_gap. The R arms use nested realization
prefixes ({0}, {0,1}, {0..3}, {0..7}) -- the standard Monte-Carlo
convergence-curve construction; realizations are mutually independent
draws. Rows whose forced route has a zero-D oracle reference stay flagged
degenerate and excluded from medians (Leg 4's rule, same rows).

STACKING ARM (registered): two-stage + realization-averaged D at R=4, full
5-world x 8-rep battery. Stage 1 = Leg 5's stage 1 EXACTLY (penalized route
selection at ridge lambda=.125; asserted per world-rep against Leg 4's
persisted arm2 rows; battery flips must equal 73). Stage 2 = V2 unpenalized
refit at the stage-1-selected route per realization r in {0..3} (realization
0 follows Leg 5's exact reuse rule and the recomputed two_stage rows are
asserted per world-rep against Leg 5's persisted per-loop rows), D and
creation_action averaged across the 4 realizations; loop transport
recomputed as D_avg @ G_v2 @ C_v2. Compared against Leg 5's persisted
pooled .7605 and per-world values. Companion arms persisted at no extra
cost: arm2_stage1_125 and two_stage (= Leg 5 bit-exact).

REGISTERED LEANS (adjudication statistics pre-coded here):
- (a) THE CONFIRMATION TEST: pooled log-log slope of the floor vs R in
  [-.65, -.35], where floor(R) = pooled author-level median e_d_paired of
  the 'avg' method at R, slope = OLS of log(median) on log(R) over all four
  R (at R=8, .418 -> ~.148 if exactly R^(-1/2)).
- (b) R=8 pooled floor <= .20.
- (c) two-stage + realization-averaged D at R=4: pooled loop geometry
  >= .82 AND both floor-pinned worlds (endogenous_source_partition_matched
  .6527, selection_creation_compensation .6209 under Leg 5) cross .70.
PIVOT-IF (registered): pooled slope > -.15 (R-invariant floor) -> the
per-realization-variance interpretation of Leg 4b is WRONG (recorded plainly
as the planner's registered miss), the floor is estimator-family bias or a
world-identifiability limit, and the next instrument is an
oracle-vs-estimator bias decomposition at increasing R. The decomposition is
computed HERE in all cases (pivot profile): does the ORACLE's own refit
error vs the law (e_orc_true) also stay flat in R? does the
estimator-minus-oracle gap (author-level e_d_true - e_orc_true) close?

Chunked execution (this arc's battery-then-stall workaround): --chunk-start/
--chunk-stop run repetition ranges in the foreground writing partial CSVs;
--assemble concatenates all partials, REFUSES missing or duplicate cells,
and adjudicates from the concatenated rows only.
"""
from __future__ import annotations

import argparse
import glob
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
import run_suica_m4_d_two_stage_leg5 as leg5  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _creation_action,
    _feedback_derivative,
    _fit_hazard_candidate,
    _flatten_events,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    _condition_panels,
    _mechanism_parameters,
    _path_panel,
)

LOOP_WORLDS = leg3.LOOP_WORLDS
R_GRID = (1, 2, 4, 8)
MAX_R = 8
STACKING_R = 4
REALIZATION_OFFSET = 1_000_000_007
STAGE1_LAMBDA = leg5.STAGE1_LAMBDA  # 0.125
STACKING_ARMS = ("arm2_stage1_125", "two_stage", "two_stage_ravg_r4")
ROW_TOLERANCE = 1e-9
LEAN_A_BAND = (-0.65, -0.35)
LEAN_B_BAR = 0.20
LEAN_C_POOLED_BAR = 0.82
LEAN_C_WORLD_BAR = 0.70
PIVOT_SLOPE_BAR = -0.15
PINNED_WORLDS = (
    "endogenous_source_partition_matched",
    "selection_creation_compensation",
)
FLOOR_METRICS = (
    "e_d_paired",
    "e_d_frozen",
    "e_d_true",
    "e_orc_true",
    "orc_self_drift",
    "reference_gap",
)
LAW_PARAMETER_KEYS = (
    "selection",
    "creation",
    "gate",
    "response_transition",
    "response_choice",
    "recovery",
    "external_persistence",
    "generated_base",
)
PANEL_FIELDS = (
    "external_menu",
    "generated_menu",
    "menu",
    "choice",
    "response",
    "history",
    "duration",
    "environment",
)


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg4_reference() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Leg 4 persisted 1x floor rows (the registered R=1 comparator)."""
    rows_path = ROOT / "results" / "m4_d_dleg_floor" / "dleg_budget_rows.csv"
    decision_path = ROOT / "results" / "m4_d_dleg_floor" / "decision.json"
    if not rows_path.exists() or not decision_path.exists():
        raise RuntimeError(
            "Leg 4 persisted floor artifacts are required references and "
            f"were not found: {rows_path} / {decision_path}"
        )
    stored = pd.read_csv(rows_path)
    stored = stored[stored["budget"] == 1.0].copy()
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    pooled = decision["part_4b"]["scaling"]["POOLED"]["e_d_paired"]
    median_1x = float(pooled["medians_by_budget"]["1.0"])
    if abs(median_1x - 0.418) > 0.005:
        raise RuntimeError(
            f"Leg 4 persisted pooled 1x median {median_1x:.4f} is not the "
            "registered ~.418 comparator; reference battery is not the one "
            "registered"
        )
    return stored, decision


def _load_leg5_reference() -> tuple[dict[str, Any], pd.DataFrame]:
    """Leg 5 persisted two_stage summary + per-loop rows (stacking asserts)."""
    decision_path = ROOT / "results" / "m4_d_two_stage" / "decision.json"
    rows_path = ROOT / "results" / "m4_d_two_stage" / "per_loop_metrics.csv"
    if not decision_path.exists() or not rows_path.exists():
        raise RuntimeError(
            "Leg 5 persisted artifacts are required references and were not "
            f"found: {decision_path} / {rows_path}"
        )
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    two = decision["arms"]["two_stage"]
    if abs(float(two["pooled_loop_geometry"]) - 0.7605) > 0.005:
        raise RuntimeError(
            "Leg 5 persisted two_stage pooled geometry "
            f"{two['pooled_loop_geometry']:.4f} is not the registered ~.7605 "
            "comparator; reference battery is not the one registered"
        )
    stored = pd.read_csv(rows_path)
    stored = stored[stored["arm"] == "two_stage"].copy()
    return two, stored


# ---------------------------------------------------------------------------
# realization generation -- frozen law, offset path seeds
# ---------------------------------------------------------------------------


def _rebuild_law(
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Reproduce the generator's law step (oracle basis + parameters)."""
    _, oracle_basis, _ = _condition_panels(
        world=world,
        spec=spec,
        seed=seed + 1_009,
    )
    parameters = _mechanism_parameters(
        world=world,
        oracle_width=oracle_basis["calibration"].shape[1],
        spec=spec,
        seed=seed + 17_021,
    )
    return oracle_basis, parameters


def _assert_law_identity(
    context: dict[str, Any],
    oracle_basis: dict[str, np.ndarray],
    parameters: dict[str, np.ndarray],
) -> None:
    truth = context["truth"]
    for role in ("calibration", "selection", "evaluation"):
        if not np.array_equal(oracle_basis[role], truth.oracle_basis[role]):
            raise RuntimeError(
                "law identity violation: reassembled oracle basis "
                f"[{role}] differs on {context['world']} rep "
                f"{context['repetition']}"
            )
    for name in LAW_PARAMETER_KEYS:
        if not np.array_equal(
            parameters[name], truth.author_parameters[name]
        ):
            raise RuntimeError(
                "law identity violation: reassembled author parameter "
                f"{name} differs on {context['world']} rep "
                f"{context['repetition']}"
            )


def _realization_cal_sel(
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
    realization: int,
    oracle_basis: dict[str, np.ndarray],
    parameters: dict[str, np.ndarray],
) -> dict[tuple[str, str], Any]:
    """Calibration+selection path panels for one realization of the law.

    Mirrors generate_m4_chart_ecology_world's path step exactly (same role
    indices 0=calibration, 1=selection; evaluation is not built -- it is
    never consumed by the floor or stage-2 fits), with the path seed offset
    by realization * REALIZATION_OFFSET. Offset 0 reproduces the battery
    panels (gated bit-exactly per world-rep before fresh realizations run).
    """
    role_occasions = {
        "calibration": spec.calibration_occasions,
        "selection": spec.selection_occasions,
    }
    panels: dict[tuple[str, str], Any] = {}
    for view_index, view in enumerate(("train", "test")):
        for role_index, (role, occasions) in enumerate(
            role_occasions.items()
        ):
            panels[(view, role)] = _path_panel(
                world=world,
                basis=oracle_basis[role],
                parameters=parameters,
                occasions=occasions,
                spec=spec,
                seed=(
                    seed
                    + realization * REALIZATION_OFFSET
                    + view_index * 10_000_019
                    + role_index * 1_000_003
                ),
            )
    return panels


def _assert_realization0_panels(
    context: dict[str, Any],
    panels0: dict[tuple[str, str], Any],
) -> dict[str, Any]:
    mismatches = []
    for view in ("train", "test"):
        for role in ("calibration", "selection"):
            battery = getattr(
                context["observed"].ecology, f"{view}_{role}"
            )
            rebuilt = panels0[(view, role)]
            for field in PANEL_FIELDS:
                if not np.array_equal(
                    getattr(battery, field), getattr(rebuilt, field)
                ):
                    mismatches.append(f"{view}_{role}.{field}")
    if mismatches:
        raise RuntimeError(
            "realization-0 reassembly identity gate FAILED on "
            f"{context['world']} rep {context['repetition']}: offset-0 "
            "path panels do not reproduce the battery panels; mismatched "
            f"fields: {mismatches}"
        )
    return {
        "world": context["world"],
        "repetition": context["repetition"],
        "fields_checked": len(PANEL_FIELDS) * 4,
        "identity_holds": True,
    }


# ---------------------------------------------------------------------------
# R=1 reproduction assert vs Leg 4 persisted 1x rows
# ---------------------------------------------------------------------------


def _assert_r1_rows(
    rows: list[dict[str, Any]],
    stored_1x: pd.DataFrame,
    world: str,
    repetition: int,
) -> dict[str, Any]:
    mine = pd.DataFrame(rows)
    reference = stored_1x[
        (stored_1x["world"] == world)
        & (stored_1x["repetition"] == repetition)
    ]
    keys = ["world", "repetition", "author", "view"]
    merged = reference.merge(mine, on=keys, suffixes=("_leg4", "_leg7"))
    if len(merged) != len(mine) or len(merged) != len(reference):
        raise RuntimeError(
            f"R=1 rows misaligned with Leg 4 1x rows on {world} rep "
            f"{repetition}: {len(merged)} matches vs mine {len(mine)} / "
            f"stored {len(reference)}"
        )
    checks: dict[str, Any] = {
        "world": world,
        "repetition": repetition,
        "rows_compared": int(len(merged)),
    }
    flags_equal = bool(
        (
            merged["degenerate_reference_leg4"]
            == merged["degenerate_reference_leg7"]
        ).all()
        and (
            merged["forced_route_leg4"] == merged["forced_route_leg7"]
        ).all()
    )
    checks["flags_equal"] = flags_equal
    usable = merged[~merged["degenerate_reference_leg4"]]
    max_diff = 0.0
    for name in FLOOR_METRICS:
        diff = float(
            np.max(np.abs(usable[f"{name}_leg4"] - usable[f"{name}_leg7"]))
        )
        checks[f"max_abs_{name}_difference"] = diff
        max_diff = max(max_diff, diff)
    checks["max_abs_difference"] = max_diff
    if max_diff > ROW_TOLERANCE or not flags_equal:
        raise RuntimeError(
            f"R=1 floor replay diverges from Leg 4 persisted 1x rows on "
            f"{world} rep {repetition}: max|diff|={max_diff:.3e} "
            f"flags_equal={flags_equal}"
        )
    return checks


# ---------------------------------------------------------------------------
# stage-1 / two_stage reproduction asserts vs persisted rows (scale-aware)
# ---------------------------------------------------------------------------
#
# Tolerance note (discovered during this run, before any battery row was
# persisted): on rows whose ORACLE stack is D-degenerate (oracle selected
# base/return, so the oracle loop is exactly zero), Leg 1's e_loop statistic
# divides ||loop_disc|| by the 1e-12 clamp and takes values ~1e+11. Bit
# reproduction of such an amplified ratio across separate processes is not
# guaranteed at ULP granularity (observed: ONE ULP, 1.5e-05 absolute =
# 1.2e-16 relative, on selection_creation_compensation rep 0 author 13 test
# -- present in a fresh process running only context -> stage 1 ->
# two_stage, so it is BLAS-level float wobble, not an input or replay
# difference; e_d_atom on the same row matches to 8.3e-17 and every
# flag/route is equal). The asserts therefore use a scale-aware tolerance
# |diff| <= 1e-9 * max(1, |reference|) per metric row -- strict-absolute on
# every regular row (magnitudes O(1)), one-ULP-relative on the amplified
# degenerate rows -- and persist BOTH the raw and the scaled maxima, plus
# the strict maximum restricted to non-amplified rows, so the faithfulness
# table can state the bit-tightness where bit-tightness is defined.


def _assert_rows_scaled(
    rows: list[dict[str, Any]],
    stored: pd.DataFrame,
    world: str,
    repetition: int,
    *,
    label: str,
) -> dict[str, Any]:
    mine = pd.DataFrame(rows)
    reference = stored[
        (stored["world"] == world) & (stored["repetition"] == repetition)
    ]
    keys = ["world", "repetition", "author", "view"]
    merged = reference.merge(mine, on=keys, suffixes=("_ref", "_leg7"))
    if len(merged) != len(mine) or len(merged) != len(reference):
        raise RuntimeError(
            f"{label} rows misaligned with persisted reference on {world} "
            f"rep {repetition}: {len(merged)} matches vs mine {len(mine)} "
            f"/ stored {len(reference)}"
        )
    checks: dict[str, Any] = {
        "world": world,
        "repetition": repetition,
        "rows_compared": int(len(merged)),
    }
    flags_equal = bool(
        (merged["model_flip_ref"] == merged["model_flip_leg7"]).all()
        and (
            merged["selected_model_arm_ref"]
            == merged["selected_model_arm_leg7"]
        ).all()
    )
    checks["flags_equal"] = flags_equal
    amplified = merged["loop_norm_oracle_ref"] <= leg3.FLIP_TOLERANCE
    checks["amplified_rows"] = int(amplified.sum())
    max_scaled = 0.0
    for name in ("e_loop", "e_d_atom"):
        diff = np.abs(merged[f"{name}_ref"] - merged[f"{name}_leg7"])
        scale = np.maximum(1.0, np.abs(merged[f"{name}_ref"]))
        checks[f"max_abs_{name}_difference"] = float(diff.max())
        checks[f"max_scaled_{name}_difference"] = float(
            (diff / scale).max()
        )
        strict = diff[~amplified]
        checks[f"max_abs_{name}_difference_nonamplified"] = float(
            strict.max() if len(strict) else 0.0
        )
        max_scaled = max(max_scaled, checks[f"max_scaled_{name}_difference"])
    if max_scaled > ROW_TOLERANCE or not flags_equal:
        raise RuntimeError(
            f"{label} replay diverges from persisted reference on {world} "
            f"rep {repetition}: max scaled diff={max_scaled:.3e} "
            f"flags_equal={flags_equal}"
        )
    return checks


# ---------------------------------------------------------------------------
# floor arm -- per-realization D at the oracle-forced route, then averaging
# ---------------------------------------------------------------------------


def _floor_rows_for_world_rep(
    context: dict[str, Any],
    *,
    spec: M4ChartEcologySpec,
    stored_1x: pd.DataFrame,
    oracle_basis: dict[str, np.ndarray],
    parameters: dict[str, np.ndarray],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[tuple[str, int, int], tuple[dict, dict]],
]:
    """Averaged rows, single-realization rows, r1 check, gates, event cache.

    Returns the flattened calibration/selection event dicts of ALL
    realizations keyed (view, author, realization); the joint fits consume
    the full cache and the stacking arm reuses realizations 1..STACKING_R-1
    without regeneration.
    """
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    v2_basis = context["v2_basis"]
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

    row_index: list[tuple[str, int]] = [
        (view, author)
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    forced_routes: dict[tuple[str, int], str] = {}
    degenerate: dict[tuple[str, int], bool] = {}
    d_orc_1x: dict[tuple[str, int], np.ndarray] = {}
    for view, author in row_index:
        oracle_stack = context["oracle_stacks"][view][author]
        forced_routes[(view, author)] = oracle_stack["selected_model"]
        d_orc_1x[(view, author)] = oracle_stack["D"]
        degenerate[(view, author)] = bool(
            float(np.linalg.norm(oracle_stack["D"])) < leg4.FLIP_TOLERANCE
        )

    # ---- realization 0 = battery panels; fits + Leg-4 identity gates ----
    events_by_realization: dict[
        tuple[str, int, int], tuple[dict, dict]
    ] = {}
    for view, author in row_index:
        calibration, selection, _ = context["flat"][(view, author)]
        events_by_realization[(view, author, 0)] = (calibration, selection)

    d_disc: dict[tuple[str, int], list[np.ndarray]] = {}
    d_orc: dict[tuple[str, int], list[np.ndarray]] = {}
    orc_identity_gap = 0.0
    disc_identity_gap = 0.0
    disc_identity_rows = 0
    for view, author in row_index:
        if degenerate[(view, author)]:
            continue
        calibration, selection = events_by_realization[(view, author, 0)]
        route = forced_routes[(view, author)]
        disc0 = leg4._forced_route_derivative(
            calibration,
            selection,
            v2_basis,
            model=route,
            hazard_ridge=hazard_ridge,
            logistic_iterations=iterations,
            dimensions=dimensions,
        )
        orc0 = leg4._forced_route_derivative(
            calibration,
            selection,
            truth.oracle_basis,
            model=route,
            hazard_ridge=hazard_ridge,
            logistic_iterations=iterations,
            dimensions=dimensions,
        )
        orc_identity_gap = max(
            orc_identity_gap,
            float(np.max(np.abs(orc0 - d_orc_1x[(view, author)]))),
        )
        base_stack = context["base_stacks"][view][author]
        if base_stack["selected_model"] == route:
            disc_identity_gap = max(
                disc_identity_gap,
                float(np.max(np.abs(disc0 - base_stack["D"]))),
            )
            disc_identity_rows += 1
        d_disc[(view, author)] = [disc0]
        d_orc[(view, author)] = [orc0]
    if (
        orc_identity_gap > ROW_TOLERANCE
        or disc_identity_gap > ROW_TOLERANCE
    ):
        raise RuntimeError(
            f"realization-0 identity gate failed on {world} rep "
            f"{repetition}: orc gap {orc_identity_gap:.3e} disc gap "
            f"{disc_identity_gap:.3e}"
        )

    # ---- R=1 rows asserted vs Leg 4 persisted 1x rows BEFORE R>1 work ----
    def _error_row(
        view: str,
        author: int,
        d_disc_value: np.ndarray | None,
        d_orc_value: np.ndarray | None,
    ) -> dict[str, Any]:
        keys = {
            "world": world,
            "repetition": repetition,
            "seed": seed,
            "author": author,
            "view": view,
            "forced_route": forced_routes[(view, author)],
        }
        reference_1x = d_orc_1x[(view, author)]
        if degenerate[(view, author)]:
            return {
                **keys,
                "degenerate_reference": True,
                "e_d_paired": np.nan,
                "e_d_frozen": np.nan,
                "e_d_true": np.nan,
                "e_orc_true": np.nan,
                "orc_self_drift": np.nan,
                "reference_gap": np.nan,
                "d_norm_disc": np.nan,
                "d_norm_orc": np.nan,
                "d_norm_orc_1x": float(np.linalg.norm(reference_1x)),
                "d_norm_true": float(np.linalg.norm(true_d[author])),
            }
        return {
            **keys,
            "degenerate_reference": False,
            "e_d_paired": leg3._relative_error(d_disc_value, d_orc_value),
            "e_d_frozen": leg3._relative_error(d_disc_value, reference_1x),
            "e_d_true": leg3._relative_error(d_disc_value, true_d[author]),
            "e_orc_true": leg3._relative_error(d_orc_value, true_d[author]),
            "orc_self_drift": leg3._relative_error(
                d_orc_value, reference_1x
            ),
            "reference_gap": leg3._relative_error(
                reference_1x, true_d[author]
            ),
            "d_norm_disc": float(np.linalg.norm(d_disc_value)),
            "d_norm_orc": float(np.linalg.norm(d_orc_value)),
            "d_norm_orc_1x": float(np.linalg.norm(reference_1x)),
            "d_norm_true": float(np.linalg.norm(true_d[author])),
        }

    r1_rows = [
        _error_row(
            view,
            author,
            d_disc[(view, author)][0]
            if not degenerate[(view, author)]
            else None,
            d_orc[(view, author)][0]
            if not degenerate[(view, author)]
            else None,
        )
        for view, author in row_index
    ]
    r1_check = _assert_r1_rows(r1_rows, stored_1x, world, repetition)

    # ---- fresh realizations 1..MAX_R-1 (identical law, offset paths) ----
    # All realizations are cached for every row: the joint fits at R=8
    # consume realizations 4..7, and the stacking arm refits stage-2 D on
    # realizations 1..STACKING_R-1 for every row including floor-degenerate
    # ones (Leg 5's two_stage covers all rows).
    for realization in range(1, MAX_R):
        panels = _realization_cal_sel(
            world, spec, seed, realization, oracle_basis, parameters
        )
        for view in ("train", "test"):
            calibration_panel = panels[(view, "calibration")]
            selection_panel = panels[(view, "selection")]
            for author in range(context["authors"]):
                calibration = _flatten_events(calibration_panel, author)
                selection = _flatten_events(selection_panel, author)
                events_by_realization[(view, author, realization)] = (
                    calibration,
                    selection,
                )
                if degenerate[(view, author)]:
                    continue
                route = forced_routes[(view, author)]
                d_disc[(view, author)].append(
                    leg4._forced_route_derivative(
                        calibration,
                        selection,
                        v2_basis,
                        model=route,
                        hazard_ridge=hazard_ridge,
                        logistic_iterations=iterations,
                        dimensions=dimensions,
                    )
                )
                d_orc[(view, author)].append(
                    leg4._forced_route_derivative(
                        calibration,
                        selection,
                        truth.oracle_basis,
                        model=route,
                        hazard_ridge=hazard_ridge,
                        logistic_iterations=iterations,
                        dimensions=dimensions,
                    )
                )

    # ---- single-realization rows (diagnostic; persisted per row) ----
    single_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        for realization in range(MAX_R):
            if degenerate[(view, author)]:
                row = _error_row(view, author, None, None)
            else:
                row = _error_row(
                    view,
                    author,
                    d_disc[(view, author)][realization],
                    d_orc[(view, author)][realization],
                )
            row["realization"] = realization
            single_rows.append(row)

    # ---- averaged rows: methods 'avg' (primary) and 'joint' (secondary) --
    averaged_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        for n_realizations in R_GRID:
            if degenerate[(view, author)]:
                for method in ("avg", "joint"):
                    row = _error_row(view, author, None, None)
                    row["R"] = n_realizations
                    row["method"] = method
                    averaged_rows.append(row)
                continue
            disc_list = d_disc[(view, author)][:n_realizations]
            orc_list = d_orc[(view, author)][:n_realizations]
            disc_avg = np.mean(disc_list, axis=0)
            orc_avg = np.mean(orc_list, axis=0)
            row = _error_row(view, author, disc_avg, orc_avg)
            row["R"] = n_realizations
            row["method"] = "avg"
            averaged_rows.append(row)
            if n_realizations == 1:
                joint_row = dict(row)
                joint_row["method"] = "joint"
                averaged_rows.append(joint_row)
                continue
            route = forced_routes[(view, author)]
            datasets_disc = []
            datasets_orc = []
            for realization in range(n_realizations):
                calibration, selection = events_by_realization[
                    (view, author, realization)
                ]
                datasets_disc.append((calibration, v2_basis["calibration"]))
                datasets_disc.append((selection, v2_basis["selection"]))
                datasets_orc.append(
                    (calibration, truth.oracle_basis["calibration"])
                )
                datasets_orc.append(
                    (selection, truth.oracle_basis["selection"])
                )
            fit_disc = _fit_hazard_candidate(
                datasets_disc,
                model=route,
                ridge=hazard_ridge,
                iterations=iterations,
            )
            fit_orc = _fit_hazard_candidate(
                datasets_orc,
                model=route,
                ridge=hazard_ridge,
                iterations=iterations,
            )
            disc_joint = _feedback_derivative(
                fit_disc[0],
                fit_disc[1],
                v2_basis["evaluation"],
                dimensions,
            )
            orc_joint = _feedback_derivative(
                fit_orc[0],
                fit_orc[1],
                truth.oracle_basis["evaluation"],
                dimensions,
            )
            joint_row = _error_row(view, author, disc_joint, orc_joint)
            joint_row["R"] = n_realizations
            joint_row["method"] = "joint"
            averaged_rows.append(joint_row)

    gates = {
        "true_d_unit_check_max_gap": unit_gap,
        "orc_refit_identity_max_gap_r0": orc_identity_gap,
        "disc_forced_identity_max_gap_r0": disc_identity_gap,
        "disc_forced_identity_rows_r0": disc_identity_rows,
    }
    return averaged_rows, single_rows, r1_check, gates, events_by_realization


# ---------------------------------------------------------------------------
# stacking arm -- two-stage + realization-averaged D at R = STACKING_R
# ---------------------------------------------------------------------------


def _stacking_rows_for_world_rep(
    context: dict[str, Any],
    *,
    leg4_arm2: pd.DataFrame,
    leg5_two_stage_rows: pd.DataFrame,
    events_by_realization: dict[
        tuple[str, int, int], tuple[dict, dict]
    ],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
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
    stage1_rows = []
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stage1_rows.append(
                leg3._loop_row(
                    {**keys_base, "author": author, "view": view},
                    "arm2_stage1_125",
                    stage1_stacks[view][author],
                    context["oracle_stacks"][view][author],
                )
            )
    stage1_check = _assert_rows_scaled(
        stage1_rows, leg4_arm2, world, repetition, label="stage-1"
    )

    # ---- two_stage (Leg 5 exactly) + persisted-row assert ----
    two_stage_stacks: dict[str, list[dict[str, Any]]] = {
        "train": [],
        "test": [],
    }
    fresh_refits = 0
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack, fresh = leg5._two_stage_stack(
                context, view, author, stage1_stacks[view][author]
            )
            two_stage_stacks[view].append(stack)
            if fresh:
                fresh_refits += 1
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
    two_stage_check = _assert_rows_scaled(
        two_stage_rows,
        leg5_two_stage_rows,
        world,
        repetition,
        label="two_stage",
    )

    # ---- two_stage_ravg_r4: stage-2 D averaged over STACKING_R panels ----
    ravg_stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    fresh_ravg_fits = 0
    for view in ("train", "test"):
        for author in range(context["authors"]):
            base = context["base_stacks"][view][author]
            stage2 = two_stage_stacks[view][author]
            route = stage2["selected_model"]
            d_list = [stage2["D"]]
            action_list = [stage2["creation_action"]]
            for realization in range(1, STACKING_R):
                calibration, selection = events_by_realization[
                    (view, author, realization)
                ]
                fit = _fit_hazard_candidate(
                    [
                        (calibration, v2_basis["calibration"]),
                        (selection, v2_basis["selection"]),
                    ],
                    model=route,
                    ridge=hazard_ridge,
                    iterations=iterations,
                )
                fresh_ravg_fits += 1
                d_list.append(
                    _feedback_derivative(
                        fit[0],
                        fit[1],
                        v2_basis["evaluation"],
                        dimensions,
                    )
                )
                action_list.append(
                    _creation_action(
                        fit[0],
                        fit[1],
                        v2_basis["evaluation"],
                        dimensions,
                    )
                )
            d_avg = np.mean(d_list, axis=0)
            ravg_stacks[view].append(
                {
                    "C": base["C"],
                    "G": base["G"],
                    "D": d_avg,
                    "loop": d_avg @ base["G"] @ base["C"],
                    "choice_action": base["choice_action"],
                    "creation_action": np.mean(action_list, axis=0),
                    "selected_model": route,
                }
            )

    arm_stacks = {
        "arm2_stage1_125": stage1_stacks,
        "two_stage": two_stage_stacks,
        "two_stage_ravg_r4": ravg_stacks,
    }
    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    for arm in STACKING_ARMS:
        if arm == "arm2_stage1_125":
            arm_rows = stage1_rows
        elif arm == "two_stage":
            arm_rows = two_stage_rows
        else:
            arm_rows = [
                leg3._loop_row(
                    {**keys_base, "author": author, "view": view},
                    arm,
                    arm_stacks[arm][view][author],
                    context["oracle_stacks"][view][author],
                )
                for view in ("train", "test")
                for author in range(context["authors"])
            ]
        loop_rows.extend(arm_rows)
        geometries = leg3._arm_geometries(
            arm_stacks[arm], context["oracle_stacks"]
        )
        world_rows.append(
            {
                **keys_base,
                "arm": arm,
                "chart_family": context["chart"].selected_family,
                "arm_lambda": (
                    STAGE1_LAMBDA if arm == "arm2_stage1_125" else np.nan
                ),
                "stacking_R": (
                    STACKING_R if arm == "two_stage_ravg_r4" else 1
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
    structure = {
        **keys_base,
        "fresh_stage2_refits": fresh_refits,
        "fresh_ravg_fits": fresh_ravg_fits,
    }
    return loop_rows, world_rows, stage1_check, two_stage_check, structure


# ---------------------------------------------------------------------------
# chunk execution
# ---------------------------------------------------------------------------


def _run_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
) -> None:
    stored_1x, _ = _load_leg4_reference()
    leg4_arm2 = leg5._load_leg4_arm2()
    _, leg5_rows = _load_leg5_reference()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    archived_path = ROOT / "results" / "m4_chart_ecology" / "metrics.csv"
    archived = pd.read_csv(archived_path) if archived_path.exists() else None

    def expected_for(world: str, repetition: int, seed: int):
        if archived is None:
            return None
        match = archived[
            (archived["world"] == world)
            & (archived["repetition"] == repetition)
            & (archived["seed"] == seed)
        ]
        if len(match) != 1:
            return None
        return {
            name: float(match[name].iloc[0])
            for name in (
                "loop_action_geometry",
                "choice_action_geometry",
                "creation_action_geometry",
            )
        }

    averaged_rows: list[dict[str, Any]] = []
    single_rows: list[dict[str, Any]] = []
    stacking_loop_rows: list[dict[str, Any]] = []
    stacking_world_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    r1_checks: list[dict[str, Any]] = []
    stage1_checks: list[dict[str, Any]] = []
    two_stage_checks: list[dict[str, Any]] = []
    identity_gates: list[dict[str, Any]] = []
    fit_gates: list[dict[str, Any]] = []
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
            validation_rows.extend(context["validation_rows"])

            # ---- law + realization-0 reassembly identity gates ----
            oracle_basis, parameters = _rebuild_law(world, spec, seed)
            _assert_law_identity(context, oracle_basis, parameters)
            panels0 = _realization_cal_sel(
                world, spec, seed, 0, oracle_basis, parameters
            )
            identity_gates.append(
                _assert_realization0_panels(context, panels0)
            )

            # ---- floor arm (R=1 asserted before R>1 inside) ----
            (
                avg_rows,
                sng_rows,
                r1_check,
                gates,
                events_cache,
            ) = _floor_rows_for_world_rep(
                context,
                spec=spec,
                stored_1x=stored_1x,
                oracle_basis=oracle_basis,
                parameters=parameters,
            )
            averaged_rows.extend(avg_rows)
            single_rows.extend(sng_rows)
            r1_checks.append(r1_check)
            fit_gates.append(
                {
                    "world": world,
                    "repetition": repetition,
                    **gates,
                }
            )

            # ---- stacking arm ----
            (
                loop_rows,
                world_rows,
                stage1_check,
                two_stage_check,
                structure,
            ) = _stacking_rows_for_world_rep(
                context,
                leg4_arm2=leg4_arm2,
                leg5_two_stage_rows=leg5_rows,
                events_by_realization=events_cache,
            )
            stacking_loop_rows.extend(loop_rows)
            stacking_world_rows.extend(world_rows)
            stage1_checks.append(stage1_check)
            two_stage_checks.append(two_stage_check)
            structures.append(structure)

            by_arm = {
                row["arm"]: round(row["loop_action_geometry"], 3)
                for row in world_rows
            }
            pooled_r8 = float(
                pd.DataFrame(
                    [
                        row
                        for row in avg_rows
                        if row["method"] == "avg"
                        and row["R"] == MAX_R
                        and not row["degenerate_reference"]
                    ]
                )["e_d_paired"].median()
            )
            print(
                f"[leg7] rep={repetition} world={world} stacking {by_arm} "
                f"floor R=8 median {pooled_r8:.4f} r1-assert max "
                f"{r1_check['max_abs_difference']:.2e} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = f"rep{repetitions[0]}-{repetitions[-1]}"
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(averaged_rows).to_csv(
        args.output / f"partial_floor_avg_rows_{suffix}.csv", index=False
    )
    pd.DataFrame(single_rows).to_csv(
        args.output / f"partial_floor_single_rows_{suffix}.csv", index=False
    )
    pd.DataFrame(stacking_loop_rows).to_csv(
        args.output / f"partial_stacking_per_loop_{suffix}.csv", index=False
    )
    pd.DataFrame(stacking_world_rows).to_csv(
        args.output / f"partial_stacking_world_rep_{suffix}.csv", index=False
    )
    pd.DataFrame(validation_rows).to_csv(
        args.output / f"partial_v2_validation_{suffix}.csv", index=False
    )
    pd.DataFrame(r1_checks).to_csv(
        args.output / f"partial_r1_check_{suffix}.csv", index=False
    )
    pd.DataFrame(stage1_checks).to_csv(
        args.output / f"partial_stage1_check_{suffix}.csv", index=False
    )
    pd.DataFrame(two_stage_checks).to_csv(
        args.output / f"partial_two_stage_check_{suffix}.csv", index=False
    )
    gates_payload = {
        "identity_gates_realization0": identity_gates,
        "fit_gates": fit_gates,
        "stacking_structure": structures,
        "repetitions": list(repetitions),
        "worlds": worlds,
    }
    with (args.output / f"partial_gates_{suffix}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(gates_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"[chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# assembly -- refuse missing/duplicate cells, adjudicate from rows only
# ---------------------------------------------------------------------------


def _concat_partials(output: Path, stem: str) -> pd.DataFrame:
    paths = sorted(glob.glob(str(output / f"partial_{stem}_rep*.csv")))
    if not paths:
        raise RuntimeError(f"no partial CSVs found for {stem} under {output}")
    return pd.concat(
        [pd.read_csv(path) for path in paths], ignore_index=True
    )


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


def _slopes_over_r(medians: dict[int, float]) -> dict[str, Any]:
    r_values = sorted(medians)
    x = np.log(np.asarray(r_values, dtype=float))
    y = np.log(np.asarray([medians[key] for key in r_values], dtype=float))
    overall = np.polyfit(x, y, 1) if len(r_values) >= 2 else (np.nan, np.nan)
    tail_values = [key for key in r_values if key >= 2]
    if len(tail_values) >= 2:
        tx = np.log(np.asarray(tail_values, dtype=float))
        ty = np.log(
            np.asarray([medians[key] for key in tail_values], dtype=float)
        )
        tail = np.polyfit(tx, ty, 1)
    else:
        tail = (np.nan, np.nan)
    segments = {
        f"{r_values[index]}->{r_values[index + 1]}": float(
            (y[index + 1] - y[index]) / (x[index + 1] - x[index])
        )
        for index in range(len(r_values) - 1)
    }
    return {
        "overall_slope": float(overall[0]),
        "overall_intercept": float(overall[1]),
        "tail_slope": float(tail[0]),
        "segment_slopes": segments,
    }


def _r_scaling_summary(
    frame: pd.DataFrame,
    method: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Author-level medians by R and log-log slopes (Leg-4b semantics)."""
    subset = frame[
        (frame["method"] == method) & (~frame["degenerate_reference"])
    ].copy()
    author_level = (
        subset.groupby(["world", "repetition", "author", "R"])
        .agg(
            e_d_paired=("e_d_paired", "mean"),
            e_d_frozen=("e_d_frozen", "mean"),
            e_d_true=("e_d_true", "mean"),
            e_orc_true=("e_orc_true", "mean"),
            orc_self_drift=("orc_self_drift", "mean"),
            reference_gap=("reference_gap", "mean"),
        )
        .reset_index()
    )
    author_level["disc_excess"] = (
        author_level["e_d_true"] - author_level["e_orc_true"]
    )
    metrics = (
        "e_d_paired",
        "e_d_true",
        "e_orc_true",
        "e_d_frozen",
        "disc_excess",
    )
    summary_rows = []
    analysis: dict[str, Any] = {}
    worlds = sorted(author_level["world"].unique())
    for scope in [*worlds, "POOLED"]:
        scoped = (
            author_level
            if scope == "POOLED"
            else author_level[author_level["world"] == scope]
        )
        medians: dict[str, dict[int, float]] = {name: {} for name in metrics}
        for r_value, group in scoped.groupby("R"):
            row = {
                "method": method,
                "world": scope,
                "R": int(r_value),
                "n_author_reps": int(len(group)),
            }
            for name in metrics:
                value = float(group[name].median())
                row[f"median_{name}"] = value
                row[f"iqr_low_{name}"] = float(group[name].quantile(0.25))
                row[f"iqr_high_{name}"] = float(group[name].quantile(0.75))
                medians[name][int(r_value)] = value
            summary_rows.append(row)
        scope_analysis: dict[str, Any] = {
            "median_reference_gap": float(scoped["reference_gap"].median()),
            "median_orc_self_drift_by_R": {
                str(int(r_value)): float(group["orc_self_drift"].median())
                for r_value, group in scoped.groupby("R")
            },
        }
        for name in metrics:
            slopes = _slopes_over_r(medians[name])
            entry: dict[str, Any] = {
                "medians_by_R": {
                    str(key): value
                    for key, value in sorted(medians[name].items())
                },
                **slopes,
            }
            if name == "e_d_paired":
                entry["floor_at_R8"] = medians[name].get(MAX_R)
                r1_value = medians[name].get(1)
                entry["r_half_reference_curve"] = {
                    str(r): (
                        float(r1_value / np.sqrt(r))
                        if r1_value is not None
                        else float("nan")
                    )
                    for r in R_GRID
                }
            scope_analysis[name] = entry
        analysis[scope] = scope_analysis
    return pd.DataFrame(summary_rows), analysis


def _assemble(args: argparse.Namespace, config: dict[str, Any]) -> None:
    stored_1x, leg4_decision = _load_leg4_reference()
    leg5_two_stage, _ = _load_leg5_reference()
    repetitions = int(config["repetitions"])
    worlds = list(LOOP_WORLDS)
    n_world_reps = len(worlds) * repetitions
    authors = 16
    n_author_views = n_world_reps * 2 * authors

    averaged = _concat_partials(args.output, "floor_avg_rows")
    singles = _concat_partials(args.output, "floor_single_rows")
    stacking_loops = _concat_partials(args.output, "stacking_per_loop")
    stacking_worlds = _concat_partials(args.output, "stacking_world_rep")
    validation = _concat_partials(args.output, "v2_validation")
    r1_checks = _concat_partials(args.output, "r1_check")
    stage1_checks = _concat_partials(args.output, "stage1_check")
    two_stage_checks = _concat_partials(args.output, "two_stage_check")
    gate_paths = sorted(
        glob.glob(str(args.output / "partial_gates_rep*.json"))
    )
    gates = []
    for path in gate_paths:
        with open(path, "r", encoding="utf-8") as handle:
            gates.append(json.load(handle))

    _refuse_bad_cells(
        averaged,
        ["world", "repetition", "author", "view", "R", "method"],
        n_author_views * len(R_GRID) * 2,
        "floor averaged rows",
    )
    _refuse_bad_cells(
        singles,
        ["world", "repetition", "author", "view", "realization"],
        n_author_views * MAX_R,
        "floor single rows",
    )
    _refuse_bad_cells(
        stacking_loops,
        ["arm", "world", "repetition", "author", "view"],
        len(STACKING_ARMS) * n_author_views,
        "stacking loop rows",
    )
    _refuse_bad_cells(
        stacking_worlds,
        ["arm", "world", "repetition"],
        len(STACKING_ARMS) * n_world_reps,
        "stacking world-rep rows",
    )
    for label, frame in (
        ("r1 checks", r1_checks),
        ("stage1 checks", stage1_checks),
        ("two_stage checks", two_stage_checks),
    ):
        _refuse_bad_cells(frame, ["world", "repetition"], n_world_reps, label)
    if not bool(r1_checks["flags_equal"].all()):
        raise RuntimeError("assembled R=1 checks contain unequal flags")
    r1_max = float(r1_checks["max_abs_difference"].max())
    if r1_max > ROW_TOLERANCE:
        raise RuntimeError(f"assembled R=1 reproduction max diff {r1_max:.3e}")
    stage1_max = float(
        np.maximum(
            stage1_checks["max_scaled_e_loop_difference"],
            stage1_checks["max_scaled_e_d_atom_difference"],
        ).max()
    )
    stage1_strict = float(
        np.maximum(
            stage1_checks["max_abs_e_loop_difference_nonamplified"],
            stage1_checks["max_abs_e_d_atom_difference_nonamplified"],
        ).max()
    )
    two_stage_max = float(
        np.maximum(
            two_stage_checks["max_scaled_e_loop_difference"],
            two_stage_checks["max_scaled_e_d_atom_difference"],
        ).max()
    )
    two_stage_strict = float(
        np.maximum(
            two_stage_checks["max_abs_e_loop_difference_nonamplified"],
            two_stage_checks["max_abs_e_d_atom_difference_nonamplified"],
        ).max()
    )
    if stage1_max > ROW_TOLERANCE or two_stage_max > ROW_TOLERANCE:
        raise RuntimeError(
            f"assembled stage1/two_stage reproduction diffs {stage1_max:.3e}"
            f"/{two_stage_max:.3e}"
        )
    stage1_flips = int(
        stacking_loops[stacking_loops["arm"] == "arm2_stage1_125"][
            "model_flip"
        ].sum()
    )
    if stage1_flips != leg5.STAGE1_EXPECTED_FLIPS:
        raise RuntimeError(
            f"stage-1 battery flips {stage1_flips} != "
            f"{leg5.STAGE1_EXPECTED_FLIPS}"
        )
    identity_gates = [
        gate
        for chunk in gates
        for gate in chunk["identity_gates_realization0"]
    ]
    if len(identity_gates) != n_world_reps:
        raise RuntimeError(
            "realization-0 identity gates missing: "
            f"{len(identity_gates)} != {n_world_reps}"
        )
    fit_gates = [
        gate for chunk in gates for gate in chunk["fit_gates"]
    ]

    # ---- floor analysis, both methods ----
    summaries = []
    floor_analysis: dict[str, Any] = {}
    for method in ("avg", "joint"):
        summary, analysis = _r_scaling_summary(averaged, method)
        summaries.append(summary)
        floor_analysis[method] = analysis
    floor_summary_frame = pd.concat(summaries, ignore_index=True)

    # decision-level cross-check: R=1 pooled median == Leg 4 persisted 1x
    persisted_1x = float(
        leg4_decision["part_4b"]["scaling"]["POOLED"]["e_d_paired"][
            "medians_by_budget"
        ]["1.0"]
    )
    pooled_avg = floor_analysis["avg"]["POOLED"]["e_d_paired"]
    r1_pooled = float(pooled_avg["medians_by_R"]["1"])
    if abs(r1_pooled - persisted_1x) > ROW_TOLERANCE:
        raise RuntimeError(
            f"pooled R=1 median {r1_pooled} diverges from Leg 4 persisted "
            f"1x median {persisted_1x}"
        )

    overall_slope = float(pooled_avg["overall_slope"])
    floor_r8 = float(pooled_avg["medians_by_R"]["8"])
    lean_a_hold = bool(
        LEAN_A_BAND[0] <= overall_slope <= LEAN_A_BAND[1]
    )
    lean_b_hold = bool(floor_r8 <= LEAN_B_BAR)
    pivot_triggered = bool(overall_slope > PIVOT_SLOPE_BAR)

    per_world_floor = {
        world: {
            "medians_by_R": floor_analysis["avg"][world]["e_d_paired"][
                "medians_by_R"
            ],
            "overall_slope": float(
                floor_analysis["avg"][world]["e_d_paired"]["overall_slope"]
            ),
            "tail_slope": float(
                floor_analysis["avg"][world]["e_d_paired"]["tail_slope"]
            ),
            "floor_at_R8": float(
                floor_analysis["avg"][world]["e_d_paired"]["floor_at_R8"]
            ),
        }
        for world in worlds
    }

    # ---- pivot profile (computed in all cases; cited under the pivot) ----
    pooled_orc = floor_analysis["avg"]["POOLED"]["e_orc_true"]
    pooled_true = floor_analysis["avg"]["POOLED"]["e_d_true"]
    pooled_gap = floor_analysis["avg"]["POOLED"]["disc_excess"]
    pivot_profile = {
        "oracle_own_error_medians_by_R": pooled_orc["medians_by_R"],
        "oracle_own_error_overall_slope": float(
            pooled_orc["overall_slope"]
        ),
        "oracle_own_error_flat": bool(
            abs(float(pooled_orc["overall_slope"])) < 0.15
        ),
        "disc_true_medians_by_R": pooled_true["medians_by_R"],
        "disc_true_overall_slope": float(pooled_true["overall_slope"]),
        "estimator_minus_oracle_gap_medians_by_R": pooled_gap[
            "medians_by_R"
        ],
        "estimator_minus_oracle_gap_overall_slope": float(
            pooled_gap["overall_slope"]
        ),
        "reading": (
            "gap closes with R -> discovered-side excess is realization "
            "variance; flat gap -> basis-mismatch bias; flat oracle error "
            "-> law-level bias shared by both bases"
        ),
    }

    # ---- joint-vs-avg comparison ----
    pooled_joint = floor_analysis["joint"]["POOLED"]["e_d_paired"]
    avg_vs_joint = {
        "avg_medians_by_R": pooled_avg["medians_by_R"],
        "joint_medians_by_R": pooled_joint["medians_by_R"],
        "joint_overall_slope": float(pooled_joint["overall_slope"]),
        "max_abs_pooled_median_difference": float(
            max(
                abs(
                    float(pooled_avg["medians_by_R"][str(r)])
                    - float(pooled_joint["medians_by_R"][str(r)])
                )
                for r in R_GRID
            )
        ),
    }

    # ---- stacking adjudication ----
    arm_summaries = {
        arm: leg4._arm_summary(stacking_loops, stacking_worlds, arm)
        for arm in STACKING_ARMS
    }
    ravg = arm_summaries["two_stage_ravg_r4"]
    pooled_ravg = float(ravg["pooled_loop_geometry"])
    leg5_per_world = leg5_two_stage["per_world_loop_geometry"]
    per_world_gain = {
        world: float(
            ravg["per_world_loop_geometry"][world] - leg5_per_world[world]
        )
        for world in worlds
    }
    pinned_values = {
        world: float(ravg["per_world_loop_geometry"][world])
        for world in PINNED_WORLDS
    }
    lean_c_pooled_hold = bool(pooled_ravg >= LEAN_C_POOLED_BAR)
    lean_c_pinned_hold = bool(
        all(value >= LEAN_C_WORLD_BAR for value in pinned_values.values())
    )
    lean_c_hold = bool(lean_c_pooled_hold and lean_c_pinned_hold)

    if pivot_triggered:
        outcome = (
            "PIVOT_PER_REALIZATION_VARIANCE_INTERPRETATION_DIES_"
            "NEXT_ORACLE_VS_ESTIMATOR_BIAS_DECOMPOSITION"
        )
        interpretation_verdict = "DEAD"
    elif lean_a_hold:
        outcome = (
            "R_SCALING_IN_REGISTERED_BAND_"
            "PER_REALIZATION_VARIANCE_INTERPRETATION_CONFIRMED"
        )
        interpretation_verdict = "CONFIRMED"
    else:
        outcome = (
            "INTERMEDIATE_R_SCALING_"
            "PARTIAL_VARIANCE_PARTIAL_BIAS_MIXED_VERDICT"
        )
        interpretation_verdict = "MIXED"

    averaged = averaged.sort_values(
        ["method", "world", "repetition", "author", "view", "R"]
    )
    singles = singles.sort_values(
        ["world", "repetition", "author", "view", "realization"]
    )
    stacking_loops = stacking_loops.sort_values(
        ["arm", "world", "repetition", "author", "view"]
    )
    stacking_worlds = stacking_worlds.sort_values(
        ["arm", "world", "repetition"]
    )
    averaged.to_csv(args.output / "floor_avg_rows.csv", index=False)
    singles.to_csv(args.output / "floor_single_rows.csv", index=False)
    floor_summary_frame.to_csv(
        args.output / "floor_scaling_summary.csv", index=False
    )
    stacking_loops.to_csv(
        args.output / "stacking_per_loop_metrics.csv", index=False
    )
    stacking_worlds.to_csv(
        args.output / "stacking_world_rep_metrics.csv", index=False
    )
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    r1_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "r1_reproduction_check.csv", index=False
    )
    stage1_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "stage1_leg4_crosscheck.csv", index=False
    )
    two_stage_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "two_stage_leg5_crosscheck.csv", index=False
    )

    n_degenerate = int(
        averaged[
            (averaged["method"] == "avg") & (averaged["R"] == 1)
        ]["degenerate_reference"].sum()
    )
    single_drift = singles[
        (~singles["degenerate_reference"]) & (singles["realization"] > 0)
    ]
    decision = {
        "estimand_id": "SUICA_M4_D_LEG7_REALIZATION_AVERAGING",
        "tier": "EXPLORATORY",
        "config_seed": int(config["seed"]),
        "outcome": outcome,
        "interpretation_verdict": interpretation_verdict,
        "design": {
            "floor_arms": (
                "R in {1,2,4,8} independent path realizations per "
                "world-rep under the identical frozen law (condition "
                "panels, mechanism parameters, oracle basis bit-identical; "
                "path-panel seeds offset by r*1_000_000_007; realization 0 "
                "= the exact battery panels), event budget fixed at 1x "
                "(120 events) per realization; D per realization at the "
                "oracle-forced route (Leg-4b protocol, chart/bases frozen "
                "at V2 1x); primary 'avg' = simple mean of the R "
                "D-estimates per side; secondary 'joint' = one pooled V2 "
                "hazard fit over the R panels; nested realization prefixes "
                "across the R grid"
            ),
            "primary_metric": (
                "e_d_paired(R) = ||D_disc_avg - D_orc_avg|| / "
                "||D_orc_avg|| (program-standard paired error; at R=1 "
                "coincides bit-exactly with Leg 4b's 1x e_d_paired)"
            ),
            "companions": [
                "e_d_true",
                "e_orc_true",
                "e_d_frozen",
                "orc_self_drift",
                "disc_excess (e_d_true - e_orc_true, author-level)",
            ],
            "stacking_arm": (
                "two-stage (Leg 5 construction bit-exact: stage 1 "
                f"penalized route selection at lambda={STAGE1_LAMBDA}, "
                "stage 2 unpenalized refit at the stage-1 route) + "
                f"realization-averaged stage-2 D over R={STACKING_R} "
                "panels (realization 0 = Leg 5's exact stage-2 fit, "
                "asserted; realizations 1-3 fresh unpenalized fits at the "
                "same route); loop = D_avg @ G_v2 @ C_v2; compared against "
                "Leg 5's persisted pooled .7605 and per-world values"
            ),
            "r_grid": list(R_GRID),
            "stacking_R": STACKING_R,
            "events_per_realization": int(
                M4ChartEcologySpec(**config["base_spec"]).events
            ),
        },
        "faithfulness": {
            "law_identity": (
                "reassembled oracle basis (3 roles) + all 8 author-"
                "parameter arrays bit-identical to battery truth on all "
                f"{n_world_reps} world-reps (asserted, RuntimeError on any "
                "mismatch)"
            ),
            "realization0_panel_identity": {
                "world_reps_gated": len(identity_gates),
                "all_hold": bool(
                    all(gate["identity_holds"] for gate in identity_gates)
                ),
                "fields_per_gate": 32,
            },
            "r1_reproduction_vs_leg4": {
                "reference": "results/m4_d_dleg_floor/dleg_budget_rows.csv "
                "(budget == 1.0 rows)",
                "world_reps_checked": int(len(r1_checks)),
                "rows_compared": int(r1_checks["rows_compared"].sum()),
                "max_abs_difference": r1_max,
                "all_flags_equal": bool(r1_checks["flags_equal"].all()),
                "pooled_r1_median_equals_persisted_1x": True,
            },
            "r0_fit_identity_gates": {
                "max_orc_refit_gap": float(
                    max(
                        gate["orc_refit_identity_max_gap_r0"]
                        for gate in fit_gates
                    )
                ),
                "max_disc_forced_gap": float(
                    max(
                        gate["disc_forced_identity_max_gap_r0"]
                        for gate in fit_gates
                    )
                ),
                "true_d_unit_check_max_gap": float(
                    max(
                        gate["true_d_unit_check_max_gap"]
                        for gate in fit_gates
                    )
                ),
            },
            "stage1_reproduction_vs_leg4": {
                "world_reps_checked": int(len(stage1_checks)),
                "max_scaled_difference": stage1_max,
                "max_abs_difference_nonamplified_rows": stage1_strict,
                "amplified_degenerate_rows": int(
                    stage1_checks["amplified_rows"].sum()
                ),
                "all_flags_equal": bool(stage1_checks["flags_equal"].all()),
                "flips_total_equals_73": bool(
                    stage1_flips == leg5.STAGE1_EXPECTED_FLIPS
                ),
            },
            "two_stage_reproduction_vs_leg5": {
                "reference": "results/m4_d_two_stage/per_loop_metrics.csv "
                "(two_stage rows)",
                "world_reps_checked": int(len(two_stage_checks)),
                "max_scaled_difference": two_stage_max,
                "max_abs_difference_nonamplified_rows": two_stage_strict,
                "amplified_degenerate_rows": int(
                    two_stage_checks["amplified_rows"].sum()
                ),
                "all_flags_equal": bool(
                    two_stage_checks["flags_equal"].all()
                ),
                "tolerance_note": (
                    "scale-aware: |diff| <= 1e-9 * max(1, |reference|); "
                    "strict-absolute on all rows with a nonzero oracle "
                    "loop; on oracle-degenerate rows e_loop is the "
                    "1e-12-clamped amplification (~1e+11) and one observed "
                    "ULP wobble (1.2e-16 relative, BLAS-level, present in "
                    "a fresh minimal process) is tolerated"
                ),
            },
            "v2_validation_max_abs_difference": (
                float(validation["abs_difference"].max())
                if len(validation)
                else float("nan")
            ),
        },
        "floor": {
            "pooled_avg": {
                "medians_by_R": pooled_avg["medians_by_R"],
                "overall_slope": overall_slope,
                "tail_slope": float(pooled_avg["tail_slope"]),
                "segment_slopes": pooled_avg["segment_slopes"],
                "floor_at_R8": floor_r8,
                "r_half_reference_curve": pooled_avg[
                    "r_half_reference_curve"
                ],
                "leg4_1x_persisted": persisted_1x,
            },
            "pooled_joint": {
                "medians_by_R": pooled_joint["medians_by_R"],
                "overall_slope": float(pooled_joint["overall_slope"]),
                "tail_slope": float(pooled_joint["tail_slope"]),
            },
            "avg_vs_joint": avg_vs_joint,
            "per_world_avg": per_world_floor,
            "companions_pooled_avg": {
                "e_d_true_medians_by_R": pooled_true["medians_by_R"],
                "e_d_true_overall_slope": float(
                    pooled_true["overall_slope"]
                ),
                "e_orc_true_medians_by_R": pooled_orc["medians_by_R"],
                "e_orc_true_overall_slope": float(
                    pooled_orc["overall_slope"]
                ),
                "disc_excess_medians_by_R": pooled_gap["medians_by_R"],
            },
            "single_realization_drift": {
                "median_orc_self_drift_fresh_realizations": float(
                    single_drift["orc_self_drift"].median()
                ),
                "iqr": [
                    float(single_drift["orc_self_drift"].quantile(0.25)),
                    float(single_drift["orc_self_drift"].quantile(0.75)),
                ],
                "median_single_e_d_paired_fresh": float(
                    single_drift["e_d_paired"].median()
                ),
            },
            "degenerate_reference_author_views": n_degenerate,
            "scaling_analysis": floor_analysis,
        },
        "pivot_profile": pivot_profile,
        "stacking": {
            "arms": arm_summaries,
            "leg5_two_stage_persisted": {
                "pooled_loop_geometry": float(
                    leg5_two_stage["pooled_loop_geometry"]
                ),
                "per_world_loop_geometry": leg5_per_world,
                "flips_total": int(leg5_two_stage["flips_total"]),
                "median_e_d": float(leg5_two_stage["median_e_d"]),
                "source": "results/m4_d_two_stage/decision.json",
            },
            "two_stage_ravg_r4_vs_leg5": {
                "pooled_gain": float(
                    pooled_ravg
                    - float(leg5_two_stage["pooled_loop_geometry"])
                ),
                "per_world_gain": per_world_gain,
                "pinned_worlds": list(PINNED_WORLDS),
                "pinned_world_values": pinned_values,
            },
            "fresh_ravg_fits_total": int(
                sum(
                    structure["fresh_ravg_fits"]
                    for chunk in gates
                    for structure in chunk["stacking_structure"]
                )
            ),
        },
        "lean_a": {
            "registered": (
                "THE CONFIRMATION TEST of the 4b interpretation: pooled "
                "log-log slope of the floor vs R in [-.65, -.35] (at R=8, "
                ".39 -> ~.14 if exactly R^(-1/2))"
            ),
            "value": overall_slope,
            "band": list(LEAN_A_BAND),
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": "at R=8 the pooled floor <= .20",
            "value": floor_r8,
            "bar": LEAN_B_BAR,
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered": (
                "two-stage + realization-averaged D at R=4: pooled loop "
                "geometry >= .82 with the two floor-pinned worlds "
                "(partition .6527, compensation .6209 under Leg 5) both "
                "crossing .70"
            ),
            "pooled_value": pooled_ravg,
            "pooled_bar_hold": lean_c_pooled_hold,
            "pinned_world_values": pinned_values,
            "pinned_crossing_hold": lean_c_pinned_hold,
            "hold": lean_c_hold,
        },
        "pivot_if": {
            "registered": (
                "the floor is R-INVARIANT too (slope > -.15) -> the "
                "'per-realization variance' interpretation of Leg 4b is "
                "WRONG (the planner's registered miss, recorded plainly); "
                "the floor is estimator-family bias or a "
                "world-identifiability limit; next instrument = "
                "oracle-vs-estimator bias decomposition at increasing R"
            ),
            "pooled_overall_slope": overall_slope,
            "bar": PIVOT_SLOPE_BAR,
            "triggered": pivot_triggered,
            "declaration": (
                "PER_REALIZATION_VARIANCE_INTERPRETATION_DEAD_"
                "FLOOR_IS_BIAS_OR_IDENTIFIABILITY"
                if pivot_triggered
                else "not triggered"
            ),
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "estimator diagnostics (oracle-basis fits, oracle-forced "
            "routes, generator-law derivatives, and generator-privileged "
            "fresh realizations of the frozen law are consumed as "
            "references), so nothing here is an operational rescue of "
            "chart transport or a reopened gate; realization averaging "
            "requires R independent draws of the same law and is not "
            "available to any single-realization observer; the V1/V2 and "
            "C3.3 NO-GO decisions stand; no natural-text, personality, "
            "emotion, or clinical claim; EXPLORATORY tier under the "
            "2026-08-01 open-exploration directive."
        ),
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "outcome": outcome,
                "interpretation_verdict": interpretation_verdict,
                "pooled_medians_by_R": pooled_avg["medians_by_R"],
                "overall_slope": overall_slope,
                "floor_at_R8": floor_r8,
                "lean_a_hold": lean_a_hold,
                "lean_b_hold": lean_b_hold,
                "lean_c_hold": lean_c_hold,
                "pivot_triggered": pivot_triggered,
                "pooled_stacking_ravg_r4": pooled_ravg,
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
        default=ROOT / "results" / "m4_d_realization_averaging",
    )
    parser.add_argument("--chunk-start", type=int, default=None)
    parser.add_argument("--chunk-stop", type=int, default=None)
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    started = time.time()
    config = leg3._load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.smoke:
        args.output = ROOT / "results" / "_smoke_m4_d_realization_averaging"
        worlds = list(LOOP_WORLDS)[:2]
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
    repetitions = tuple(range(args.chunk_start, args.chunk_stop))
    _run_chunk(args, config, spec, repetitions, list(LOOP_WORLDS))
    print(f"[done] total {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
