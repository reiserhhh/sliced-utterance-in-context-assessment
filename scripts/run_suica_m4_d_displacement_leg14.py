#!/usr/bin/env python3
"""M4-D Leg 14: discovery-objective displacement reduction -- the
quadratic-basin prediction test.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 14 -- discovery-objective displacement reduction", 2026-08-02 loop cycle
9, commit 693141d, BEFORE this run; ledger row M4-D.17). Machinery is IMPORTED
from the validated legs -- Leg 4's context build + canonical forced-route
refit, Leg 9's row-norm swap (the oracle point of the basin) and persisted
swap rows, Leg 11's stacked-frame quotient machinery (Kendall size-and-shape
space; its per-rep procrustes_residual is THIS leg's displacement anchor).
No estimator internals are copied: every refit calls the canonical
`_fit_hazard_candidate` + `_feedback_derivative` via leg4's
`_forced_route_derivative`, and the t=0 / v2 anchors certify the whole path
end-to-end against Leg 9's persisted rows.

THE QUESTION. Leg 11 closed the arc with a quantitative object: the paired
gap is a smooth, near-quadratic basin around the oracle point (gap(theta) ~
theta^p, p = 1.842/1.764/1.871 per high-gap world), and the residual ~.21-.23
gap is direction content accrued across the WHOLE oracle->discovered frame
displacement. Therefore any method that shrinks the frame displacement by
factor alpha should shrink the gap toward ~alpha^p -- a THEORY PREDICTION.
This leg builds two one-step displacement-reduction constructions and tests
the prediction point by point.

ARMS (registered; 3 high-gap worlds x 8 reps):

A (consensus discovery): the chordal/Frechet mean of the 8 per-rep discovered
  frames per world, then per rep refit D at the consensus frame (V2 estimator
  semantics, oracle-forced route, 1x r=0 panels). MEAN ALGORITHM (stated):
  generalized Procrustes iteration on the Kendall size-and-shape quotient
  R^(48xW)/O(W) -- Leg 11 established that the paired functional consumes the
  stacked frame S = [B_cal; B_sel; B_eval] only through its row Gram, so
  frames are points of that quotient and the chordal (Procrustes) metric is
  the registered Leg-11 metric. All 8 frames are zero-padded to the common
  width W; one GPA run iterates [align every frame to the current mean by
  the Procrustes rotation R* = UV' of svd(F' M); average the aligned
  representatives] until the fixed-point residual < 1e-11 (cap 50000;
  non-convergence refuses). TWO PREFLIGHT FACTS, both discovered on the
  iteration itself BEFORE any adjudicated output existed, and both folded
  into the stated algorithm: (1) the iteration contracts linearly at
  ~.9954/step on these widely spread frames, so the original 1e-12-in-500
  control was unreachable (~6e3 steps reach 1e-11; the contraction bound
  puts the converged representative within ~2e-9 of its fixed point);
  (2) the chordal Frechet objective is MULTI-MODAL here (two inits landed
  4.67 apart in quotient distance -- the per-rep discovered frames are
  spread ~28 pairwise, comparable to their own norms ~18, so curvature
  effects are macroscopic). The mean algorithm is therefore MULTI-START
  GPA: one run from each of the 8 rep frames as init, consensus = the
  converged mean with the LOWEST Frechet objective (mean squared quotient
  distance; ties broken by lowest init index) -- the honest practical
  proxy for the global Frechet mean, deterministic and stated. The basin
  structure (number of distinct converged means at 1e-6 resolution,
  objective range, best init) is RECORDED in the diagnostics.
  FRAME-MANIFOLD VERIFICATION (stated): the quotient is of the full matrix
  space, so every finite representative is a point on it; what must be
  verified is that the consensus is (i) a Frechet stationary point
  (fixed-point residual reported), (ii) the argmin of the recorded
  multi-start objective map, and (iii) WELL-DEFINED UNDER THE FUNCTIONAL:
  refit D at the mean representative and at the mean right-multiplied by a
  random O(W) rotation -- relative D error <= 1e-6 (Leg 11's rotation
  gate, re-run here on the new object).
B (split-half agreement): within each rep, split the AUTHORS of all five
  condition panels into first/second half (the estimator's own
  `_author_split_features` split unit), re-run the FULL discovery pipeline
  (candidate battery + chart selection + freeze + prototype transform) per
  half, then apply the registered one-step symmetric shrinkage: each
  half-frame moves half-way toward the other along the aligned chord and the
  two results are averaged -- algebraically both land on the chordal
  midpoint of the two half-frames (same quotient point from either side;
  empirically gated by refitting at both representatives, <= 1e-6). Chart
  refusals on a half are RECORDED LOUDLY and the half-frame is still used
  (diagnostic arm, not deployment); a half whose candidate battery raises
  outright leaves NaN rows for the rep, reported.
C (prediction check): for every arm/world/rep,
  alpha = d(swap_rep, frame_arm) / d(swap_rep, v2_rep) and
  gap_fraction = rep_gap_arm / rep_gap_v2, where d is the chordal quotient
  distance (Leg 11's procrustes_residual formula; the per-rep V2 denominator
  is ANCHORED <= 1e-9 to Leg 11's persisted per-rep procrustes_residual),
  swap_rep is Leg 9's row-norm swap (oracle directions + the rep's own
  discovered norms -- the t=0 oracle point of the basin), and rep_gap = the
  median over authors of the author-level (view-mean) paired gap. The
  prediction is gap_fraction ~ alpha^p with the per-world Leg-11 exponents,
  RECOMPUTED here from Leg 11's persisted gap_theta_rows.csv under Leg 11's
  own aggregation and GATED against the registered printed values
  1.842/1.764/1.871 (<= 5e-4); the full-precision recomputed values are used.

GAP SEMANTICS (Leg 9's, unchanged): per author-view at the oracle-forced
route, 1x r=0 panels, gap_arm = e_arm_true - e_orc_true; author level = view
mean; rep level = median over authors; world level = median over pooled
author-reps; pooled level = median over pooled author-reps of all 3 worlds.

HONESTY NOTE, STATED UP FRONT (companion diagnostics, no adjudication
weight): the truths are REP-LEVEL draws -- each rep has its own oracle basis,
so the 8 discovered frames estimate 8 moving targets. Consensus can reduce
per-rep displacement only down to the floor set by cross-rep target motion.
The run therefore also reports (i) the GPA mean of the 8 SWAP anchors and the
per-rep displacement to it in alpha units (the target-motion floor), (ii) the
quotient distance between the v2 consensus and the swap consensus (the
consensus-level systematic offset), and (iii) the pairwise spread of the v2
frames. If the pivot fires while the target-motion floor is itself ~1, the
"systematic bias of the discovery objective" verdict is CONFOUNDED with
target motion and the report says so plainly.

REGISTERED LEANS (adjudication statistics pre-coded here, BEFORE the run):
- (a) consensus reduces frame displacement >= 30% in >= 2/3 worlds:
  per world, reduction = 1 - median_reps d(swap_rep, consensus) /
  median_reps d(swap_rep, v2_rep); held iff reduction >= .30 in >= 2 worlds.
- (b) where displacement shrinks, the gap follows the basin prediction
  within a factor-2 band in >= 2/3 worlds: points = (arm, world, rep), both
  arms pooled; a point is SHRINKING iff alpha <= .90 (primary bar, matching
  the pivot's 10% materiality threshold; the loose alpha < 1.0 reading is
  reported as sensitivity, not adjudicated) and its denominators are stable
  (rep_gap_v2 >= .01; disp_v2 > 0); factor band fb = gap_fraction /
  alpha^exponent; a world PASSES iff it has >= 1 eligible shrinking point
  and the median fb over them lies in [0.5, 2.0]; held iff >= 2 worlds pass.
  If no world has any shrinking point the lean is N/A -> MISS, labeled
  (Leg 11 precedent). Registered-exact gap_fraction = rep_gap_arm /
  rep_gap_v2; the swap-baselined variant (rep_gap_arm - rep_gap_swap) /
  (rep_gap_v2 - rep_gap_swap) is reported as a LABELED SENSITIVITY because
  the basin floor is not exactly zero per rep (Leg 9's negative swap gaps).
- (c) the best arm cuts the pooled high-gap paired gap >= 25% vs gap_v2:
  pooled gap per arm = median over all usable author-reps of the 3 worlds;
  reduction_arm = 1 - pooled_arm / pooled_v2; best arm = the larger
  reduction; held iff best >= .25.
PIVOT-IF (registered): consensus reduces displacement < 10% -- pre-coded as
reduction < .10 in >= 2/3 worlds -> displacement is SYSTEMATIC BIAS of the
discovery objective, not rep noise; recorded plainly; the objective-redesign
item (beyond one-step) is deferred as the arc's closing open problem and the
loop moves to fresh question mining (hand-off stated in the report). If
lean (a) misses and the pivot clause also fails, the honest in-between is
recorded.

FAITHFULNESS GATES (refused, not warned):
1. context build asserts V2 replay geometries vs archived
   results/m4_chart_ecology/metrics.csv (Leg 4 machinery);
2. analytic D_true unit check (Leg 4) at 1e-10;
3. per author-view, the swap refit must match Leg 9's persisted
   gap_swap_rows.csv (e_i_true, gap_i, e_orc_true) at <= 1e-9 and the v2
   refit must match (e_d_true_v2, gap_v2) at <= 1e-9, degenerate flags
   equal -- certifying the canonical refit path end-to-end;
4. per rep, d(swap_rep, v2_rep) must match Leg 11's persisted
   procrustes_residual at <= 1e-9 (the displacement metric is bit-continuous
   with the basin measurement);
5. full-data discovery rebuild (chart + freeze + prototypes) must equal the
   context's v2_basis exactly (max |diff| = 0 observed in the preflight;
   gate at 1e-12) -- certifying the split-half pipeline shares the exact
   discovery path;
6. consensus and midpoint rotation gates (<= 1e-6) as in Arm A/B above;
7. recomputed Leg-11 exponents match the registered printed values at
   <= 5e-4.

Chunked execution: consensus needs all 8 reps of a world, so the unit of
execution is the WHOLE WORLD (--worlds subsets allowed); the full 3-world
run takes ~7 minutes and is executed as one foreground call (arc discipline:
all compute foreground; this leg needs no rep-level chunking).
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
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)

HIGH_GAP_WORLDS = leg11.HIGH_GAP_WORLDS
ROLES = leg11.ROLES

ROW_TOLERANCE = 1e-9  # persisted-row anchors (Leg 9)
DISPLACEMENT_ANCHOR_TOLERANCE = 1e-9  # Leg 11 procrustes_residual anchor
REBUILD_GATE_TOLERANCE = 1e-12  # full-data discovery rebuild vs v2_basis
ROT_GATE_TOLERANCE = 1e-6  # functional well-definedness on new frames
UNIT_CHECK_TOLERANCE = 1e-10
GPA_TOLERANCE = 1e-11
GPA_MAX_ITERATIONS = 50000
BASIN_RESOLUTION = 1e-6  # distinct-converged-mean resolution (recorded)
EXPONENT_ANCHOR_TOLERANCE = 5e-4
ROT_SEED_TAG = 1408  # rng = default_rng([seed, TAG])

# registered printed Leg-11 exponents (report line: 1.842 / 1.764 / 1.871)
REGISTERED_EXPONENTS = {
    "endogenous_creation_expansion": 1.842,
    "selection_creation_compensation": 1.764,
    "source_rotated_feedback": 1.871,
}

LEAN_A_REDUCTION_BAR = 0.30
LEAN_MIN_WORLDS = 2
PIVOT_REDUCTION_BAR = 0.10
SHRINK_ALPHA_BAR = 0.90  # primary "displacement shrinks" bar
BAND = (0.5, 2.0)
LEAN_C_REDUCTION_BAR = 0.25
GAP_V2_DENOMINATOR_GUARD = 0.01
EPS = 1e-300

ARM_LABELS = ("consensus", "split_half")


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg11_displacement_anchors() -> dict[tuple[str, int], float]:
    paths = sorted(
        glob.glob(
            str(ROOT / "results" / "m4_d_perturbation" / "partial_gates_*.json")
        )
    )
    if not paths:
        raise RuntimeError(
            "Leg 11 persisted gates are a required displacement anchor"
        )
    anchors: dict[tuple[str, int], float] = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for gate in payload["gates"]:
            anchors[(gate["world"], int(gate["repetition"]))] = float(
                gate["procrustes_residual"]
            )
    return anchors


def _recompute_leg11_exponents() -> dict[str, float]:
    """Leg 11's own aggregation: view-mean per (rep, author, draw), world
    median, OLS slope of log(gap) on log(theta) over the five angles."""
    path = ROOT / "results" / "m4_d_perturbation" / "gap_theta_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 11 persisted gap_theta rows are a required anchor: {path}"
        )
    rows = pd.read_csv(path)
    usable = rows[~rows["degenerate_reference"]]
    author = (
        usable.groupby(
            ["world", "repetition", "author", "draw", "theta_deg"]
        )["gap_theta"]
        .mean()
        .reset_index()
    )
    exponents: dict[str, float] = {}
    for world in HIGH_GAP_WORLDS:
        scoped = author[author["world"] == world]
        medians = scoped.groupby("theta_deg")["gap_theta"].median()
        if (medians <= 0).any():
            raise RuntimeError(
                f"non-positive median gap(theta) on {world}; cannot fit the "
                "log-log exponent"
            )
        slope = float(
            np.polyfit(np.log(medians.index.values),
                       np.log(medians.values), 1)[0]
        )
        registered = REGISTERED_EXPONENTS[world]
        if abs(slope - registered) > EXPONENT_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"recomputed Leg-11 exponent diverges on {world}: "
                f"{slope:.6f} vs registered {registered:.3f}"
            )
        exponents[world] = slope
    return exponents


# ---------------------------------------------------------------------------
# quotient geometry (Leg 11's chordal metric on stacked frames)
# ---------------------------------------------------------------------------


def _pad(frame: np.ndarray, width: int) -> np.ndarray:
    if frame.shape[1] > width:
        raise RuntimeError("cannot pad a frame down")
    if frame.shape[1] == width:
        return frame
    padded = np.zeros((frame.shape[0], width))
    padded[:, : frame.shape[1]] = frame
    return padded


def _align(frame: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Procrustes-align frame to target (Leg 11's convention: R* = UV' from
    svd(frame' target); returns frame @ R*)."""
    left, _, right_t = np.linalg.svd(frame.T @ target)
    return frame @ (left @ right_t)


