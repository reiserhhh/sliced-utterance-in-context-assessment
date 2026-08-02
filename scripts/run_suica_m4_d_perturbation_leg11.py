#!/usr/bin/env python3
"""M4-D Leg 11: perturbation analysis -- is the paired gap a non-smooth
functional at the oracle point? (THE DESIGNATED FINAL LEG OF THE M4-D ARC.)

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 11 -- perturbation analysis", 2026-08-02 loop cycle 6, commit 0e81907,
BEFORE this run). Machinery is IMPORTED from the validated legs -- Leg 4's
context build + forced-route derivative semantics, Leg 9's row-norm swap
(the t=0 anchor) and persisted swap rows, Leg 10's cosine-gram alignment
statistic -- nothing is silently reimplemented; the ONE local copy
(`_fit_logistic` with instrumentation) is bit-gated against the canonical
estimator and against Leg 9's persisted rows at every anchor point.

THE QUESTION. Leg 9: EXACT oracle row directions (+ discovered norms)
eliminate the paired gap entirely (gap_i -.0199/+.0052/-.0096 author-level vs
gap_v2 .2150/.2102/.2283). Leg 10: partial direction repair (.24-.50 of the
deficit) buys ~nothing (closures +.113/-.140/-.138; rho(direction
improvement, gap improvement) = .218/-.133). The gap therefore LOOKS
all-or-nothing in direction content. This leg walks a continuous path from
the oracle point to the discovered chart and asks whether gap(.) is
non-smooth (a knee, with an identifiable discrete decision flipping at it)
or smooth (proportional growth -- the all-or-nothing reading is WRONG and
the residual is genuinely distributed object-level direction content).

ARMS (registered; 3 high-gap worlds x 8 reps):

A (geodesic interpolation): frame-manifold geodesic from the oracle point
  (t=0 = Leg 9's swap_i basis: oracle row directions + discovered row norms
  -- the registered t=0 anchor) to the discovered chart (t=1 = v2 basis),
  t in {0, .05, .1, .2, .4, .7, 1.0}; refit D at each t (V2 estimator
  semantics, oracle-forced route, 1x r=0 panels); gap(t) per world.
  GEODESIC CONSTRUCTION (implementation decision, stated): the paired
  functional consumes the three role bases ONLY through the row-Gram kernel
  of the stacked frame S = [B_cal; B_sel; B_eval] (48 x w):
  `_hazard_design` is linear in the basis rows (blocks: condition,
  feedback = basis x response, gate = feedback x history-indicator), the
  IRLS ridge penalty is uniform on every basis-derived column (only the
  design intercept, which is not basis-derived, is exempt), and the readout
  probes are basis-linear -- so the functional is invariant under
  right-orthogonal maps S -> S R and under zero-column padding, and the
  frame manifold is the quotient of stacked frames by O(w) (Kendall
  size-and-shape space). The geodesic between orbits is the straight
  segment between OPTIMALLY ALIGNED representatives: pad the width-7 swap
  frame S0 with zero columns to width 13, Procrustes-align the discovered
  frame S1 to it (R* = U V' from SVD of S1'S0), and set
  S(t) = (1-t) S0 + t S1 R*. Both invariances are EMPIRICALLY GATED per
  author-view (zero-padding at t=0, rotation at t=1), and the t=0 / t=1
  curve values themselves are computed at the RAW representatives so they
  bit-anchor to the persisted rows (Leg 9 gap_swap_rows.csv at <= 1e-9;
  world medians to Leg 10's gap_world_table.csv at <= 1e-9).

B (controlled angular perturbations of ORACLE directions): perturb the pure
  oracle basis (truth.oracle_basis) by fixed angles theta in {1, 2, 5, 10,
  20} degrees: for every (role, category), rotate the FULL row (Leg 9's
  direction convention: direction = full row up to norm) by exactly theta
  in the plane spanned by the row and a random orthogonal direction; row
  norm preserved exactly. 8 draws per world-rep; the SAME plane set per
  draw is swept across all five angles (common random numbers -- sharper
  gap(theta) shape; stated implementation decision). gap(theta) per world;
  theta=0 is the exact oracle point (gap identically 0 by the Leg 9-gated
  identity of the oracle stack and the forced refit).

C (discrete-event instrumentation): the paired evaluator's discrete internal
  decisions, ENUMERATED FROM THE CODE (suica_core/m4_chart_ecology_estimator
  + leg3._fit_v2_stack), logged along A's path at every t for every
  author-view:
    REGISTERED FAMILIES (adjudicated):
    - category association: the fitted hazard's event->category association
      cells (fitted p >= .5 on the stacked cal+sel design at the final
      coefficient) -- flips between consecutive t;
    - route agreement: the route the V2 selection rule WOULD choose at
      basis(t) (candidate fits on calibration only, selection logloss +
      complexity penalty, first-model tie-break at 1e-10 -- verbatim
      `_fit_v2_stack` semantics) vs the forced oracle route -- changes of
      the would-be route between consecutive t;
    - support-cell membership: cells whose IRLS weight is floored
      (fitted p(1-p) < 1e-4 at the final coefficient -- outside the
      effective support) -- flips between consecutive t.
    COMPANION INTERNALS (logged, no adjudication weight): logit clipping
    |z| >= 20 at fit and at readout probes, IRLS iteration count (early
    stop at 1e-10), readout sign pattern sign(D[k,d]), the data-fixed gate
    indicator (history > 0) and degenerate-reference flags (both
    path-invariant by construction).
    HONESTY NOTE (stated up front): under the ORACLE-FORCED route the
    would-be route selection and the association mask are SHADOW decisions
    -- they do not enter the computed functional; the only discrete
    internals that can mechanically produce a knee in gap(t) are the weight
    floor, the logit clips, and the IRLS early stop. The registered
    families are adjudicated as registered; the report states which side of
    that line the knee's co-movers fall on.

DIAGNOSTIC (unregistered-secondary, LOUD LABEL, no adjudication weight
except registered lean (c)): two soft-assignment variants of the paired
functional, both computed along the full path so lean (c) can be
adjudicated wherever (b) identifies:
  - soft-support: IRLS with NO weight floor and NO logit clip (fit and
    readout), applied to BOTH sides (shared conventions, Leg 9's lesson);
  - soft-route: score-softmax route mixture D_soft = sum_m w_m D_m,
    w = softmax(-score_m / T), T = 0.01 (sensitivity T in {0.001, 0.1}
    reported), applied SYMMETRICALLY (each side mixes its own candidate
    derivatives at its own basis; base/return contribute D = 0 exactly).

GAP SEMANTICS (Leg 9's, unchanged): per author-view at the oracle-forced
route, 1x r=0 panels, gap_arm = e_arm_true - e_orc_true; author level =
view mean; world level = median over author-reps.

REGISTERED LEANS (adjudication statistics pre-coded here, BEFORE the run):
- (a) NON-SMOOTHNESS: with rise(t) = gap_w(t) - gap_w(0) and full_rise =
  gap_w(1) - gap_w(0): rise(.2)/full_rise >= .5 (geodesic reading), or
  gap_w(theta=5deg) >= .5 * gap_w(t=1) (angular reading), in >= 2/3 worlds
  (either reading suffices; both reported separately).
- (b) C isolates a single flipping decision family in >= 2/3 worlds:
  per world, co-occurrence share of family F = sum over author-view rows
  and consecutive intervals of positive gap increments in row-intervals
  where F flips, divided by the sum of all positive increments; F isolated
  iff EXACTLY ONE registered family has share >= .5; lean (b) holds iff
  >= 2 worlds isolate and the isolated family is THE SAME across them.
- (c) where (b) identified, the matching soft variant removes >= half the
  knee jump: knee interval = consecutive t-pair with maximum
  slope = d(gap_w)/dt; removal = 1 - jump_soft/jump_hard on that interval;
  held iff removal >= .5 in ALL worlds where (b) isolated (N/A -> miss,
  labeled).
PIVOT-IF (registered): gap(t) SMOOTH -- no knee, ~proportional growth --
pre-coded as: lean (a) NOT held under either reading AND >= 2/3 worlds
satisfy [rise(.2)/full_rise < .5 AND max interval slope / mean slope < 3].
Then the all-or-nothing reading is WRONG, recorded plainly, and the
residual gap is accepted as genuinely distributed object-level direction
content. If (a) misses but the smoothness clause also fails, the honest
in-between (late/other knee) is recorded. EITHER WAY THE ARC CLOSES:
the registered hand-off is the arc-final synthesis (planner's job) plus
the loop's standing queue (two-stage retrofit of the C.3 attribution
NO-GO; R->V bridge heteroscedastic calibration).

FAITHFULNESS GATES (refused, not warned):
1. context build asserts V2 replay geometries vs archived
   results/m4_chart_ecology/metrics.csv (Leg 4 machinery);
2. analytic D_true unit check (Leg 4) at 1e-10;
3. per author-view, t=0 RAW swap refit must match Leg 9's persisted
   gap_swap_rows.csv (e_i_true, gap_i) at <= 1e-9, and t=1 RAW v2 refit
   must match (e_d_true_v2, gap_v2, e_orc_true) at <= 1e-9, degenerate
   flags equal -- this simultaneously certifies the instrumented IRLS copy
   against the canonical estimator end-to-end;
4. zero-padding invariance at t=0 and rotation invariance at t=1
   (relative D error <= 1e-8 / 1e-6);
5. instrumented copy vs canonical `_fit_hazard_candidate` coefficient
   bit-gate (<= 1e-15) on one cell per world-rep;
6. instrumented readout vs canonical `_feedback_derivative` bit-gate on
   every hard readout;
7. assembled world medians: t=1 vs Leg 10's persisted gap_world_table
   (<= 1e-9), t=0 vs Leg 9's persisted author-level swap medians
   (<= 1e-9).

Chunked execution (arc standard): --chunk-start/--chunk-stop [--worlds] run
repetition ranges in the foreground writing partial CSVs; --assemble
concatenates, REFUSES missing/duplicate cells, adjudicates from the
concatenated rows only.
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
from scipy.special import expit

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
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    HAZARD_MODELS,
    _feedback_derivative,
    _fit_hazard_candidate,
    _hazard_design,
    _hazard_logloss,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)

HIGH_GAP_WORLDS = (
    "endogenous_creation_expansion",
    "selection_creation_compensation",
    "source_rotated_feedback",
)
ROLES = ("calibration", "selection", "evaluation")
T_GRID = (0.0, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0)
THETA_GRID_DEG = (1.0, 2.0, 5.0, 10.0, 20.0)
N_THETA_DRAWS = 8
THETA_SEED_TAG = 1104  # rng = default_rng([world_seed, TAG, draw])

ROW_TOLERANCE = 1e-9  # persisted-row anchors
PAD_GATE_TOLERANCE = 1e-8  # zero-padding invariance at t=0
ROT_GATE_TOLERANCE = 1e-6  # rotation invariance at t=1
COPY_GATE_TOLERANCE = 1e-15  # instrumented vs canonical coefficient
UNIT_CHECK_TOLERANCE = 1e-10
WORLD_MEDIAN_TOLERANCE = 1e-9

WEIGHT_FLOOR = 1e-4  # verbatim estimator constants
LOGIT_CLIP = 20.0
IRLS_STOP = 1e-10
ASSOC_THRESHOLD = 0.5
ROUTE_TIE_TOLERANCE = 1e-10

LEAN_A_FRACTION = 0.5
LEAN_A_T = 0.2
LEAN_A_THETA_DEG = 5.0
LEAN_MIN_WORLDS = 2
SMOOTH_SLOPE_RATIO_BAR = 3.0
COOCCURRENCE_BAR = 0.5
REMOVAL_BAR = 0.5
SOFT_ROUTE_TEMPERATURE = 0.01
SOFT_ROUTE_TEMPERATURES_SECONDARY = (0.001, 0.1)
REGISTERED_FAMILIES = ("category_association", "route_agreement",
                       "support_cell_membership")
EPS = 1e-300


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg9_swap_reference() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_bias_variance" / "gap_swap_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 9 persisted gap swap rows are a required anchor: {path}"
        )
    return pd.read_csv(path)


def _load_leg10_world_table() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_direction_anatomy" / "gap_world_table.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 10 persisted gap world table is a required anchor: {path}"
        )
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# instrumented IRLS (verbatim `_fit_logistic` + logging; soft variant)
# ---------------------------------------------------------------------------


def _fit_logistic_instrumented(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge: float,
    iterations: int,
    soft: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Copy of estimator._fit_logistic; identical op order when soft=False.

    soft=True removes the two hard nonlinearities (logit clip, weight
    floor) -- the soft-support variant of the paired functional.
    """
    y = np.asarray(target, dtype=float).reshape(-1)
    penalty = ridge * len(y) * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    coefficient = np.zeros(design.shape[1])
    probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
    coefficient[0] = np.log(probability / (1.0 - probability))
    used = 0
    for _ in range(iterations):
        if soft:
            # exact weights, no clip/floor; the working response is folded
            # algebraically (weight * adjusted = weight * z + (y - fitted))
            # so saturated cells contribute their exact residual instead of
            # a 0 * inf division
            fitted = expit(design @ coefficient)
            weight = fitted * (1.0 - fitted)
            rhs = weight * (design @ coefficient) + (y - fitted)
        else:
            fitted = expit(np.clip(design @ coefficient, -LOGIT_CLIP,
                                   LOGIT_CLIP))
            weight = np.clip(fitted * (1.0 - fitted), WEIGHT_FLOOR, None)
            adjusted = (
                design @ coefficient + (y - fitted) / weight
            )
            rhs = weight * adjusted
        system = design.T @ (weight[:, None] * design) + penalty
        updated = np.linalg.solve(
            system,
            design.T @ rhs,
        )
        used += 1
        if np.max(np.abs(updated - coefficient)) < IRLS_STOP:
            coefficient = updated
            break
        coefficient = updated
    raw_logit = design @ coefficient
    if soft:
        prob = expit(raw_logit)
    else:
        prob = expit(np.clip(raw_logit, -LOGIT_CLIP, LOGIT_CLIP))
    info = {
        "iterations": used,
        "clip_mask": np.abs(raw_logit) >= LOGIT_CLIP,
        "floor_mask": prob * (1.0 - prob) < WEIGHT_FLOOR,
        "assoc_mask": prob >= ASSOC_THRESHOLD,
    }
    return coefficient, info


