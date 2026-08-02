#!/usr/bin/env python3
"""M4-D Leg 12: two-stage retrofit of the M4-C.3 physical-edge attribution NO-GO.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 12 -- two-stage retrofit of the M4-C.3 physical-edge attribution NO-GO",
2026-08-02, before this run; first standing-queue item after the closed M4-D
arc).

TARGET: the M4-C.3 error-budget attribution NO-GO
(reports/SUICA_M4_PHYSICAL_EDGE_COMPOSITION_V1_NO_GO.md;
results/m4_physical_edge_audit_v1_no_go/): pooled budget Spearman .7264 < .75,
passing reps 4 < 6, fault accuracy 1.0. It was measured with V2 single-stage
route production. The M4-D arc established that two-stage route-then-refit
removes route-flip contamination (196 -> 73 flips; pooled loop geometry
.6519 -> .7605; Legs 3/4a/5). Question: does recomputing the C.3 attribution
over TWO-STAGE loops lift the attribution ordering past its own registered
bar?

DESIGN (bounded retrofit; no new estimators, no redesign of the attribution
formula): rerun the EXACT C.3 attribution battery -- same config, same worlds,
same 8 repetitions, same seeds, same Shapley/error-budget formulas, same
Spearman target, same decision function -- changing ONLY the DISCOVERED-side
loop/leg production to the two-stage construction reused from
scripts/run_suica_m4_d_two_stage_leg5.py:

- STAGE 1 (route selection): the arm-2 penalized hazard candidate flow at the
  route-accuracy-selected ridge lambda = .125
  (leg3._fit_hazard_penalized, extra ridge on feedback_*/gate_* coordinates,
  candidates fit on the calibration panel only), scored with the C.3
  estimator's own selection rule (selection-panel logloss +
  complexity_penalty x design width, tie rule <= min + 1e-10). Models with no
  feedback/gate coordinates (base, return) reuse the V2 candidate scores --
  the penalty is vacuous on them, exactly as in leg5's stage 1.
- STAGE 2 (V2 unpenalized refit at the selected route): the C.3 estimator's
  own final-refit semantics (_fit_hazard_candidate on the combined
  calibration+selection panels, hazard ridge .005, 30 IRLS iterations) at the
  FIXED stage-1 route; no selection anywhere in stage 2. Where the stage-1
  route coincides with the V2-selected route the stage-2 refit is
  bit-identical to the V2 final fit by determinism (asserted per author).

The oracle reference route is frozen V2 semantics, shared bit-for-bit between
arms (M4-D arm discipline: arms modify the discovered-side estimation only).
Consequently the fault-injection sub-battery (oracle-side only) is IDENTICAL
between arms by construction, and fault accuracy 1.0 carries over.

REPRODUCE-FIRST DISCIPLINE: per world-rep, the freshly computed ORIGINAL-arm
rows (view diagnostics, fault rows, rank rows) are asserted against the
persisted results/m4_physical_edge_audit_v1_no_go/*.csv BEFORE the retrofit
arm runs on that world-rep; the reassembled original decision is asserted
against the persisted decision.json (Spearman .7264181903422411, passing reps
4, fault accuracy 1.0, decision string) before adjudication.

REGISTERED LEANS (adjudication statistics pre-coded here, before the run):
- (a) retrofit pooled budget Spearman >= .75 (the original bar; from .7264);
- (b) retrofit passing repetitions >= 6 (from 4);
- (c) the improvement concentrates in reps where stage-1 corrected route
  flips. Pre-coded operationalization (the registration is verbal; this
  coding is fixed before any retrofit number is seen): the split variable is
  the per-repetition count of CORRECTED D-ZERO FLIPS (Leg 1's flip
  definition, exactly one of ||D_disc||, ||D_oracle|| < 1e-10: rows that flip
  under V2 and do not flip under two-stage, summed over worlds x views x
  authors in the rep). Primary split: reps with corrected flips > 0 vs = 0;
  (c) HOLDS iff both groups are nonempty AND mean delta-Spearman (retrofit -
  original, per-rep) of the corrected group exceeds the untouched group's AND
  is positive. Degenerate fallback (one group empty): (c) HOLDS iff Spearman
  between per-rep corrected-flip count and per-rep delta-Spearman >= .5 over
  the 8 reps. The name-level route-correction variant is reported alongside
  in both cases.

PIVOT-IF (registered): pooled budget Spearman moves < .01 in absolute value
-> the attribution deficit is INDEPENDENT of route contamination; record
plainly and return the item to the M4-C track's queue unchanged.
"""
from __future__ import annotations

import argparse
import copy
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

import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402  bit-exact reuse
import run_suica_m4_physical_edge_audit as c3  # noqa: E402  bit-exact reuse

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    HAZARD_MODELS,
    _choice_delta,
    _choice_logloss,
    _feedback_derivative,
    _fit_choice,
    _fit_hazard_candidate,
    _fit_response,
    _flatten_events,
    _hazard_design,
    _hazard_logloss,
    _hazard_probability,
    _response_loss,
    build_m4_discovered_basis,
    rotate_whitened_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    M4PhysicalEdgeRoute,
    M4PhysicalEdgeView,
    fit_m4_physical_edge_route,
)

