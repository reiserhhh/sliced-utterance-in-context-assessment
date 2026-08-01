#!/usr/bin/env python3
"""M4-D Leg 5: two-stage route-then-refit estimation (decouple the trade-off law).

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 5 -- two-stage route-then-refit estimation", 2026-08-02, before this
run). All V2 replay and arm-2 ridge machinery is IMPORTED from
scripts/run_suica_m4_d_overspan_control_leg3.py and
scripts/run_suica_m4_d_dleg_floor_leg4.py (bit-exact reuse; Legs 3/4
validated the replay chain to ~1e-16); nothing there is reimplemented.

Target: the loop-wall synthesis's TRADE-OFF LAW (route fidelity vs creation
fidelity compete at any single lambda; docs/SUICA_M4_D_LOOP_WALL_SYNTHESIS.md
section 2). If they compete at a single lambda, decouple them:

PRIMARY ARM (two_stage):
- STAGE 1 = Leg 4a's winning configuration EXACTLY: the arm-2 penalized
  hazard candidate/selection/final flow at the route-accuracy-selected ridge
  lambda = .125 (interior optimum; results/m4_d_dleg_floor/decision.json).
  By construction stage-1 flips must equal 73. Per world-rep the freshly
  computed stage-1 rows are ASSERTED (<= 1e-9 on e_loop/e_d_atom, flip and
  route flags exactly equal) against Leg 4's persisted per_loop_metrics.csv
  BEFORE stage 2 runs on that world-rep; the battery total is asserted
  == 73 before adjudication.
- STAGE 2 = at each author-view's stage-1-selected route, refit the creation
  derivative with the V2 BASELINE (unpenalized) estimator: V2 final-refit
  semantics (_fit_hazard_candidate on the combined calibration+selection
  panels, hazard ridge .005, 30 IRLS iterations) at the FIXED stage-1 route;
  no selection anywhere in stage 2. Where the stage-1 route coincides with
  arm 0's V2-selected route, the stage-2 refit is bit-identical to arm 0's
  final hazard fit by construction and is reused directly.
  Coupling note (pre-coded reading of the registered "(and GC legs where the
  estimator couples them)" clause): in this estimator the GC legs
  (choice/response fits) never consume the hazard fit -- the arm-2 stack
  already shares C/G/choice_action with the V2 base stack -- so the clause
  is vacuous here: stage 2 refits exactly the hazard/D leg, and C/G are the
  V2 baseline legs on every arm by construction.
- Loop transport recomputed from stage-2 fits (D_stage2 @ G_v2 @ C_v2);
  creation_action likewise from the stage-2 hazard fit.

SECONDARY ARM (single_stage_025): the full 5-world x 8-repetition battery at
single-stage lambda = .025 -- the Leg-4a discovery-loop-geometry peak (.6928
on discovery reps), one grid point, cheap. Licenses the discovery
observation Leg 4's report explicitly left unlicensed ("No battery run at
.025 exists").

Baselines in every table: arm0_v2 (196 flips, pooled .6519), Leg 3
arm2@.005 (148, .6886; persisted, not recomputed), Leg 4a arm2@.125
(73, .6901; recomputed here as stage 1 and asserted against persisted rows).

Measured per arm x world x repetition x author x view (persisted per-row):
Leg 1's D-zero flip definition, route-name mismatch, e_loop, chart-free
e_d_atom, GC-composite and leg-swap errors, D/loop norms. Per arm: flips,
author-level median e_d, pooled + per-world loop geometry (V2's own
statistic), worlds >= .75 count, non-flip-row loop error, and within-cell
rho(D-improvement, loop-improvement) -- computed both against arm 0
(program-standard) and against stage 1 (the within-construction question).

Registered leans (adjudication statistics pre-coded here):
- (a) two_stage median e_d <= .55 (author-level train/test-mean e_d_atom on
  oracle-nondegenerate rows, pooled battery median -- the statistic whose
  prior values are .4869 arm0 / .7830 stage 1);
- (b) two_stage pooled loop geometry >= .70 (mean loop_action_geometry over
  the 40 world-reps) -- THE DECISIVE TEST, missed twice by ~.01
  (.6886 Leg 3, .6901 Leg 4a);
- (c) two_stage worlds with 8-rep mean loop geometry >= .75: count in
  {2, 3} of 5 (registered band; currently 2/5 under stage 1).
Pivot-if (registered): (a) holds but (b) misses -> D-quality-at-fixed-route
was NOT the binding path on route-stabilized rows, the residual wall on
non-flip rows is the Leg-4b realization-variance floor already at work at
1x; the two-stage construction is declared EXHAUSTED and the wall passes
fully to the design-change track (C3.3 excitation). Recorded plainly as a
registered, honorable outcome.
"""
from __future__ import annotations