def _fit_hazard_instrumented(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    model: str,
    ridge: float,
    iterations: int,
    soft: bool = False,
) -> tuple[np.ndarray, tuple[str, ...], dict[str, Any]]:
    designs = []
    targets = []
    names: tuple[str, ...] | None = None
    for rows, basis in datasets:
        design, current_names = _hazard_design(rows, basis, model=model)
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
        names = current_names
    coefficient, info = _fit_logistic_instrumented(
        np.vstack(designs),
        np.concatenate(targets),
        ridge=ridge,
        iterations=iterations,
        soft=soft,
    )
    return coefficient, names or (), info


def _readout_derivative(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis_eval: np.ndarray,
    dimensions: int,
    *,
    model: str,
    soft: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Probe readout with clip flags; hard path bit-gated vs canonical."""
    categories = len(basis_eval)
    output = np.empty((categories, dimensions))
    clip_count = 0
    for dimension in range(dimensions):
        positive = np.zeros((1, dimensions))
        negative = np.zeros((1, dimensions))
        positive[0, dimension] = leg4.PROBE_EPSILON
        negative[0, dimension] = -leg4.PROBE_EPSILON
        design_pos, _ = _hazard_design(
            leg8._probe_rows(basis_eval, positive, np.zeros(1)),
            basis_eval,
            model=model,
        )
        design_neg, _ = _hazard_design(
            leg8._probe_rows(basis_eval, negative, np.zeros(1)),
            basis_eval,
            model=model,
        )
        logit_pos = design_pos @ coefficient
        logit_neg = design_neg @ coefficient
        clip_count += int(np.sum(np.abs(logit_pos) >= LOGIT_CLIP))
        clip_count += int(np.sum(np.abs(logit_neg) >= LOGIT_CLIP))
        if soft:
            prob_pos = expit(logit_pos)
            prob_neg = expit(logit_neg)
        else:
            prob_pos = expit(np.clip(logit_pos, -LOGIT_CLIP, LOGIT_CLIP))
            prob_neg = expit(np.clip(logit_neg, -LOGIT_CLIP, LOGIT_CLIP))
        output[:, dimension] = (prob_pos - prob_neg) / (
            2.0 * leg4.PROBE_EPSILON
        )
    if not soft:
        canonical = _feedback_derivative(
            coefficient, names, basis_eval, dimensions
        )
        gate = float(np.max(np.abs(output - canonical)))
        if gate > COPY_GATE_TOLERANCE:
            raise RuntimeError(
                f"instrumented readout diverges from canonical "
                f"_feedback_derivative: {gate:.3e}"
            )
    return output, {
        "readout_clip_count": clip_count,
        "sign_pattern": np.sign(output).astype(int),
    }


# ---------------------------------------------------------------------------
# route selection replay (verbatim `_fit_v2_stack` selection semantics)
# ---------------------------------------------------------------------------


def _route_scores(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    fit_kwargs: dict[str, Any],
) -> tuple[str, dict[str, float]]:
    scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        fit = _fit_hazard_candidate(
            [(calibration, basis["calibration"])],
            model=model,
            ridge=fit_kwargs["hazard_ridge"],
            iterations=fit_kwargs["logistic_iterations"],
        )
        design, _ = _hazard_design(
            selection, basis["selection"], model=model
        )
        loss = _hazard_logloss(fit[0], design, selection["generated_next"])
        scores[model] = loss + fit_kwargs["complexity_penalty"] * len(fit[1])
    minimum = min(scores.values())
    selected = next(
        model
        for model in HAZARD_MODELS
        if scores[model] <= minimum + ROUTE_TIE_TOLERANCE
    )
    return selected, scores


def _soft_route_derivative(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    scores: dict[str, float],
    fit_kwargs: dict[str, Any],
    dimensions: int,
    hard_fits: dict[str, tuple[np.ndarray, tuple[str, ...]]],
    temperature: float,
) -> np.ndarray:
    """Score-softmax mixture of per-route combined-fit derivatives."""
    values = np.asarray([scores[m] for m in HAZARD_MODELS])
    logits = -(values - values.min()) / max(temperature, EPS)
    weights = np.exp(logits)
    weights = weights / weights.sum()
    mixture = np.zeros((basis["evaluation"].shape[0], dimensions))
    for model, weight in zip(HAZARD_MODELS, weights, strict=True):
        if weight < 1e-12 or model in ("base", "return"):
            continue  # base/return have no feedback block -> D = 0 exactly
        if model not in hard_fits:
            coefficient, names, _ = _fit_hazard_instrumented(
                [
                    (calibration, basis["calibration"]),
                    (selection, basis["selection"]),
                ],
                model=model,
                ridge=fit_kwargs["hazard_ridge"],
                iterations=fit_kwargs["logistic_iterations"],
            )
            hard_fits[model] = (coefficient, names)
        coefficient, names = hard_fits[model]
        derivative, _ = _readout_derivative(
            coefficient, names, basis["evaluation"], dimensions, model=model
        )
        mixture += weight * derivative
    return mixture


# ---------------------------------------------------------------------------
# frames: geodesic (Arm A) and angular perturbations (Arm B)
# ---------------------------------------------------------------------------


def _stack_frame(basis: dict[str, np.ndarray]) -> np.ndarray:
    return np.vstack([basis[role] for role in ROLES])


def _slice_frame(stacked: np.ndarray, categories: int) -> dict[str, np.ndarray]:
    return {
        role: stacked[index * categories : (index + 1) * categories]
        for index, role in enumerate(ROLES)
    }


def _geodesic_machinery(
    swap_basis: dict[str, np.ndarray],
    v2_basis: dict[str, np.ndarray],
) -> dict[str, Any]:
    categories = swap_basis["calibration"].shape[0]
    s0_raw = _stack_frame(swap_basis)
    s1 = _stack_frame(v2_basis)
    width = s1.shape[1]
    s0 = np.zeros((s0_raw.shape[0], width))
    s0[:, : s0_raw.shape[1]] = s0_raw
    cross = s1.T @ s0
    left, singular, right_t = np.linalg.svd(cross)
    rotation = left @ right_t
    s1_aligned = s1 @ rotation
    return {
        "s0": s0,
        "s1_aligned": s1_aligned,
        "rotation": rotation,
        "categories": categories,
        "procrustes_residual": float(np.linalg.norm(s0 - s1_aligned)),
        "frame_distance_raw": float(np.linalg.norm(s0 - s1)),
        "procrustes_singular_values": [float(v) for v in singular],
    }


def _basis_at_t(machinery: dict[str, Any], t: float) -> dict[str, np.ndarray]:
    stacked = (1.0 - t) * machinery["s0"] + t * machinery["s1_aligned"]
    return _slice_frame(stacked, machinery["categories"])


def _theta_plane_set(
    oracle_basis: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """One draw: a random unit vector orthogonal to every (role, category) row."""
    planes: dict[str, np.ndarray] = {}
    for role in ROLES:
        rows = oracle_basis[role]
        units = np.empty_like(rows)
        for category in range(rows.shape[0]):
            row = rows[category]
            norm = float(np.linalg.norm(row))
            if norm <= 1e-12:
                raise RuntimeError("zero oracle row cannot be perturbed")
            unit_row = row / norm
            gaussian = rng.standard_normal(rows.shape[1])
            ortho = gaussian - (gaussian @ unit_row) * unit_row
            ortho_norm = float(np.linalg.norm(ortho))
            if ortho_norm <= 1e-9:
                raise RuntimeError("degenerate random plane draw")
            units[category] = ortho / ortho_norm
        planes[role] = units
    return planes


def _theta_perturbed_basis(
    oracle_basis: dict[str, np.ndarray],
    planes: dict[str, np.ndarray],
    theta_rad: float,
) -> dict[str, np.ndarray]:
    perturbed: dict[str, np.ndarray] = {}
    cos_t = np.cos(theta_rad)
    sin_t = np.sin(theta_rad)
    for role in ROLES:
        rows = oracle_basis[role]
        norms = np.linalg.norm(rows, axis=1, keepdims=True)
        unit_rows = rows / np.maximum(norms, 1e-12)
        perturbed[role] = norms * (
            cos_t * unit_rows + sin_t * planes[role]
        )
    return perturbed


def _mean_deficit_vs_oracle(
    basis: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
) -> float:
    """Leg 10's registered alignment statistic (full-row cosine-gram)."""
    values = []
    for role in ROLES:
        gram = leg10._cosine_gram(basis[role])
        gram_oracle = leg10._cosine_gram(oracle_basis[role])
        for category in range(len(gram)):
            values.append(
                1.0
                - leg10._profile_alignment(gram, gram_oracle, category)
            )
    return float(np.mean(values))


# ---------------------------------------------------------------------------
# per-row evaluation helpers
# ---------------------------------------------------------------------------


def _hard_fit_row(
    context: dict[str, Any],
    view: str,
    author: int,
    basis: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, Any], tuple[np.ndarray, tuple[str, ...]]]:
    """Instrumented forced-route refit; returns D, discrete info, fit."""
    calibration, selection, _ = context["flat"][(view, author)]
    route = context["oracle_stacks"][view][author]["selected_model"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    coefficient, names, info = _fit_hazard_instrumented(
        [
            (calibration, basis["calibration"]),
            (selection, basis["selection"]),
        ],
        model=route,
        ridge=context["fit_kwargs"]["hazard_ridge"],
        iterations=context["fit_kwargs"]["logistic_iterations"],
    )
    derivative, readout_info = _readout_derivative(
        coefficient, names, basis["evaluation"], dimensions, model=route
    )
    info = {**info, **readout_info}
    return derivative, info, (coefficient, names)


def _soft_support_derivative(
    context: dict[str, Any],
    view: str,
    author: int,
    basis: dict[str, np.ndarray],
) -> np.ndarray:
    calibration, selection, _ = context["flat"][(view, author)]
    route = context["oracle_stacks"][view][author]["selected_model"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    coefficient, names, _ = _fit_hazard_instrumented(
        [
            (calibration, basis["calibration"]),
            (selection, basis["selection"]),
        ],
        model=route,
        ridge=context["fit_kwargs"]["hazard_ridge"],
        iterations=context["fit_kwargs"]["logistic_iterations"],
        soft=True,
    )
    derivative, _ = _readout_derivative(
        coefficient,
        names,
        basis["evaluation"],
        dimensions,
        model=route,
        soft=True,
    )
    return derivative


# ---------------------------------------------------------------------------
# per-world-rep pass
# ---------------------------------------------------------------------------


def _world_rep_pass(
    context: dict[str, Any],
    stored_swaps: pd.DataFrame,
) -> dict[str, Any]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    oracle_basis = truth.oracle_basis
    v2_basis = context["v2_basis"]
    fit_kwargs = context["fit_kwargs"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]

    unit_gap = leg4._true_derivative_unit_check(truth, dimensions)
    if unit_gap > UNIT_CHECK_TOLERANCE:
        raise RuntimeError(
            f"analytic D_true fails the probe unit check on {world} rep "
            f"{repetition}: {unit_gap:.3e}"
        )
    true_d = {
        author: leg4._true_derivative(truth, author)
        for author in range(context["authors"])
    }

    swap_basis = leg9._row_norm_swap(oracle_basis, v2_basis)
    machinery = _geodesic_machinery(swap_basis, v2_basis)

    # Arm B bases are world-rep-level objects (like the chart): one plane
    # set per draw, swept across all angles, shared by every author-view.
    theta_bases: dict[tuple[int, float], dict[str, np.ndarray]] = {}
    for draw in range(N_THETA_DRAWS):
        rng = np.random.default_rng([seed, THETA_SEED_TAG, draw])
        planes = _theta_plane_set(oracle_basis, rng)
        for theta in THETA_GRID_DEG:
            theta_bases[(draw, theta)] = _theta_perturbed_basis(
                oracle_basis, planes, np.deg2rad(theta)
            )

    reference = stored_swaps[
        (stored_swaps["world"] == world)
        & (stored_swaps["repetition"] == repetition)
    ]
    if len(reference) != 2 * context["authors"]:
        raise RuntimeError(
            f"Leg 9 swap reference incomplete for {world} rep {repetition}"
        )

    row_index = [
        (view, author)
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    degenerate: dict[tuple[str, int], bool] = {}
    for view, author in row_index:
        stack = context["oracle_stacks"][view][author]
        degenerate[(view, author)] = bool(
            float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE
        )

    keys_base = {"world": world, "repetition": repetition, "seed": seed}
    gap_t_rows: list[dict[str, Any]] = []
    discrete_rows: list[dict[str, Any]] = []
    soft_rows: list[dict[str, Any]] = []
    gap_theta_rows: list[dict[str, Any]] = []
    copy_gate_max = 0.0
    swap_anchor_max = 0.0
    v2_anchor_max = 0.0
    pad_gate_max = 0.0
    rot_gate_max = 0.0
    copy_gate_done = False

    # basis-level alignment along the path (companion)
    alignment_path_rows = [
        {
            **keys_base,
            "t": t,
            "deficit_vs_oracle": _mean_deficit_vs_oracle(
                (
                    swap_basis
                    if t == 0.0
                    else v2_basis
                    if t == 1.0
                    else _basis_at_t(machinery, t)
                ),
                oracle_basis,
            ),
        }
        for t in T_GRID
    ]

    for view, author in row_index:
        stack = context["oracle_stacks"][view][author]
        route = stack["selected_model"]
        keys = {
            **keys_base,
            "author": author,
            "view": view,
            "forced_route": route,
        }
        stored_row = reference[
            (reference["author"] == author) & (reference["view"] == view)
        ]
        if len(stored_row) != 1:
            raise RuntimeError(
                f"Leg 9 swap reference missing {world} r{repetition} "
                f"{view} a{author}"
            )
        stored_row = stored_row.iloc[0]
        if degenerate[(view, author)] != bool(
            stored_row["degenerate_reference"]
        ):
            raise RuntimeError(
                f"degenerate flag mismatch vs Leg 9 on {world} "
                f"r{repetition} {view} a{author}"
            )
        if degenerate[(view, author)]:
            for t in T_GRID:
                gap_t_rows.append(
                    {
                        **keys,
                        "t": t,
                        "degenerate_reference": True,
                        "e_t_true": np.nan,
                        "gap_t": np.nan,
                        "e_orc_true": np.nan,
                    }
                )
                discrete_rows.append(
                    {
                        **keys,
                        "t": t,
                        "degenerate_reference": True,
                    }
                )
                soft_rows.append(
                    {
                        **keys,
                        "t": t,
                        "degenerate_reference": True,
                        "gap_soft_support": np.nan,
                        "gap_soft_route": np.nan,
                    }
                )
            for draw in range(N_THETA_DRAWS):
                for theta in THETA_GRID_DEG:
                    gap_theta_rows.append(
                        {
                            **keys,
                            "draw": draw,
                            "theta_deg": theta,
                            "degenerate_reference": True,
                            "e_theta_true": np.nan,
                            "gap_theta": np.nan,
                        }
                    )
            continue

        d_true = true_d[author]
        e_orc = leg3._relative_error(stack["D"], d_true)

        # one-shot instrumented-vs-canonical coefficient bit-gate
        if not copy_gate_done:
            calibration, selection, _ = context["flat"][(view, author)]
            canonical = _fit_hazard_candidate(
                [
                    (calibration, v2_basis["calibration"]),
                    (selection, v2_basis["selection"]),
                ],
                model=route,
                ridge=fit_kwargs["hazard_ridge"],
                iterations=fit_kwargs["logistic_iterations"],
            )
            mine, _, _ = _fit_hazard_instrumented(
                [
                    (calibration, v2_basis["calibration"]),
                    (selection, v2_basis["selection"]),
                ],
                model=route,
                ridge=fit_kwargs["hazard_ridge"],
                iterations=fit_kwargs["logistic_iterations"],
            )
            copy_gate = float(np.max(np.abs(canonical[0] - mine)))
            copy_gate_max = max(copy_gate_max, copy_gate)
            if copy_gate > COPY_GATE_TOLERANCE:
                raise RuntimeError(
                    f"instrumented IRLS copy diverges from canonical on "
                    f"{world} r{repetition}: {copy_gate:.3e}"
                )
            copy_gate_done = True

        # ---- raw anchors: t=0 (Leg 9 swap_i) and t=1 (v2) ----------------
        d_swap_raw, _, _ = _hard_fit_row(context, view, author, swap_basis)
        e_swap_raw = leg3._relative_error(d_swap_raw, d_true)
        d_v2_raw, _, _ = _hard_fit_row(context, view, author, v2_basis)
        e_v2_raw = leg3._relative_error(d_v2_raw, d_true)
        anchor_gap = max(
            abs(e_swap_raw - float(stored_row["e_i_true"])),
            abs((e_swap_raw - e_orc) - float(stored_row["gap_i"])),
            abs(e_orc - float(stored_row["e_orc_true"])),
        )
        swap_anchor_max = max(swap_anchor_max, anchor_gap)
        if anchor_gap > ROW_TOLERANCE:
            raise RuntimeError(
                f"t=0 swap anchor diverges from Leg 9 persisted rows on "
                f"{world} r{repetition} {view} a{author}: {anchor_gap:.3e}"
            )
        v2_gap = max(
            abs(e_v2_raw - float(stored_row["e_d_true_v2"])),
            abs((e_v2_raw - e_orc) - float(stored_row["gap_v2"])),
        )
        v2_anchor_max = max(v2_anchor_max, v2_gap)
        if v2_gap > ROW_TOLERANCE:
            raise RuntimeError(
                f"t=1 v2 anchor diverges from Leg 9 persisted rows on "
                f"{world} r{repetition} {view} a{author}: {v2_gap:.3e}"
            )

        # ---- invariance gates (quotient construction is real) ------------
        d_pad, _, _ = _hard_fit_row(
            context, view, author, _basis_at_t(machinery, 0.0)
        )
        pad_gate = leg3._relative_error(d_pad, d_swap_raw)
        pad_gate_max = max(pad_gate_max, pad_gate)
        if pad_gate > PAD_GATE_TOLERANCE:
            raise RuntimeError(
                f"zero-padding invariance fails on {world} r{repetition} "
                f"{view} a{author}: {pad_gate:.3e}"
            )
        d_rot, _, _ = _hard_fit_row(
            context, view, author, _basis_at_t(machinery, 1.0)
        )
        rot_gate = leg3._relative_error(d_rot, d_v2_raw)
        rot_gate_max = max(rot_gate_max, rot_gate)
        if rot_gate > ROT_GATE_TOLERANCE:
            raise RuntimeError(
                f"rotation invariance fails on {world} r{repetition} "
                f"{view} a{author}: {rot_gate:.3e} -- the kernel-invariance "
                "premise of the geodesic is broken; refusing"
            )

        # soft-orc references (t-invariant, once per row)
        d_orc_soft = _soft_support_derivative(
            context, view, author, oracle_basis
        )
        e_orc_soft = leg3._relative_error(d_orc_soft, d_true)
        calibration, selection, _ = context["flat"][(view, author)]
        orc_selected, orc_scores = _route_scores(
            calibration, selection, oracle_basis, fit_kwargs
        )
        # the oracle stack's final combined fit IS the forced-route
        # component at the oracle basis -- reuse it (shared conventions)
        orc_fit_cache: dict[str, tuple[np.ndarray, tuple[str, ...]]] = {
            route: stack["final_hazard"]
        }
        e_orc_softroute: dict[float, float] = {}
        for temperature in (
            SOFT_ROUTE_TEMPERATURE,
            *SOFT_ROUTE_TEMPERATURES_SECONDARY,
        ):
            d_orc_mix = _soft_route_derivative(
                calibration,
                selection,
                oracle_basis,
                orc_scores,
                fit_kwargs,
                dimensions,
                orc_fit_cache,
                temperature,
            )
            e_orc_softroute[temperature] = leg3._relative_error(
                d_orc_mix, d_true
            )

        # ---- Arm A: walk the geodesic -------------------------------------
        previous_info: dict[str, Any] | None = None
        previous_route: str | None = None
        for t in T_GRID:
            if t == 0.0:
                basis_t = swap_basis
            elif t == 1.0:
                basis_t = v2_basis
            else:
                basis_t = _basis_at_t(machinery, t)
            derivative, info, fit = _hard_fit_row(
                context, view, author, basis_t
            )
            e_t = leg3._relative_error(derivative, d_true)
            gap_t_rows.append(
                {
                    **keys,
                    "t": t,
                    "degenerate_reference": False,
                    "e_t_true": e_t,
                    "gap_t": e_t - e_orc,
                    "e_orc_true": e_orc,
                }
            )
            selected_t, scores_t = _route_scores(
                calibration, selection, basis_t, fit_kwargs
            )
            floor_mask = info["floor_mask"]
            clip_mask = info["clip_mask"]
            assoc_mask = info["assoc_mask"]
            sign_pattern = info["sign_pattern"]
            row: dict[str, Any] = {
                **keys,
                "t": t,
                "degenerate_reference": False,
                "route_selected": selected_t,
                "route_agrees_forced": selected_t == route,
                "irls_iterations": info["iterations"],
                "n_cells": int(floor_mask.size),
                "n_floored": int(floor_mask.sum()),
                "n_clipped": int(clip_mask.sum()),
                "n_assoc_pos": int(assoc_mask.sum()),
                "readout_clip_count": info["readout_clip_count"],
                "readout_sign_pos": int((sign_pattern > 0).sum()),
            }
            if previous_info is None:
                row.update(
                    {
                        "route_changed": np.nan,
                        "n_floor_flips": np.nan,
                        "n_clip_flips": np.nan,
                        "n_assoc_flips": np.nan,
                        "n_sign_flips": np.nan,
                        "readout_clip_changed": np.nan,
                    }
                )
            else:
                row.update(
                    {
                        "route_changed": int(selected_t != previous_route),
                        "n_floor_flips": int(
                            (floor_mask != previous_info["floor_mask"]).sum()
                        ),
                        "n_clip_flips": int(
                            (clip_mask != previous_info["clip_mask"]).sum()
                        ),
                        "n_assoc_flips": int(
                            (assoc_mask != previous_info["assoc_mask"]).sum()
                        ),
                        "n_sign_flips": int(
                            (
                                sign_pattern
                                != previous_info["sign_pattern"]
                            ).sum()
                        ),
                        "readout_clip_changed": int(
                            info["readout_clip_count"]
                            != previous_info["readout_clip_count"]
                        ),
                    }
                )
            discrete_rows.append(row)
            previous_info = {
                "floor_mask": floor_mask,
                "clip_mask": clip_mask,
                "assoc_mask": assoc_mask,
                "sign_pattern": sign_pattern,
                "readout_clip_count": info["readout_clip_count"],
            }
            previous_route = selected_t

            # soft variants (diagnostic; both sides / symmetric)
            d_soft = _soft_support_derivative(
                context, view, author, basis_t
            )
            e_soft = leg3._relative_error(d_soft, d_true)
            arm_cache = {route: fit}
            soft_row = {
                **keys,
                "t": t,
                "degenerate_reference": False,
                "gap_soft_support": e_soft - e_orc_soft,
                "e_soft_support": e_soft,
                "e_orc_soft_support": e_orc_soft,
            }
            for temperature in (
                SOFT_ROUTE_TEMPERATURE,
                *SOFT_ROUTE_TEMPERATURES_SECONDARY,
            ):
                d_mix = _soft_route_derivative(
                    calibration,
                    selection,
                    basis_t,
                    scores_t,
                    fit_kwargs,
                    dimensions,
                    arm_cache,
                    temperature,
                )
                e_mix = leg3._relative_error(d_mix, d_true)
                suffix = (
                    ""
                    if temperature == SOFT_ROUTE_TEMPERATURE
                    else f"_T{temperature:g}"
                )
                soft_row[f"gap_soft_route{suffix}"] = (
                    e_mix - e_orc_softroute[temperature]
                )
            soft_row["orc_route_selected_replay"] = orc_selected
            soft_rows.append(soft_row)

        # ---- Arm B: angular perturbations of oracle directions ------------
        for draw in range(N_THETA_DRAWS):
            for theta in THETA_GRID_DEG:
                d_theta, _, _ = _hard_fit_row(
                    context, view, author, theta_bases[(draw, theta)]
                )
                e_theta = leg3._relative_error(d_theta, d_true)
                gap_theta_rows.append(
                    {
                        **keys,
                        "draw": draw,
                        "theta_deg": theta,
                        "degenerate_reference": False,
                        "e_theta_true": e_theta,
                        "gap_theta": e_theta - e_orc,
                    }
                )

    # basis-level theta alignment companion (per draw x theta)
    theta_alignment_rows = [
        {
            **keys_base,
            "draw": draw,
            "theta_deg": theta,
            "deficit_vs_oracle": _mean_deficit_vs_oracle(
                theta_bases[(draw, theta)], oracle_basis
            ),
        }
        for draw in range(N_THETA_DRAWS)
        for theta in THETA_GRID_DEG
    ]

    gates = {
        "world": world,
        "repetition": repetition,
        "true_d_unit_check_max_gap": unit_gap,
        "copy_gate_max_abs_diff": copy_gate_max,
        "swap_anchor_max_abs_diff": swap_anchor_max,
        "v2_anchor_max_abs_diff": v2_anchor_max,
        "pad_gate_max_rel_error": pad_gate_max,
        "rot_gate_max_rel_error": rot_gate_max,
        "procrustes_residual": machinery["procrustes_residual"],
        "frame_distance_raw": machinery["frame_distance_raw"],
        "degenerate_rows": int(sum(degenerate.values())),
    }
    return {
        "gap_t_rows": gap_t_rows,
        "gap_theta_rows": gap_theta_rows,
        "discrete_event_rows": discrete_rows,
        "soft_gap_rows": soft_rows,
        "alignment_path_rows": alignment_path_rows,
        "theta_alignment_rows": theta_alignment_rows,
        "gates": gates,
    }


# ---------------------------------------------------------------------------
# chunk driver
# ---------------------------------------------------------------------------


def _world_tag(worlds: list[str]) -> str:
    if list(worlds) == list(HIGH_GAP_WORLDS):
        return ""
    indices = "".join(
        str(list(HIGH_GAP_WORLDS).index(world)) for world in worlds
    )
    return f"_w{indices}"


def _run_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
) -> None:
    stored_swaps = _load_leg9_swap_reference()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    expected_for = leg8._expected_geometries_lookup(config)

    collections: dict[str, list] = {
        name: []
        for name in (
            "gap_t_rows",
            "gap_theta_rows",
            "discrete_event_rows",
            "soft_gap_rows",
            "alignment_path_rows",
            "theta_alignment_rows",
            "validation",
        )
    }
    gates: list[dict[str, Any]] = []
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
            result = _world_rep_pass(context, stored_swaps)
            for name in (
                "gap_t_rows",
                "gap_theta_rows",
                "discrete_event_rows",
                "soft_gap_rows",
                "alignment_path_rows",
                "theta_alignment_rows",
            ):
                collections[name].extend(result[name])
            gates.append(result["gates"])

            frame = pd.DataFrame(
                [
                    row
                    for row in result["gap_t_rows"]
                    if not row["degenerate_reference"]
                ]
            )
            curve = {
                f"t{t:g}": round(
                    float(frame[frame["t"] == t]["gap_t"].median()), 4
                )
                for t in T_GRID
            }
            theta_frame = pd.DataFrame(
                [
                    row
                    for row in result["gap_theta_rows"]
                    if not row["degenerate_reference"]
                ]
            )
            theta_curve = {
                f"th{theta:g}": round(
                    float(
                        theta_frame[theta_frame["theta_deg"] == theta][
                            "gap_theta"
                        ].median()
                    ),
                    4,
                )
                for theta in THETA_GRID_DEG
            }
            print(
                f"[leg11] rep={repetition} world={world} gap(t) {curve} "
                f"gap(theta) {theta_curve} "
                f"rot_gate={result['gates']['rot_gate_max_rel_error']:.1e} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = f"rep{repetitions[0]}-{repetitions[-1]}{_world_tag(worlds)}"
    args.output.mkdir(parents=True, exist_ok=True)
    stems = {
        "gap_t_rows": "gap_t_rows",
        "gap_theta_rows": "gap_theta_rows",
        "discrete_event_rows": "discrete_event_rows",
        "soft_gap_rows": "soft_gap_rows",
        "alignment_path_rows": "alignment_path",
        "theta_alignment_rows": "theta_alignment",
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
                "repetitions": list(repetitions),
                "worlds": worlds,
            },
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )
        handle.write("\n")
    print(f"[chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# assembly + adjudication
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


def _author_curve(
    frame: pd.DataFrame,
    value: str,
    coordinate: str,
    extra_keys: list[str] | None = None,
) -> pd.DataFrame:
    """View-mean per author, per coordinate (Leg 9 aggregation semantics)."""
    keys = ["world", "repetition", "author", coordinate] + (extra_keys or [])
    return (
        frame.groupby(keys)[value]
        .mean()
        .reset_index()
    )


def _assemble(args: argparse.Namespace, config: dict[str, Any]) -> None:
    repetitions = int(config["repetitions"])
    authors = 16
    worlds = list(HIGH_GAP_WORLDS)
    n_world_reps = len(worlds) * repetitions
    n_rows = n_world_reps * 2 * authors

    gap_t = _concat_partials(args.output, "gap_t_rows")
    gap_theta = _concat_partials(args.output, "gap_theta_rows")
    discrete = _concat_partials(args.output, "discrete_event_rows")
    soft = _concat_partials(args.output, "soft_gap_rows")
    alignment_path = _concat_partials(args.output, "alignment_path")
    theta_alignment = _concat_partials(args.output, "theta_alignment")
    validation = _concat_partials(args.output, "v2_validation")
    gate_payloads = []
    for path in sorted(
        glob.glob(str(args.output / "partial_gates_rep*.json"))
    ):
        with open(path, "r", encoding="utf-8") as handle:
            gate_payloads.append(json.load(handle))
    gates = [gate for chunk in gate_payloads for gate in chunk["gates"]]

    _refuse_bad_cells(
        gap_t,
        ["world", "repetition", "author", "view", "t"],
        n_rows * len(T_GRID),
        "gap(t) rows",
    )
    _refuse_bad_cells(
        gap_theta,
        ["world", "repetition", "author", "view", "draw", "theta_deg"],
        n_rows * N_THETA_DRAWS * len(THETA_GRID_DEG),
        "gap(theta) rows",
    )
    _refuse_bad_cells(
        discrete,
        ["world", "repetition", "author", "view", "t"],
        n_rows * len(T_GRID),
        "discrete event rows",
    )
    _refuse_bad_cells(
        soft,
        ["world", "repetition", "author", "view", "t"],
        n_rows * len(T_GRID),
        "soft gap rows",
    )
    _refuse_bad_cells(
        alignment_path,
        ["world", "repetition", "t"],
        n_world_reps * len(T_GRID),
        "alignment path rows",
    )
    if len(gates) != n_world_reps:
        raise RuntimeError(
            f"gate payloads cover {len(gates)} world-reps != {n_world_reps}"
        )

    usable_t = gap_t[~gap_t["degenerate_reference"]].copy()
    usable_theta = gap_theta[~gap_theta["degenerate_reference"]].copy()
    usable_soft = soft[~soft["degenerate_reference"]].copy()

    # ---- world-level curves (Leg 9 semantics) -----------------------------
    author_t = _author_curve(usable_t, "gap_t", "t")
    world_curves: dict[str, dict[float, float]] = {}
    for world in worlds:
        scoped = author_t[author_t["world"] == world]
        world_curves[world] = {
            float(t): float(scoped[scoped["t"] == t]["gap_t"].median())
            for t in T_GRID
        }
    author_theta = _author_curve(
        usable_theta, "gap_theta", "theta_deg", ["draw"]
    )
    theta_curves: dict[str, dict[float, float]] = {}
    for world in worlds:
        scoped = author_theta[author_theta["world"] == world]
        theta_curves[world] = {
            float(theta): float(
                scoped[scoped["theta_deg"] == theta]["gap_theta"].median()
            )
            for theta in THETA_GRID_DEG
        }

    # ---- anchor asserts at world level ------------------------------------
    stored_swaps = _load_leg9_swap_reference()
    stored_usable = stored_swaps[~stored_swaps["degenerate_reference"]]
    stored_author = (
        stored_usable.groupby(["world", "repetition", "author"])[
            ["gap_i", "gap_v2"]
        ]
        .mean()
        .reset_index()
    )
    leg10_table = _load_leg10_world_table().set_index("world")
    anchor_report = {}
    for world in worlds:
        scoped = stored_author[stored_author["world"] == world]
        stored_t0 = float(scoped["gap_i"].median())
        stored_t1_leg9 = float(scoped["gap_v2"].median())
        stored_t1_leg10 = float(leg10_table.loc[world, "median_gap_v2"])
        mine_t0 = world_curves[world][0.0]
        mine_t1 = world_curves[world][1.0]
        gap0 = abs(mine_t0 - stored_t0)
        gap1 = max(
            abs(mine_t1 - stored_t1_leg9), abs(mine_t1 - stored_t1_leg10)
        )
        if gap0 > WORLD_MEDIAN_TOLERANCE or gap1 > WORLD_MEDIAN_TOLERANCE:
            raise RuntimeError(
                f"world-median anchors diverge on {world}: t0 {gap0:.3e} "
                f"t1 {gap1:.3e}"
            )
        anchor_report[world] = {
            "t0_mine": mine_t0,
            "t0_leg9_swap_i": stored_t0,
            "t1_mine": mine_t1,
            "t1_leg9_gap_v2": stored_t1_leg9,
            "t1_leg10_gap_world_table": stored_t1_leg10,
        }

    # ---- lean (a): non-smoothness ------------------------------------------
    t_values = [float(t) for t in T_GRID]
    lean_a_worlds_t: list[str] = []
    lean_a_worlds_theta: list[str] = []
    knee_table = []
    smooth_worlds: list[str] = []
    for world in worlds:
        curve = world_curves[world]
        gap0 = curve[0.0]
        gap1 = curve[1.0]
        full_rise = gap1 - gap0
        rise_at_bar = curve[LEAN_A_T] - gap0
        early_share = rise_at_bar / max(full_rise, EPS)
        slopes = {}
        for first, second in zip(t_values[:-1], t_values[1:], strict=True):
            slopes[f"{first:g}->{second:g}"] = (
                (curve[second] - curve[first]) / (second - first)
            )
        mean_slope = full_rise / 1.0
        max_slope_key = max(slopes, key=lambda key: slopes[key])
        max_slope_ratio = slopes[max_slope_key] / max(mean_slope, EPS)
        theta5 = theta_curves[world][LEAN_A_THETA_DEG]
        theta_share = theta5 / max(gap1, EPS)
        condition_t = early_share >= LEAN_A_FRACTION
        condition_theta = theta_share >= LEAN_A_FRACTION
        if condition_t:
            lean_a_worlds_t.append(world)
        if condition_theta:
            lean_a_worlds_theta.append(world)
        is_smooth = (
            (not condition_t)
            and max_slope_ratio < SMOOTH_SLOPE_RATIO_BAR
        )
        if is_smooth:
            smooth_worlds.append(world)
        knee_table.append(
            {
                "world": world,
                "gap_t0": gap0,
                "gap_t1": gap1,
                "full_rise": full_rise,
                "rise_at_t0.2": rise_at_bar,
                "early_share_t0.2": early_share,
                "gap_theta5": theta5,
                "theta5_share_of_gap_v2": theta_share,
                "knee_interval_max_slope": max_slope_key,
                "max_slope": slopes[max_slope_key],
                "mean_slope": mean_slope,
                "max_slope_ratio": max_slope_ratio,
                "smooth_flag": is_smooth,
                **{f"slope_{key}": value for key, value in slopes.items()},
            }
        )
    lean_a = {
        "statement": (
            "gap jumps >= half its full value by t <= .2 (geodesic) or "
            "theta <= 5 deg (angular) in >= 2/3 worlds"
        ),
        "worlds_geodesic_reading": lean_a_worlds_t,
        "worlds_angular_reading": lean_a_worlds_theta,
        "held_geodesic": len(lean_a_worlds_t) >= LEAN_MIN_WORLDS,
        "held_angular": len(lean_a_worlds_theta) >= LEAN_MIN_WORLDS,
        "held": (
            len(lean_a_worlds_t) >= LEAN_MIN_WORLDS
            or len(lean_a_worlds_theta) >= LEAN_MIN_WORLDS
        ),
    }

    # ---- lean (b): co-occurrence of discrete flips with the gap rise ------
    usable_discrete = discrete[~discrete["degenerate_reference"]].copy()
    merged = usable_t.merge(
        usable_discrete[
            [
                "world",
                "repetition",
                "author",
                "view",
                "t",
                "route_changed",
                "n_floor_flips",
                "n_assoc_flips",
                "n_clip_flips",
                "n_sign_flips",
                "readout_clip_changed",
                "route_selected",
                "route_agrees_forced",
            ]
        ],
        on=["world", "repetition", "author", "view", "t"],
    )
    if len(merged) != len(usable_t):
        raise RuntimeError("discrete/gap row merge lost cells")
    merged = merged.sort_values(
        ["world", "repetition", "author", "view", "t"]
    )
    group_keys = ["world", "repetition", "author", "view"]
    merged["gap_prev"] = merged.groupby(group_keys)["gap_t"].shift(1)
    intervals = merged[~merged["gap_prev"].isna()].copy()
    intervals["delta_gap_pos"] = np.maximum(
        intervals["gap_t"] - intervals["gap_prev"], 0.0
    )
    family_columns = {
        "category_association": "n_assoc_flips",
        "route_agreement": "route_changed",
        "support_cell_membership": "n_floor_flips",
    }
    companion_columns = {
        "logit_clip_fit": "n_clip_flips",
        "readout_sign": "n_sign_flips",
        "readout_clip": "readout_clip_changed",
    }
    cooccurrence: dict[str, dict[str, float]] = {}
    flip_density: dict[str, dict[str, float]] = {}
    isolation: dict[str, dict[str, Any]] = {}
    for world in worlds:
        scoped = intervals[intervals["world"] == world]
        total = float(scoped["delta_gap_pos"].sum())
        shares = {}
        densities = {}
        for family, column in {
            **family_columns,
            **companion_columns,
        }.items():
            flagged = scoped[column].astype(float) > 0
            shares[family] = float(
                scoped.loc[flagged, "delta_gap_pos"].sum()
                / max(total, EPS)
            )
            # ubiquity guard (companion, no adjudication weight): a family
            # flipping in every row-interval absorbs all rise trivially --
            # the density makes that visible
            densities[family] = float(flagged.mean())
        cooccurrence[world] = shares
        flip_density[world] = densities
        registered_hits = [
            family
            for family in REGISTERED_FAMILIES
            if shares[family] >= COOCCURRENCE_BAR
        ]
        isolation[world] = {
            "families_at_or_above_bar": registered_hits,
            "isolated": len(registered_hits) == 1,
            "isolated_family": (
                registered_hits[0] if len(registered_hits) == 1 else None
            ),
            "total_positive_rise": total,
        }
    isolating_worlds = [
        world for world in worlds if isolation[world]["isolated"]
    ]
    isolated_families = {
        isolation[world]["isolated_family"] for world in isolating_worlds
    }
    lean_b = {
        "statement": (
            "C isolates a single flipping decision family (registered "
            "families: category association / route agreement / "
            "support-cell membership) in >= 2/3 worlds, same family"
        ),
        "cooccurrence_shares": cooccurrence,
        "flip_density_companion": flip_density,
        "isolation_by_world": isolation,
        "isolating_worlds": isolating_worlds,
        "held": (
            len(isolating_worlds) >= LEAN_MIN_WORLDS
            and len(isolated_families) == 1
        ),
        "isolated_family_global": (
            next(iter(isolated_families))
            if len(isolated_families) == 1 and isolating_worlds
            else None
        ),
    }

    # ---- lean (c): soft-assignment diagnostic at the knee ------------------
    author_soft_support = _author_curve(
        usable_soft, "gap_soft_support", "t"
    )
    author_soft_route = _author_curve(usable_soft, "gap_soft_route", "t")
    soft_curves: dict[str, dict[str, dict[float, float]]] = {}
    for world in worlds:
        soft_curves[world] = {}
        for label, source in (
            ("soft_support", author_soft_support),
            ("soft_route", author_soft_route),
        ):
            scoped = source[source["world"] == world]
            value = "gap_soft_support" if label == "soft_support" else (
                "gap_soft_route"
            )
            soft_curves[world][label] = {
                float(t): float(
                    scoped[scoped["t"] == t][value].median()
                )
                for t in T_GRID
            }
    family_to_variant = {
        "support_cell_membership": "soft_support",
        "category_association": "soft_support",  # same logits thresholded;
        # nearest causal analog -- association mask is a shadow decision
        "route_agreement": "soft_route",
    }
    removal_rows = []
    lean_c_applicable = bool(isolating_worlds)
    lean_c_all_pass = lean_c_applicable
    knee_lookup = {row["world"]: row for row in knee_table}
    for world in isolating_worlds:
        family = isolation[world]["isolated_family"]
        variant = family_to_variant[family]
        knee_key = knee_lookup[world]["knee_interval_max_slope"]
        first_s, second_s = knee_key.split("->")
        first, second = float(first_s), float(second_s)
        hard_jump = (
            world_curves[world][second] - world_curves[world][first]
        )
        soft_jump = (
            soft_curves[world][variant][second]
            - soft_curves[world][variant][first]
        )
        removal = 1.0 - soft_jump / max(hard_jump, EPS)
        passed = removal >= REMOVAL_BAR
        lean_c_all_pass = lean_c_all_pass and passed
        removal_rows.append(
            {
                "world": world,
                "isolated_family": family,
                "soft_variant": variant,
                "knee_interval": knee_key,
                "jump_hard": hard_jump,
                "jump_soft": soft_jump,
                "removal": removal,
                "passed": passed,
            }
        )
    lean_c = {
        "statement": (
            "soft-assignment variant removes >= half the knee jump in "
            "every world where (b) isolated (DIAGNOSTIC, "
            "unregistered-secondary functional variants)"
        ),
        "applicable": lean_c_applicable,
        "removal_rows": removal_rows,
        "held": bool(lean_c_applicable and lean_c_all_pass),
        "label": (
            "SOFT VARIANTS ARE DIAGNOSTIC ONLY -- NOT DEPLOYABLE "
            "ESTIMATOR SEMANTICS"
        ),
    }

    leans_held = int(lean_a["held"]) + int(lean_b["held"]) + int(
        lean_c["held"]
    )

    # ---- pivot ----------------------------------------------------------
    pivot_fires = (not lean_a["held"]) and (
        len(smooth_worlds) >= LEAN_MIN_WORLDS
    )
    if pivot_fires:
        verdict = "SMOOTH_GAP_ALL_OR_NOTHING_READING_WRONG"
    elif lean_a["held"]:
        verdict = "NON_SMOOTH_EARLY_JUMP"
    else:
        verdict = "NEITHER_EARLY_JUMP_NOR_SMOOTH_LATE_OR_MIXED_KNEE"
    pivot = {
        "registered": (
            "gap(t) SMOOTH (no knee, ~proportional growth) -> the "
            "all-or-nothing reading is WRONG; residual accepted as "
            "genuinely distributed object-level direction content; arc "
            "closes either way"
        ),
        "pre_coded_rule": (
            "fires iff lean (a) misses under BOTH readings AND >= 2/3 "
            "worlds have early_share < .5 AND max_slope/mean_slope < 3"
        ),
        "smooth_worlds": smooth_worlds,
        "fires": pivot_fires,
        "verdict": verdict,
    }

    # ---- faithfulness summary --------------------------------------------
    faithfulness = {
        "v2_replay_rows": int(len(validation)),
        "v2_replay_max_abs_difference": float(
            validation["abs_difference"].max()
        )
        if len(validation)
        else None,
        "true_d_unit_check_max": max(
            float(gate["true_d_unit_check_max_gap"]) for gate in gates
        ),
        "copy_gate_max_abs_diff": max(
            float(gate["copy_gate_max_abs_diff"]) for gate in gates
        ),
        "leg9_swap_anchor_max_abs_diff": max(
            float(gate["swap_anchor_max_abs_diff"]) for gate in gates
        ),
        "leg9_v2_anchor_max_abs_diff": max(
            float(gate["v2_anchor_max_abs_diff"]) for gate in gates
        ),
        "pad_gate_max_rel_error": max(
            float(gate["pad_gate_max_rel_error"]) for gate in gates
        ),
        "rot_gate_max_rel_error": max(
            float(gate["rot_gate_max_rel_error"]) for gate in gates
        ),
        "world_median_anchors": anchor_report,
        "degenerate_rows_total": int(
            sum(int(gate["degenerate_rows"]) for gate in gates)
        ),
    }

    # ---- descriptive tables -------------------------------------------------
    alignment_summary = (
        alignment_path.groupby("t")["deficit_vs_oracle"]
        .median()
        .to_dict()
    )
    theta_alignment_summary = (
        theta_alignment.groupby("theta_deg")["deficit_vs_oracle"]
        .median()
        .to_dict()
    )
    route_profile = (
        usable_discrete.groupby(["world", "t"])["route_agrees_forced"]
        .mean()
        .reset_index()
        .pivot(index="world", columns="t", values="route_agrees_forced")
        .to_dict(orient="index")
    )
    floored_profile = (
        usable_discrete.groupby(["world", "t"])["n_floored"]
        .median()
        .reset_index()
        .pivot(index="world", columns="t", values="n_floored")
        .to_dict(orient="index")
    )

    decision = {
        "estimand_id": "SUICA_M4_D_PERTURBATION_LEG11",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md Leg 11 "
            "(2026-08-02, loop cycle 6, commit 0e81907, before run); "
            "DESIGNATED FINAL LEG OF THE M4-D ARC"
        ),
        "design": {
            "worlds": worlds,
            "repetitions": repetitions,
            "t_grid": list(T_GRID),
            "theta_grid_deg": list(THETA_GRID_DEG),
            "theta_draws": N_THETA_DRAWS,
            "geodesic": (
                "Kendall size-and-shape quotient geodesic on stacked role "
                "frames: t=0 = Leg 9 swap_i (oracle directions + "
                "discovered norms, zero-padded 7->13), t=1 = discovered v2 "
                "basis Procrustes-aligned (R* = UV' of S1'S0); functional "
                "invariance under padding/rotation EMPIRICALLY GATED per "
                "author-view; endpoint curve values computed at raw "
                "representatives, bit-anchored to persisted rows"
            ),
            "theta_arm": (
                "full-row rotations of the pure oracle basis by exactly "
                "theta in a random plane per (role, category); norms "
                "preserved; common plane set per draw swept across angles"
            ),
            "discrete_families_registered": list(REGISTERED_FAMILIES),
            "discrete_companions": list(companion_columns),
            "gap_semantics": (
                "Leg 9: forced-route refits at 1x r=0, gap = e_arm_true - "
                "e_orc_true, author-level view-mean, world median"
            ),
            "shadow_decision_note": (
                "route selection and the association mask are SHADOW "
                "decisions under the forced route -- they do not enter "
                "the computed functional; the functional's own hard "
                "nonlinearities are the weight floor, the logit clips, "
                "and the IRLS early stop"
            ),
        },
        "faithfulness": faithfulness,
        "world_curves_gap_t": {
            world: {f"{t:g}": value for t, value in curve.items()}
            for world, curve in world_curves.items()
        },
        "world_curves_gap_theta": {
            world: {f"{theta:g}": value for theta, value in curve.items()}
            for world, curve in theta_curves.items()
        },
        "soft_world_curves": {
            world: {
                label: {f"{t:g}": value for t, value in curve.items()}
                for label, curve in variants.items()
            }
            for world, variants in soft_curves.items()
        },
        "knee_table": knee_table,
        "alignment_deficit_along_path_median": {
            f"{t:g}": float(value)
            for t, value in alignment_summary.items()
        },
        "alignment_deficit_theta_median": {
            f"{theta:g}": float(value)
            for theta, value in theta_alignment_summary.items()
        },
        "route_agreement_profile": route_profile,
        "floored_cells_profile": floored_profile,
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "leans_held": leans_held,
        "pivot_if": pivot,
        "arc_closure": {
            "statement": (
                "Leg 11 is the arc's designated last leg. Registered "
                "hand-off: the arc-final synthesis is the PLANNER's job; "
                "the loop's standing queue is (1) two-stage retrofit of "
                "the C.3 attribution NO-GO, (2) R->V bridge "
                "heteroscedastic calibration."
            )
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "diagnostic; V1/V2 NO-GO decisions stand; soft variants are "
            "diagnostic only, never deployable estimator semantics; no "
            "natural-text, personality, or clinical claim."
        ),
    }

    args.output.mkdir(parents=True, exist_ok=True)
    gap_t.sort_values(
        ["world", "repetition", "author", "view", "t"]
    ).to_csv(args.output / "gap_t_rows.csv", index=False)
    gap_theta.sort_values(
        ["world", "repetition", "author", "view", "draw", "theta_deg"]
    ).to_csv(args.output / "gap_theta_rows.csv", index=False)
    discrete.sort_values(
        ["world", "repetition", "author", "view", "t"]
    ).to_csv(args.output / "discrete_event_rows.csv", index=False)
    soft.sort_values(
        ["world", "repetition", "author", "view", "t"]
    ).to_csv(args.output / "soft_gap_rows.csv", index=False)
    alignment_path.sort_values(["world", "repetition", "t"]).to_csv(
        args.output / "alignment_path_rows.csv", index=False
    )
    theta_alignment.sort_values(
        ["world", "repetition", "draw", "theta_deg"]
    ).to_csv(args.output / "theta_alignment_rows.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    pd.DataFrame(knee_table).to_csv(
        args.output / "knee_table.csv", index=False
    )
    with (args.output / "decision.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(
        json.dumps(
            {
                "lean_a_held": lean_a["held"],
                "lean_b_held": lean_b["held"],
                "lean_c_held": lean_c["held"],
                "pivot_fires": pivot_fires,
                "verdict": verdict,
                "early_shares": {
                    row["world"]: round(row["early_share_t0.2"], 4)
                    for row in knee_table
                },
                "theta5_shares": {
                    row["world"]: round(row["theta5_share_of_gap_v2"], 4)
                    for row in knee_table
                },
            },
            indent=2,
        )
    )


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
        default=ROOT / "results" / "m4_d_perturbation",
    )
    parser.add_argument("--chunk-start", type=int, default=None)
    parser.add_argument("--chunk-stop", type=int, default=None)
    parser.add_argument(
        "--worlds",
        type=str,
        default=None,
        help="comma-separated subset of the three high-gap worlds",
    )
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args, config)
        return
    if args.chunk_start is None or args.chunk_stop is None:
        raise SystemExit(
            "either --assemble or both --chunk-start/--chunk-stop required"
        )
    worlds = (
        [w for w in args.worlds.split(",") if w]
        if args.worlds
        else list(HIGH_GAP_WORLDS)
    )
    for world in worlds:
        if world not in HIGH_GAP_WORLDS:
            raise SystemExit(f"not a registered high-gap world: {world}")
    repetitions = tuple(range(args.chunk_start, args.chunk_stop))
    _run_chunk(args, config, spec, repetitions, worlds)


if __name__ == "__main__":
    main()