STAGE1_EXTRA_RIDGE = 0.125  # Leg 4a route-accuracy-selected ridge (leg5 stage 1)
PENALIZED_MODELS = ("feedback", "gate")  # models with feedback_/gate_ coords
FLIP_TOLERANCE = 1e-10  # Leg 1's D-zero flip tolerance (leg3.FLIP_TOLERANCE)
ROW_TOLERANCE = 1e-9  # persisted-row reproduction assert bar (leg5 convention)
ORIGINAL_RESULTS = ROOT / "results" / "m4_physical_edge_audit_v1_no_go"
LEAN_A_BAR = 0.75
LEAN_B_BAR = 6
PIVOT_EPSILON = 0.01
LEAN_C_FALLBACK_RHO = 0.5

METRIC_KEYS = ["repetition", "world", "view"]
FAULT_KEYS = ["repetition", "world", "view", "planted_edge"]
RANK_KEYS = ["repetition", "world", "view", "requested_rank"]


# ---------------------------------------------------------------------------
# two-stage author fitter (verbatim C.3 numeric path; hazard block two-staged)
# ---------------------------------------------------------------------------


def _fit_author_edges_two_stage(
    calibration_panel: Any,
    selection_panel: Any,
    evaluation_panel: Any,
    basis: dict[str, np.ndarray],
    author: int,
    *,
    ridge_grid: tuple[float, ...],
    hazard_ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
) -> dict[str, Any]:
    """C.3 _fit_author_edges with the hazard block replaced by two-stage.

    Choice/response fits and every downstream reconstruction line are copied
    verbatim from suica_core.m4_physical_edge_composition._fit_author_edges;
    only the hazard-route production differs (stage-1 penalized selection at
    extra ridge .125, stage-2 V2 unpenalized refit at the fixed route).
    """
    calibration = _flatten_events(calibration_panel, author)
    selection = _flatten_events(selection_panel, author)
    evaluation = _flatten_events(evaluation_panel, author)
    calibration_pair = (calibration, basis["calibration"])
    selection_pair = (selection, basis["selection"])
    combined = [calibration_pair, selection_pair]

    choice_candidates = [
        _fit_choice([calibration_pair], ridge=ridge)
        for ridge in ridge_grid
    ]
    choice_losses = [
        _choice_logloss(
            coefficient,
            selection,
            basis["selection"],
        )
        for coefficient in choice_candidates
    ]
    minimum_choice_loss = float(np.min(choice_losses))
    choice_ridge = next(
        ridge
        for ridge, loss in zip(ridge_grid, choice_losses, strict=True)
        if loss <= minimum_choice_loss + 1e-10
    )
    choice_coefficient = _fit_choice(combined, ridge=choice_ridge)

    response_candidates = [
        _fit_response([calibration_pair], ridge=ridge)
        for ridge in ridge_grid
    ]
    response_losses = [
        _response_loss(
            coefficient,
            selection,
            basis["selection"],
        )
        for coefficient in response_candidates
    ]
    minimum_response_loss = float(np.min(response_losses))
    response_ridge = next(
        ridge
        for ridge, loss in zip(ridge_grid, response_losses, strict=True)
        if loss <= minimum_response_loss + 1e-10
    )
    response_coefficient = _fit_response(
        combined,
        ridge=response_ridge,
    )

    # -- V2 candidate scores (verbatim C.3 hazard-candidate block) --
    v2_scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        coefficient, _ = _fit_hazard_candidate(
            [calibration_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
        )
        design, _ = _hazard_design(
            selection,
            basis["selection"],
            model=model,
        )
        v2_scores[model] = (
            _hazard_logloss(
                coefficient,
                design,
                selection["generated_next"],
            )
            + complexity_penalty * design.shape[1]
        )
    minimum_v2_score = min(v2_scores.values())
    v2_selected = next(
        model
        for model in HAZARD_MODELS
        if v2_scores[model] <= minimum_v2_score + 1e-10
    )

    # -- STAGE 1: penalized route selection at extra ridge .125 --
    stage1_scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        if model not in PENALIZED_MODELS:
            # no feedback_/gate_ coordinates: the penalty is vacuous and the
            # penalized fit is bit-identical to the V2 candidate (leg5 reuse)
            stage1_scores[model] = v2_scores[model]
            continue
        coefficient, _ = leg3._fit_hazard_penalized(
            [calibration_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
            extra_ridge=STAGE1_EXTRA_RIDGE,
        )
        design, _ = _hazard_design(
            selection,
            basis["selection"],
            model=model,
        )
        stage1_scores[model] = (
            _hazard_logloss(
                coefficient,
                design,
                selection["generated_next"],
            )
            + complexity_penalty * design.shape[1]
        )
    minimum_stage1_score = min(stage1_scores.values())
    stage1_selected = next(
        model
        for model in HAZARD_MODELS
        if stage1_scores[model] <= minimum_stage1_score + 1e-10
    )

    # -- STAGE 2: V2 unpenalized final refit at the fixed stage-1 route --
    hazard_coefficient, hazard_names = _fit_hazard_candidate(
        combined,
        model=stage1_selected,
        ridge=hazard_ridge,
        iterations=logistic_iterations,
    )

    # -- verbatim C.3 reconstruction from the fitted legs --
    evaluation_basis = basis["evaluation"]
    response_dimensions = evaluation["response"].shape[1]
    basis_width = evaluation_basis.shape[1]
    response_choice = response_coefficient[
        response_dimensions : response_dimensions + basis_width
    ].T
    choice_basis = _choice_delta(
        choice_coefficient,
        evaluation_basis,
    )
    basis_reconstruction = np.linalg.pinv(
        evaluation_basis.T,
        rcond=1e-10,
    )
    choice_physical = basis_reconstruction @ choice_basis
    response_physical = response_choice @ evaluation_basis.T
    creation_physical = _feedback_derivative(
        hazard_coefficient,
        hazard_names,
        evaluation_basis,
        response_dimensions,
    )
    jacobian_loop = (
        creation_physical @ response_physical @ choice_physical
    )
    legacy_loop = creation_physical @ response_choice @ choice_basis
    projection_error = (
        np.linalg.norm(
            evaluation_basis.T @ choice_physical - choice_basis
        )
        / max(np.linalg.norm(choice_basis), 1e-12)
    )
    legacy_difference = (
        np.linalg.norm(jacobian_loop - legacy_loop)
        / max(np.linalg.norm(legacy_loop), 1e-12)
    )

    baseline = _hazard_probability(
        hazard_coefficient,
        hazard_names,
        evaluation_basis,
        np.zeros((1, response_dimensions)),
        np.zeros(1),
    )[0]
    finite_loop = np.empty_like(jacobian_loop)
    for category in range(len(evaluation_basis)):
        response_delta = (
            response_physical @ choice_physical[:, category]
        )
        changed = _hazard_probability(
            hazard_coefficient,
            hazard_names,
            evaluation_basis,
            response_delta[None],
            np.zeros(1),
        )[0]
        finite_loop[:, category] = changed - baseline
    return {
        "creation": creation_physical,
        "response": response_physical,
        "choice": choice_physical,
        "jacobian_loop": jacobian_loop,
        "finite_loop": finite_loop,
        "projection_error": float(projection_error),
        "legacy_loop_difference": float(legacy_difference),
        "v2_selected": v2_selected,
        "stage1_selected": stage1_selected,
    }


def _fit_view_two_stage(
    calibration: Any,
    selection: Any,
    evaluation: Any,
    basis: dict[str, np.ndarray],
    original_view: M4PhysicalEdgeView | None,
    **parameters: Any,
) -> tuple[M4PhysicalEdgeView, list[dict[str, Any]]]:
    """Two-stage view; asserts shared legs against the original V2 view.

    When original_view is supplied (the primary discovered route), three
    internal-consistency gates certify the verbatim numeric path:
    (i) the recomputed V2 route selection equals the original view's
    selected_model per author; (ii) the response/choice physical legs are
    exactly equal (bit-identical shared fits); (iii) on authors whose stage-1
    route equals the V2 route the stage-2 creation leg is exactly equal to
    the original (fresh refit == reuse by determinism).
    """
    rows = [
        _fit_author_edges_two_stage(
            calibration,
            selection,
            evaluation,
            basis,
            author,
            **parameters,
        )
        for author in range(calibration.menu.shape[0])
    ]
    if original_view is not None:
        for author, row in enumerate(rows):
            if row["v2_selected"] != str(original_view.selected_model[author]):
                raise RuntimeError(
                    "recomputed V2 route diverges from the original view "
                    f"(author {author}: {row['v2_selected']} vs "
                    f"{original_view.selected_model[author]})"
                )
            if not np.array_equal(
                row["response"], original_view.response[author]
            ) or not np.array_equal(
                row["choice"], original_view.choice[author]
            ):
                raise RuntimeError(
                    f"shared response/choice legs not bit-identical to the "
                    f"original view (author {author})"
                )
            if row["stage1_selected"] == row["v2_selected"] and not (
                np.array_equal(
                    row["creation"], original_view.creation[author]
                )
            ):
                raise RuntimeError(
                    "unchanged-route stage-2 creation leg not bit-identical "
                    f"to the original view (author {author})"
                )
    view = M4PhysicalEdgeView(
        creation=np.stack([row["creation"] for row in rows]),
        response=np.stack([row["response"] for row in rows]),
        choice=np.stack([row["choice"] for row in rows]),
        jacobian_loop=np.stack([row["jacobian_loop"] for row in rows]),
        finite_loop=np.stack([row["finite_loop"] for row in rows]),
        selected_model=np.asarray(
            [row["stage1_selected"] for row in rows]
        ),
        projection_error=np.asarray(
            [row["projection_error"] for row in rows]
        ),
        legacy_loop_difference=np.asarray(
            [row["legacy_loop_difference"] for row in rows]
        ),
    )
    return view, rows


def fit_two_stage_route(
    ecology: Any,
    basis: dict[str, np.ndarray],
    *,
    basis_name: str,
    original_route: M4PhysicalEdgeRoute | None = None,
    ridge_grid: tuple[float, ...] = (0.03, 0.10, 0.30),
    hazard_ridge: float = 0.10,
    logistic_iterations: int = 14,
    complexity_penalty: float = 0.0004,
    **_: Any,
) -> tuple[M4PhysicalEdgeRoute, dict[str, list[dict[str, Any]]]]:
    """Two-stage analog of fit_m4_physical_edge_route (same signature)."""
    parameters = {
        "ridge_grid": ridge_grid,
        "hazard_ridge": hazard_ridge,
        "logistic_iterations": logistic_iterations,
        "complexity_penalty": complexity_penalty,
    }
    views: dict[str, M4PhysicalEdgeView] = {}
    records: dict[str, list[dict[str, Any]]] = {}
    for view_name, panels in (
        ("train", (ecology.train_calibration, ecology.train_selection,
                   ecology.train_evaluation)),
        ("test", (ecology.test_calibration, ecology.test_selection,
                  ecology.test_evaluation)),
    ):
        views[view_name], records[view_name] = _fit_view_two_stage(
            *panels,
            basis,
            getattr(original_route, view_name) if original_route else None,
            **parameters,
        )
    return (
        M4PhysicalEdgeRoute(
            basis_name=basis_name,
            train=views["train"],
            test=views["test"],
        ),
        records,
    )


def _basis_invariance_difference_two_stage(
    ecology: Any,
    basis: dict[str, np.ndarray],
    route: M4PhysicalEdgeRoute,
    *,
    route_parameters: dict[str, Any],
    seed: int,
) -> float:
    """c3._basis_invariance_difference with the two-stage route builder."""
    rotated, _ = fit_two_stage_route(
        ecology,
        rotate_whitened_basis(basis, seed=seed),
        basis_name="rotated_two_stage",
        **route_parameters,
    )
    values = []
    for view_name in ("train", "test"):
        first = getattr(route, view_name)
        second = getattr(rotated, view_name)
        for edge in (
            "creation",
            "response",
            "choice",
            "jacobian_loop",
            "finite_loop",
        ):
            values.append(
                float(
                    np.max(
                        np.abs(
                            getattr(first, edge) - getattr(second, edge)
                        )
                    )
                )
            )
    return max(values)


# ---------------------------------------------------------------------------
# route-structure bookkeeping (flip / correction accounting)
# ---------------------------------------------------------------------------


def _route_rows(
    oracle_route: M4PhysicalEdgeRoute,
    original_route: M4PhysicalEdgeRoute,
    two_stage_route: M4PhysicalEdgeRoute,
    records: dict[str, list[dict[str, Any]]],
    *,
    repetition: int,
    world: str,
) -> list[dict[str, Any]]:
    rows = []
    for view_name in ("train", "test"):
        oracle = getattr(oracle_route, view_name)
        original = getattr(original_route, view_name)
        retrofit = getattr(two_stage_route, view_name)
        for author, record in enumerate(records[view_name]):
            d_oracle = float(np.linalg.norm(oracle.creation[author]))
            d_v2 = float(np.linalg.norm(original.creation[author]))
            d_ts = float(np.linalg.norm(retrofit.creation[author]))
            oracle_zero = d_oracle < FLIP_TOLERANCE
            flip_v2 = bool((d_v2 < FLIP_TOLERANCE) != oracle_zero)
            flip_ts = bool((d_ts < FLIP_TOLERANCE) != oracle_zero)
            oracle_model = str(oracle.selected_model[author])
            v2_model = record["v2_selected"]
            ts_model = record["stage1_selected"]
            rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "view": view_name,
                    "author": author,
                    "oracle_model": oracle_model,
                    "v2_model": v2_model,
                    "two_stage_model": ts_model,
                    "route_changed": bool(ts_model != v2_model),
                    "v2_route_mismatch": bool(v2_model != oracle_model),
                    "two_stage_route_mismatch": bool(
                        ts_model != oracle_model
                    ),
                    "route_corrected": bool(
                        v2_model != oracle_model and ts_model == oracle_model
                    ),
                    "route_broken": bool(
                        v2_model == oracle_model and ts_model != oracle_model
                    ),
                    "flip_v2": flip_v2,
                    "flip_two_stage": flip_ts,
                    "flip_corrected": bool(flip_v2 and not flip_ts),
                    "flip_broken": bool(not flip_v2 and flip_ts),
                    "d_norm_oracle": d_oracle,
                    "d_norm_v2": d_v2,
                    "d_norm_two_stage": d_ts,
                }
            )
    return rows