def _quotient_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Chordal size-and-shape distance: min over O(W) after zero-padding
    both representatives to the common width (Leg 11's residual formula)."""
    width = max(first.shape[1], second.shape[1])
    a = _pad(first, width)
    b = _pad(second, width)
    return float(np.linalg.norm(a - _align(b, a)))


def _gpa_mean(
    frames: list[np.ndarray],
    *,
    init_index: int,
) -> dict[str, Any]:
    """Chordal Frechet mean by generalized Procrustes iteration."""
    width = max(frame.shape[1] for frame in frames)
    padded = [_pad(frame, width) for frame in frames]
    mean = padded[init_index].copy()
    residual = np.inf
    iterations = 0
    for iterations in range(1, GPA_MAX_ITERATIONS + 1):
        aligned = [_align(frame, mean) for frame in padded]
        updated = np.mean(aligned, axis=0)
        residual = float(np.linalg.norm(updated - mean))
        mean = updated
        if residual < GPA_TOLERANCE:
            break
    if residual >= GPA_TOLERANCE:
        raise RuntimeError(
            f"GPA failed to converge in {GPA_MAX_ITERATIONS} iterations "
            f"(residual {residual:.3e}); refusing"
        )
    objective = float(
        np.mean([_quotient_distance(mean, frame) ** 2 for frame in padded])
    )
    return {
        "mean": mean,
        "iterations": iterations,
        "fixed_point_residual": residual,
        "objective_mean_squared_distance": objective,
        "width": width,
    }


def _frechet_mean_multistart(frames: list[np.ndarray]) -> dict[str, Any]:
    """Multi-start GPA: one run per rep init; argmin Frechet objective.

    The chordal Frechet objective is multi-modal on these frames (preflight
    fact stated in the module docstring); the consensus is the converged
    mean with the lowest objective, ties broken by lowest init index, and
    the whole basin map is recorded.
    """
    runs = [
        _gpa_mean(frames, init_index=index) for index in range(len(frames))
    ]
    objectives = [run["objective_mean_squared_distance"] for run in runs]
    best_index = int(np.argmin(objectives))
    best = dict(runs[best_index])
    distinct: list[np.ndarray] = []
    basin_of_run: list[int] = []
    for run in runs:
        for basin_index, representative in enumerate(distinct):
            if _quotient_distance(run["mean"], representative) <= (
                BASIN_RESOLUTION
            ):
                basin_of_run.append(basin_index)
                break
        else:
            distinct.append(run["mean"])
            basin_of_run.append(len(distinct) - 1)
    return {
        **best,
        "best_init_index": best_index,
        "n_starts": len(runs),
        "n_distinct_basins": len(distinct),
        "basin_of_run": basin_of_run,
        "objective_by_init": objectives,
        "objective_spread": float(max(objectives) - min(objectives)),
        "max_iterations_over_starts": int(
            max(run["iterations"] for run in runs)
        ),
        "max_fixed_point_residual_over_starts": float(
            max(run["fixed_point_residual"] for run in runs)
        ),
        "all_means": [run["mean"] for run in runs],
    }


# ---------------------------------------------------------------------------
# discovery (canonical pipeline; full-data rebuild gated vs context v2_basis)
# ---------------------------------------------------------------------------


def _discover_basis(
    observed_full: Any,
    condition: Any,
    config: dict[str, Any],
) -> tuple[dict[str, np.ndarray], Any]:
    chart = fit_m4_condition_chart(
        condition,
        candidates=tuple(dict(value) for value in config["candidates"]),
        **config["chart_thresholds"],
    )
    _, basis = build_m4_discovered_basis(
        replace(observed_full, condition=condition),
        chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=config.get("maximum_rank"),
    )
    return basis, chart


def _half_condition(condition: Any, half: int) -> Any:
    def cut(panel: Any) -> Any:
        authors = panel.pre_context.shape[1]
        midpoint = authors // 2
        selector = slice(0, midpoint) if half == 0 else slice(midpoint, authors)
        return replace(
            panel,
            pre_context=panel.pre_context[:, selector],
            response=panel.response[selector],
        )

    return replace(
        condition,
        reference_calibration=cut(condition.reference_calibration),
        reference_selection=cut(condition.reference_selection),
        mechanism_calibration=cut(condition.mechanism_calibration),
        mechanism_selection=cut(condition.mechanism_selection),
        mechanism_evaluation=cut(condition.mechanism_evaluation),
    )


# ---------------------------------------------------------------------------
# canonical forced-route refit (no local estimator copies)
# ---------------------------------------------------------------------------


def _forced_refit(
    context: dict[str, Any],
    view: str,
    author: int,
    basis: dict[str, np.ndarray],
) -> np.ndarray:
    calibration, selection, _ = context["flat"][(view, author)]
    route = context["oracle_stacks"][view][author]["selected_model"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    return leg4._forced_route_derivative(
        calibration,
        selection,
        basis,
        model=route,
        hazard_ridge=context["fit_kwargs"]["hazard_ridge"],
        logistic_iterations=context["fit_kwargs"]["logistic_iterations"],
        dimensions=dimensions,
    )


def _random_rotation(width: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng([seed, ROT_SEED_TAG])
    q, _ = np.linalg.qr(rng.standard_normal((width, width)))
    return q


# ---------------------------------------------------------------------------
# per-world pass (consensus needs all 8 reps)
# ---------------------------------------------------------------------------


def _world_pass(
    world: str,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    stored_swaps: pd.DataFrame,
    displacement_anchors: dict[tuple[str, int], float],
) -> dict[str, Any]:
    repetitions = int(config["repetitions"])
    world_index = {
        name: index for index, name in enumerate(config["worlds"])
    }[world]
    expected_for = leg8._expected_geometries_lookup(config)

    contexts: list[dict[str, Any]] = []
    for repetition in range(repetitions):
        seed = leg3._world_seed(
            int(config["seed"]), repetition, world, world_index
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
        unit_gap = leg4._true_derivative_unit_check(
            context["truth"],
            context["flat"][("train", 0)][0]["response_next"].shape[1],
        )
        if unit_gap > UNIT_CHECK_TOLERANCE:
            raise RuntimeError(
                f"analytic D_true fails the unit check on {world} rep "
                f"{repetition}: {unit_gap:.3e}"
            )
        context["unit_gap"] = unit_gap
        contexts.append(context)
        print(
            f"[leg14] context {world} rep={repetition} "
            f"({time.time() - started:.1f}s)",
            flush=True,
        )

    # ---- frames, gate 5 (discovery rebuild), arm B discoveries -------------
    v2_frames: list[np.ndarray] = []
    swap_frames: list[np.ndarray] = []
    swap_bases: list[dict[str, np.ndarray]] = []
    rebuild_gate_max = 0.0
    half_records: list[dict[str, Any]] = []
    midpoint_frames: list[np.ndarray | None] = []
    for context in contexts:
        v2_basis = context["v2_basis"]
        swap_basis = leg9._row_norm_swap(
            context["truth"].oracle_basis, v2_basis
        )
        swap_bases.append(swap_basis)
        v2_frames.append(leg11._stack_frame(v2_basis))
        swap_frames.append(leg11._stack_frame(swap_basis))

        rebuilt, _ = _discover_basis(
            context["observed"], context["observed"].condition, config
        )
        rebuild_gate = max(
            float(np.max(np.abs(rebuilt[role] - v2_basis[role])))
            for role in ROLES
        )
        rebuild_gate_max = max(rebuild_gate_max, rebuild_gate)
        if rebuild_gate > REBUILD_GATE_TOLERANCE:
            raise RuntimeError(
                f"full-data discovery rebuild diverges from context "
                f"v2_basis on {world} rep {context['repetition']}: "
                f"{rebuild_gate:.3e}"
            )

        record: dict[str, Any] = {
            "world": world,
            "repetition": context["repetition"],
        }
        halves: list[np.ndarray | None] = []
        for half in (0, 1):
            try:
                basis_h, chart_h = _discover_basis(
                    context["observed"],
                    _half_condition(context["observed"].condition, half),
                    config,
                )
                halves.append(leg11._stack_frame(basis_h))
                record[f"half{half}_family"] = chart_h.selected_family
                record[f"half{half}_refused"] = bool(chart_h.refused)
                record[f"half{half}_refusal_reasons"] = ";".join(
                    chart_h.refusal_reasons
                )
                record[f"half{half}_width"] = int(
                    basis_h["calibration"].shape[1]
                )
            except (RuntimeError, ValueError, np.linalg.LinAlgError) as error:
                halves.append(None)
                record[f"half{half}_family"] = "FAILED"
                record[f"half{half}_refused"] = True
                record[f"half{half}_refusal_reasons"] = (
                    f"candidate_battery_raised:{error}"
                )
                record[f"half{half}_width"] = -1
        if halves[0] is not None and halves[1] is not None:
            width_pair = max(halves[0].shape[1], halves[1].shape[1])
            h0 = _pad(halves[0], width_pair)
            h1 = _pad(halves[1], width_pair)
            # registered one-step symmetric shrinkage = chordal midpoint
            midpoint = 0.5 * (h0 + _align(h1, h0))
            midpoint_other_side = 0.5 * (h1 + _align(h0, h1))
            record["half_frame_distance"] = _quotient_distance(h0, h1)
            record["midpoint_equivalence_qdist"] = _quotient_distance(
                midpoint, midpoint_other_side
            )
            midpoint_frames.append(midpoint)
            record["midpoint_ok"] = True
        else:
            midpoint_frames.append(None)
            record["half_frame_distance"] = np.nan
            record["midpoint_equivalence_qdist"] = np.nan
            record["midpoint_ok"] = False
        half_records.append(record)

    # ---- displacement anchors (gate 4) --------------------------------------
    disp_v2: list[float] = []
    disp_anchor_max = 0.0
    for repetition, (swap_frame, v2_frame) in enumerate(
        zip(swap_frames, v2_frames, strict=True)
    ):
        value = _quotient_distance(swap_frame, v2_frame)
        anchor = displacement_anchors.get((world, repetition))
        if anchor is None:
            raise RuntimeError(
                f"no Leg 11 displacement anchor for {world} rep {repetition}"
            )
        difference = abs(value - anchor)
        disp_anchor_max = max(disp_anchor_max, difference)
        if difference > DISPLACEMENT_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"displacement metric diverges from Leg 11 "
                f"procrustes_residual on {world} rep {repetition}: "
                f"{value:.12f} vs {anchor:.12f}"
            )
        disp_v2.append(value)

    # ---- Arm A: consensus (chordal Frechet mean of the 8 v2 frames) --------
    gpa = _frechet_mean_multistart(v2_frames)
    print(
        f"[leg14] {world} consensus GPA: basins="
        f"{gpa['n_distinct_basins']}/8 best_init={gpa['best_init_index']} "
        f"objective={gpa['objective_mean_squared_distance']:.4f} "
        f"(spread {gpa['objective_spread']:.4f}) "
        f"iters<={gpa['max_iterations_over_starts']}",
        flush=True,
    )
    consensus = gpa["mean"]
    consensus_basis = leg11._slice_frame(
        consensus, consensus.shape[0] // len(ROLES)
    )

    # companions (no adjudication weight): target-motion floor + offsets +
    # basin robustness of the lean-a statistic + cloud decomposition
    swap_gpa = _frechet_mean_multistart(swap_frames)
    swap_consensus = swap_gpa["mean"]
    pairwise = [
        _quotient_distance(v2_frames[i], v2_frames[j])
        for i in range(len(v2_frames))
        for j in range(i + 1, len(v2_frames))
    ]
    reduction_by_basin = []
    for basin_mean in gpa["all_means"]:
        disp_basin = [
            _quotient_distance(swap_frames[r], basin_mean)
            for r in range(repetitions)
        ]
        reduction_by_basin.append(
            float(
                1.0
                - np.median(disp_basin) / max(np.median(disp_v2), EPS)
            )
        )
    companions = {
        "target_motion_floor_alpha": [
            _quotient_distance(swap_frames[r], swap_consensus) / disp_v2[r]
            for r in range(repetitions)
        ],
        "v2_consensus_to_swap_consensus": _quotient_distance(
            consensus, swap_consensus
        ),
        "v2_pairwise_distance_median": float(np.median(pairwise)),
        "v2_pairwise_distance_max": float(np.max(pairwise)),
        "swap_gpa_objective": swap_gpa["objective_mean_squared_distance"],
        "swap_gpa_n_distinct_basins": swap_gpa["n_distinct_basins"],
        "swap_gpa_objective_spread": swap_gpa["objective_spread"],
        "v2_cloud_rms_spread": float(
            np.sqrt(gpa["objective_mean_squared_distance"])
        ),
        "swap_cloud_rms_spread": float(
            np.sqrt(swap_gpa["objective_mean_squared_distance"])
        ),
        "median_d_v2_to_v2_consensus": float(
            np.median(
                [
                    _quotient_distance(frame, consensus)
                    for frame in v2_frames
                ]
            )
        ),
        "median_d_swap_to_swap_consensus": float(
            np.median(
                [
                    _quotient_distance(frame, swap_consensus)
                    for frame in swap_frames
                ]
            )
        ),
        "lean_a_reduction_by_basin": reduction_by_basin,
        "lean_a_reduction_basin_min": float(np.min(reduction_by_basin)),
        "lean_a_reduction_basin_max": float(np.max(reduction_by_basin)),
    }

    # ---- refits + anchors (gates 2/3/6) -------------------------------------
    gap_rows: list[dict[str, Any]] = []
    swap_anchor_max = 0.0
    v2_anchor_max = 0.0
    rot_gate_consensus_max = 0.0
    rot_gate_midpoint_max = 0.0
    validation_rows: list[dict[str, Any]] = []
    displacement_rows: list[dict[str, Any]] = []

    for repetition, context in enumerate(contexts):
        validation_rows.extend(context["validation_rows"])
        seed = context["seed"]
        truth = context["truth"]
        authors = context["authors"]
        true_d = {
            author: leg4._true_derivative(truth, author)
            for author in range(authors)
        }
        reference = stored_swaps[
            (stored_swaps["world"] == world)
            & (stored_swaps["repetition"] == repetition)
        ]
        if len(reference) != 2 * authors:
            raise RuntimeError(
                f"Leg 9 swap reference incomplete for {world} rep "
                f"{repetition}"
            )
        swap_basis = swap_bases[repetition]
        v2_basis = context["v2_basis"]
        midpoint = midpoint_frames[repetition]
        midpoint_basis = (
            leg11._slice_frame(midpoint, midpoint.shape[0] // len(ROLES))
            if midpoint is not None
            else None
        )

        rot_gated = False
        for view in ("train", "test"):
            for author in range(authors):
                stack = context["oracle_stacks"][view][author]
                stored_row = reference[
                    (reference["author"] == author)
                    & (reference["view"] == view)
                ]
                if len(stored_row) != 1:
                    raise RuntimeError(
                        f"Leg 9 swap reference missing {world} "
                        f"r{repetition} {view} a{author}"
                    )
                stored_row = stored_row.iloc[0]
                degenerate = bool(
                    float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE
                )
                if degenerate != bool(stored_row["degenerate_reference"]):
                    raise RuntimeError(
                        f"degenerate flag mismatch vs Leg 9 on {world} "
                        f"r{repetition} {view} a{author}"
                    )
                keys = {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "forced_route": stack["selected_model"],
                    "degenerate_reference": degenerate,
                }
                if degenerate:
                    gap_rows.append(
                        {
                            **keys,
                            "e_orc_true": np.nan,
                            "e_swap_true": np.nan,
                            "gap_swap": np.nan,
                            "e_v2_true": np.nan,
                            "gap_v2": np.nan,
                            "e_consensus_true": np.nan,
                            "gap_consensus": np.nan,
                            "e_split_true": np.nan,
                            "gap_split": np.nan,
                        }
                    )
                    continue

                d_true = true_d[author]
                e_orc = leg3._relative_error(stack["D"], d_true)
                d_swap = _forced_refit(context, view, author, swap_basis)
                e_swap = leg3._relative_error(d_swap, d_true)
                d_v2 = _forced_refit(context, view, author, v2_basis)
                e_v2 = leg3._relative_error(d_v2, d_true)

                anchor_gap = max(
                    abs(e_swap - float(stored_row["e_i_true"])),
                    abs((e_swap - e_orc) - float(stored_row["gap_i"])),
                    abs(e_orc - float(stored_row["e_orc_true"])),
                )
                swap_anchor_max = max(swap_anchor_max, anchor_gap)
                if anchor_gap > ROW_TOLERANCE:
                    raise RuntimeError(
                        f"swap anchor diverges from Leg 9 persisted rows "
                        f"on {world} r{repetition} {view} a{author}: "
                        f"{anchor_gap:.3e}"
                    )
                v2_gap = max(
                    abs(e_v2 - float(stored_row["e_d_true_v2"])),
                    abs((e_v2 - e_orc) - float(stored_row["gap_v2"])),
                )
                v2_anchor_max = max(v2_anchor_max, v2_gap)
                if v2_gap > ROW_TOLERANCE:
                    raise RuntimeError(
                        f"v2 anchor diverges from Leg 9 persisted rows on "
                        f"{world} r{repetition} {view} a{author}: "
                        f"{v2_gap:.3e}"
                    )

                d_consensus = _forced_refit(
                    context, view, author, consensus_basis
                )
                e_consensus = leg3._relative_error(d_consensus, d_true)
                if midpoint_basis is not None:
                    d_split = _forced_refit(
                        context, view, author, midpoint_basis
                    )
                    e_split = leg3._relative_error(d_split, d_true)
                else:
                    e_split = np.nan

                if not rot_gated:
                    rotation = _random_rotation(
                        consensus.shape[1], seed
                    )
                    rotated_basis = leg11._slice_frame(
                        consensus @ rotation,
                        consensus.shape[0] // len(ROLES),
                    )
                    d_rotated = _forced_refit(
                        context, view, author, rotated_basis
                    )
                    rot_gate = leg3._relative_error(d_rotated, d_consensus)
                    rot_gate_consensus_max = max(
                        rot_gate_consensus_max, rot_gate
                    )
                    if rot_gate > ROT_GATE_TOLERANCE:
                        raise RuntimeError(
                            f"consensus frame is not well-defined on the "
                            f"quotient on {world} r{repetition}: "
                            f"{rot_gate:.3e}"
                        )
                    if midpoint_basis is not None:
                        h_rot = _random_rotation(
                            midpoint.shape[1], seed + 1
                        )
                        rotated_mid = leg11._slice_frame(
                            midpoint @ h_rot,
                            midpoint.shape[0] // len(ROLES),
                        )
                        d_mid_rot = _forced_refit(
                            context, view, author, rotated_mid
                        )
                        mid_gate = leg3._relative_error(d_mid_rot, d_split)
                        rot_gate_midpoint_max = max(
                            rot_gate_midpoint_max, mid_gate
                        )
                        if mid_gate > ROT_GATE_TOLERANCE:
                            raise RuntimeError(
                                f"midpoint frame is not well-defined on "
                                f"the quotient on {world} r{repetition}: "
                                f"{mid_gate:.3e}"
                            )
                    rot_gated = True

                gap_rows.append(
                    {
                        **keys,
                        "e_orc_true": e_orc,
                        "e_swap_true": e_swap,
                        "gap_swap": e_swap - e_orc,
                        "e_v2_true": e_v2,
                        "gap_v2": e_v2 - e_orc,
                        "e_consensus_true": e_consensus,
                        "gap_consensus": e_consensus - e_orc,
                        "e_split_true": e_split,
                        "gap_split": (
                            e_split - e_orc
                            if np.isfinite(e_split)
                            else np.nan
                        ),
                    }
                )

        disp_consensus = _quotient_distance(
            swap_frames[repetition], consensus
        )
        disp_split = (
            _quotient_distance(swap_frames[repetition], midpoint)
            if midpoint is not None
            else np.nan
        )
        displacement_rows.append(
            {
                "world": world,
                "repetition": repetition,
                "seed": seed,
                "v2_width": int(v2_frames[repetition].shape[1]),
                "disp_v2": disp_v2[repetition],
                "disp_consensus": disp_consensus,
                "alpha_consensus": disp_consensus / disp_v2[repetition],
                "disp_split": disp_split,
                "alpha_split": disp_split / disp_v2[repetition],
                "disp_swap_to_swap_consensus": companions[
                    "target_motion_floor_alpha"
                ][repetition]
                * disp_v2[repetition],
                "alpha_target_motion_floor": companions[
                    "target_motion_floor_alpha"
                ][repetition],
                **{
                    key: half_records[repetition][key]
                    for key in half_records[repetition]
                    if key not in ("world", "repetition")
                },
            }
        )
        print(
            f"[leg14] refits {world} rep={repetition} "
            f"alpha_A={disp_consensus / disp_v2[repetition]:.3f} "
            f"alpha_B={disp_split / disp_v2[repetition] if np.isfinite(disp_split) else float('nan'):.3f}",
            flush=True,
        )

    gates = {
        "world": world,
        "unit_check_max": max(
            float(context["unit_gap"]) for context in contexts
        ),
        "rebuild_gate_max": rebuild_gate_max,
        "displacement_anchor_max_abs_diff": disp_anchor_max,
        "swap_anchor_max_abs_diff": swap_anchor_max,
        "v2_anchor_max_abs_diff": v2_anchor_max,
        "rot_gate_consensus_max_rel_error": rot_gate_consensus_max,
        "rot_gate_midpoint_max_rel_error": rot_gate_midpoint_max,
        "gpa_best_init_index": gpa["best_init_index"],
        "gpa_n_distinct_basins": gpa["n_distinct_basins"],
        "gpa_basin_of_run": gpa["basin_of_run"],
        "gpa_objective_by_init": gpa["objective_by_init"],
        "gpa_objective_spread": gpa["objective_spread"],
        "gpa_max_iterations_over_starts": gpa[
            "max_iterations_over_starts"
        ],
        "gpa_fixed_point_residual": gpa[
            "max_fixed_point_residual_over_starts"
        ],
        "gpa_objective_mean_squared_distance": gpa[
            "objective_mean_squared_distance"
        ],
        "consensus_width": int(consensus.shape[1]),
        "degenerate_rows": int(
            sum(1 for row in gap_rows if row["degenerate_reference"])
        ),
    }
    return {
        "gap_rows": gap_rows,
        "displacement_rows": displacement_rows,
        "validation_rows": validation_rows,
        "gates": gates,
        "companions": companions,
    }


# ---------------------------------------------------------------------------
# adjudication (pre-coded; see docstring)
# ---------------------------------------------------------------------------


def _rep_gap_table(gap_rows: pd.DataFrame) -> pd.DataFrame:
    usable = gap_rows[~gap_rows["degenerate_reference"]]
    author = (
        usable.groupby(["world", "repetition", "author"])[
            ["gap_swap", "gap_v2", "gap_consensus", "gap_split"]
        ]
        .mean()
        .reset_index()
    )
    return (
        author.groupby(["world", "repetition"])[
            ["gap_swap", "gap_v2", "gap_consensus", "gap_split"]
        ]
        .median()
        .reset_index()
    )


def _adjudicate(
    gap_rows: pd.DataFrame,
    displacement: pd.DataFrame,
    exponents: dict[str, float],
    worlds: list[str],
) -> dict[str, Any]:
    rep_gaps = _rep_gap_table(gap_rows)
    merged = displacement.merge(rep_gaps, on=["world", "repetition"])
    if len(merged) != len(displacement):
        raise RuntimeError("rep-gap merge lost displacement rows")

    # ---- lean (a): consensus displacement reduction -------------------------
    reductions: dict[str, float] = {}
    for world in worlds:
        scoped = merged[merged["world"] == world]
        reductions[world] = float(
            1.0
            - scoped["disp_consensus"].median()
            / max(scoped["disp_v2"].median(), EPS)
        )
    lean_a_worlds = [
        world
        for world in worlds
        if reductions[world] >= LEAN_A_REDUCTION_BAR
    ]
    lean_a = {
        "statement": (
            "consensus reduces frame displacement >= 30% in >= 2/3 worlds "
            "(reduction = 1 - median_reps disp_consensus / median_reps "
            "disp_v2)"
        ),
        "reduction_by_world": reductions,
        "worlds_at_bar": lean_a_worlds,
        "held": len(lean_a_worlds) >= LEAN_MIN_WORLDS,
    }

    # ---- pivot ---------------------------------------------------------------
    pivot_worlds = [
        world
        for world in worlds
        if reductions[world] < PIVOT_REDUCTION_BAR
    ]
    pivot_fires = len(pivot_worlds) >= LEAN_MIN_WORLDS
    pivot = {
        "registered": (
            "consensus reduces displacement < 10% -> displacement is "
            "SYSTEMATIC BIAS of the discovery objective, not rep noise; "
            "objective redesign deferred as the arc's closing open "
            "problem; loop moves to fresh question mining"
        ),
        "pre_coded_rule": (
            "fires iff per-world consensus displacement reduction < .10 "
            "in >= 2/3 worlds"
        ),
        "worlds_below_pivot_bar": pivot_worlds,
        "fires": pivot_fires,
    }

    # ---- Arm C points + lean (b) ----------------------------------------------
    points: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        for arm, disp_column, gap_column in (
            ("consensus", "disp_consensus", "gap_consensus"),
            ("split_half", "disp_split", "gap_split"),
        ):
            disp_arm = float(row[disp_column])
            gap_arm = float(row[gap_column])
            disp_ref = float(row["disp_v2"])
            gap_ref = float(row["gap_v2"])
            gap_swap = float(row["gap_swap"])
            alpha = disp_arm / max(disp_ref, EPS)
            denominator_ok = (
                np.isfinite(gap_ref)
                and gap_ref >= GAP_V2_DENOMINATOR_GUARD
                and disp_ref > 0
            )
            gap_fraction = (
                gap_arm / gap_ref if denominator_ok else np.nan
            )
            rise_denominator = gap_ref - gap_swap
            gap_fraction_swap_baselined = (
                (gap_arm - gap_swap) / rise_denominator
                if denominator_ok and abs(rise_denominator) > EPS
                else np.nan
            )
            exponent = exponents[str(row["world"])]
            predicted = (
                alpha ** exponent if np.isfinite(alpha) else np.nan
            )
            factor_band = (
                gap_fraction / predicted
                if np.isfinite(gap_fraction) and predicted > 0
                else np.nan
            )
            points.append(
                {
                    "arm": arm,
                    "world": row["world"],
                    "repetition": int(row["repetition"]),
                    "alpha": alpha,
                    "gap_fraction": gap_fraction,
                    "gap_fraction_swap_baselined_SENSITIVITY": (
                        gap_fraction_swap_baselined
                    ),
                    "exponent": exponent,
                    "predicted_fraction": predicted,
                    "factor_band": factor_band,
                    "in_band": bool(
                        np.isfinite(factor_band)
                        and BAND[0] <= factor_band <= BAND[1]
                    ),
                    "shrinking_primary": bool(
                        np.isfinite(alpha) and alpha <= SHRINK_ALPHA_BAR
                    ),
                    "shrinking_loose": bool(
                        np.isfinite(alpha) and alpha < 1.0
                    ),
                    "denominator_ok": bool(denominator_ok),
                }
            )
    points_frame = pd.DataFrame(points)

    basin_by_world: dict[str, dict[str, Any]] = {}
    passing_worlds: list[str] = []
    for world in worlds:
        scoped = points_frame[
            (points_frame["world"] == world)
            & points_frame["shrinking_primary"]
            & points_frame["denominator_ok"]
            & np.isfinite(points_frame["factor_band"])
        ]
        loose = points_frame[
            (points_frame["world"] == world)
            & points_frame["shrinking_loose"]
            & points_frame["denominator_ok"]
            & np.isfinite(points_frame["factor_band"])
        ]
        median_band = (
            float(scoped["factor_band"].median()) if len(scoped) else np.nan
        )
        world_passes = bool(
            len(scoped) >= 1 and BAND[0] <= median_band <= BAND[1]
        )
        if world_passes:
            passing_worlds.append(world)
        basin_by_world[world] = {
            "n_shrinking_points_primary": int(len(scoped)),
            "median_factor_band": median_band,
            "share_points_in_band": (
                float(scoped["in_band"].mean()) if len(scoped) else np.nan
            ),
            "passes": world_passes,
            "n_shrinking_points_loose_SENSITIVITY": int(len(loose)),
            "median_factor_band_loose_SENSITIVITY": (
                float(loose["factor_band"].median())
                if len(loose)
                else np.nan
            ),
        }
    any_shrinking = any(
        value["n_shrinking_points_primary"] > 0
        for value in basin_by_world.values()
    )
    lean_b = {
        "statement": (
            "where displacement shrinks (alpha <= .90, both arms pooled), "
            "gap_fraction within [0.5, 2.0] x alpha^exponent in >= 2/3 "
            "worlds (median factor band over the shrinking points)"
        ),
        "by_world": basin_by_world,
        "passing_worlds": passing_worlds,
        "applicable": any_shrinking,
        "held": bool(any_shrinking and len(passing_worlds) >= LEAN_MIN_WORLDS),
        "na_note": (
            None
            if any_shrinking
            else "no shrinking points anywhere -> N/A -> MISS, labeled"
        ),
    }

    # ---- lean (c): pooled gap reduction of the best arm -----------------------
    usable = gap_rows[~gap_rows["degenerate_reference"]]
    author = (
        usable.groupby(["world", "repetition", "author"])[
            ["gap_v2", "gap_consensus", "gap_split"]
        ]
        .mean()
        .reset_index()
    )
    pooled = {
        "gap_v2": float(author["gap_v2"].median()),
        "gap_consensus": float(author["gap_consensus"].median()),
        "gap_split": float(author["gap_split"].median()),
    }
    world_medians = {
        world: {
            column: float(
                author[author["world"] == world][column].median()
            )
            for column in ("gap_v2", "gap_consensus", "gap_split")
        }
        for world in worlds
    }
    arm_reductions = {
        "consensus": 1.0 - pooled["gap_consensus"] / max(
            pooled["gap_v2"], EPS
        ),
        "split_half": 1.0 - pooled["gap_split"] / max(
            pooled["gap_v2"], EPS
        ),
    }
    finite_arms = {
        arm: value
        for arm, value in arm_reductions.items()
        if np.isfinite(value)
    }
    best_arm = max(finite_arms, key=finite_arms.get) if finite_arms else None
    lean_c = {
        "statement": (
            "the best arm cuts the pooled high-gap paired gap >= 25% vs "
            "gap_v2 (pooled = median over all usable author-reps of the 3 "
            "worlds)"
        ),
        "pooled_gaps": pooled,
        "world_medians": world_medians,
        "arm_reductions": arm_reductions,
        "best_arm": best_arm,
        "best_reduction": (
            float(finite_arms[best_arm]) if best_arm is not None else np.nan
        ),
        "held": bool(
            best_arm is not None
            and finite_arms[best_arm] >= LEAN_C_REDUCTION_BAR
        ),
    }

    return {
        "rep_gaps": rep_gaps,
        "merged": merged,
        "points_frame": points_frame,
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_chart_ecology.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "m4_d_discovery_displacement",
    )
    parser.add_argument(
        "--worlds",
        type=str,
        default=None,
        help="comma-separated subset of the three high-gap worlds",
    )
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])
    worlds = (
        [w for w in args.worlds.split(",") if w]
        if args.worlds
        else list(HIGH_GAP_WORLDS)
    )
    for world in worlds:
        if world not in HIGH_GAP_WORLDS:
            raise SystemExit(f"not a registered high-gap world: {world}")

    stored_swaps = leg11._load_leg9_swap_reference()
    displacement_anchors = _load_leg11_displacement_anchors()
    exponents = _recompute_leg11_exponents()
    print(
        f"[leg14] recomputed Leg-11 exponents (gated vs 1.842/1.764/1.871): "
        f"{ {w: round(v, 4) for w, v in exponents.items()} }",
        flush=True,
    )

    gap_collections: list[dict[str, Any]] = []
    displacement_collections: list[dict[str, Any]] = []
    validation_collections: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    companions: dict[str, Any] = {}
    for world in worlds:
        result = _world_pass(
            world, config, spec, stored_swaps, displacement_anchors
        )
        gap_collections.extend(result["gap_rows"])
        displacement_collections.extend(result["displacement_rows"])
        validation_collections.extend(result["validation_rows"])
        gates.append(result["gates"])
        companions[world] = result["companions"]

    gap_rows = pd.DataFrame(gap_collections)
    displacement = pd.DataFrame(displacement_collections)
    validation = pd.DataFrame(validation_collections)

    repetitions = int(config["repetitions"])
    expected_rows = len(worlds) * repetitions * 2 * 16
    if len(gap_rows) != expected_rows:
        raise RuntimeError(
            f"gap rows {len(gap_rows)} != expected {expected_rows}"
        )
    if gap_rows.duplicated(
        subset=["world", "repetition", "author", "view"]
    ).any():
        raise RuntimeError("duplicate gap cells refused")
    if len(displacement) != len(worlds) * repetitions:
        raise RuntimeError("displacement rows incomplete")

    adjudication = _adjudicate(gap_rows, displacement, exponents, worlds)
    lean_a = adjudication["lean_a"]
    lean_b = adjudication["lean_b"]
    lean_c = adjudication["lean_c"]
    pivot = adjudication["pivot"]
    leans_held = int(lean_a["held"]) + int(lean_b["held"]) + int(
        lean_c["held"]
    )
    if pivot["fires"]:
        verdict = "DISPLACEMENT_IS_SYSTEMATIC_OBJECTIVE_BIAS"
    elif lean_a["held"]:
        verdict = "DISPLACEMENT_SUBSTANTIALLY_REP_NOISE"
    else:
        verdict = "PARTIAL_REDUCTION_NEITHER_LEAN_NOR_PIVOT"

    faithfulness = {
        "v2_replay_rows": int(len(validation)),
        "v2_replay_max_abs_difference": (
            float(validation["abs_difference"].max())
            if len(validation)
            else None
        ),
        "unit_check_max": max(
            float(gate["unit_check_max"]) for gate in gates
        ),
        "discovery_rebuild_gate_max": max(
            float(gate["rebuild_gate_max"]) for gate in gates
        ),
        "leg11_displacement_anchor_max_abs_diff": max(
            float(gate["displacement_anchor_max_abs_diff"])
            for gate in gates
        ),
        "leg9_swap_anchor_max_abs_diff": max(
            float(gate["swap_anchor_max_abs_diff"]) for gate in gates
        ),
        "leg9_v2_anchor_max_abs_diff": max(
            float(gate["v2_anchor_max_abs_diff"]) for gate in gates
        ),
        "rot_gate_consensus_max_rel_error": max(
            float(gate["rot_gate_consensus_max_rel_error"])
            for gate in gates
        ),
        "rot_gate_midpoint_max_rel_error": max(
            float(gate["rot_gate_midpoint_max_rel_error"])
            for gate in gates
        ),
        "gpa_fixed_point_residual_max": max(
            float(gate["gpa_fixed_point_residual"]) for gate in gates
        ),
        "gpa_n_distinct_basins_by_world": {
            gate["world"]: int(gate["gpa_n_distinct_basins"])
            for gate in gates
        },
        "gpa_objective_spread_by_world": {
            gate["world"]: float(gate["gpa_objective_spread"])
            for gate in gates
        },
        "exponents_recomputed": exponents,
        "degenerate_rows_total": int(
            sum(int(gate["degenerate_rows"]) for gate in gates)
        ),
        "per_world_gates": gates,
    }

    decision = {
        "estimand_id": "SUICA_M4_D_DISCOVERY_DISPLACEMENT_LEG14",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md Leg 14 "
            "(2026-08-02, loop cycle 9, commit 693141d, before run); "
            "ledger row M4-D.17"
        ),
        "design": {
            "worlds": worlds,
            "repetitions": repetitions,
            "arms": {
                "consensus": (
                    "chordal Frechet mean (generalized Procrustes "
                    "iteration, Kendall size-and-shape quotient of stacked "
                    "role frames, zero-padded to common width) of the 8 "
                    "per-rep discovered frames per world; per-rep refit at "
                    "the consensus"
                ),
                "split_half": (
                    "authors of all five condition panels split "
                    "first/second half; full discovery pipeline per half; "
                    "registered one-step symmetric shrinkage = chordal "
                    "midpoint of the two half-frames; per-rep refit at the "
                    "midpoint"
                ),
                "prediction_check": (
                    "alpha = d(swap_rep, frame)/d(swap_rep, v2_rep) "
                    "(chordal quotient distance, anchored to Leg 11 "
                    "procrustes_residual); gap_fraction = rep_gap_arm / "
                    "rep_gap_v2; test vs alpha^exponent with recomputed "
                    "Leg-11 per-world exponents; factor band [0.5, 2.0]"
                ),
            },
            "gap_semantics": (
                "Leg 9: forced-route refits at 1x r=0, gap = e_arm_true - "
                "e_orc_true, author-level view-mean, rep median over "
                "authors, world/pooled median over author-reps"
            ),
            "estimator_path": (
                "canonical _fit_hazard_candidate + _feedback_derivative "
                "via leg4._forced_route_derivative -- no local estimator "
                "copies in this leg"
            ),
        },
        "faithfulness": faithfulness,
        "displacement_table": {
            world: {
                "median_disp_v2": float(
                    displacement[displacement["world"] == world][
                        "disp_v2"
                    ].median()
                ),
                "median_disp_consensus": float(
                    displacement[displacement["world"] == world][
                        "disp_consensus"
                    ].median()
                ),
                "median_disp_split": float(
                    displacement[displacement["world"] == world][
                        "disp_split"
                    ].median()
                ),
                "median_alpha_consensus": float(
                    displacement[displacement["world"] == world][
                        "alpha_consensus"
                    ].median()
                ),
                "median_alpha_split": float(
                    displacement[displacement["world"] == world][
                        "alpha_split"
                    ].median()
                ),
            }
            for world in worlds
        },
        "companions_target_motion_and_basins": {
            world: {
                "median_alpha_target_motion_floor": float(
                    np.median(
                        companions[world]["target_motion_floor_alpha"]
                    )
                ),
                "v2_consensus_to_swap_consensus": companions[world][
                    "v2_consensus_to_swap_consensus"
                ],
                "v2_pairwise_distance_median": companions[world][
                    "v2_pairwise_distance_median"
                ],
                "v2_cloud_rms_spread": companions[world][
                    "v2_cloud_rms_spread"
                ],
                "swap_cloud_rms_spread": companions[world][
                    "swap_cloud_rms_spread"
                ],
                "median_d_v2_to_v2_consensus": companions[world][
                    "median_d_v2_to_v2_consensus"
                ],
                "median_d_swap_to_swap_consensus": companions[world][
                    "median_d_swap_to_swap_consensus"
                ],
                "lean_a_reduction_by_basin": companions[world][
                    "lean_a_reduction_by_basin"
                ],
                "lean_a_reduction_basin_min": companions[world][
                    "lean_a_reduction_basin_min"
                ],
                "lean_a_reduction_basin_max": companions[world][
                    "lean_a_reduction_basin_max"
                ],
            }
            for world in worlds
        },
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "leans_held": leans_held,
        "pivot_if": pivot,
        "verdict": verdict,
        "hand_off": (
            "objective-redesign (beyond one-step) recorded as the arc's "
            "closing open problem if the pivot fires; the loop moves to "
            "fresh question mining either way (Leg 14 is the last "
            "registered M4-D queue item)"
        ),
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "diagnostic; V1/V2 NO-GO decisions stand; consensus and "
            "split-half frames are DIAGNOSTIC constructions of this leg, "
            "not deployable estimator semantics (the consensus consumes "
            "all 8 reps; the midpoint consumes the full panel twice); no "
            "natural-text, personality, or clinical claim."
        ),
    }

    args.output.mkdir(parents=True, exist_ok=True)
    gap_rows.sort_values(
        ["world", "repetition", "author", "view"]
    ).to_csv(args.output / "gap_rows.csv", index=False)
    displacement.sort_values(["world", "repetition"]).to_csv(
        args.output / "displacement_rows.csv", index=False
    )
    adjudication["merged"].sort_values(["world", "repetition"]).to_csv(
        args.output / "rep_summary_rows.csv", index=False
    )
    adjudication["points_frame"].sort_values(
        ["arm", "world", "repetition"]
    ).to_csv(args.output / "prediction_points.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    with (args.output / "decision.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(
        json.dumps(
            {
                "lean_a_held": lean_a["held"],
                "lean_a_reductions": {
                    world: round(value, 4)
                    for world, value in lean_a[
                        "reduction_by_world"
                    ].items()
                },
                "lean_b_held": lean_b["held"],
                "lean_b_median_bands": {
                    world: (
                        round(value["median_factor_band"], 4)
                        if np.isfinite(value["median_factor_band"])
                        else None
                    )
                    for world, value in lean_b["by_world"].items()
                },
                "lean_c_held": lean_c["held"],
                "lean_c_best": (
                    lean_c["best_arm"],
                    round(lean_c["best_reduction"], 4),
                ),
                "pivot_fires": pivot["fires"],
                "verdict": verdict,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