import argparse
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

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _fit_hazard_candidate,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)

LOOP_WORLDS = leg3.LOOP_WORLDS
ARMS = ("arm0_v2", "arm2_stage1_125", "two_stage", "single_stage_025")
STAGE1_LAMBDA = 0.125
SECONDARY_LAMBDA = 0.025
STAGE1_EXPECTED_FLIPS = 73
ROW_TOLERANCE = 1e-9
LEAN_A_BAR = 0.55
LEAN_B_BAR = 0.70
LEAN_C_BAND = (2, 3)


# ---------------------------------------------------------------------------
# stage 2 -- V2 unpenalized final-refit at the stage-1-selected route
# ---------------------------------------------------------------------------


def _two_stage_stack(
    context: dict[str, Any],
    view: str,
    author: int,
    stage1_stack: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    """Stage-2 stack; returns (stack, fresh_refit_performed)."""
    base = context["base_stacks"][view][author]
    route = stage1_stack["selected_model"]
    calibration, selection, evaluation = context["flat"][(view, author)]
    basis = context["v2_basis"]
    if route == base["selected_model"]:
        # V2's final refit at this route is exactly base's final hazard fit.
        final = base["final_hazard"]
        fresh = False
    else:
        final = _fit_hazard_candidate(
            [
                (calibration, basis["calibration"]),
                (selection, basis["selection"]),
            ],
            model=route,
            ridge=context["fit_kwargs"]["hazard_ridge"],
            iterations=context["fit_kwargs"]["logistic_iterations"],
        )
        fresh = True
    return (
        leg3._derived_from_hazard(base, final, route, evaluation, basis),
        fresh,
    )


# ---------------------------------------------------------------------------
# stage-1 faithfulness vs Leg 4 persisted rows
# ---------------------------------------------------------------------------


def _load_leg4_arm2() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_dleg_floor" / "per_loop_metrics.csv"
    if not path.exists():
        raise RuntimeError(
            "Leg 4 persisted per-loop rows are required for the registered "
            f"stage-1 assert and were not found: {path}"
        )
    stored = pd.read_csv(path)
    arm2 = stored[stored["arm"] == "arm2_penalized"].copy()
    total = int(arm2["model_flip"].sum())
    if total != STAGE1_EXPECTED_FLIPS:
        raise RuntimeError(
            f"Leg 4 persisted arm2 flips {total} != "
            f"{STAGE1_EXPECTED_FLIPS}; reference battery is not the one "
            "registered"
        )
    return arm2


def _assert_stage1_rows(
    rows: list[dict[str, Any]],
    leg4_arm2: pd.DataFrame,
    world: str,
    repetition: int,
) -> dict[str, Any]:
    """Per world-rep bit-tight check of freshly computed stage-1 rows."""
    mine = pd.DataFrame(rows)
    stored = leg4_arm2[
        (leg4_arm2["world"] == world) & (leg4_arm2["repetition"] == repetition)
    ]
    keys = ["world", "repetition", "author", "view"]
    merged = stored.merge(mine, on=keys, suffixes=("_leg4", "_leg5"))
    if len(merged) != len(mine) or len(merged) != len(stored):
        raise RuntimeError(
            f"stage-1 rows misaligned with Leg 4 on {world} rep "
            f"{repetition}: {len(merged)} matches vs mine {len(mine)} / "
            f"stored {len(stored)}"
        )
    max_e_loop = float(
        np.max(np.abs(merged["e_loop_leg4"] - merged["e_loop_leg5"]))
    )
    max_e_d = float(
        np.max(np.abs(merged["e_d_atom_leg4"] - merged["e_d_atom_leg5"]))
    )
    flags_equal = bool(
        (merged["model_flip_leg4"] == merged["model_flip_leg5"]).all()
        and (
            merged["selected_model_arm_leg4"]
            == merged["selected_model_arm_leg5"]
        ).all()
    )
    if max_e_loop > ROW_TOLERANCE or max_e_d > ROW_TOLERANCE or not flags_equal:
        raise RuntimeError(
            f"stage-1 replay diverges from Leg 4 on {world} rep "
            f"{repetition}: max|e_loop diff|={max_e_loop:.3e} "
            f"max|e_d diff|={max_e_d:.3e} flags_equal={flags_equal}"
        )
    return {
        "world": world,
        "repetition": repetition,
        "rows_compared": int(len(merged)),
        "max_abs_e_loop_difference": max_e_loop,
        "max_abs_e_d_difference": max_e_d,
        "flags_equal": flags_equal,
        "flips": int(mine["model_flip"].sum()),
    }


# ---------------------------------------------------------------------------
# mediation with a parameterized baseline (leg3._mediation body, generalized)
# ---------------------------------------------------------------------------


def _mediation_between(
    per_author: pd.DataFrame,
    baseline_arm: str,
    treated_arm: str,
) -> dict[str, Any]:
    """leg3._mediation with the baseline arm parameterized (same statistics)."""
    baseline = per_author[per_author["arm"] == baseline_arm]
    treated = per_author[per_author["arm"] == treated_arm]
    merged = baseline.merge(
        treated,
        on=["world", "repetition", "author"],
        suffixes=("_base", "_arm"),
    )
    merged = merged.copy()
    merged["delta_e_d"] = merged["e_d_atom_base"] - merged["e_d_atom_arm"]
    merged["delta_e_loop"] = merged["e_loop_base"] - merged["e_loop_arm"]
    cells = []
    for (world, repetition), group in merged.groupby(["world", "repetition"]):
        if len(group) < 8:
            continue
        if (
            float(np.std(group["delta_e_d"])) < 1e-15
            or float(np.std(group["delta_e_loop"])) < 1e-15
        ):
            cells.append(
                {
                    "world": world,
                    "repetition": repetition,
                    "rho": float("nan"),
                    "degenerate_cell": True,
                }
            )
            continue
        cells.append(
            {
                "world": world,
                "repetition": repetition,
                "rho": leg3._pooled_spearman(
                    group, "delta_e_d", "delta_e_loop"
                ),
                "degenerate_cell": False,
            }
        )
    cell_frame = pd.DataFrame(cells)
    valid = (
        cell_frame[~cell_frame["degenerate_cell"]]["rho"].dropna()
        if len(cell_frame)
        else pd.Series(dtype=float)
    )
    return {
        "baseline_arm": baseline_arm,
        "median_within_cell_rho": (
            float(valid.median()) if len(valid) else float("nan")
        ),
        "n_cells_total": int(len(cell_frame)),
        "n_cells_with_variation": int(len(valid)),
        "iqr": (
            [float(valid.quantile(0.25)), float(valid.quantile(0.75))]
            if len(valid)
            else [float("nan"), float("nan")]
        ),
        "pooled_rho": leg3._pooled_spearman(
            merged, "delta_e_d", "delta_e_loop"
        ),
    }


# ---------------------------------------------------------------------------
# paired-row diagnostics
# ---------------------------------------------------------------------------


def _paired_rows(
    loops: pd.DataFrame,
    arm_a: str,
    arm_b: str,
) -> pd.DataFrame:
    keys = ["world", "repetition", "author", "view"]
    columns = keys + ["model_flip", "e_loop", "e_d_atom"]
    a = loops[loops["arm"] == arm_a][columns]
    b = loops[loops["arm"] == arm_b][columns]
    return a.merge(b, on=keys, suffixes=("_a", "_b"))


def _both_nonflip_diagnostic(
    loops: pd.DataFrame,
    arm_a: str,
    arm_b: str,
) -> dict[str, Any]:
    merged = _paired_rows(loops, arm_a, arm_b)
    both = merged[~merged["model_flip_a"] & ~merged["model_flip_b"]]
    return {
        "arms": [arm_a, arm_b],
        "rows": int(len(both)),
        "median_e_loop_a": float(both["e_loop_a"].median()),
        "median_e_loop_b": float(both["e_loop_b"].median()),
        "median_e_d_a": float(both["e_d_atom_a"].median()),
        "median_e_d_b": float(both["e_d_atom_b"].median()),
        "fraction_b_better_e_loop": float(
            (both["e_loop_b"] < both["e_loop_a"]).mean()
        ),
    }


def _changed_route_diagnostic(
    loops: pd.DataFrame,
    changed_keys: set[tuple[str, int, int, str]],
) -> dict[str, Any]:
    """arm0 vs two_stage on exactly the rows where stage 1 changed the route."""
    merged = _paired_rows(loops, "arm0_v2", "two_stage")
    mask = merged.apply(
        lambda row: (
            row["world"],
            int(row["repetition"]),
            int(row["author"]),
            row["view"],
        )
        in changed_keys,
        axis=1,
    )
    changed = merged[mask]
    unchanged = merged[~mask]
    return {
        "rows_changed": int(len(changed)),
        "rows_unchanged": int(len(unchanged)),
        "changed_median_e_loop_arm0": float(changed["e_loop_a"].median()),
        "changed_median_e_loop_two_stage": float(
            changed["e_loop_b"].median()
        ),
        "changed_fraction_two_stage_better": float(
            (changed["e_loop_b"] < changed["e_loop_a"]).mean()
        ),
        "changed_arm0_flips": int(changed["model_flip_a"].sum()),
        "changed_two_stage_flips": int(changed["model_flip_b"].sum()),
        "unchanged_max_abs_e_loop_difference": float(
            np.max(np.abs(unchanged["e_loop_a"] - unchanged["e_loop_b"]))
            if len(unchanged)
            else float("nan")
        ),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


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
        default=ROOT / "results" / "m4_d_two_stage",
    )
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    started_all = time.time()
    config = leg3._load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    repetitions = (
        int(args.repetitions)
        if args.repetitions is not None
        else int(config["repetitions"])
    )
    worlds = list(LOOP_WORLDS)
    if args.smoke:
        repetitions = 1
        worlds = worlds[:2]
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

    leg4_arm2 = _load_leg4_arm2()

    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    stage1_check_rows: list[dict[str, Any]] = []
    changed_keys: set[tuple[str, int, int, str]] = set()
    fresh_refits = 0
    for repetition in range(repetitions):
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
            keys_base = {
                "world": world,
                "repetition": repetition,
                "seed": seed,
            }

            # ---- stage 1 (Leg 4a arm exactly) + registered assert ----
            stage1_stacks = leg4._arm2_stacks_for_lambda(
                context, STAGE1_LAMBDA
            )
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
            stage1_check_rows.append(
                _assert_stage1_rows(
                    stage1_rows, leg4_arm2, world, repetition
                )
            )

            # ---- stage 2 (unpenalized refit at stage-1 routes) ----
            two_stage_stacks: dict[str, list[dict[str, Any]]] = {
                "train": [],
                "test": [],
            }
            for view in ("train", "test"):
                for author in range(context["authors"]):
                    stack, fresh = _two_stage_stack(
                        context, view, author, stage1_stacks[view][author]
                    )
                    two_stage_stacks[view].append(stack)
                    if fresh:
                        fresh_refits += 1
                        changed_keys.add(
                            (world, repetition, author, view)
                        )

            # ---- secondary arm (single-stage lambda = .025) ----
            secondary_stacks = leg4._arm2_stacks_for_lambda(
                context, SECONDARY_LAMBDA
            )

            arm_stacks = {
                "arm0_v2": context["base_stacks"],
                "arm2_stage1_125": stage1_stacks,
                "two_stage": two_stage_stacks,
                "single_stage_025": secondary_stacks,
            }
            for arm in ARMS:
                if arm == "arm2_stage1_125":
                    arm_rows = stage1_rows
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
                geometries = (
                    context["arm0_geometries"]
                    if arm == "arm0_v2"
                    else leg3._arm_geometries(
                        arm_stacks[arm], context["oracle_stacks"]
                    )
                )
                world_rows.append(
                    {
                        **keys_base,
                        "arm": arm,
                        "chart_family": context["chart"].selected_family,
                        "v2_transform_rank": int(
                            context["v2_transform"].effective_rank
                        ),
                        "width_basis": int(
                            context["v2_basis"]["evaluation"].shape[1]
                        ),
                        "oracle_width": int(
                            context["truth"].oracle_basis[
                                "evaluation"
                            ].shape[1]
                        ),
                        "arm_lambda": (
                            STAGE1_LAMBDA
                            if arm == "arm2_stage1_125"
                            else SECONDARY_LAMBDA
                            if arm == "single_stage_025"
                            else np.nan
                        ),
                        **geometries,
                        "flips": int(
                            sum(row["model_flip"] for row in arm_rows)
                        ),
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
            by_arm = {
                row["arm"]: (
                    round(row["loop_action_geometry"], 3),
                    row["flips"],
                )
                for row in world_rows
                if row["world"] == world
                and row["repetition"] == repetition
            }
            print(
                f"[battery] rep={repetition} world={world} "
                f"(geometry, flips) by arm: {by_arm} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    loops = pd.DataFrame(loop_rows).sort_values(
        ["arm", "world", "repetition", "author", "view"]
    )
    worlds_frame = pd.DataFrame(world_rows).sort_values(
        ["arm", "world", "repetition"]
    )
    validation = pd.DataFrame(validation_rows)
    stage1_checks = pd.DataFrame(stage1_check_rows)

    args.output.mkdir(parents=True, exist_ok=True)
    loops.to_csv(args.output / "per_loop_metrics.csv", index=False)
    worlds_frame.to_csv(args.output / "world_rep_metrics.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    stage1_checks.to_csv(
        args.output / "stage1_leg4_crosscheck.csv", index=False
    )

    # ---- battery-level asserts before adjudication ----
    stage1_total_flips = int(
        loops[loops["arm"] == "arm2_stage1_125"]["model_flip"].sum()
    )
    if not args.smoke and stage1_total_flips != STAGE1_EXPECTED_FLIPS:
        raise RuntimeError(
            f"stage-1 battery flips {stage1_total_flips} != "
            f"{STAGE1_EXPECTED_FLIPS}"
        )
    leg1_check = (
        leg3._leg1_per_row_check(loops)
        if not args.smoke
        else {"leg1_per_row_available": False}
    )

    arm_summaries = {
        arm: leg4._arm_summary(loops, worlds_frame, arm) for arm in ARMS
    }
    per_author = leg3._author_level(loops)
    mediation = {
        "two_stage_vs_arm0": _mediation_between(
            per_author, "arm0_v2", "two_stage"
        ),
        "two_stage_vs_stage1": _mediation_between(
            per_author, "arm2_stage1_125", "two_stage"
        ),
        "single_stage_025_vs_arm0": _mediation_between(
            per_author, "arm0_v2", "single_stage_025"
        ),
    }

    two = arm_summaries["two_stage"]
    lean_a_hold = bool(two["median_e_d"] <= LEAN_A_BAR)
    lean_b_hold = bool(two["pooled_loop_geometry"] >= LEAN_B_BAR)
    worlds_count = int(two["worlds_at_or_above_075"])
    lean_c_hold = bool(LEAN_C_BAND[0] <= worlds_count <= LEAN_C_BAND[1])
    pivot_triggered = bool(lean_a_hold and not lean_b_hold)

    decision = {
        "estimand_id": "SUICA_M4_D_LEG5_TWO_STAGE_ROUTE_THEN_REFIT",
        "tier": "EXPLORATORY",
        "config_seed": int(config["seed"]),
        "arm0_faithfulness": {
            "validation_max_abs_difference": (
                float(validation["abs_difference"].max())
                if len(validation)
                else float("nan")
            ),
            "flips_total_equals_196": bool(
                arm_summaries["arm0_v2"]["flips_total"] == 196
            ),
            "pooled_loop_geometry": arm_summaries["arm0_v2"][
                "pooled_loop_geometry"
            ],
            **leg1_check,
        },
        "stage1_faithfulness": {
            "reference": "results/m4_d_dleg_floor/per_loop_metrics.csv "
            "(arm2_penalized rows)",
            "world_reps_checked": int(len(stage1_checks)),
            "rows_compared": int(stage1_checks["rows_compared"].sum()),
            "max_abs_e_loop_difference": float(
                stage1_checks["max_abs_e_loop_difference"].max()
            ),
            "max_abs_e_d_difference": float(
                stage1_checks["max_abs_e_d_difference"].max()
            ),
            "all_flags_equal": bool(stage1_checks["flags_equal"].all()),
            "flips_total": stage1_total_flips,
            "flips_total_equals_73": bool(
                stage1_total_flips == STAGE1_EXPECTED_FLIPS
            ),
        },
        "design": {
            "stage1": (
                f"Leg 4a winning configuration exactly: arm-2 penalized "
                f"hazard flow at ridge lambda={STAGE1_LAMBDA} (interior "
                "route-accuracy optimum), asserted per world-rep against "
                "Leg 4 persisted rows before stage 2"
            ),
            "stage2": (
                "V2 baseline (unpenalized) final refit at the fixed "
                "stage-1-selected route on combined calibration+selection "
                "panels; no selection in stage 2; rows whose stage-1 route "
                "equals arm 0's reuse arm 0's final hazard fit "
                "(bit-identical by construction)"
            ),
            "gc_coupling_note": (
                "the estimator fits choice/response independently of the "
                "hazard, so the registered '(and GC legs where the "
                "estimator couples them)' clause is vacuous: stage 2 "
                "refits exactly the D leg; C/G are V2 baseline legs on "
                "every arm"
            ),
            "secondary": (
                f"single-stage lambda={SECONDARY_LAMBDA} full battery "
                "(Leg 4a discovery-loop-geometry peak; licenses that "
                "discovery observation)"
            ),
        },
        "two_stage_structure": {
            "rows_route_changed_vs_arm0": int(len(changed_keys)),
            "fresh_stage2_refits": int(fresh_refits),
            "rows_reusing_arm0_final_hazard": int(
                len(loops[loops["arm"] == "two_stage"]) - fresh_refits
            ),
            "stage1_flips": stage1_total_flips,
            "stage2_flips": int(two["flips_total"]),
            "changed_rows_diagnostic": _changed_route_diagnostic(
                loops, changed_keys
            ),
        },
        "arms": arm_summaries,
        "mediation": mediation,
        "paired_nonflip_diagnostics": {
            "arm0_vs_two_stage": _both_nonflip_diagnostic(
                loops, "arm0_v2", "two_stage"
            ),
            "stage1_vs_two_stage": _both_nonflip_diagnostic(
                loops, "arm2_stage1_125", "two_stage"
            ),
            "arm0_vs_single_stage_025": _both_nonflip_diagnostic(
                loops, "arm0_v2", "single_stage_025"
            ),
        },
        "comparison_table": {
            "arm0_v2": {
                "flips": arm_summaries["arm0_v2"]["flips_total"],
                "pooled_loop_geometry": arm_summaries["arm0_v2"][
                    "pooled_loop_geometry"
                ],
                "median_e_d": arm_summaries["arm0_v2"]["median_e_d"],
                "worlds_at_or_above_075": arm_summaries["arm0_v2"][
                    "worlds_at_or_above_075"
                ],
            },
            "leg3_arm2_at_005_persisted": {
                "flips": 148,
                "pooled_loop_geometry": 0.6885829871801226,
                "median_e_d": 0.4769160041170094,
                "worlds_at_or_above_075": 1,
                "source": "results/m4_d_overspan_control/decision.json "
                "(persisted, not recomputed here)",
            },
            "leg4a_arm2_at_125_stage1": {
                "flips": arm_summaries["arm2_stage1_125"]["flips_total"],
                "pooled_loop_geometry": arm_summaries["arm2_stage1_125"][
                    "pooled_loop_geometry"
                ],
                "median_e_d": arm_summaries["arm2_stage1_125"]["median_e_d"],
                "worlds_at_or_above_075": arm_summaries["arm2_stage1_125"][
                    "worlds_at_or_above_075"
                ],
            },
            "two_stage": {
                "flips": arm_summaries["two_stage"]["flips_total"],
                "pooled_loop_geometry": arm_summaries["two_stage"][
                    "pooled_loop_geometry"
                ],
                "median_e_d": arm_summaries["two_stage"]["median_e_d"],
                "worlds_at_or_above_075": arm_summaries["two_stage"][
                    "worlds_at_or_above_075"
                ],
            },
            "single_stage_025": {
                "flips": arm_summaries["single_stage_025"]["flips_total"],
                "pooled_loop_geometry": arm_summaries["single_stage_025"][
                    "pooled_loop_geometry"
                ],
                "median_e_d": arm_summaries["single_stage_025"][
                    "median_e_d"
                ],
                "worlds_at_or_above_075": arm_summaries["single_stage_025"][
                    "worlds_at_or_above_075"
                ],
            },
        },
        "lean_a": {
            "registered": (
                "stage-2 median e_d at selected routes <= .55 (from .783 "
                "under the flip-optimal ridge; baseline .487)"
            ),
            "value": two["median_e_d"],
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": (
                "pooled loop geometry >= .70 (missed twice by ~.01: .6886 "
                "Leg 3, .6901 Leg 4a) -- the decisive test"
            ),
            "value": two["pooled_loop_geometry"],
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered": (
                "worlds >= .75: 2-3 of 5 (band; currently 2/5 under 4a)"
            ),
            "value": worlds_count,
            "hold": lean_c_hold,
        },
        "pivot_if": {
            "registered": (
                "(a) holds but (b) misses -> D-quality-at-fixed-route was "
                "NOT the binding path on route-stabilized rows; the "
                "residual wall on non-flip rows is the Leg-4b floor "
                "already at work at 1x; the two-stage construction is "
                "EXHAUSTED and the wall passes fully to the design-change "
                "track (C3.3 excitation)"
            ),
            "triggered": pivot_triggered,
            "declaration": (
                "TWO_STAGE_CONSTRUCTION_EXHAUSTED_WALL_PASSES_TO_DESIGN_CHANGE_TRACK"
                if pivot_triggered
                else "not triggered"
            ),
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; the loop-transport "
            "statistic compares against oracle-basis fits, so this is a "
            "truth-referenced diagnostic of the estimator, not an "
            "operational rescue of chart transport and not a reopened "
            "gate; the V1/V2 NO-GO decisions stand; no natural-text, "
            "personality, emotion, or clinical claim; EXPLORATORY tier "
            "under the 2026-08-01 open-exploration directive."
        ),
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(decision, indent=2, sort_keys=True))
    print(f"[done] total {time.time() - started_all:.0f}s", flush=True)


if __name__ == "__main__":
    main()