# ---------------------------------------------------------------------------
# persisted-row reproduction asserts
# ---------------------------------------------------------------------------


def _load_persisted() -> dict[str, Any]:
    if not ORIGINAL_RESULTS.exists():
        raise RuntimeError(
            f"persisted NO-GO results are required: {ORIGINAL_RESULTS}"
        )
    with (ORIGINAL_RESULTS / "decision.json").open(
        "r", encoding="utf-8"
    ) as handle:
        decision = json.load(handle)
    return {
        "decision": decision,
        "metrics": pd.read_csv(ORIGINAL_RESULTS / "metrics.csv"),
        "faults": pd.read_csv(
            ORIGINAL_RESULTS / "fault_attribution.csv",
            keep_default_na=False,
            na_values=[""],
        ),
        "ranks": pd.read_csv(ORIGINAL_RESULTS / "rank_diagnostics.csv"),
        "repetition_metrics": pd.read_csv(
            ORIGINAL_RESULTS / "repetition_metrics.csv"
        ),
    }


def _frame_max_difference(
    mine: pd.DataFrame,
    stored: pd.DataFrame,
    keys: list[str],
    label: str,
) -> float:
    """Align two frames on keys and return the max abs float difference."""
    if sorted(mine.columns) != sorted(stored.columns):
        raise RuntimeError(
            f"{label}: column sets differ "
            f"({sorted(mine.columns)} vs {sorted(stored.columns)})"
        )
    merged = stored.merge(
        mine, on=keys, suffixes=("_stored", "_mine"), how="outer",
        indicator=True,
    )
    if (merged["_merge"] != "both").any() or len(merged) != len(stored):
        raise RuntimeError(
            f"{label}: rows misaligned ({len(mine)} mine vs "
            f"{len(stored)} stored, {int((merged['_merge'] == 'both').sum())}"
            " matched)"
        )
    worst = 0.0
    for column in mine.columns:
        if column in keys:
            continue
        left = stored.sort_values(keys)[column].to_numpy()
        right = mine.sort_values(keys)[column].to_numpy()
        if left.dtype.kind in "OUSb" or right.dtype.kind in "OUSb":
            same = pd.Series(left).fillna("__nan__").eq(
                pd.Series(right).fillna("__nan__")
            )
            if not bool(same.all()):
                raise RuntimeError(
                    f"{label}: non-numeric column {column} differs"
                )
            continue
        left = np.asarray(left, dtype=float)
        right = np.asarray(right, dtype=float)
        nan_left = np.isnan(left)
        nan_right = np.isnan(right)
        if not np.array_equal(nan_left, nan_right):
            raise RuntimeError(f"{label}: NaN pattern differs in {column}")
        good = ~nan_left
        if good.any():
            worst = max(
                worst, float(np.max(np.abs(left[good] - right[good])))
            )
    if worst > ROW_TOLERANCE:
        raise RuntimeError(
            f"{label}: reproduction diverges from persisted rows "
            f"(max abs difference {worst:.3e} > {ROW_TOLERANCE:.0e})"
        )
    return worst


