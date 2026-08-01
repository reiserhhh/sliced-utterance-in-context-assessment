#!/usr/bin/env python3
"""M4-D Leg 4: is the D-leg floor structural or estimator-limited?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 4 -- is the D-leg floor structural or estimator-limited?", before this
run). Two parts, one battery, same V2 worlds. All V2 replay and arm-2 ridge
machinery is IMPORTED from scripts/run_suica_m4_d_overspan_control_leg3.py
(bit-exact reuse; Leg 3 validated the replay to 1.1e-16) -- nothing there is
reimplemented.

PART 4a -- lambda-grid extension with the registered selection-rule change.
Grid {.005, .025, .125, .625, 3.125}. Lambda is selected by OUT-OF-FOLD
ROUTE-IDENTIFICATION ACCURACY on the same discovery repetitions Leg 3 used
({0, 1}), not by raw likelihood (Leg 3 showed the likelihood criterion is
monotone in lambda and binds at the grid boundary). Pre-coded rule, stated
before the run:

- For each lambda, run the full arm-2 procedure (leg3._arm2_stack: penalized
  feedback/gate candidates, V2 selection rule, penalized final refit) on every
  discovery author-view; route-identification accuracy = 1 - (D-zero
  model-selection flips vs the oracle route) / rows, with Leg 1's flip
  definition (exactly one of the discovered/oracle pair has a zero D leg).
- Selection: fewest discovery flips; ties broken by fewer route-name
  mismatches, then by SMALLER lambda (weakest treatment, mirroring the V2
  first-at-minimum convention). Route-name accuracy is recorded as companion.
- If the selected lambda sits at a grid boundary (.005 or 3.125), the
  registered soft outcome fires: report the full lambda-response curve
  (discovery flips + loop geometry per lambda) and declare the ridge
  mechanism saturated. The curve is persisted in all cases.
- The full 5-world x 8-repetition battery is rerun at the selected lambda
  (arm0_v2 exact replay + arm2_penalized at lambda*), with Leg 3's
  faithfulness gates: arm-0 geometries vs archived metrics.csv per world-rep
  (before treatment), arm-0 per-row vs Leg 1's per_loop_metrics.csv, PLUS a
  new cross-check of arm-0 rows (all repetitions) and discovery arm-2 rows at
  lambda=.005 against Leg 3's persisted per_loop_metrics.csv.

Registered leans: (a4a) total battery flips <= 120 at the selected lambda;
(b4a) pooled loop geometry >= .70.

PART 4b -- D-leg resolution scaling at the ORACLE-FORCED route.
For each world-rep and author-view, the hazard route is FORCED to the oracle
stack's V2-selected model at the default budget (no selection anywhere), and
the creation derivative D is re-estimated at event budgets {0.5x, 1x, 2x, 4x}
of the V2 default (spec.events = 120 -> {60, 120, 240, 480}; 4x is possible,
so the registered fallback grid is not needed). Budget mechanics, stated
before the run: the generator parameterizes event count as
M4ChartEcologySpec.events (events per occasion); condition panels, mechanism
parameters, and the oracle basis do not consume it, so the frozen world law
is bit-identical across budgets (asserted bit-exactly per budget). The
generator consumes RNG per event, so non-1x panels are FRESH path
realizations from the identical frozen law; the 1x budget reuses the exact
battery panels. The chart and both bases stay frozen at their V2 (1x)
estimates -- only the dynamic event panels scale. The V2 estimator semantics
(hazard ridge .005, 30 IRLS iterations, combined calibration+selection final
refit) are unchanged; no extra ridge is applied in 4b.

Error references, pre-coded before the run:
- PRIMARY e_d_paired(b) = ||D_disc(b) - D_orc(b)|| / ||D_orc(b)||, both legs
  refit at budget b at the forced route (the program-standard D-leg error;
  at 1x it coincides bit-exactly with e_d_atom at the correct route).
- Companions: e_d_true(b) = ||D_disc(b) - D_true|| / ||D_true|| and
  e_orc_true(b) = ||D_orc(b) - D_true|| / ||D_true||, where D_true is the
  ANALYTIC creation derivative of the generator law at the estimator's own
  probe (central difference, epsilon .05): the generator's hazard is
  logit p_k = logit(base) + .40(2g-1) + .035 tanh(dur/4) + [B C_a r]_k
  (+ gate term, zero at the probes), so at the probes
  D_true[k,d] = (expit(l0 + eps M[k,d]) - expit(l0 - eps M[k,d])) / (2 eps)
  with M = B_eval @ C_a and l0 = logit(clip(base)) - .40. This formula is
  unit-checked per world-rep against _feedback_derivative applied to the
  exact generator coefficients (gate < 1e-10). The companions decompose any
  paired plateau into discovered-side bias vs oracle-side noise.
  e_d_frozen(b) = ||D_disc(b) - D_orc(1x)|| / ||D_orc(1x)|| is persisted for
  completeness.
- Rows whose forced route has a zero D leg (oracle selected base/return;
  ~1% of rows) have no meaningful relative reference and are flagged
  degenerate and excluded from medians (counted).
- Identity gates at 1x: the oracle-side refit must reproduce the oracle
  stack's D bit-exactly on every nondegenerate row, and the forced
  discovered-side refit must reproduce arm-0's D bit-exactly on rows where
  arm 0 already selected the oracle route.

Scaling fit and registered fork, pre-coded: per world (and pooled), median
author-level e_d per budget (train/test mean per author-rep, median over the
128 author-reps); overall slope = OLS of log(median e_d) on log(budget) over
all four budgets; tail slope = same over budgets {1x, 2x, 4x}; plateau test =
|tail slope| < 0.15. Verdict per world on the PRIMARY:
  STRUCTURAL_FLOOR    if plateau (|tail| < .15)  -> state the floor (median
                      at 4x and the {2x,4x} mean) in T4-economics style;
  BUDGET_LIMITED      if overall slope in [-.65, -.35] and no plateau ->
                      report the projected budget multiple to reach
                      e_d <= .25 from the fitted power law;
  BUDGET_LIMITED_STEEP if overall slope < -.65 and no plateau (faster than
                      the registered -1/2 band; still estimator-limited);
  INTERMEDIATE        otherwise (numbers reported honestly).
The same machinery is reported for e_d_true; mixed outcomes across worlds
are allowed and reported per world. No kill (mapping experiment).
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

import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402  bit-exact reuse

from scipy.special import expit, logit  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _feedback_derivative,
    _fit_hazard_candidate,
    _flatten_events,
    _hazard_names,
    _query_masks,
    build_m4_discovered_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)

LOOP_WORLDS = leg3.LOOP_WORLDS
ARMS = ("arm0_v2", "arm2_penalized")
DISCOVERY_REPS = (0, 1)
LAMBDA_GRID = (0.005, 0.025, 0.125, 0.625, 3.125)
BUDGETS = (0.5, 1.0, 2.0, 4.0)
FLIP_TOLERANCE = leg3.FLIP_TOLERANCE
PROBE_EPSILON = 0.05
TARGET_E_D = 0.25
PLATEAU_BAR = 0.15
BUDGET_BAND = (-0.65, -0.35)


# ---------------------------------------------------------------------------
# world context (generation + chart + stacks), faithfulness-gated
# ---------------------------------------------------------------------------


def _build_context(
    world: str,
    repetition: int,
    seed: int,
    *,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
    expected_geometries: dict[str, float] | None,
    faithfulness_tolerance: float = 1e-6,
) -> dict[str, Any]:
    observed, truth = generate_m4_chart_ecology_world(
        world=world,
        spec=spec,
        seed=seed,
    )
    chart = fit_m4_condition_chart(
        observed.condition,
        candidates=tuple(dict(value) for value in config["candidates"]),
        **config["chart_thresholds"],
    )
    if chart.refused:
        raise RuntimeError(
            f"chart refused on {world} rep {repetition}: archived V2 battery "
            "has no refusals here, so the replay is unfaithful"
        )
    v2_transform, v2_basis = build_m4_discovered_basis(
        observed,
        chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=config.get("maximum_rank"),
    )
    route = dict(config["route_estimator"])
    route.pop("alias_match_threshold", None)
    fit_kwargs = {
        "ridge_grid": tuple(float(x) for x in route["ridge_grid"]),
        "hazard_ridge": float(route["hazard_ridge"]),
        "logistic_iterations": int(route["logistic_iterations"]),
        "complexity_penalty": float(route["complexity_penalty"]),
    }
    categories = observed.ecology.train_calibration.menu.shape[-1]
    query_masks = _query_masks(categories)
    authors = observed.ecology.train_calibration.menu.shape[0]

    flat: dict[tuple[str, int], tuple[dict, dict, dict]] = {}
    oracle_stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    base_stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    for view in ("train", "test"):
        panels = (
            getattr(observed.ecology, f"{view}_calibration"),
            getattr(observed.ecology, f"{view}_selection"),
            getattr(observed.ecology, f"{view}_evaluation"),
        )
        for author in range(authors):
            events = tuple(_flatten_events(panel, author) for panel in panels)
            flat[(view, author)] = events
            oracle_stacks[view].append(
                leg3._fit_v2_stack(
                    *events,
                    truth.oracle_basis,
                    **fit_kwargs,
                    query_masks=query_masks,
                )
            )
            base_stacks[view].append(
                leg3._fit_v2_stack(
                    *events,
                    v2_basis,
                    **fit_kwargs,
                    query_masks=query_masks,
                )
            )

    arm0_geometries = leg3._arm_geometries(base_stacks, oracle_stacks)
    validation_rows: list[dict[str, Any]] = []
    if expected_geometries is not None:
        for name, expected in expected_geometries.items():
            difference = abs(arm0_geometries[name] - expected)
            if difference > faithfulness_tolerance:
                raise RuntimeError(
                    f"V2 replay unfaithful on {world} rep {repetition}: "
                    f"{name} recomputed {arm0_geometries[name]:.12f} vs "
                    f"archived {expected:.12f} (|diff| {difference:.3e})"
                )
            validation_rows.append(
                {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "metric": name,
                    "recomputed": arm0_geometries[name],
                    "archived": expected,
                    "abs_difference": difference,
                }
            )
    return {
        "world": world,
        "repetition": repetition,
        "seed": seed,
        "observed": observed,
        "truth": truth,
        "chart": chart,
        "v2_transform": v2_transform,
        "v2_basis": v2_basis,
        "fit_kwargs": fit_kwargs,
        "query_masks": query_masks,
        "authors": authors,
        "flat": flat,
        "oracle_stacks": oracle_stacks,
        "base_stacks": base_stacks,
        "arm0_geometries": arm0_geometries,
        "validation_rows": validation_rows,
    }


def _arm2_stacks_for_lambda(
    context: dict[str, Any],
    lam: float,
) -> dict[str, list[dict[str, Any]]]:
    stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stacks[view].append(
                leg3._arm2_stack(
                    context["base_stacks"][view][author],
                    *context["flat"][(view, author)],
                    context["v2_basis"],
                    hazard_ridge=context["fit_kwargs"]["hazard_ridge"],
                    logistic_iterations=context["fit_kwargs"][
                        "logistic_iterations"
                    ],
                    complexity_penalty=context["fit_kwargs"][
                        "complexity_penalty"
                    ],
                    extra_ridge=lam,
                )
            )
    return stacks


# ---------------------------------------------------------------------------
# part 4a -- discovery lambda selection by route-identification accuracy
# ---------------------------------------------------------------------------


def _discovery_rows(
    context: dict[str, Any],
    lam: float,
    stacks: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    keys_base = {
        "world": context["world"],
        "repetition": context["repetition"],
        "seed": context["seed"],
    }
    rows = []
    for view in ("train", "test"):
        for author in range(context["authors"]):
            row = leg3._loop_row(
                {**keys_base, "author": author, "view": view},
                "arm2_penalized",
                stacks[view][author],
                context["oracle_stacks"][view][author],
            )
            row["lam"] = lam
            rows.append(row)
    return rows


def _select_lambda(
    discovery_frame: pd.DataFrame,
    curve_frame: pd.DataFrame,
) -> tuple[float, dict[str, Any]]:
    per_lambda: dict[float, dict[str, Any]] = {}
    for lam, group in discovery_frame.groupby("lam"):
        flips = int(group["model_flip"].sum())
        mismatches = int(group["route_mismatch"].sum())
        n_rows = int(len(group))
        geometry = float(
            curve_frame[curve_frame["lam"] == lam][
                "loop_action_geometry"
            ].mean()
        )
        per_lambda[float(lam)] = {
            "discovery_flips": flips,
            "discovery_rows": n_rows,
            "route_identification_accuracy": 1.0 - flips / n_rows,
            "route_name_mismatches": mismatches,
            "route_name_accuracy": 1.0 - mismatches / n_rows,
            "mean_discovery_loop_geometry": geometry,
            "median_discovery_e_d": float(group["e_d_atom"].median()),
        }
    chosen = min(
        per_lambda,
        key=lambda lam: (
            per_lambda[lam]["discovery_flips"],
            per_lambda[lam]["route_name_mismatches"],
            lam,
        ),
    )
    return chosen, per_lambda


# ---------------------------------------------------------------------------
# part 4b -- D-leg resolution scaling at the oracle-forced route
# ---------------------------------------------------------------------------


def _true_derivative(
    truth: Any,
    author: int,
    *,
    epsilon: float = PROBE_EPSILON,
) -> np.ndarray:
    basis_eval = truth.oracle_basis["evaluation"]
    creation = truth.author_parameters["creation"][author]
    base = float(
        np.clip(truth.author_parameters["generated_base"][author], 0.02, 0.98)
    )
    l0 = float(logit(base)) - 0.40
    m = basis_eval @ creation
    return (expit(l0 + epsilon * m) - expit(l0 - epsilon * m)) / (
        2.0 * epsilon
    )


def _true_derivative_unit_check(truth: Any, dimensions: int) -> float:
    """Check the analytic D_true against the estimator's own probe machinery.

    Builds the EXACT generator coefficients for the feedback hazard model in
    the oracle basis and runs _feedback_derivative on them; the analytic
    formula must agree to float roundoff.
    """
    author = 0
    basis_eval = truth.oracle_basis["evaluation"]
    width = basis_eval.shape[1]
    names = _hazard_names("feedback", width, dimensions)
    creation = truth.author_parameters["creation"][author]
    base = float(
        np.clip(truth.author_parameters["generated_base"][author], 0.02, 0.98)
    )
    coefficient = np.zeros(len(names))
    coefficient[0] = float(logit(base)) - 0.40
    coefficient[1 + width] = 0.80
    coefficient[2 + width] = 0.035
    coefficient[3 + width :] = creation.reshape(-1)
    probe = _feedback_derivative(
        coefficient,
        names,
        basis_eval,
        dimensions,
        epsilon=PROBE_EPSILON,
    )
    analytic = _true_derivative(truth, author)
    return float(np.max(np.abs(probe - analytic)))


def _forced_route_derivative(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    model: str,
    hazard_ridge: float,
    logistic_iterations: int,
    dimensions: int,
) -> np.ndarray:
    fit = _fit_hazard_candidate(
        [
            (calibration, basis["calibration"]),
            (selection, basis["selection"]),
        ],
        model=model,
        ridge=hazard_ridge,
        iterations=logistic_iterations,
    )
    return _feedback_derivative(
        fit[0],
        fit[1],
        basis["evaluation"],
        dimensions,
    )


def _budget_rows_for_world_rep(
    context: dict[str, Any],
    *,
    spec: M4ChartEcologySpec,
    budgets: tuple[float, ...],
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    v2_basis = context["v2_basis"]
    oracle_basis = truth.oracle_basis
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]

    unit_gap = _true_derivative_unit_check(truth, dimensions)
    if unit_gap > 1e-10:
        raise RuntimeError(
            f"analytic D_true fails the probe unit check on {world} rep "
            f"{repetition}: max abs gap {unit_gap:.3e}"
        )

    true_d = {
        author: _true_derivative(truth, author)
        for author in range(context["authors"])
    }
    rows: list[dict[str, Any]] = []
    orc_identity_gap = 0.0
    disc_identity_gap = 0.0
    disc_identity_rows = 0
    for budget in budgets:
        events_b = int(round(spec.events * budget))
        if budget == 1.0:
            observed_b = context["observed"]
        else:
            spec_b = replace(spec, events=events_b)
            observed_b, truth_b = generate_m4_chart_ecology_world(
                world=world,
                spec=spec_b,
                seed=seed,
            )
            for role in ("calibration", "selection", "evaluation"):
                if not np.array_equal(
                    truth_b.oracle_basis[role], oracle_basis[role]
                ):
                    raise RuntimeError(
                        f"frozen-world violation at budget {budget}: oracle "
                        f"basis[{role}] changed on {world} rep {repetition}"
                    )
            for name in ("creation", "gate", "generated_base", "selection"):
                if not np.array_equal(
                    truth_b.author_parameters[name],
                    truth.author_parameters[name],
                ):
                    raise RuntimeError(
                        f"frozen-world violation at budget {budget}: author "
                        f"parameter {name} changed on {world} rep {repetition}"
                    )
        for view in ("train", "test"):
            calibration_panel = getattr(
                observed_b.ecology, f"{view}_calibration"
            )
            selection_panel = getattr(observed_b.ecology, f"{view}_selection")
            for author in range(context["authors"]):
                oracle_stack = context["oracle_stacks"][view][author]
                forced_route = oracle_stack["selected_model"]
                d_orc_1x = oracle_stack["D"]
                d_norm_orc_1x = float(np.linalg.norm(d_orc_1x))
                keys = {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "budget": budget,
                    "events": events_b,
                    "forced_route": forced_route,
                }
                if d_norm_orc_1x < FLIP_TOLERANCE:
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
                            "d_norm_orc_1x": d_norm_orc_1x,
                            "d_norm_true": float(
                                np.linalg.norm(true_d[author])
                            ),
                        }
                    )
                    continue
                calibration = _flatten_events(calibration_panel, author)
                selection = _flatten_events(selection_panel, author)
                d_disc = _forced_route_derivative(
                    calibration,
                    selection,
                    v2_basis,
                    model=forced_route,
                    hazard_ridge=hazard_ridge,
                    logistic_iterations=iterations,
                    dimensions=dimensions,
                )
                d_orc = _forced_route_derivative(
                    calibration,
                    selection,
                    oracle_basis,
                    model=forced_route,
                    hazard_ridge=hazard_ridge,
                    logistic_iterations=iterations,
                    dimensions=dimensions,
                )
                if budget == 1.0:
                    orc_identity_gap = max(
                        orc_identity_gap,
                        float(np.max(np.abs(d_orc - d_orc_1x))),
                    )
                    base_stack = context["base_stacks"][view][author]
                    if base_stack["selected_model"] == forced_route:
                        disc_identity_gap = max(
                            disc_identity_gap,
                            float(np.max(np.abs(d_disc - base_stack["D"]))),
                        )
                        disc_identity_rows += 1
                d_true = true_d[author]
                rows.append(
                    {
                        **keys,
                        "degenerate_reference": False,
                        "e_d_paired": leg3._relative_error(d_disc, d_orc),
                        "e_d_frozen": leg3._relative_error(d_disc, d_orc_1x),
                        "e_d_true": leg3._relative_error(d_disc, d_true),
                        "e_orc_true": leg3._relative_error(d_orc, d_true),
                        "orc_self_drift": leg3._relative_error(
                            d_orc, d_orc_1x
                        ),
                        "reference_gap": leg3._relative_error(
                            d_orc_1x, d_true
                        ),
                        "d_norm_disc_b": float(np.linalg.norm(d_disc)),
                        "d_norm_orc_b": float(np.linalg.norm(d_orc)),
                        "d_norm_orc_1x": d_norm_orc_1x,
                        "d_norm_true": float(np.linalg.norm(d_true)),
                    }
                )
    gates = {
        "true_d_unit_check_max_gap": unit_gap,
        "orc_refit_identity_max_gap_1x": orc_identity_gap,
        "disc_forced_identity_max_gap_1x": disc_identity_gap,
        "disc_forced_identity_rows_1x": disc_identity_rows,
    }
    return rows, gates


def _scaling_summary(
    budget_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    usable = budget_frame[~budget_frame["degenerate_reference"]].copy()
    author_level = (
        usable.groupby(["world", "repetition", "author", "budget"])
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
    metrics = ("e_d_paired", "e_d_true", "e_orc_true", "e_d_frozen")
    summary_rows = []
    analysis: dict[str, Any] = {}
    worlds = sorted(author_level["world"].unique())
    for scope in [*worlds, "POOLED"]:
        scoped = (
            author_level
            if scope == "POOLED"
            else author_level[author_level["world"] == scope]
        )
        medians: dict[str, dict[float, float]] = {name: {} for name in metrics}
        for budget, group in scoped.groupby("budget"):
            row = {
                "world": scope,
                "budget": float(budget),
                "n_author_reps": int(len(group)),
            }
            for name in metrics:
                value = float(group[name].median())
                row[f"median_{name}"] = value
                row[f"iqr_low_{name}"] = float(group[name].quantile(0.25))
                row[f"iqr_high_{name}"] = float(group[name].quantile(0.75))
                medians[name][float(budget)] = value
            summary_rows.append(row)
        scope_analysis: dict[str, Any] = {
            "median_reference_gap": float(scoped["reference_gap"].median()),
            "median_orc_self_drift_by_budget": {
                str(budget): float(group["orc_self_drift"].median())
                for budget, group in scoped.groupby("budget")
            },
        }
        for name in metrics:
            slopes = _slopes(medians[name])
            entry: dict[str, Any] = {
                "medians_by_budget": {
                    str(key): value
                    for key, value in sorted(medians[name].items())
                },
                **slopes,
            }
            if name in ("e_d_paired", "e_d_true"):
                entry["verdict"] = _verdict(slopes)
                entry["projected_budget_for_target"] = _projected_budget(
                    slopes
                )
                entry["floor_median_at_4x"] = medians[name].get(4.0)
                entry["floor_mean_2x_4x"] = float(
                    np.mean(
                        [
                            medians[name][key]
                            for key in (2.0, 4.0)
                            if key in medians[name]
                        ]
                    )
                    if any(key in medians[name] for key in (2.0, 4.0))
                    else np.nan
                )
            scope_analysis[name] = entry
        analysis[scope] = scope_analysis
    return pd.DataFrame(summary_rows), analysis


def _slopes(medians: dict[float, float]) -> dict[str, Any]:
    budgets = sorted(medians)
    x = np.log(np.asarray(budgets, dtype=float))
    y = np.log(np.asarray([medians[key] for key in budgets], dtype=float))
    overall = np.polyfit(x, y, 1) if len(budgets) >= 2 else (np.nan, np.nan)
    tail_budgets = [key for key in budgets if key >= 1.0]
    if len(tail_budgets) >= 2:
        tx = np.log(np.asarray(tail_budgets, dtype=float))
        ty = np.log(
            np.asarray([medians[key] for key in tail_budgets], dtype=float)
        )
        tail = np.polyfit(tx, ty, 1)
    else:
        tail = (np.nan, np.nan)
    segments = {
        f"{budgets[index]}->{budgets[index + 1]}": float(
            (y[index + 1] - y[index]) / (x[index + 1] - x[index])
        )
        for index in range(len(budgets) - 1)
    }
    return {
        "overall_slope": float(overall[0]),
        "overall_intercept": float(overall[1]),
        "tail_slope": float(tail[0]),
        "segment_slopes": segments,
    }


def _verdict(slopes: dict[str, Any]) -> str:
    tail = slopes["tail_slope"]
    overall = slopes["overall_slope"]
    if np.isfinite(tail) and abs(tail) < PLATEAU_BAR:
        return "STRUCTURAL_FLOOR"
    if BUDGET_BAND[0] <= overall <= BUDGET_BAND[1]:
        return "BUDGET_LIMITED"
    if overall < BUDGET_BAND[0]:
        return "BUDGET_LIMITED_STEEP"
    return "INTERMEDIATE"


def _projected_budget(slopes: dict[str, Any]) -> float | None:
    slope = slopes["overall_slope"]
    intercept = slopes["overall_intercept"]
    if not np.isfinite(slope) or slope >= -1e-9:
        return None
    return float(np.exp((np.log(TARGET_E_D) - intercept) / slope))


# ---------------------------------------------------------------------------
# leg-3 persisted-row cross-check
# ---------------------------------------------------------------------------


def _leg3_cross_check(
    loops: pd.DataFrame,
    discovery_frame: pd.DataFrame,
) -> dict[str, Any]:
    path = ROOT / "results" / "m4_d_overspan_control" / "per_loop_metrics.csv"
    if not path.exists():
        return {"leg3_per_row_available": False}
    stored = pd.read_csv(path)
    checks: dict[str, Any] = {"leg3_per_row_available": True}
    keys = ["world", "repetition", "author", "view"]

    arm0_mine = loops[loops["arm"] == "arm0_v2"]
    arm0_stored = stored[stored["arm"] == "arm0_v2"]
    merged = arm0_stored.merge(
        arm0_mine,
        on=keys,
        suffixes=("_leg3", "_leg4"),
    )
    if len(merged) != len(arm0_mine):
        raise RuntimeError(
            f"arm0 rows do not align with leg3 rows: {len(merged)} matches "
            f"vs mine {len(arm0_mine)}"
        )
    checks["arm0_rows_compared"] = int(len(merged))
    checks["arm0_max_abs_e_loop_difference"] = float(
        np.max(np.abs(merged["e_loop_leg3"] - merged["e_loop_leg4"]))
    )
    checks["arm0_max_abs_e_d_difference"] = float(
        np.max(np.abs(merged["e_d_atom_leg3"] - merged["e_d_atom_leg4"]))
    )
    checks["arm0_flags_equal"] = bool(
        (merged["model_flip_leg3"] == merged["model_flip_leg4"]).all()
        and (
            merged["selected_model_arm_leg3"]
            == merged["selected_model_arm_leg4"]
        ).all()
    )
    if (
        checks["arm0_max_abs_e_loop_difference"] > 1e-9
        or checks["arm0_max_abs_e_d_difference"] > 1e-9
        or not checks["arm0_flags_equal"]
    ):
        raise RuntimeError(f"arm0 rows diverge from leg3: {checks}")

    mine_005 = discovery_frame[
        np.isclose(discovery_frame["lam"], 0.005)
    ]
    stored_arm2 = stored[
        (stored["arm"] == "arm2_penalized")
        & stored["repetition"].isin(sorted(mine_005["repetition"].unique()))
        & stored["world"].isin(sorted(mine_005["world"].unique()))
    ]
    merged2 = stored_arm2.merge(
        mine_005,
        on=keys,
        suffixes=("_leg3", "_leg4"),
    )
    if len(merged2) != len(mine_005):
        raise RuntimeError(
            "discovery lambda=.005 rows do not align with leg3 arm2 rows: "
            f"{len(merged2)} matches vs mine {len(mine_005)}"
        )
    checks["arm2_005_rows_compared"] = int(len(merged2))
    checks["arm2_005_max_abs_e_d_difference"] = float(
        np.max(np.abs(merged2["e_d_atom_leg3"] - merged2["e_d_atom_leg4"]))
    )
    checks["arm2_005_flags_equal"] = bool(
        (merged2["model_flip_leg3"] == merged2["model_flip_leg4"]).all()
        and (
            merged2["selected_model_arm_leg3"]
            == merged2["selected_model_arm_leg4"]
        ).all()
    )
    if (
        checks["arm2_005_max_abs_e_d_difference"] > 1e-9
        or not checks["arm2_005_flags_equal"]
    ):
        raise RuntimeError(
            f"discovery arm2@.005 rows diverge from leg3: {checks}"
        )
    return checks


# ---------------------------------------------------------------------------
# adjudication
# ---------------------------------------------------------------------------


def _arm_summary(
    loops: pd.DataFrame,
    worlds_frame: pd.DataFrame,
    arm: str,
) -> dict[str, Any]:
    arm_loops = loops[loops["arm"] == arm]
    arm_worlds = worlds_frame[worlds_frame["arm"] == arm]
    per_author = leg3._author_level(loops)
    arm_author = per_author[per_author["arm"] == arm]
    per_world_geometry = {
        world: float(group["loop_action_geometry"].mean())
        for world, group in arm_worlds.groupby("world")
    }
    nonflip = arm_loops[~arm_loops["model_flip"]]
    return {
        "flips_total": int(arm_loops["model_flip"].sum()),
        "flips_by_world": {
            world: int(group["model_flip"].sum())
            for world, group in arm_loops.groupby("world")
        },
        "route_mismatch_total": int(arm_loops["route_mismatch"].sum()),
        "pooled_loop_geometry": float(
            arm_worlds["loop_action_geometry"].mean()
        ),
        "per_world_loop_geometry": per_world_geometry,
        "worlds_at_or_above_075": int(
            sum(value >= 0.75 for value in per_world_geometry.values())
        ),
        "pooled_creation_geometry": float(
            arm_worlds["creation_action_geometry"].mean()
        ),
        "median_e_d": float(arm_author["e_d_atom"].median()),
        "median_e_loop": float(arm_author["e_loop"].median()),
        "nonflip_mean_e_loop": float(nonflip["e_loop"].mean()),
    }


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
        default=ROOT / "results" / "m4_d_dleg_floor",
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
    discovery_reps = tuple(
        rep for rep in DISCOVERY_REPS if rep < repetitions
    )
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

    # ------------------------------------------------------------------ 4a
    contexts: dict[tuple[str, int], dict[str, Any]] = {}
    arm2_cache: dict[tuple[str, int, float], dict[str, Any]] = {}
    discovery_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    for repetition in discovery_reps:
        for world in worlds:
            seed = leg3._world_seed(
                int(config["seed"]), repetition, world, world_index[world]
            )
            started = time.time()
            context = _build_context(
                world,
                repetition,
                seed,
                spec=spec,
                config=config,
                expected_geometries=expected_for(world, repetition, seed),
            )
            contexts[(world, repetition)] = context
            for lam in LAMBDA_GRID:
                stacks = _arm2_stacks_for_lambda(context, lam)
                arm2_cache[(world, repetition, lam)] = stacks
                rows = _discovery_rows(context, lam, stacks)
                discovery_rows.extend(rows)
                geometries = leg3._arm_geometries(
                    stacks, context["oracle_stacks"]
                )
                curve_rows.append(
                    {
                        "world": world,
                        "repetition": repetition,
                        "seed": seed,
                        "lam": lam,
                        "flips": int(
                            sum(row["model_flip"] for row in rows)
                        ),
                        "route_mismatches": int(
                            sum(row["route_mismatch"] for row in rows)
                        ),
                        "rows": len(rows),
                        **geometries,
                    }
                )
            print(
                f"[4a-discovery] {world} rep={repetition} grid done "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )
    discovery_frame = pd.DataFrame(discovery_rows)
    curve_frame = pd.DataFrame(curve_rows)
    chosen_lambda, lambda_table = _select_lambda(
        discovery_frame, curve_frame
    )
    boundary_bound = chosen_lambda in (min(LAMBDA_GRID), max(LAMBDA_GRID))
    print(
        f"[4a] chosen lambda {chosen_lambda} by route-identification "
        f"accuracy on discovery reps {discovery_reps}; "
        f"boundary_bound={boundary_bound}",
        flush=True,
    )
    # free non-selected cached stacks
    for key in list(arm2_cache):
        if key[2] != chosen_lambda:
            del arm2_cache[key]

    # ------------------------------------------------------ battery + 4b
    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    budget_rows: list[dict[str, Any]] = []
    budget_gates: list[dict[str, Any]] = []
    for repetition in range(repetitions):
        for world in worlds:
            seed = leg3._world_seed(
                int(config["seed"]), repetition, world, world_index[world]
            )
            started = time.time()
            cached = (world, repetition) in contexts
            context = (
                contexts.pop((world, repetition))
                if cached
                else _build_context(
                    world,
                    repetition,
                    seed,
                    spec=spec,
                    config=config,
                    expected_geometries=expected_for(
                        world, repetition, seed
                    ),
                )
            )
            validation_rows.extend(context["validation_rows"])
            arm_stacks = {
                "arm0_v2": context["base_stacks"],
                "arm2_penalized": arm2_cache.pop(
                    (world, repetition, chosen_lambda),
                    None,
                )
                or _arm2_stacks_for_lambda(context, chosen_lambda),
            }
            keys_base = {
                "world": world,
                "repetition": repetition,
                "seed": seed,
            }
            for arm in ARMS:
                arm_rows = []
                for view in ("train", "test"):
                    for author in range(context["authors"]):
                        arm_rows.append(
                            leg3._loop_row(
                                {
                                    **keys_base,
                                    "author": author,
                                    "view": view,
                                },
                                arm,
                                arm_stacks[arm][view][author],
                                context["oracle_stacks"][view][author],
                            )
                        )
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
                        "arm2_lambda": (
                            chosen_lambda
                            if arm == "arm2_penalized"
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
            rows_4b, gates_4b = _budget_rows_for_world_rep(
                context,
                spec=spec,
                budgets=BUDGETS,
            )
            budget_rows.extend(rows_4b)
            budget_gates.append(
                {**keys_base, **gates_4b}
            )
            if (
                gates_4b["orc_refit_identity_max_gap_1x"] > 1e-9
                or gates_4b["disc_forced_identity_max_gap_1x"] > 1e-9
            ):
                raise RuntimeError(
                    f"1x identity gate failed on {world} rep {repetition}: "
                    f"{gates_4b}"
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
                f"[battery+4b] rep={repetition} world={world} "
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
    budget_frame = pd.DataFrame(budget_rows).sort_values(
        ["world", "repetition", "author", "view", "budget"]
    )
    scaling_frame, scaling_analysis = _scaling_summary(budget_frame)

    args.output.mkdir(parents=True, exist_ok=True)
    loops.to_csv(args.output / "per_loop_metrics.csv", index=False)
    worlds_frame.to_csv(args.output / "world_rep_metrics.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    discovery_frame.to_csv(
        args.output / "lambda_discovery_rows.csv", index=False
    )
    curve_frame.to_csv(
        args.output / "lambda_response_curve.csv", index=False
    )
    budget_frame.to_csv(args.output / "dleg_budget_rows.csv", index=False)
    scaling_frame.to_csv(
        args.output / "dleg_scaling_summary.csv", index=False
    )

    leg1_check = (
        leg3._leg1_per_row_check(loops)
        if not args.smoke
        else {"leg1_per_row_available": False}
    )
    leg3_check = _leg3_cross_check(loops, discovery_frame)

    arm_summaries = {
        arm: _arm_summary(loops, worlds_frame, arm) for arm in ARMS
    }
    lean_a4a_hold = bool(
        arm_summaries["arm2_penalized"]["flips_total"] <= 120
    )
    lean_b4a_hold = bool(
        arm_summaries["arm2_penalized"]["pooled_loop_geometry"] >= 0.70
    )
    primary_verdicts = {
        world: scaling_analysis[world]["e_d_paired"]["verdict"]
        for world in scaling_analysis
        if world != "POOLED"
    }
    values = set(primary_verdicts.values())
    if values <= {"BUDGET_LIMITED", "BUDGET_LIMITED_STEEP"}:
        fork = "BUDGET_THEOREM"
    elif values == {"STRUCTURAL_FLOOR"}:
        fork = "RESOLUTION_LIMIT"
    else:
        fork = "MIXED"

    n_degenerate = int(budget_frame["degenerate_reference"].sum())
    decision = {
        "estimand_id": "SUICA_M4_D_LEG4_DLEG_FLOOR",
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
            **leg3_check,
        },
        "part_4a": {
            "selection_rule": (
                "lambda by out-of-fold route-identification accuracy "
                "(fewest D-zero flips vs oracle route) on discovery reps "
                f"{list(discovery_reps)}; ties -> fewer route-name "
                "mismatches -> smaller lambda"
            ),
            "lambda_grid": list(LAMBDA_GRID),
            "lambda_table": {
                str(lam): lambda_table[lam] for lam in sorted(lambda_table)
            },
            "chosen_lambda": chosen_lambda,
            "boundary_bound": boundary_bound,
            "mechanism_saturated_declaration": (
                "route-accuracy selection binds at a grid boundary; the "
                "ridge mechanism is declared saturated per the registered "
                "soft outcome"
                if boundary_bound
                else "selection is interior; mechanism not saturated"
            ),
            "arms": arm_summaries,
            "lean_a4a": {
                "registered": "total flips <= 120 at the selected lambda",
                "value": arm_summaries["arm2_penalized"]["flips_total"],
                "hold": lean_a4a_hold,
            },
            "lean_b4a": {
                "registered": "pooled loop geometry >= .70",
                "value": arm_summaries["arm2_penalized"][
                    "pooled_loop_geometry"
                ],
                "hold": lean_b4a_hold,
            },
            "leg3_comparison": {
                "lambda": 0.005,
                "flips": 148,
                "pooled_loop_geometry": 0.6885829871801226,
            },
        },
        "part_4b": {
            "design": {
                "budgets": list(BUDGETS),
                "events_by_budget": {
                    str(budget): int(round(spec.events * budget))
                    for budget in BUDGETS
                },
                "four_x_possible": True,
                "route": "oracle stack's V2-selected model per author-view, "
                "forced on both sides; no selection anywhere",
                "primary_metric": "e_d_paired (D_disc(b) vs D_orc(b), "
                "program-standard D-leg error; coincides with e_d_atom at "
                "1x at the correct route)",
                "companions": [
                    "e_d_true",
                    "e_orc_true",
                    "e_d_frozen",
                ],
                "frozen_world_semantics": "condition panels, mechanism "
                "parameters, oracle basis bit-identical across budgets "
                "(asserted); chart and bases frozen at V2 1x; non-1x "
                "panels are fresh path realizations of the identical law",
            },
            "identity_gates": {
                "true_d_unit_check_max_gap": float(
                    max(
                        gate["true_d_unit_check_max_gap"]
                        for gate in budget_gates
                    )
                ),
                "orc_refit_identity_max_gap_1x": float(
                    max(
                        gate["orc_refit_identity_max_gap_1x"]
                        for gate in budget_gates
                    )
                ),
                "disc_forced_identity_max_gap_1x": float(
                    max(
                        gate["disc_forced_identity_max_gap_1x"]
                        for gate in budget_gates
                    )
                ),
                "disc_forced_identity_rows_1x": int(
                    sum(
                        gate["disc_forced_identity_rows_1x"]
                        for gate in budget_gates
                    )
                ),
            },
            "degenerate_reference_rows": n_degenerate,
            "scaling": scaling_analysis,
            "per_world_verdict_primary": primary_verdicts,
            "per_world_verdict_true": {
                world: scaling_analysis[world]["e_d_true"]["verdict"]
                for world in scaling_analysis
                if world != "POOLED"
            },
            "pooled_verdict_primary": scaling_analysis["POOLED"][
                "e_d_paired"
            ]["verdict"],
            "fork_verdict": fork,
            "verdict_rules": {
                "plateau": f"|tail slope (1x,2x,4x)| < {PLATEAU_BAR}",
                "budget_limited": f"overall slope in {list(BUDGET_BAND)} "
                "and no plateau",
                "target": TARGET_E_D,
            },
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "estimator diagnostics (oracle-basis fits and generator-law "
            "derivatives are consumed as references), so nothing here is an "
            "operational rescue of chart transport or a reopened gate; the "
            "V1/V2 NO-GO decisions stand; the 4b budget curve maps the "
            "resolution economics of the V2 creation-derivative estimator "
            "at the correct route, not a deployable estimator; no "
            "natural-text, personality, emotion, or clinical claim; "
            "EXPLORATORY tier under the 2026-08-01 open-exploration "
            "directive."
        ),
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(decision, indent=2, sort_keys=True))
    print(
        f"[done] total {time.time() - started_all:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