def _assert_original_decision(
    reproduced: dict[str, Any],
    persisted: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "decision_string_equal": bool(
            reproduced["decision"] == persisted["decision"]
        ),
        "checks_equal": bool(
            reproduced["checks"] == persisted["checks"]
        ),
    }
    worst = 0.0
    for name, stored_value in persisted["diagnostics"].items():
        mine_value = reproduced["diagnostics"][name]
        if isinstance(stored_value, dict):
            for key, inner in stored_value.items():
                worst = max(
                    worst, abs(float(mine_value[key]) - float(inner))
                )
        elif isinstance(stored_value, (int, float)):
            worst = max(worst, abs(float(mine_value) - float(stored_value)))
    checks["diagnostics_max_abs_difference"] = worst
    if not checks["decision_string_equal"] or not checks["checks_equal"]:
        raise RuntimeError(
            "reproduced original decision diverges from persisted "
            f"decision.json: {checks}"
        )
    if worst > 1e-12:
        raise RuntimeError(
            "reproduced original diagnostics diverge from persisted "
            f"decision.json (max abs difference {worst:.3e} > 1e-12)"
        )
    return checks


# ---------------------------------------------------------------------------
# lean (c) split + adjudication (pre-coded; see module docstring)
# ---------------------------------------------------------------------------


def _lean_c_adjudication(
    per_rep: pd.DataFrame,
    count_column: str,
) -> dict[str, Any]:
    corrected = per_rep[per_rep[count_column] > 0]
    untouched = per_rep[per_rep[count_column] == 0]
    graded = (
        leg3._pooled_spearman(per_rep, count_column, "delta_spearman")
        if per_rep[count_column].nunique() > 1
        else float("nan")
    )
    if len(corrected) and len(untouched):
        mode = "primary_split"
        mean_corrected = float(corrected["delta_spearman"].mean())
        mean_untouched = float(untouched["delta_spearman"].mean())
        hold = bool(
            mean_corrected > mean_untouched and mean_corrected > 0.0
        )
    else:
        mode = "degenerate_fallback"
        mean_corrected = (
            float(corrected["delta_spearman"].mean())
            if len(corrected)
            else float("nan")
        )
        mean_untouched = (
            float(untouched["delta_spearman"].mean())
            if len(untouched)
            else float("nan")
        )
        hold = bool(
            np.isfinite(graded) and graded >= LEAN_C_FALLBACK_RHO
        )
    return {
        "split_variable": count_column,
        "mode": mode,
        "reps_corrected": int(len(corrected)),
        "reps_untouched": int(len(untouched)),
        "mean_delta_spearman_corrected": mean_corrected,
        "mean_delta_spearman_untouched": mean_untouched,
        "graded_spearman_count_vs_delta": graded,
        "hold": hold,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_physical_edge_audit.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "m4_d_c3_retrofit",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    started_all = time.time()
    config = c3._load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    candidates = tuple(dict(value) for value in config["candidates"])
    route_parameters = c3._route_parameters(config)
    query_bank = np.asarray(config["query_bank"], dtype=float).T
    persisted = _load_persisted()

    repetitions = int(config["repetitions"])
    worlds = list(config["worlds"])
    if args.smoke:
        repetitions = 1
        worlds = worlds[:2]
        output = args.output / "smoke"
    else:
        output = args.output

    original_rows: list[dict[str, Any]] = []
    retrofit_rows: list[dict[str, Any]] = []
    fault_rows: list[dict[str, Any]] = []
    original_rank_rows: list[dict[str, Any]] = []
    retrofit_rank_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    reproduction_rows: list[dict[str, Any]] = []

    for repetition in range(repetitions):
        for world_index, world in enumerate(worlds):
            started = time.time()
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            observed, truth = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            chart = fit_m4_condition_chart(
                observed.condition,
                candidates=candidates,
                **config["chart_thresholds"],
            )
            _, discovered_basis = build_m4_discovered_basis(
                observed,
                chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["primary_rank"]),
            )
            oracle = fit_m4_physical_edge_route(
                observed.ecology,
                truth.oracle_basis,
                basis_name="oracle",
                **route_parameters,
            )
            discovered = fit_m4_physical_edge_route(
                observed.ecology,
                discovered_basis,
                basis_name="discovered",
                **route_parameters,
            )
            basis_difference = (
                c3._basis_invariance_difference(
                    observed.ecology,
                    discovered_basis,
                    discovered,
                    route_parameters=route_parameters,
                    seed=seed + 800_009,
                )
                if repetition == 0 and world_index == 0
                else 0.0
            )
            cell_original_rows = []
            for view_name in ("train", "test"):
                values = c3._view_diagnostics(
                    getattr(oracle, view_name),
                    getattr(discovered, view_name),
                    query_bank,
                )
                cell_original_rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "view": view_name,
                        "transform_rank": discovered_basis[
                            "evaluation"
                        ].shape[1],
                        "basis_invariance_max_difference": basis_difference,
                        **values,
                    }
                )
            cell_fault_rows = c3._fault_rows(
                oracle,
                repetition=repetition,
                world=world,
                strength=float(config["fault_strength"]),
                seed=seed + 900_001,
            )
            cell_rank_rows = []
            rank_bases: dict[int, dict[str, np.ndarray]] = {}
            if repetition < int(config["rank_diagnostic_repetitions"]):
                for requested_rank in config["rank_arms"]:
                    _, rank_basis = build_m4_discovered_basis(
                        observed,
                        chart,
                        rank_tolerance=float(config["rank_tolerance"]),
                        maximum_rank=int(requested_rank),
                    )
                    rank_bases[int(requested_rank)] = rank_basis
                    rank_route = fit_m4_physical_edge_route(
                        observed.ecology,
                        rank_basis,
                        basis_name=f"rank_{requested_rank}",
                        **route_parameters,
                    )
                    for view_name in ("train", "test"):
                        cell_rank_rows.append(
                            {
                                "repetition": repetition,
                                "world": world,
                                "view": view_name,
                                "requested_rank": requested_rank,
                                "realized_rank": rank_basis[
                                    "evaluation"
                                ].shape[1],
                                "loop_geometry": c3._geometry(
                                    getattr(
                                        rank_route,
                                        view_name,
                                    ).jacobian_loop,
                                    getattr(
                                        oracle,
                                        view_name,
                                    ).jacobian_loop,
                                ),
                            }
                        )

            # ---- reproduction asserts BEFORE the retrofit arm ----
            reproduction = {
                "repetition": repetition,
                "world": world,
                "seed": seed,
            }
            if not args.smoke:
                stored_metrics = persisted["metrics"]
                reproduction["metrics_max_abs_difference"] = (
                    _frame_max_difference(
                        pd.DataFrame(cell_original_rows),
                        stored_metrics[
                            (stored_metrics["repetition"] == repetition)
                            & (stored_metrics["world"] == world)
                        ],
                        METRIC_KEYS,
                        f"metrics {world} rep {repetition}",
                    )
                )
                stored_faults = persisted["faults"]
                reproduction["faults_max_abs_difference"] = (
                    _frame_max_difference(
                        pd.DataFrame(cell_fault_rows),
                        stored_faults[
                            (stored_faults["repetition"] == repetition)
                            & (stored_faults["world"] == world)
                        ],
                        FAULT_KEYS,
                        f"faults {world} rep {repetition}",
                    )
                )
                if cell_rank_rows:
                    stored_ranks = persisted["ranks"]
                    reproduction["ranks_max_abs_difference"] = (
                        _frame_max_difference(
                            pd.DataFrame(cell_rank_rows),
                            stored_ranks[
                                (stored_ranks["repetition"] == repetition)
                                & (stored_ranks["world"] == world)
                            ],
                            RANK_KEYS,
                            f"ranks {world} rep {repetition}",
                        )
                    )
            reproduction_rows.append(reproduction)
            original_rows.extend(cell_original_rows)
            fault_rows.extend(cell_fault_rows)
            original_rank_rows.extend(cell_rank_rows)

            # ---- retrofit arm: two-stage discovered-side production ----
            two_stage, records = fit_two_stage_route(
                observed.ecology,
                discovered_basis,
                basis_name="two_stage_discovered",
                original_route=discovered,
                **route_parameters,
            )
            retrofit_basis_difference = (
                _basis_invariance_difference_two_stage(
                    observed.ecology,
                    discovered_basis,
                    two_stage,
                    route_parameters=route_parameters,
                    seed=seed + 800_009,
                )
                if repetition == 0 and world_index == 0
                else 0.0
            )
            for view_name in ("train", "test"):
                values = c3._view_diagnostics(
                    getattr(oracle, view_name),
                    getattr(two_stage, view_name),
                    query_bank,
                )
                retrofit_rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "view": view_name,
                        "transform_rank": discovered_basis[
                            "evaluation"
                        ].shape[1],
                        "basis_invariance_max_difference": (
                            retrofit_basis_difference
                        ),
                        **values,
                    }
                )
            route_rows.extend(
                _route_rows(
                    oracle,
                    discovered,
                    two_stage,
                    records,
                    repetition=repetition,
                    world=world,
                )
            )
            for requested_rank, rank_basis in rank_bases.items():
                rank_two_stage, _ = fit_two_stage_route(
                    observed.ecology,
                    rank_basis,
                    basis_name=f"two_stage_rank_{requested_rank}",
                    original_route=None,
                    **route_parameters,
                )
                for view_name in ("train", "test"):
                    retrofit_rank_rows.append(
                        {
                            "repetition": repetition,
                            "world": world,
                            "view": view_name,
                            "requested_rank": requested_rank,
                            "realized_rank": rank_basis[
                                "evaluation"
                            ].shape[1],
                            "loop_geometry": c3._geometry(
                                getattr(
                                    rank_two_stage,
                                    view_name,
                                ).jacobian_loop,
                                getattr(
                                    oracle,
                                    view_name,
                                ).jacobian_loop,
                            ),
                        }
                    )
            cell_routes = [
                row
                for row in route_rows
                if row["repetition"] == repetition and row["world"] == world
            ]
            print(
                f"[battery] rep={repetition} world={world} "
                f"changed={sum(r['route_changed'] for r in cell_routes)} "
                f"flip_corrected="
                f"{sum(r['flip_corrected'] for r in cell_routes)} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    metrics_original = pd.DataFrame(original_rows)
    metrics_retrofit = pd.DataFrame(retrofit_rows)
    faults = pd.DataFrame(fault_rows)
    ranks_original = pd.DataFrame(original_rank_rows)
    ranks_retrofit = pd.DataFrame(retrofit_rank_rows)
    routes = pd.DataFrame(route_rows)
    reproduction_frame = pd.DataFrame(reproduction_rows)

    original_decision = c3._decision(
        metrics_original, faults, ranks_original, config
    )
    retrofit_config = copy.deepcopy(config)
    retrofit_config["estimand_id"] = (
        "SUICA_M4_D_LEG12_C3_TWO_STAGE_RETROFIT"
    )
    retrofit_decision = c3._decision(
        metrics_retrofit, faults, ranks_retrofit, retrofit_config
    )

    reproduction_summary: dict[str, Any] = {
        "reference": str(ORIGINAL_RESULTS.relative_to(ROOT)),
        "world_reps_checked": int(len(reproduction_frame)),
        "row_assert_tolerance": ROW_TOLERANCE,
    }
    if not args.smoke:
        for column in (
            "metrics_max_abs_difference",
            "faults_max_abs_difference",
            "ranks_max_abs_difference",
        ):
            if column in reproduction_frame:
                reproduction_summary[column] = float(
                    reproduction_frame[column].max()
                )
        reproduction_summary.update(
            _assert_original_decision(
                original_decision, persisted["decision"]
            )
        )

    # ---- per-rep comparison + registered lean (c) split ----
    original_reps = pd.DataFrame(
        original_decision["repetition_metrics"]
    ).set_index("repetition")
    retrofit_reps = pd.DataFrame(
        retrofit_decision["repetition_metrics"]
    ).set_index("repetition")
    rep_structure = (
        routes.groupby("repetition")[
            [
                "route_changed",
                "route_corrected",
                "route_broken",
                "flip_v2",
                "flip_two_stage",
                "flip_corrected",
                "flip_broken",
                "v2_route_mismatch",
                "two_stage_route_mismatch",
            ]
        ]
        .sum()
        .astype(int)
    )
    per_rep = pd.DataFrame(
        {
            "error_spearman_original": original_reps["error_spearman"],
            "error_spearman_retrofit": retrofit_reps["error_spearman"],
        }
    )
    per_rep["pass_original"] = (
        original_reps["error_spearman"]
        >= config["targets"]["minimum_error_loss_spearman"]
    ) & (
        original_reps["fault_accuracy"]
        >= config["targets"]["minimum_fault_localization_accuracy"]
    ) & original_reps["exact_reconstruction"]
    per_rep["pass_retrofit"] = (
        retrofit_reps["error_spearman"]
        >= config["targets"]["minimum_error_loss_spearman"]
    ) & (
        retrofit_reps["fault_accuracy"]
        >= config["targets"]["minimum_fault_localization_accuracy"]
    ) & retrofit_reps["exact_reconstruction"]
    per_rep["delta_spearman"] = (
        per_rep["error_spearman_retrofit"]
        - per_rep["error_spearman_original"]
    )
    per_rep = per_rep.join(rep_structure)
    per_rep = per_rep.reset_index()

    lean_c_primary = _lean_c_adjudication(per_rep, "flip_corrected")
    lean_c_secondary = _lean_c_adjudication(per_rep, "route_corrected")

    original_spearman = float(
        original_decision["diagnostics"]["error_budget_loss_spearman"]
    )
    retrofit_spearman = float(
        retrofit_decision["diagnostics"]["error_budget_loss_spearman"]
    )
    spearman_movement = retrofit_spearman - original_spearman
    lean_a_hold = bool(retrofit_spearman >= LEAN_A_BAR)
    retrofit_passing = int(
        retrofit_decision["diagnostics"]["passing_repetitions"]
    )
    lean_b_hold = bool(retrofit_passing >= LEAN_B_BAR)
    pivot_triggered = bool(abs(spearman_movement) < PIVOT_EPSILON)

    decision = {
        "estimand_id": "SUICA_M4_D_LEG12_C3_TWO_STAGE_RETROFIT",
        "tier": "EXPLORATORY",
        "config_seed": int(config["seed"]),
        "smoke": bool(args.smoke),
        "design": {
            "battery": (
                "exact C.3 attribution battery (config, worlds, seeds, "
                "repetitions, Shapley/error-budget formulas, decision "
                "function) with the DISCOVERED-side loop/leg production "
                "replaced by the two-stage construction; oracle reference "
                "route frozen V2 semantics shared bit-for-bit between arms"
            ),
            "stage1": (
                f"arm-2 penalized hazard candidate flow at extra ridge "
                f"lambda={STAGE1_EXTRA_RIDGE} (leg3._fit_hazard_penalized, "
                "calibration-only candidates, C.3 selection rule; "
                "base/return reuse the V2 candidate scores -- penalty "
                "vacuous on them)"
            ),
            "stage2": (
                "C.3's own V2 unpenalized final refit "
                "(_fit_hazard_candidate on combined calibration+selection, "
                f"hazard ridge {route_parameters['hazard_ridge']}, "
                f"{route_parameters['logistic_iterations']} IRLS "
                "iterations) at the FIXED stage-1 route; no selection in "
                "stage 2; unchanged-route rows bit-identical to the V2 "
                "final fit (asserted per author)"
            ),
            "fault_battery_note": (
                "the fault-injection sub-battery consumes the oracle route "
                "only, so its rows are IDENTICAL between arms by "
                "construction; fault accuracy 1.0 carries over"
            ),
        },
        "reproduction": reproduction_summary,
        "two_stage_structure": {
            "author_view_rows": int(len(routes)),
            "routes_changed": int(routes["route_changed"].sum()),
            "v2_route_mismatches": int(routes["v2_route_mismatch"].sum()),
            "two_stage_route_mismatches": int(
                routes["two_stage_route_mismatch"].sum()
            ),
            "routes_corrected": int(routes["route_corrected"].sum()),
            "routes_broken": int(routes["route_broken"].sum()),
            "v2_flips": int(routes["flip_v2"].sum()),
            "two_stage_flips": int(routes["flip_two_stage"].sum()),
            "flips_corrected": int(routes["flip_corrected"].sum()),
            "flips_broken": int(routes["flip_broken"].sum()),
        },
        "original_headline": {
            "decision": original_decision["decision"],
            "error_budget_loss_spearman": original_spearman,
            "passing_repetitions": int(
                original_decision["diagnostics"]["passing_repetitions"]
            ),
            "fault_localization_accuracy": float(
                original_decision["diagnostics"][
                    "fault_localization_accuracy"
                ]
            ),
            "jacobian_loop_transport_geometry": float(
                original_decision["diagnostics"][
                    "jacobian_loop_transport_geometry"
                ]
            ),
            "mean_shapley_loss": original_decision["diagnostics"][
                "mean_shapley_loss"
            ],
        },
        "retrofit_headline": {
            "decision": retrofit_decision["decision"],
            "error_budget_loss_spearman": retrofit_spearman,
            "passing_repetitions": retrofit_passing,
            "fault_localization_accuracy": float(
                retrofit_decision["diagnostics"][
                    "fault_localization_accuracy"
                ]
            ),
            "jacobian_loop_transport_geometry": float(
                retrofit_decision["diagnostics"][
                    "jacobian_loop_transport_geometry"
                ]
            ),
            "mean_shapley_loss": retrofit_decision["diagnostics"][
                "mean_shapley_loss"
            ],
        },
        "per_repetition": json.loads(per_rep.to_json(orient="records")),
        "lean_a": {
            "registered": (
                "pooled budget Spearman >= .75 (the original bar; from "
                ".7264)"
            ),
            "value": retrofit_spearman,
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": "passing repetitions >= 6 (from 4)",
            "value": retrofit_passing,
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered": (
                "improvement concentrated in reps where stage-1 corrected "
                "route flips (flip-corrected vs untouched rep split); "
                "operationalization pre-coded in the module docstring"
            ),
            "primary_flip_corrected": lean_c_primary,
            "secondary_route_corrected": lean_c_secondary,
            "hold": lean_c_primary["hold"],
        },
        "pivot_if": {
            "registered": (
                "pooled budget Spearman moves < .01 -> the attribution "
                "deficit is INDEPENDENT of route contamination; record "
                "plainly and return the item to the M4-C track's queue "
                "unchanged"
            ),
            "spearman_movement": spearman_movement,
            "triggered": pivot_triggered,
            "declaration": (
                "ATTRIBUTION_DEFICIT_INDEPENDENT_OF_ROUTE_CONTAMINATION_"
                "ITEM_RETURNS_TO_M4_C_QUEUE"
                if pivot_triggered
                else "not triggered"
            ),
        },
        "original_decision": original_decision,
        "retrofit_decision": retrofit_decision,
        "claim_boundary": (
            "Finite synthetic decomposition of physical choice, response, "
            "and creation edges on the frozen C.3 battery only; the "
            "retrofit changes the discovered-side estimator construction, "
            "not the attribution formula, targets, or worlds; the original "
            "C.3 NO-GO remains the decision of record unless the retrofit "
            "battery passes its own gates, and even then the result is an "
            "EXPLORATORY estimator finding -- it does not convert M4-C.2 "
            "to a pass, identify personality, validate natural text, or "
            "reopen M4-D; no seal, no independent verification (operator "
            "directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    metrics_original.to_csv(output / "metrics_original.csv", index=False)
    metrics_retrofit.to_csv(output / "metrics_retrofit.csv", index=False)
    faults.to_csv(output / "fault_attribution.csv", index=False)
    ranks_original.to_csv(
        output / "rank_diagnostics_original.csv", index=False
    )
    ranks_retrofit.to_csv(
        output / "rank_diagnostics_retrofit.csv", index=False
    )
    routes.to_csv(output / "route_structure.csv", index=False)
    reproduction_frame.to_csv(
        output / "reproduction_check.csv", index=False
    )
    per_rep.to_csv(
        output / "repetition_metrics_comparison.csv", index=False
    )
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        json.dumps(
            {
                key: decision[key]
                for key in (
                    "reproduction",
                    "two_stage_structure",
                    "original_headline",
                    "retrofit_headline",
                    "lean_a",
                    "lean_b",
                    "lean_c",
                    "pivot_if",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"[done] total {time.time() - started_all:.0f}s", flush=True)


if __name__ == "__main__":
    main()
