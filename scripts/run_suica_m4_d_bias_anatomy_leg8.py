#!/usr/bin/env python3
"""M4-D Leg 8: bias anatomy -- de-biasing, family enlargement, subspace
alignment, and the stacks.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 8 -- bias anatomy", 2026-08-02 loop cycle 3, commit bc3a15a, BEFORE this
run). All prior machinery is IMPORTED, not reimplemented: the Leg-4b floor
protocol (oracle-forced route, e_d_paired/e_orc_true, frozen-world budget
regeneration) from scripts/run_suica_m4_d_dleg_floor_leg4.py, the excitation
generator wiring and amplitude-0 identity gate from
scripts/run_suica_m4_d_excitation_floor_leg6.py, the two-stage construction
from scripts/run_suica_m4_d_two_stage_leg5.py, and the scale-aware persisted-
row asserts from scripts/run_suica_m4_d_realization_averaging_leg7.py.

THE TARGET (Leg-7 pivot profile / synthesis Addendum 2). The ~.39 D-leg floor
decomposed into two R-invariant BIAS components: law-level bias ~.376
(oracle-own-error e_orc_true at 1x, shared by both bases; excitation-
responsive per Leg 6: .376 -> .292) and basis-mismatch bias ~.136 (author-
level e_d_true - e_orc_true gap, flat under everything tested). Three
registered levers, one battery:

ARM A (de-biased oracle refit; oracle basis + oracle-forced route):
  (i)  A_unpen  -- penalty -> 0 (unpenalized). DISCOVERED INSTABILITY,
       documented guard: the oracle basis contains an exact constant column
       (its first column is all ones, duplicating the intercept), so the
       unpenalized IRLS normal system is exactly singular by construction.
       Guard ladder per IRLS iteration: np.linalg.solve -> np.linalg.lstsq
       (gelsd minimum-norm; its SVD iteration was observed to fail on
       ill-conditioned 704-feature unpenalized enlarged systems) ->
       scipy gelsy (QR, no SVD iteration) -> trace-scaled jitter solve.
       Fallback counts are persisted per fit. The redundant direction does
       not affect predicted probabilities, so the derivative probes are
       well defined.
  (ii) A_lam1n  -- penalty scaled to vanish with n: penalty = hazard_ridge*I
       (intercept exempt), i.e. the V2 penalty divided by len(y) -- an
       effective lambda ~ 1/n. Numerically stable (no guard fires).
  e_orc_true at 1x and 4x, per world.
ARM B (family enlargement, ONE registered step, no search): B_enlarged --
  append ALL pairwise interaction products x_i*x_j (i<j, non-intercept) of
  the existing hazard design columns of the forced-route model, at the
  oracle basis, fit with V2 penalty semantics (ridge*n*I). e_orc_true at
  1x/4x. Companion AB_enlarged_unpen (enlarged family + penalty -> 0, same
  lstsq guard) at 1x -- the "A and B together" arm the registered pivot
  condition evaluates.
ARM C (subspace alignment, DIAGNOSTIC -- the oracle basis is consumed, so
  this is unavailable operationally): orthogonal Procrustes alignment of the
  DISCOVERED chart frame onto the oracle frame -- W = argmin over
  column-orthonormal maps of ||A W - B||_F with A = the three stacked v2
  basis roles, B = the stacked oracle roles; aligned basis = v2_basis @ W
  (width 7). Refit D at the aligned frame (V2 estimator semantics, forced
  route); gap_aligned = e_aligned_true - e_orc_true at author level; measure
  how much of the ~.136 estimator-minus-oracle gap closes.
ARM D (stacks): (part 1) every lever refit on the Leg-6 C3.3-excited 1x
  panels at the oracle basis (law-level target; excitation alone got .292);
  (part 2) best-of-A/B/C + two-stage: the full 5x8 battery where stage 1 =
  Leg 5's penalized route selection (lambda=.125, asserted) and stage 2
  refits D with the selected estimator lever at the selected frame; loop =
  D_lever @ G_v2 @ C_v2, vs Leg 5's persisted .7605.

REGISTERED SELECTION RULE for the stack (no discretion at run time):
  estimator lever = argmin over {baseline_v2, A_unpen, A_lam1n, B_enlarged,
  AB_enlarged_unpen} of pooled author-level median e_orc_true at natural 1x
  (baseline winning = no estimator lever); frame = aligned iff pooled
  gap_aligned < pooled gap_v2 else v2. COMPUTE GUARD (pre-registered): the
  enlarged family at the discovered width-12/13 frame is ~2,279 features x
  30 lstsq iterations x 1,280 rows (multi-hour); if the selection pairs an
  enlarged estimator with the v2 frame, the stack substitutes the ALIGNED
  frame (width 7) and the decision records the substitution.

REGISTERED LEANS (adjudication statistics pre-coded here):
  (a) de-biasing alone: per-world median e_orc_true(A variant) <= .25 at
      natural 1x in >= 3/5 worlds (either A variant qualifying; both
      reported);
  (b) A or B + excitation: pooled e_orc_true <= .18 at excited 1x, min over
      {A_unpen, A_lam1n, B_enlarged} (AB reported alongside, not binding);
  (c) alignment closes >= half the .136 gap: pooled gap_aligned <= .068;
  (d) full stack: two_stage_lever pooled loop geometry >= .80.
PIVOT-IF (registered): A and B together move oracle-own-error < .05 --
  evaluated as (baseline pooled natural-1x e_orc_true) minus (min pooled
  over all four lever arms) < .05 -> verdict WORLD_IDENTIFIABILITY_LIMIT;
  next instrument = information-operator conditioning analysis of the
  creation estimand at the oracle basis, PROFILED IN-RUN here (first look,
  not a full leg): per non-degenerate author-view at 1x, the Fisher
  information matrix I_n = X^T diag(p(1-p)) X / n of the forced-route hazard
  fit at the oracle basis, its eigen-spectrum (raw + effective condition
  numbers, near-null counts), the creation estimand's coefficient Jacobian J
  (probe construction), the Cramer-Rao-style relative sd proxy
  sqrt(tr(J I_n^+ J^T)/n)/||D_true||, and the fraction of ||J||^2 lying in
  the near-null eigenspace. NOTE: the oracle basis constant column makes ONE
  exact null direction structural (intercept aliasing); the effective
  statistics exclude it.

FAITHFULNESS GATES (all hard RuntimeError, per world-rep, before new arms):
  baseline V2 floor rows at budgets {1x, 4x} recomputed via
  leg4._budget_rows_for_world_rep and asserted against Leg 4's persisted
  dleg_budget_rows.csv (leg6._assert_passive_rows, <= 1e-9, flags equal);
  flex-fit identity -- the flexible-penalty fitter in V2 mode reproduces the
  V2 coefficients EXACTLY (same design, same op order) on the first
  non-degenerate row; enlarged-family zero-interaction identity -- the
  enlarged probe machinery with interaction coefficients at zero reproduces
  the base derivative to <= 1e-12 (exact zero is unattainable: the longer
  hstacked probe rows change BLAS blocked-summation order, producing
  ULP-level ~1e-15 wobble on identical terms -- the Leg-7 tolerance note's
  phenomenon; gate values persisted); excited
  1x V2 rows asserted against Leg 6's persisted excitation rows; frozen-law
  asserts on every 4x regeneration; amplitude-0 excitation identity gate at
  repetition 0 per world (leg6 reuse); stage-1 rows vs Leg 4 persisted arm2
  rows and two_stage rows vs Leg 5 persisted rows (leg7._assert_rows_scaled,
  scale-aware, flips must total 73).

Chunked execution (this arc's battery-then-stall workaround): --chunk-start/
--chunk-stop run floor repetition ranges in the foreground writing partial
CSVs; --select-stack applies the registered selection rule to the floor
partials and writes stack_composition.json; --stack-chunk-start/--stack-
chunk-stop run the stack battery (refused until the composition exists);
--assemble concatenates all partials, REFUSES missing or duplicate cells,
and adjudicates from the concatenated rows only.
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
import run_suica_m4_d_excitation_floor_leg6 as leg6  # noqa: E402
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_realization_averaging_leg7 as leg7  # noqa: E402
import run_suica_m4_d_two_stage_leg5 as leg5  # noqa: E402

from scipy.linalg import lstsq as scipy_lstsq  # noqa: E402
from scipy.special import expit  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _creation_action,
    _feedback_derivative,
    _fit_logistic,
    _flatten_events,
    _hazard_design,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
)

LOOP_WORLDS = leg3.LOOP_WORLDS
NATURAL_BUDGETS = (1.0, 4.0)
AMPLITUDE = leg6.AMPLITUDE  # 1.0, C3.3's frozen excitation amplitude
STAGE1_LAMBDA = leg5.STAGE1_LAMBDA  # 0.125
ROW_TOLERANCE = 1e-9
LEVER_ARMS = ("A_unpen", "A_lam1n", "B_enlarged", "AB_enlarged_unpen")
LEVER_SPECS: dict[str, dict[str, Any]] = {
    "A_unpen": {"family": "base", "penalty_mode": "zero", "ridge": 0.0},
    "A_lam1n": {"family": "base", "penalty_mode": "const", "ridge": None},
    "B_enlarged": {"family": "enlarged", "penalty_mode": "n", "ridge": None},
    "AB_enlarged_unpen": {
        "family": "enlarged",
        "penalty_mode": "zero",
        "ridge": 0.0,
    },
}
# natural-panel budgets per arm (registered: A and B at 1x/4x; AB at 1x)
LEVER_NATURAL_BUDGETS: dict[str, tuple[float, ...]] = {
    "A_unpen": (1.0, 4.0),
    "A_lam1n": (1.0, 4.0),
    "B_enlarged": (1.0, 4.0),
    "AB_enlarged_unpen": (1.0,),
}
STACKING_ARMS = ("arm2_stage1_125", "two_stage", "two_stage_lever")
LEAN_A_BAR = 0.25
LEAN_A_MIN_WORLDS = 3
LEAN_B_BAR = 0.18
LEAN_C_BAR = 0.068
LEAN_D_BAR = 0.80
PIVOT_MOVE_BAR = 0.05
NULL_RELATIVE_TOLERANCE = 1e-8  # near-null eigenvalue cut (relative)
RANK_RELATIVE_TOLERANCE = 1e-10  # numerical-rank cut (relative)


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg4_reference() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Leg 4 persisted floor rows at budgets {1x, 4x} + decision."""
    rows_path = ROOT / "results" / "m4_d_dleg_floor" / "dleg_budget_rows.csv"
    decision_path = ROOT / "results" / "m4_d_dleg_floor" / "decision.json"
    if not rows_path.exists() or not decision_path.exists():
        raise RuntimeError(
            "Leg 4 persisted floor artifacts are required references and "
            f"were not found: {rows_path} / {decision_path}"
        )
    stored = pd.read_csv(rows_path)
    stored = stored[stored["budget"].isin(NATURAL_BUDGETS)].copy()
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    pooled = decision["part_4b"]["scaling"]["POOLED"]
    orc_1x = float(pooled["e_orc_true"]["medians_by_budget"]["1.0"])
    if abs(orc_1x - 0.3756) > 0.005:
        raise RuntimeError(
            f"Leg 4 persisted pooled 1x e_orc_true {orc_1x:.4f} is not the "
            "registered ~.376 comparator; reference battery is not the one "
            "registered"
        )
    return stored, decision


def _load_leg6_excited_reference() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Leg 6 persisted 1x excitation rows + decision (the .292 comparator)."""
    rows_path = (
        ROOT / "results" / "m4_d_excitation_floor" / "floor_budget_rows.csv"
    )
    decision_path = (
        ROOT / "results" / "m4_d_excitation_floor" / "decision.json"
    )
    if not rows_path.exists() or not decision_path.exists():
        raise RuntimeError(
            "Leg 6 persisted excitation artifacts are required references "
            f"and were not found: {rows_path} / {decision_path}"
        )
    stored = pd.read_csv(rows_path)
    stored = stored[
        (stored["arm"] == "excitation") & (stored["budget"] == 1.0)
    ].copy()
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    excited_1x = float(
        decision["floor"]["scaling_analysis"]["excitation"]["POOLED"][
            "e_orc_true"
        ]["medians_by_budget"]["1.0"]
    )
    if abs(excited_1x - 0.2921) > 0.005:
        raise RuntimeError(
            f"Leg 6 persisted excited 1x e_orc_true {excited_1x:.4f} is not "
            "the registered ~.292 comparator; reference battery is not the "
            "one registered"
        )
    return stored, decision


def _load_leg7_gap_reference() -> float:
    """Leg 7 persisted R=1 estimator-minus-oracle gap (the .136 comparator)."""
    path = ROOT / "results" / "m4_d_realization_averaging" / "decision.json"
    if not path.exists():
        raise RuntimeError(
            "Leg 7 persisted decision is a required reference and was not "
            f"found: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    gap = float(
        decision["pivot_profile"][
            "estimator_minus_oracle_gap_medians_by_R"
        ]["1"]
    )
    if abs(gap - 0.1364) > 0.005:
        raise RuntimeError(
            f"Leg 7 persisted R=1 gap {gap:.4f} is not the registered ~.136 "
            "comparator; reference battery is not the one registered"
        )
    return gap


# ---------------------------------------------------------------------------
# flexible-penalty logistic fit (V2 IRLS with the penalty family swapped)
# ---------------------------------------------------------------------------


def _fit_logistic_flex(
    design: np.ndarray,
    target: np.ndarray,
    *,
    penalty_mode: str,
    ridge: float,
    iterations: int,
) -> tuple[np.ndarray, int]:
    """V2's `_fit_logistic` IRLS loop with a configurable penalty matrix.

    penalty_mode:
      'n'     -- V2 semantics: penalty = ridge * len(y) * I, intercept
                 exempt (bit-identical path to the estimator's fitter);
      'const' -- lambda ~ 1/n de-biasing: penalty = ridge * I, intercept
                 exempt (the V2 penalty divided by len(y));
      'zero'  -- penalty -> 0 (unpenalized).
    Returns (coefficient, fallback_count). The fallback ladder is the
    documented instability guard: the oracle basis carries an exact
    constant column duplicating the intercept, so the unpenalized normal
    system is exactly singular. Per IRLS iteration: (1) np.linalg.solve;
    on LinAlgError or a non-finite update (2) np.linalg.lstsq (gelsd,
    minimum-norm); if its SVD iteration fails to converge -- observed on
    ill-conditioned 704-feature unpenalized enlarged systems -- (3)
    scipy.linalg.lstsq with lapack_driver='gelsy' (QR with column
    pivoting, no SVD iteration); as an ultimate guard (4) a trace-scaled
    jitter solve (system + 1e-12*tr(system)/p * I). All fallback rungs
    count toward the persisted per-fit total.
    """
    y = np.asarray(target, dtype=float).reshape(-1)
    width = design.shape[1]
    if penalty_mode == "n":
        penalty = ridge * len(y) * np.eye(width)
        penalty[0, 0] = 0.0
    elif penalty_mode == "const":
        penalty = ridge * np.eye(width)
        penalty[0, 0] = 0.0
    elif penalty_mode == "zero":
        penalty = np.zeros((width, width))
    else:  # pragma: no cover - registered modes only
        raise ValueError(f"unknown penalty_mode {penalty_mode}")
    coefficient = np.zeros(width)
    probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
    coefficient[0] = np.log(probability / (1.0 - probability))
    fallbacks = 0
    for _ in range(iterations):
        fitted = expit(np.clip(design @ coefficient, -20.0, 20.0))
        weight = np.clip(fitted * (1.0 - fitted), 1e-4, None)
        adjusted = design @ coefficient + (y - fitted) / weight
        system = design.T @ (weight[:, None] * design) + penalty
        rhs = design.T @ (weight * adjusted)
        updated = None
        try:
            updated = np.linalg.solve(system, rhs)
            if not np.all(np.isfinite(updated)):
                raise np.linalg.LinAlgError("non-finite update")
        except np.linalg.LinAlgError:
            fallbacks += 1
            try:
                updated = np.linalg.lstsq(system, rhs, rcond=None)[0]
                if not np.all(np.isfinite(updated)):
                    raise np.linalg.LinAlgError("non-finite lstsq")
            except np.linalg.LinAlgError:
                try:
                    updated = scipy_lstsq(
                        system, rhs, lapack_driver="gelsy"
                    )[0]
                    if not np.all(np.isfinite(updated)):
                        raise np.linalg.LinAlgError("non-finite gelsy")
                except (np.linalg.LinAlgError, ValueError):
                    jitter = (
                        1e-12 * float(np.trace(system)) / max(width, 1)
                    )
                    updated = np.linalg.solve(
                        system + jitter * np.eye(width), rhs
                    )
        if np.max(np.abs(updated - coefficient)) < 1e-10:
            coefficient = updated
            break
        coefficient = updated
    if not np.all(np.isfinite(coefficient)):
        raise RuntimeError("flex logistic fit produced non-finite coefficients")
    return coefficient, fallbacks


# ---------------------------------------------------------------------------
# enlarged hazard family (arm B): pairwise interactions of design columns
# ---------------------------------------------------------------------------


def _enlarged_design(
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
    model: str,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Base V2 hazard design + all pairwise products of non-intercept cols."""
    base, names = _hazard_design(rows, basis, model=model)
    nonintercept = base[:, 1:]
    count = nonintercept.shape[1]
    left, right = np.triu_indices(count, 1)
    interactions = nonintercept[:, left] * nonintercept[:, right]
    interaction_names = tuple(
        f"x_{names[1 + a]}*{names[1 + b]}"
        for a, b in zip(left, right, strict=True)
    )
    return np.hstack([base, interactions]), names + interaction_names


def _probe_rows(
    basis: np.ndarray,
    response: np.ndarray,
    history_gate: np.ndarray,
) -> dict[str, np.ndarray]:
    """Verbatim `_hazard_probability` probe-row construction."""
    events = len(response)
    categories = len(basis)
    return {
        "choice": np.zeros(events, dtype=int),
        "response_next": np.asarray(response, dtype=float),
        "history": np.column_stack(
            [np.asarray(history_gate, dtype=float), np.zeros(events)]
        ),
        "generated": np.zeros((events, categories), dtype=bool),
        "duration": np.zeros((events, categories)),
    }


def _enlarged_probability(
    coefficient: np.ndarray,
    model: str,
    basis: np.ndarray,
    response: np.ndarray,
    history_gate: np.ndarray,
) -> np.ndarray:
    rows = _probe_rows(basis, response, history_gate)
    design, _ = _enlarged_design(rows, basis, model)
    return expit(np.clip(design @ coefficient, -20.0, 20.0)).reshape(
        len(response),
        len(basis),
    )


def _enlarged_feedback_derivative(
    coefficient: np.ndarray,
    model: str,
    basis: np.ndarray,
    dimensions: int,
    *,
    epsilon: float = 0.05,
) -> np.ndarray:
    output = np.empty((len(basis), dimensions))
    for dimension in range(dimensions):
        positive = np.zeros((1, dimensions))
        negative = np.zeros((1, dimensions))
        positive[0, dimension] = epsilon
        negative[0, dimension] = -epsilon
        output[:, dimension] = (
            _enlarged_probability(
                coefficient, model, basis, positive, np.zeros(1)
            )[0]
            - _enlarged_probability(
                coefficient, model, basis, negative, np.zeros(1)
            )[0]
        ) / (2.0 * epsilon)
    return output


def _enlarged_creation_action(
    coefficient: np.ndarray,
    model: str,
    basis: np.ndarray,
    dimensions: int,
) -> np.ndarray:
    gate_probe = np.ones((1, dimensions))
    probes = np.vstack(
        [
            np.zeros((1, dimensions)),
            np.eye(dimensions),
            -np.eye(dimensions),
            gate_probe,
            gate_probe,
        ]
    )
    gate = np.zeros(len(probes))
    gate[-1] = 1.0
    return _enlarged_probability(coefficient, model, basis, probes, gate)


# ---------------------------------------------------------------------------
# lever fits (arms A / B / AB) at an arbitrary basis + forced route
# ---------------------------------------------------------------------------


def _lever_fit(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    model: str,
    arm: str,
    hazard_ridge: float,
    iterations: int,
) -> tuple[np.ndarray, tuple[str, ...], str, int]:
    spec = LEVER_SPECS[arm]
    ridge = hazard_ridge if spec["ridge"] is None else float(spec["ridge"])
    designs = []
    targets = []
    names: tuple[str, ...] = ()
    for rows, role in ((calibration, "calibration"), (selection, "selection")):
        if spec["family"] == "enlarged":
            design, names = _enlarged_design(rows, basis[role], model)
        else:
            design, names = _hazard_design(rows, basis[role], model=model)
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
    coefficient, fallbacks = _fit_logistic_flex(
        np.vstack(designs),
        np.concatenate(targets),
        penalty_mode=spec["penalty_mode"],
        ridge=ridge,
        iterations=iterations,
    )
    return coefficient, names, spec["family"], fallbacks


def _lever_derivative(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    model: str,
    arm: str,
    hazard_ridge: float,
    iterations: int,
    dimensions: int,
) -> tuple[np.ndarray, int, int]:
    """Returns (D, lstsq_fallback_count, n_features)."""
    coefficient, names, family, fallbacks = _lever_fit(
        calibration,
        selection,
        basis,
        model=model,
        arm=arm,
        hazard_ridge=hazard_ridge,
        iterations=iterations,
    )
    if family == "enlarged":
        derivative = _enlarged_feedback_derivative(
            coefficient, model, basis["evaluation"], dimensions
        )
    else:
        derivative = _feedback_derivative(
            coefficient, names, basis["evaluation"], dimensions
        )
    if not np.all(np.isfinite(derivative)):
        raise RuntimeError(f"lever {arm} produced a non-finite derivative")
    return derivative, fallbacks, len(names)


# ---------------------------------------------------------------------------
# arm C: orthogonal Procrustes alignment of the discovered frame
# ---------------------------------------------------------------------------


def _procrustes_align(
    v2_basis: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    roles = ("calibration", "selection", "evaluation")
    stacked_v2 = np.vstack([v2_basis[role] for role in roles])
    stacked_orc = np.vstack([oracle_basis[role] for role in roles])
    cross = stacked_v2.T @ stacked_orc
    left, _, right_t = np.linalg.svd(cross, full_matrices=False)
    w = left @ right_t  # (width_disc x width_orc), orthonormal columns
    aligned = {role: v2_basis[role] @ w for role in roles}
    residual = float(
        np.linalg.norm(stacked_v2 @ w - stacked_orc)
        / max(np.linalg.norm(stacked_orc), 1e-12)
    )
    ortho_gap = float(
        np.max(np.abs(w.T @ w - np.eye(w.shape[1])))
    )
    q_v2, _ = np.linalg.qr(stacked_v2)
    q_orc, _ = np.linalg.qr(stacked_orc)
    principal_cos = np.linalg.svd(
        q_v2.T @ q_orc, compute_uv=False
    )
    diagnostics = {
        "width_discovered": int(stacked_v2.shape[1]),
        "width_oracle": int(stacked_orc.shape[1]),
        "procrustes_relative_residual": residual,
        "w_orthonormality_gap": ortho_gap,
        "principal_cos_min": float(np.min(principal_cos)),
        "principal_cos_max": float(np.max(principal_cos)),
    }
    return aligned, diagnostics


# ---------------------------------------------------------------------------
# pivot instrument profile: information-operator conditioning (first look)
# ---------------------------------------------------------------------------


def _conditioning_row(
    keys: dict[str, Any],
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
    final_hazard: tuple[np.ndarray, tuple[str, ...]],
    model: str,
    dimensions: int,
    d_true: np.ndarray,
    *,
    epsilon: float = leg4.PROBE_EPSILON,
) -> dict[str, Any]:
    coefficient, _ = final_hazard
    designs = [
        _hazard_design(calibration, oracle_basis["calibration"], model=model)[0],
        _hazard_design(selection, oracle_basis["selection"], model=model)[0],
    ]
    design = np.vstack(designs)
    n_rows = design.shape[0]
    probability = expit(np.clip(design @ coefficient, -20.0, 20.0))
    weight = probability * (1.0 - probability)
    information = (design.T @ (weight[:, None] * design)) / n_rows
    eigenvalues, eigenvectors = np.linalg.eigh(information)
    lam_max = float(eigenvalues[-1])
    lam_min = float(eigenvalues[0])
    near_null = eigenvalues < NULL_RELATIVE_TOLERANCE * lam_max
    above_rank = eigenvalues > RANK_RELATIVE_TOLERANCE * lam_max
    positive = eigenvalues[~near_null]
    effective_min = float(positive[0]) if len(positive) else float("nan")
    # estimand Jacobian via the probe construction
    basis_eval = oracle_basis["evaluation"]
    categories = len(basis_eval)
    jacobian_blocks = []
    for dimension in range(dimensions):
        response_pos = np.zeros((1, dimensions))
        response_neg = np.zeros((1, dimensions))
        response_pos[0, dimension] = epsilon
        response_neg[0, dimension] = -epsilon
        design_pos, _ = _hazard_design(
            _probe_rows(basis_eval, response_pos, np.zeros(1)),
            basis_eval,
            model=model,
        )
        design_neg, _ = _hazard_design(
            _probe_rows(basis_eval, response_neg, np.zeros(1)),
            basis_eval,
            model=model,
        )
        prob_pos = expit(np.clip(design_pos @ coefficient, -20.0, 20.0))
        prob_neg = expit(np.clip(design_neg @ coefficient, -20.0, 20.0))
        weight_pos = (prob_pos * (1.0 - prob_pos))[:, None]
        weight_neg = (prob_neg * (1.0 - prob_neg))[:, None]
        jacobian_blocks.append(
            (weight_pos * design_pos - weight_neg * design_neg)
            / (2.0 * epsilon)
        )
    jacobian = np.vstack(jacobian_blocks)  # (categories*dims, p)
    pseudo = np.linalg.pinv(information, rcond=1e-12)
    variance_total = float(
        np.einsum("ip,pq,iq->", jacobian, pseudo, jacobian) / n_rows
    )
    variance_total = max(variance_total, 0.0)
    d_true_norm = float(np.linalg.norm(d_true))
    jacobian_norm_sq = float(np.sum(jacobian**2))
    if int(near_null.sum()):
        null_vectors = eigenvectors[:, near_null]
        null_fraction = float(
            np.sum((jacobian @ null_vectors) ** 2) / max(jacobian_norm_sq, 1e-300)
        )
    else:
        null_fraction = 0.0
    return {
        **keys,
        "model": model,
        "n_features": int(design.shape[1]),
        "n_fit_rows": int(n_rows),
        "lambda_max": lam_max,
        "lambda_min_raw": lam_min,
        "lambda_min_effective": effective_min,
        "condition_number_raw": float(lam_max / max(lam_min, 1e-300)),
        "condition_number_effective": float(
            lam_max / max(effective_min, 1e-300)
        ),
        "near_null_count": int(near_null.sum()),
        "numerical_rank": int(above_rank.sum()),
        "cr_sd_over_d_true": float(
            np.sqrt(variance_total / n_rows) / max(d_true_norm, 1e-300)
        ),
        "jacobian_null_fraction": null_fraction,
        "categories": int(categories),
    }


# ---------------------------------------------------------------------------
# per-world-rep floor battery (baselines, levers, alignment, excitation)
# ---------------------------------------------------------------------------


def _flex_identity_gates(
    context: dict[str, Any],
) -> dict[str, float]:
    """Bit-anchor the new fitters to V2 on the first non-degenerate row."""
    truth = context["truth"]
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    target_row = None
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            if float(np.linalg.norm(stack["D"])) >= leg4.FLIP_TOLERANCE:
                target_row = (view, author, stack)
                break
        if target_row:
            break
    if target_row is None:
        raise RuntimeError(
            f"no non-degenerate row found on {context['world']} rep "
            f"{context['repetition']} for the flex identity gate"
        )
    view, author, stack = target_row
    calibration, selection, _ = context["flat"][(view, author)]
    model = stack["selected_model"]
    basis = truth.oracle_basis
    # gate 1: flex in V2 mode == estimator._fit_logistic path bit-exactly
    designs = []
    targets = []
    for rows, role in ((calibration, "calibration"), (selection, "selection")):
        design, names = _hazard_design(rows, basis[role], model=model)
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
    stacked = np.vstack(designs)
    target = np.concatenate(targets)
    v2_coefficient = _fit_logistic(
        stacked, target, ridge=hazard_ridge, iterations=iterations
    )
    flex_coefficient, flex_fallbacks = _fit_logistic_flex(
        stacked,
        target,
        penalty_mode="n",
        ridge=hazard_ridge,
        iterations=iterations,
    )
    flex_gap = float(np.max(np.abs(v2_coefficient - flex_coefficient)))
    if flex_gap != 0.0 or flex_fallbacks != 0:
        raise RuntimeError(
            "flex-fit V2-mode identity gate FAILED on "
            f"{context['world']} rep {context['repetition']}: max gap "
            f"{flex_gap:.3e}, fallbacks {flex_fallbacks}"
        )
    # gate 2: enlarged probes with zero interactions == base probes
    d_base = _feedback_derivative(
        v2_coefficient, names, basis["evaluation"], dimensions
    )
    enlarged_rows = _probe_rows(
        basis["evaluation"], np.zeros((1, dimensions)), np.zeros(1)
    )
    enlarged_width = _enlarged_design(
        enlarged_rows, basis["evaluation"], model
    )[0].shape[1]
    padded = np.zeros(enlarged_width)
    padded[: len(v2_coefficient)] = v2_coefficient
    d_enlarged_zero = _enlarged_feedback_derivative(
        padded, model, basis["evaluation"], dimensions
    )
    enlarged_gap = float(np.max(np.abs(d_base - d_enlarged_zero)))
    if enlarged_gap > 1e-12:
        raise RuntimeError(
            "enlarged zero-interaction identity gate FAILED on "
            f"{context['world']} rep {context['repetition']}: max gap "
            f"{enlarged_gap:.3e} (ULP-level BLAS wobble tolerance 1e-12)"
        )
    return {
        "flex_v2_identity_max_gap": flex_gap,
        "enlarged_zero_identity_max_gap": enlarged_gap,
        "gate_row_model": model,
    }


def _floor_rows_for_world_rep(
    context: dict[str, Any],
    *,
    spec: M4ChartEcologySpec,
    leg4_stored: pd.DataFrame,
    leg6_stored: pd.DataFrame,
) -> dict[str, Any]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    v2_basis = context["v2_basis"]
    oracle_basis = truth.oracle_basis
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    true_d = {
        author: leg4._true_derivative(truth, author)
        for author in range(context["authors"])
    }
    keys_base = {"world": world, "repetition": repetition, "seed": seed}

    # ---- baseline V2 replay at {1x, 4x} + assert vs Leg 4 persisted ----
    baseline_rows, fit_gates = leg4._budget_rows_for_world_rep(
        context, spec=spec, budgets=NATURAL_BUDGETS
    )
    baseline_check = leg6._assert_passive_rows(
        baseline_rows,
        leg4_stored,
        world,
        repetition,
    )

    # ---- new-machinery identity gates ----
    flex_gates = _flex_identity_gates(context)

    # ---- row index / forced routes / degeneracy (Leg-4b semantics) ----
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

    # ---- natural panels: 1x from context, 4x regenerated (frozen law) ----
    events_by_budget: dict[
        tuple[float, str, int], tuple[dict, dict]
    ] = {}
    for view, author in row_index:
        calibration, selection, _ = context["flat"][(view, author)]
        events_by_budget[(1.0, view, author)] = (calibration, selection)
    for budget in NATURAL_BUDGETS:
        if budget == 1.0:
            continue
        spec_b = replace(spec, events=int(round(spec.events * budget)))
        observed_b, truth_b = generate_m4_chart_ecology_world(
            world=world, spec=spec_b, seed=seed
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
                events_by_budget[(budget, view, author)] = (
                    _flatten_events(calibration_panel, author),
                    _flatten_events(selection_panel, author),
                )

    # ---- excited panels at 1x (Leg 6 machinery) + baseline assert ----
    excited_1x = build_excited_observed(
        context["observed"],
        truth,
        spec,
        seed=seed,
        amplitude=AMPLITUDE,
    )
    excited_events: dict[tuple[str, int], tuple[dict, dict]] = {}
    for view in ("train", "test"):
        calibration_panel = getattr(excited_1x.ecology, f"{view}_calibration")
        selection_panel = getattr(excited_1x.ecology, f"{view}_selection")
        for author in range(context["authors"]):
            excited_events[(view, author)] = (
                _flatten_events(calibration_panel, author),
                _flatten_events(selection_panel, author),
            )
    excited_scale = excited_1x.ecology.design["response_excitation_scale"]

    excited_base_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        oracle_stack = context["oracle_stacks"][view][author]
        d_orc_1x = oracle_stack["D"]
        keys = {
            **keys_base,
            "author": author,
            "view": view,
            "budget": 1.0,
            "events": int(spec.events),
            "forced_route": forced_routes[(view, author)],
        }
        if degenerate[(view, author)]:
            excited_base_rows.append(
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
                    "d_norm_true": float(np.linalg.norm(true_d[author])),
                }
            )
            continue
        calibration, selection = excited_events[(view, author)]
        route = forced_routes[(view, author)]
        d_disc = leg4._forced_route_derivative(
            calibration,
            selection,
            v2_basis,
            model=route,
            hazard_ridge=hazard_ridge,
            logistic_iterations=iterations,
            dimensions=dimensions,
        )
        d_orc = leg4._forced_route_derivative(
            calibration,
            selection,
            oracle_basis,
            model=route,
            hazard_ridge=hazard_ridge,
            logistic_iterations=iterations,
            dimensions=dimensions,
        )
        d_true = true_d[author]
        excited_base_rows.append(
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
    excited_check = leg6._assert_passive_rows(
        excited_base_rows,
        leg6_stored,
        world,
        repetition,
    )

    # ---- lever rows (arms A / B / AB), natural {1x,4x} + excited 1x ----
    lever_rows: list[dict[str, Any]] = []

    def _lever_row(
        panel: str,
        budget: float,
        arm: str,
        view: str,
        author: int,
        calibration: dict[str, np.ndarray] | None,
        selection: dict[str, np.ndarray] | None,
    ) -> dict[str, Any]:
        keys = {
            **keys_base,
            "panel": panel,
            "budget": budget,
            "arm": arm,
            "author": author,
            "view": view,
            "forced_route": forced_routes[(view, author)],
        }
        if degenerate[(view, author)]:
            return {
                **keys,
                "degenerate_reference": True,
                "e_orc_true": np.nan,
                "d_norm_orc_lever": np.nan,
                "d_norm_true": float(np.linalg.norm(true_d[author])),
                "lstsq_fallbacks": 0,
                "n_features": 0,
            }
        derivative, fallbacks, n_features = _lever_derivative(
            calibration,
            selection,
            oracle_basis,
            model=forced_routes[(view, author)],
            arm=arm,
            hazard_ridge=hazard_ridge,
            iterations=iterations,
            dimensions=dimensions,
        )
        return {
            **keys,
            "degenerate_reference": False,
            "e_orc_true": leg3._relative_error(derivative, true_d[author]),
            "d_norm_orc_lever": float(np.linalg.norm(derivative)),
            "d_norm_true": float(np.linalg.norm(true_d[author])),
            "lstsq_fallbacks": fallbacks,
            "n_features": n_features,
        }

    for arm in LEVER_ARMS:
        for budget in LEVER_NATURAL_BUDGETS[arm]:
            for view, author in row_index:
                if degenerate[(view, author)]:
                    lever_rows.append(
                        _lever_row("natural", budget, arm, view, author, None, None)
                    )
                    continue
                calibration, selection = events_by_budget[
                    (budget, view, author)
                ]
                lever_rows.append(
                    _lever_row(
                        "natural", budget, arm, view, author,
                        calibration, selection,
                    )
                )
        for view, author in row_index:
            if degenerate[(view, author)]:
                lever_rows.append(
                    _lever_row("excited", 1.0, arm, view, author, None, None)
                )
                continue
            calibration, selection = excited_events[(view, author)]
            lever_rows.append(
                _lever_row(
                    "excited", 1.0, arm, view, author, calibration, selection
                )
            )

    # ---- arm C: Procrustes alignment + refit at the aligned frame (1x) ----
    aligned_basis, procrustes = _procrustes_align(v2_basis, oracle_basis)
    baseline_1x = {
        (row["view"], row["author"]): row
        for row in baseline_rows
        if row["budget"] == 1.0
    }
    alignment_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        keys = {
            **keys_base,
            "author": author,
            "view": view,
            "forced_route": forced_routes[(view, author)],
        }
        base_row = baseline_1x[(view, author)]
        if degenerate[(view, author)]:
            alignment_rows.append(
                {
                    **keys,
                    "degenerate_reference": True,
                    "e_d_true_v2": np.nan,
                    "e_orc_true": np.nan,
                    "gap_v2": np.nan,
                    "e_aligned_true": np.nan,
                    "gap_aligned": np.nan,
                    "e_d_paired_aligned": np.nan,
                    **procrustes,
                }
            )
            continue
        calibration, selection = events_by_budget[(1.0, view, author)]
        route = forced_routes[(view, author)]
        d_aligned = leg4._forced_route_derivative(
            calibration,
            selection,
            aligned_basis,
            model=route,
            hazard_ridge=hazard_ridge,
            logistic_iterations=iterations,
            dimensions=dimensions,
        )
        d_orc_1x = context["oracle_stacks"][view][author]["D"]
        e_aligned_true = leg3._relative_error(d_aligned, true_d[author])
        alignment_rows.append(
            {
                **keys,
                "degenerate_reference": False,
                "e_d_true_v2": float(base_row["e_d_true"]),
                "e_orc_true": float(base_row["e_orc_true"]),
                "gap_v2": float(
                    base_row["e_d_true"] - base_row["e_orc_true"]
                ),
                "e_aligned_true": e_aligned_true,
                "gap_aligned": float(
                    e_aligned_true - base_row["e_orc_true"]
                ),
                "e_d_paired_aligned": leg3._relative_error(
                    d_aligned, d_orc_1x
                ),
                **procrustes,
            }
        )

    # ---- conditioning profile (pivot instrument, 1x oracle basis) ----
    conditioning_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        keys = {
            **keys_base,
            "author": author,
            "view": view,
        }
        if degenerate[(view, author)]:
            conditioning_rows.append(
                {
                    **keys,
                    "degenerate_reference": True,
                    "model": forced_routes[(view, author)],
                    "n_features": 0,
                    "n_fit_rows": 0,
                    "lambda_max": np.nan,
                    "lambda_min_raw": np.nan,
                    "lambda_min_effective": np.nan,
                    "condition_number_raw": np.nan,
                    "condition_number_effective": np.nan,
                    "near_null_count": 0,
                    "numerical_rank": 0,
                    "cr_sd_over_d_true": np.nan,
                    "jacobian_null_fraction": np.nan,
                    "categories": 0,
                }
            )
            continue
        calibration, selection = events_by_budget[(1.0, view, author)]
        row = _conditioning_row(
            keys,
            calibration,
            selection,
            oracle_basis,
            context["oracle_stacks"][view][author]["final_hazard"],
            forced_routes[(view, author)],
            dimensions,
            true_d[author],
        )
        row["degenerate_reference"] = False
        conditioning_rows.append(row)

    return {
        "baseline_rows": baseline_rows,
        "baseline_check": baseline_check,
        "excited_base_rows": excited_base_rows,
        "excited_check": excited_check,
        "lever_rows": lever_rows,
        "alignment_rows": alignment_rows,
        "conditioning_rows": conditioning_rows,
        "fit_gates": {
            "world": world,
            "repetition": repetition,
            **fit_gates,
            **flex_gates,
        },
        "excited_scale": {
            "world": world,
            "repetition": repetition,
            "budget": 1.0,
            "scale_0": float(excited_scale[0]),
            "scale_1": float(excited_scale[1]),
            "amplitude": AMPLITUDE,
        },
    }


# ---------------------------------------------------------------------------
# floor chunks
# ---------------------------------------------------------------------------


def _expected_geometries_lookup(config: dict[str, Any]):
    archived_path = ROOT / "results" / "m4_chart_ecology" / "metrics.csv"
    archived = pd.read_csv(archived_path) if archived_path.exists() else None

    def lookup(world: str, repetition: int, seed: int):
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

    return lookup


def _run_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
) -> None:
    leg4_stored, _ = _load_leg4_reference()
    leg6_stored, _ = _load_leg6_excited_reference()
    _load_leg7_gap_reference()
    probe_gate = leg6._probe_design_gate()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    expected_for = _expected_geometries_lookup(config)

    bundles: dict[str, list[dict[str, Any]]] = {
        "baseline_rows": [],
        "excited_base_rows": [],
        "lever_rows": [],
        "alignment_rows": [],
        "conditioning_rows": [],
    }
    baseline_checks: list[dict[str, Any]] = []
    excited_checks: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    fit_gates: list[dict[str, Any]] = []
    excited_scales: list[dict[str, Any]] = []
    amp0_gates: list[dict[str, Any]] = []
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
            if repetition == 0:
                amp0_gates.append(
                    leg6._amplitude0_identity_gate(context, spec)
                )
            bundle = _floor_rows_for_world_rep(
                context,
                spec=spec,
                leg4_stored=leg4_stored,
                leg6_stored=leg6_stored,
            )
            for name in bundles:
                bundles[name].extend(bundle[name])
            baseline_checks.append(bundle["baseline_check"])
            excited_checks.append(bundle["excited_check"])
            fit_gates.append(bundle["fit_gates"])
            excited_scales.append(bundle["excited_scale"])

            lever_frame = pd.DataFrame(bundle["lever_rows"])
            usable = lever_frame[~lever_frame["degenerate_reference"]]
            natural_1x = usable[
                (usable["panel"] == "natural") & (usable["budget"] == 1.0)
            ]
            summary = {
                arm: round(
                    float(
                        natural_1x[natural_1x["arm"] == arm][
                            "e_orc_true"
                        ].median()
                    ),
                    4,
                )
                for arm in LEVER_ARMS
            }
            gap_aligned = float(
                pd.DataFrame(bundle["alignment_rows"])["gap_aligned"].median()
            )
            print(
                f"[leg8] rep={repetition} world={world} lever-1x-medians "
                f"{summary} gap_aligned~{gap_aligned:.4f} baseline-assert "
                f"{bundle['baseline_check']['max_abs_difference']:.2e} "
                f"excited-assert "
                f"{bundle['excited_check']['max_abs_difference']:.2e} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = f"rep{repetitions[0]}-{repetitions[-1]}"
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in bundles.items():
        pd.DataFrame(rows).to_csv(
            args.output / f"partial_{name}_{suffix}.csv", index=False
        )
    pd.DataFrame(baseline_checks).to_csv(
        args.output / f"partial_baseline_check_{suffix}.csv", index=False
    )
    pd.DataFrame(excited_checks).to_csv(
        args.output / f"partial_excited_check_{suffix}.csv", index=False
    )
    pd.DataFrame(validation_rows).to_csv(
        args.output / f"partial_v2_validation_{suffix}.csv", index=False
    )
    payload = {
        "probe_design_gate": probe_gate,
        "fit_gates": fit_gates,
        "excited_scales": excited_scales,
        "amplitude0_gates": amp0_gates,
        "repetitions": list(repetitions),
        "worlds": worlds,
    }
    with (args.output / f"partial_gates_{suffix}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"[chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# aggregation helpers (Leg-4b author-level median semantics)
# ---------------------------------------------------------------------------


def _author_level_stats(
    frame: pd.DataFrame,
    metric: str,
    group_cols: list[str],
) -> pd.DataFrame:
    usable = frame[~frame["degenerate_reference"]]
    return (
        usable.groupby(group_cols + ["world", "repetition", "author"])[metric]
        .mean()
        .reset_index()
    )


def _scoped_medians(
    author_frame: pd.DataFrame,
    metric: str,
    group_cols: list[str],
) -> dict[tuple, dict[str, Any]]:
    output: dict[tuple, dict[str, Any]] = {}
    for key, group in author_frame.groupby(group_cols):
        key_tuple = key if isinstance(key, tuple) else (key,)
        entry = {
            "pooled_median": float(group[metric].median()),
            "n_author_reps": int(len(group)),
            "per_world_median": {
                world: float(world_group[metric].median())
                for world, world_group in group.groupby("world")
            },
        }
        output[key_tuple] = entry
    return output


def _concat_partials(output: Path, stem: str) -> pd.DataFrame:
    paths = sorted(glob.glob(str(output / f"partial_{stem}_rep*.csv")))
    if not paths:
        raise RuntimeError(f"no partial CSVs found for {stem} under {output}")
    return pd.concat(
        [pd.read_csv(path) for path in paths], ignore_index=True
    )


def _load_gate_payloads(output: Path) -> list[dict[str, Any]]:
    paths = sorted(glob.glob(str(output / "partial_gates_rep*.json")))
    payloads = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as handle:
            payloads.append(json.load(handle))
    return payloads


def _law_tables(
    baseline: pd.DataFrame,
    excited_base: pd.DataFrame,
    levers: pd.DataFrame,
) -> dict[str, Any]:
    """Pooled/per-world author-level medians of e_orc_true for every arm."""
    pieces = []
    base_natural = baseline.copy()
    base_natural["panel"] = "natural"
    base_natural["arm"] = "baseline_v2"
    pieces.append(
        base_natural[
            [
                "panel",
                "arm",
                "budget",
                "world",
                "repetition",
                "author",
                "e_orc_true",
                "degenerate_reference",
            ]
        ]
    )
    excited = excited_base.copy()
    excited["panel"] = "excited"
    excited["arm"] = "baseline_v2"
    pieces.append(
        excited[
            [
                "panel",
                "arm",
                "budget",
                "world",
                "repetition",
                "author",
                "e_orc_true",
                "degenerate_reference",
            ]
        ]
    )
    pieces.append(
        levers[
            [
                "panel",
                "arm",
                "budget",
                "world",
                "repetition",
                "author",
                "e_orc_true",
                "degenerate_reference",
            ]
        ]
    )
    combined = pd.concat(pieces, ignore_index=True)
    author = _author_level_stats(
        combined, "e_orc_true", ["panel", "arm", "budget"]
    )
    scoped = _scoped_medians(author, "e_orc_true", ["panel", "arm", "budget"])
    table: dict[str, Any] = {}
    for (panel, arm, budget), entry in scoped.items():
        table.setdefault(panel, {}).setdefault(arm, {})[
            f"{float(budget):g}x"
        ] = entry
    return table


def _registered_composition(
    law_table: dict[str, Any],
    gap_pooled_v2: float,
    gap_pooled_aligned: float,
) -> dict[str, Any]:
    """The registered stack-selection rule (argmin, no discretion)."""
    candidates = {"baseline_v2": law_table["natural"]["baseline_v2"]["1x"][
        "pooled_median"
    ]}
    for arm in LEVER_ARMS:
        candidates[arm] = law_table["natural"][arm]["1x"]["pooled_median"]
    estimator_winner = min(candidates, key=lambda arm: candidates[arm])
    estimator_lever = (
        None if estimator_winner == "baseline_v2" else estimator_winner
    )
    frame = "aligned" if gap_pooled_aligned < gap_pooled_v2 else "v2"
    substituted = False
    if (
        estimator_lever is not None
        and LEVER_SPECS[estimator_lever]["family"] == "enlarged"
        and frame == "v2"
    ):
        frame = "aligned"
        substituted = True
    return {
        "estimator_candidates_pooled_natural_1x": candidates,
        "estimator_winner": estimator_winner,
        "estimator_lever": estimator_lever,
        "frame": frame,
        "gap_pooled_v2": gap_pooled_v2,
        "gap_pooled_aligned": gap_pooled_aligned,
        "compute_guard_substituted_aligned_frame": substituted,
        "rule": (
            "estimator lever = argmin pooled author-level median "
            "e_orc_true at natural 1x over {baseline_v2, A_unpen, A_lam1n, "
            "B_enlarged, AB_enlarged_unpen} (baseline winning = no lever); "
            "frame = aligned iff pooled gap_aligned < pooled gap_v2; "
            "pre-registered compute guard: enlarged estimator at the v2 "
            "frame substitutes the aligned frame"
        ),
    }


def _select_stack(args: argparse.Namespace, config: dict[str, Any]) -> None:
    baseline = _concat_partials(args.output, "baseline_rows")
    excited_base = _concat_partials(args.output, "excited_base_rows")
    levers = _concat_partials(args.output, "lever_rows")
    alignment = _concat_partials(args.output, "alignment_rows")
    law_table = _law_tables(
        baseline[baseline["budget"] == 1.0], excited_base, levers
    )
    align_author = _author_level_stats(alignment, "gap_aligned", [])
    align_v2_author = _author_level_stats(alignment, "gap_v2", [])
    gap_aligned = float(align_author["gap_aligned"].median())
    gap_v2 = float(align_v2_author["gap_v2"].median())
    composition = _registered_composition(law_table, gap_v2, gap_aligned)
    with (args.output / "stack_composition.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(composition, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(composition, indent=2, sort_keys=True))


# ---------------------------------------------------------------------------
# stack battery (arm D part 2): two-stage + selected lever
# ---------------------------------------------------------------------------


def _stack_rows_for_world_rep(
    context: dict[str, Any],
    *,
    composition: dict[str, Any],
    leg4_arm2: pd.DataFrame,
    leg5_rows: pd.DataFrame,
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
    truth = context["truth"]
    v2_basis = context["v2_basis"]
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    estimator_lever = composition["estimator_lever"]
    frame = composition["frame"]

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
    stage1_check = leg7._assert_rows_scaled(
        stage1_rows, leg4_arm2, world, repetition, label="stage-1"
    )

    # ---- two_stage (Leg 5 exactly) + persisted-row assert ----
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
        two_stage_rows,
        leg5_rows,
        world,
        repetition,
        label="two_stage",
    )

    # ---- two_stage_lever: stage-2 refit with the selected composition ----
    if frame == "aligned":
        stage2_basis, procrustes = _procrustes_align(
            v2_basis, truth.oracle_basis
        )
    else:
        stage2_basis, procrustes = v2_basis, {}
    lever_stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    total_fallbacks = 0
    identity_composition = estimator_lever is None and frame == "v2"
    for view in ("train", "test"):
        for author in range(context["authors"]):
            base = context["base_stacks"][view][author]
            stage2 = two_stage_stacks[view][author]
            route = stage2["selected_model"]
            if identity_composition:
                lever_stacks[view].append(stage2)
                continue
            calibration, selection, _ = context["flat"][(view, author)]
            if estimator_lever is None:
                # V2 estimator semantics at the aligned frame
                fit = leg3._fit_hazard_penalized(
                    [
                        (calibration, stage2_basis["calibration"]),
                        (selection, stage2_basis["selection"]),
                    ],
                    model=route,
                    ridge=hazard_ridge,
                    iterations=iterations,
                    extra_ridge=0.0,
                )
                derivative = _feedback_derivative(
                    fit[0], fit[1], stage2_basis["evaluation"], dimensions
                )
                action = _creation_action(
                    fit[0], fit[1], stage2_basis["evaluation"], dimensions
                )
            else:
                coefficient, names, family, fallbacks = _lever_fit(
                    calibration,
                    selection,
                    stage2_basis,
                    model=route,
                    arm=estimator_lever,
                    hazard_ridge=hazard_ridge,
                    iterations=iterations,
                )
                total_fallbacks += fallbacks
                if family == "enlarged":
                    derivative = _enlarged_feedback_derivative(
                        coefficient,
                        route,
                        stage2_basis["evaluation"],
                        dimensions,
                    )
                    action = _enlarged_creation_action(
                        coefficient,
                        route,
                        stage2_basis["evaluation"],
                        dimensions,
                    )
                else:
                    derivative = _feedback_derivative(
                        coefficient,
                        names,
                        stage2_basis["evaluation"],
                        dimensions,
                    )
                    action = _creation_action(
                        coefficient,
                        names,
                        stage2_basis["evaluation"],
                        dimensions,
                    )
            lever_stacks[view].append(
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

    arm_stacks = {
        "arm2_stage1_125": stage1_stacks,
        "two_stage": two_stage_stacks,
        "two_stage_lever": lever_stacks,
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
                "stack_frame": frame if arm == "two_stage_lever" else "v2",
                "stack_estimator": (
                    (estimator_lever or "v2_semantics")
                    if arm == "two_stage_lever"
                    else "v2_semantics"
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
        "identity_composition": identity_composition,
        "stage2_lstsq_fallbacks": total_fallbacks,
        **{f"procrustes_{k}": v for k, v in procrustes.items()},
    }
    return loop_rows, world_rows, stage1_check, two_stage_check, structure


def _run_stack_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
    composition: dict[str, Any] | None = None,
) -> None:
    if composition is None:
        composition_path = args.output / "stack_composition.json"
        if not composition_path.exists():
            raise RuntimeError(
                "stack_composition.json not found -- run --select-stack "
                "after the floor chunks before any stack chunk"
            )
        with composition_path.open("r", encoding="utf-8") as handle:
            composition = json.load(handle)
    leg4_arm2 = leg5._load_leg4_arm2()
    _, leg5_rows = leg7._load_leg5_reference()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    expected_for = _expected_geometries_lookup(config)

    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    stage1_checks: list[dict[str, Any]] = []
    two_stage_checks: list[dict[str, Any]] = []
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
            rows, worlds_out, s1, s2, structure = _stack_rows_for_world_rep(
                context,
                composition=composition,
                leg4_arm2=leg4_arm2,
                leg5_rows=leg5_rows,
            )
            loop_rows.extend(rows)
            world_rows.extend(worlds_out)
            stage1_checks.append(s1)
            two_stage_checks.append(s2)
            structures.append(structure)
            by_arm = {
                row["arm"]: round(row["loop_action_geometry"], 3)
                for row in worlds_out
            }
            print(
                f"[leg8-stack] rep={repetition} world={world} {by_arm} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = f"rep{repetitions[0]}-{repetitions[-1]}"
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(loop_rows).to_csv(
        args.output / f"partial_stack_per_loop_{suffix}.csv", index=False
    )
    pd.DataFrame(world_rows).to_csv(
        args.output / f"partial_stack_world_rep_{suffix}.csv", index=False
    )
    pd.DataFrame(stage1_checks).to_csv(
        args.output / f"partial_stack_stage1_check_{suffix}.csv", index=False
    )
    pd.DataFrame(two_stage_checks).to_csv(
        args.output / f"partial_stack_two_stage_check_{suffix}.csv",
        index=False,
    )
    with (args.output / f"partial_stack_structure_{suffix}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(
            {"structures": structures, "composition": composition},
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
    print(f"[stack chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# assembly -- refuse missing/duplicate cells, adjudicate from rows only
# ---------------------------------------------------------------------------


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


def _assemble(args: argparse.Namespace, config: dict[str, Any]) -> None:
    _, leg4_decision = _load_leg4_reference()
    _, leg6_decision = _load_leg6_excited_reference()
    leg7_gap = _load_leg7_gap_reference()
    leg5_two_stage, _ = leg7._load_leg5_reference()
    repetitions = int(config["repetitions"])
    worlds = list(LOOP_WORLDS)
    n_world_reps = len(worlds) * repetitions
    authors = 16
    n_author_views = n_world_reps * 2 * authors  # 1280

    baseline = _concat_partials(args.output, "baseline_rows")
    excited_base = _concat_partials(args.output, "excited_base_rows")
    levers = _concat_partials(args.output, "lever_rows")
    alignment = _concat_partials(args.output, "alignment_rows")
    conditioning = _concat_partials(args.output, "conditioning_rows")
    baseline_checks = _concat_partials(args.output, "baseline_check")
    excited_checks = _concat_partials(args.output, "excited_check")
    validation = _concat_partials(args.output, "v2_validation")
    stack_loops = _concat_partials(args.output, "stack_per_loop")
    stack_worlds = _concat_partials(args.output, "stack_world_rep")
    stack_stage1_checks = _concat_partials(args.output, "stack_stage1_check")
    stack_two_stage_checks = _concat_partials(
        args.output, "stack_two_stage_check"
    )
    gates = _load_gate_payloads(args.output)
    structure_paths = sorted(
        glob.glob(str(args.output / "partial_stack_structure_rep*.json"))
    )
    stack_structures = []
    composition: dict[str, Any] | None = None
    for path in structure_paths:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        stack_structures.extend(payload["structures"])
        composition = payload["composition"]
    if composition is None:
        raise RuntimeError("no stack structure partials found")

    # ---- refuse missing/duplicate cells ----
    _refuse_bad_cells(
        baseline,
        ["world", "repetition", "author", "view", "budget"],
        n_author_views * len(NATURAL_BUDGETS),
        "baseline rows",
    )
    _refuse_bad_cells(
        excited_base,
        ["world", "repetition", "author", "view"],
        n_author_views,
        "excited baseline rows",
    )
    expected_lever = n_author_views * (
        sum(len(LEVER_NATURAL_BUDGETS[arm]) for arm in LEVER_ARMS)
        + len(LEVER_ARMS)
    )
    _refuse_bad_cells(
        levers,
        ["panel", "arm", "budget", "world", "repetition", "author", "view"],
        expected_lever,
        "lever rows",
    )
    _refuse_bad_cells(
        alignment,
        ["world", "repetition", "author", "view"],
        n_author_views,
        "alignment rows",
    )
    _refuse_bad_cells(
        conditioning,
        ["world", "repetition", "author", "view"],
        n_author_views,
        "conditioning rows",
    )
    _refuse_bad_cells(
        stack_loops,
        ["arm", "world", "repetition", "author", "view"],
        len(STACKING_ARMS) * n_author_views,
        "stack loop rows",
    )
    _refuse_bad_cells(
        stack_worlds,
        ["arm", "world", "repetition"],
        len(STACKING_ARMS) * n_world_reps,
        "stack world-rep rows",
    )
    for label, frame in (
        ("baseline checks", baseline_checks),
        ("excited checks", excited_checks),
        ("stack stage1 checks", stack_stage1_checks),
        ("stack two_stage checks", stack_two_stage_checks),
    ):
        _refuse_bad_cells(frame, ["world", "repetition"], n_world_reps, label)

    # ---- faithfulness maxima ----
    baseline_max = float(baseline_checks["max_abs_difference"].max())
    excited_max = float(excited_checks["max_abs_difference"].max())
    if baseline_max > ROW_TOLERANCE or excited_max > ROW_TOLERANCE:
        raise RuntimeError(
            f"assembled replay diffs baseline {baseline_max:.3e} / excited "
            f"{excited_max:.3e}"
        )
    if not bool(baseline_checks["flags_equal"].all()) or not bool(
        excited_checks["flags_equal"].all()
    ):
        raise RuntimeError("assembled replay checks contain unequal flags")
    stage1_max = float(
        np.maximum(
            stack_stage1_checks["max_scaled_e_loop_difference"],
            stack_stage1_checks["max_scaled_e_d_atom_difference"],
        ).max()
    )
    two_stage_max = float(
        np.maximum(
            stack_two_stage_checks["max_scaled_e_loop_difference"],
            stack_two_stage_checks["max_scaled_e_d_atom_difference"],
        ).max()
    )
    if stage1_max > ROW_TOLERANCE or two_stage_max > ROW_TOLERANCE:
        raise RuntimeError(
            f"assembled stage1/two_stage reproduction diffs {stage1_max:.3e}"
            f"/{two_stage_max:.3e}"
        )
    stage1_flips = int(
        stack_loops[stack_loops["arm"] == "arm2_stage1_125"][
            "model_flip"
        ].sum()
    )
    if stage1_flips != leg5.STAGE1_EXPECTED_FLIPS:
        raise RuntimeError(
            f"stage-1 battery flips {stage1_flips} != "
            f"{leg5.STAGE1_EXPECTED_FLIPS}"
        )
    fit_gates = [gate for chunk in gates for gate in chunk["fit_gates"]]
    if len(fit_gates) != n_world_reps:
        raise RuntimeError(
            f"fit gates missing: {len(fit_gates)} != {n_world_reps}"
        )
    amp0_gates = [
        gate for chunk in gates for gate in chunk["amplitude0_gates"]
    ]

    # ---- law-level tables + registered composition reproduction ----
    law_table = _law_tables(
        baseline[baseline["budget"] == 1.0], excited_base, levers
    )
    baseline_4x = _law_tables(
        baseline[baseline["budget"] == 4.0],
        excited_base.iloc[0:0],
        levers.iloc[0:0],
    )
    law_table["natural"]["baseline_v2"]["4x"] = baseline_4x["natural"][
        "baseline_v2"
    ]["4x"]

    align_gap_author = _author_level_stats(alignment, "gap_aligned", [])
    align_gap_v2_author = _author_level_stats(alignment, "gap_v2", [])
    gap_pooled_aligned = float(align_gap_author["gap_aligned"].median())
    gap_pooled_v2 = float(align_gap_v2_author["gap_v2"].median())
    gap_per_world_aligned = {
        world: float(group["gap_aligned"].median())
        for world, group in align_gap_author.groupby("world")
    }
    gap_per_world_v2 = {
        world: float(group["gap_v2"].median())
        for world, group in align_gap_v2_author.groupby("world")
    }
    recomputed_composition = _registered_composition(
        law_table, gap_pooled_v2, gap_pooled_aligned
    )
    for key in ("estimator_lever", "frame"):
        if recomputed_composition[key] != composition[key]:
            raise RuntimeError(
                "stack composition drift between --select-stack and "
                f"assembly on '{key}': {composition[key]} vs "
                f"{recomputed_composition[key]}"
            )

    # ---- decision-level cross-checks vs persisted references ----
    baseline_pooled_1x = law_table["natural"]["baseline_v2"]["1x"][
        "pooled_median"
    ]
    persisted_1x = float(
        leg4_decision["part_4b"]["scaling"]["POOLED"]["e_orc_true"][
            "medians_by_budget"
        ]["1.0"]
    )
    if abs(baseline_pooled_1x - persisted_1x) > ROW_TOLERANCE:
        raise RuntimeError(
            f"pooled natural-1x baseline e_orc_true {baseline_pooled_1x} "
            f"diverges from Leg 4 persisted {persisted_1x}"
        )
    baseline_pooled_4x = law_table["natural"]["baseline_v2"]["4x"][
        "pooled_median"
    ]
    persisted_4x = float(
        leg4_decision["part_4b"]["scaling"]["POOLED"]["e_orc_true"][
            "medians_by_budget"
        ]["4.0"]
    )
    if abs(baseline_pooled_4x - persisted_4x) > ROW_TOLERANCE:
        raise RuntimeError(
            f"pooled natural-4x baseline e_orc_true {baseline_pooled_4x} "
            f"diverges from Leg 4 persisted {persisted_4x}"
        )
    excited_pooled_baseline = law_table["excited"]["baseline_v2"]["1x"][
        "pooled_median"
    ]
    persisted_excited = float(
        leg6_decision["floor"]["scaling_analysis"]["excitation"]["POOLED"][
            "e_orc_true"
        ]["medians_by_budget"]["1.0"]
    )
    if abs(excited_pooled_baseline - persisted_excited) > ROW_TOLERANCE:
        raise RuntimeError(
            f"pooled excited-1x baseline e_orc_true "
            f"{excited_pooled_baseline} diverges from Leg 6 persisted "
            f"{persisted_excited}"
        )
    if abs(gap_pooled_v2 - leg7_gap) > ROW_TOLERANCE:
        raise RuntimeError(
            f"pooled 1x gap_v2 {gap_pooled_v2} diverges from Leg 7 "
            f"persisted R=1 gap {leg7_gap}"
        )

    # ---- lean (a): de-biasing alone, per-world at natural 1x ----
    lean_a_counts = {}
    lean_a_worlds = {}
    for arm in ("A_unpen", "A_lam1n"):
        per_world = law_table["natural"][arm]["1x"]["per_world_median"]
        passing = {
            world: value
            for world, value in per_world.items()
            if value <= LEAN_A_BAR
        }
        lean_a_counts[arm] = len(passing)
        lean_a_worlds[arm] = passing
    lean_a_hold = bool(max(lean_a_counts.values()) >= LEAN_A_MIN_WORLDS)

    # ---- lean (b): A or B + excitation, pooled at excited 1x ----
    lean_b_candidates = {
        arm: law_table["excited"][arm]["1x"]["pooled_median"]
        for arm in ("A_unpen", "A_lam1n", "B_enlarged")
    }
    lean_b_winner = min(lean_b_candidates, key=lambda a: lean_b_candidates[a])
    lean_b_value = lean_b_candidates[lean_b_winner]
    lean_b_hold = bool(lean_b_value <= LEAN_B_BAR)

    # ---- lean (c): alignment closes >= half the gap ----
    lean_c_hold = bool(gap_pooled_aligned <= LEAN_C_BAR)
    gap_closed_fraction = float(
        (gap_pooled_v2 - gap_pooled_aligned) / gap_pooled_v2
    )

    # ---- pivot: A and B together move oracle-own-error < .05 ----
    lever_pooled_1x = {
        arm: law_table["natural"][arm]["1x"]["pooled_median"]
        for arm in LEVER_ARMS
    }
    best_lever = min(lever_pooled_1x, key=lambda a: lever_pooled_1x[a])
    pivot_move = float(baseline_pooled_1x - lever_pooled_1x[best_lever])
    pivot_triggered = bool(pivot_move < PIVOT_MOVE_BAR)

    # ---- lean (d): the full stack vs Leg 5's .7605 ----
    arm_summaries = {
        arm: leg4._arm_summary(stack_loops, stack_worlds, arm)
        for arm in STACKING_ARMS
    }
    lever_summary = arm_summaries["two_stage_lever"]
    pooled_lever = float(lever_summary["pooled_loop_geometry"])
    lean_d_hold = bool(pooled_lever >= LEAN_D_BAR)
    leg5_per_world = leg5_two_stage["per_world_loop_geometry"]
    per_world_gain = {
        world: float(
            lever_summary["per_world_loop_geometry"][world]
            - leg5_per_world[world]
        )
        for world in worlds
    }

    # ---- conditioning profile summary (pivot instrument, first look) ----
    conditioning_usable = conditioning[
        ~conditioning["degenerate_reference"]
    ].copy()
    conditioning_summary = {}
    for scope in [*worlds, "POOLED"]:
        scoped = (
            conditioning_usable
            if scope == "POOLED"
            else conditioning_usable[conditioning_usable["world"] == scope]
        )
        conditioning_summary[scope] = {
            "median_condition_number_raw": float(
                scoped["condition_number_raw"].median()
            ),
            "median_condition_number_effective": float(
                scoped["condition_number_effective"].median()
            ),
            "median_lambda_min_effective": float(
                scoped["lambda_min_effective"].median()
            ),
            "median_near_null_count": float(
                scoped["near_null_count"].median()
            ),
            "max_near_null_count": int(scoped["near_null_count"].max()),
            "median_cr_sd_over_d_true": float(
                scoped["cr_sd_over_d_true"].median()
            ),
            "iqr_cr_sd_over_d_true": [
                float(scoped["cr_sd_over_d_true"].quantile(0.25)),
                float(scoped["cr_sd_over_d_true"].quantile(0.75)),
            ],
            "median_jacobian_null_fraction": float(
                scoped["jacobian_null_fraction"].median()
            ),
            "max_jacobian_null_fraction": float(
                scoped["jacobian_null_fraction"].max()
            ),
            "n_rows": int(len(scoped)),
        }

    # ---- bias ledger ----
    def _entry(panel: str, arm: str, budget: str) -> float | None:
        try:
            return float(law_table[panel][arm][budget]["pooled_median"])
        except KeyError:
            return None

    law_ledger_rows = []
    for arm in ("baseline_v2", *LEVER_ARMS):
        row: dict[str, Any] = {"arm": arm}
        for panel, budget, label in (
            ("natural", "1x", "natural_1x"),
            ("natural", "4x", "natural_4x"),
            ("excited", "1x", "excited_1x"),
        ):
            value = _entry(panel, arm, budget)
            row[label] = value
            row[f"{label}_removed_vs_baseline_1x"] = (
                None
                if value is None
                else float(baseline_pooled_1x - value)
            )
        law_ledger_rows.append(row)
    bias_ledger = {
        "law_level_component": {
            "reference_baseline_natural_1x": baseline_pooled_1x,
            "rows": law_ledger_rows,
            "excitation_alone_leg6_persisted": persisted_excited,
        },
        "basis_mismatch_component": {
            "gap_v2_pooled_1x": gap_pooled_v2,
            "gap_aligned_pooled_1x": gap_pooled_aligned,
            "removed": float(gap_pooled_v2 - gap_pooled_aligned),
            "closed_fraction": gap_closed_fraction,
            "per_world_gap_v2": gap_per_world_v2,
            "per_world_gap_aligned": gap_per_world_aligned,
        },
        "loop_transport": {
            "leg5_two_stage_persisted": float(
                leg5_two_stage["pooled_loop_geometry"]
            ),
            "two_stage_lever_pooled": pooled_lever,
            "gain": float(
                pooled_lever
                - float(leg5_two_stage["pooled_loop_geometry"])
            ),
            "per_world_gain": per_world_gain,
        },
    }

    # ---- anomalies (honest) ----
    lever_usable = levers[~levers["degenerate_reference"]]
    fallback_totals = {
        arm: int(
            lever_usable[lever_usable["arm"] == arm]["lstsq_fallbacks"].sum()
        )
        for arm in LEVER_ARMS
    }
    anomalies: list[str] = []
    anomalies.append(
        "the oracle basis carries an exact constant column (its first "
        "column is all ones, duplicating the intercept), so every "
        "unpenalized normal system is exactly singular by construction; "
        "the registered guard (per-iteration lstsq minimum-norm fallback) "
        f"fired {fallback_totals['A_unpen']} times on A_unpen and "
        f"{fallback_totals['AB_enlarged_unpen']} times on AB_enlarged_unpen "
        "(persisted per fit); predictions are unaffected by the redundant "
        "direction"
    )
    if fallback_totals["A_lam1n"] or fallback_totals["B_enlarged"]:
        anomalies.append(
            "unexpected lstsq fallbacks on penalized arms: "
            f"A_lam1n {fallback_totals['A_lam1n']}, B_enlarged "
            f"{fallback_totals['B_enlarged']}"
        )
    if composition.get("compute_guard_substituted_aligned_frame"):
        anomalies.append(
            "the pre-registered compute guard fired: the enlarged estimator "
            "was selected with the v2 frame and the stack substituted the "
            "aligned frame"
        )
    identity_composition = all(
        structure["identity_composition"] for structure in stack_structures
    )

    # ---- outcome ----
    if pivot_triggered:
        outcome = (
            "PIVOT_WORLD_IDENTIFIABILITY_LIMIT_"
            "NEXT_INFORMATION_OPERATOR_CONDITIONING"
        )
    else:
        held = sum(
            [lean_a_hold, lean_b_hold, lean_c_hold, lean_d_hold]
        )
        outcome = f"BIAS_ANATOMY_LEVERS_MOVE_{held}_OF_4_LEANS_HOLD"

    # ---- persist final CSVs ----
    baseline.sort_values(
        ["world", "repetition", "author", "view", "budget"]
    ).to_csv(args.output / "baseline_replay_rows.csv", index=False)
    excited_base.sort_values(
        ["world", "repetition", "author", "view"]
    ).to_csv(args.output / "excited_baseline_rows.csv", index=False)
    levers.sort_values(
        ["panel", "arm", "budget", "world", "repetition", "author", "view"]
    ).to_csv(args.output / "lever_rows.csv", index=False)
    alignment.sort_values(
        ["world", "repetition", "author", "view"]
    ).to_csv(args.output / "alignment_rows.csv", index=False)
    conditioning.sort_values(
        ["world", "repetition", "author", "view"]
    ).to_csv(args.output / "conditioning_rows.csv", index=False)
    stack_loops.sort_values(
        ["arm", "world", "repetition", "author", "view"]
    ).to_csv(args.output / "stack_per_loop_metrics.csv", index=False)
    stack_worlds.sort_values(["arm", "world", "repetition"]).to_csv(
        args.output / "stack_world_rep_metrics.csv", index=False
    )
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    baseline_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "baseline_leg4_crosscheck.csv", index=False
    )
    excited_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "excited_leg6_crosscheck.csv", index=False
    )
    stack_stage1_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "stack_stage1_leg4_crosscheck.csv", index=False
    )
    stack_two_stage_checks.sort_values(["world", "repetition"]).to_csv(
        args.output / "stack_two_stage_leg5_crosscheck.csv", index=False
    )

    n_degenerate = int(
        baseline[baseline["budget"] == 1.0]["degenerate_reference"].sum()
    )
    decision = {
        "estimand_id": "SUICA_M4_D_LEG8_BIAS_ANATOMY",
        "tier": "EXPLORATORY",
        "config_seed": int(config["seed"]),
        "outcome": outcome,
        "design": {
            "arm_a": (
                "de-biased oracle refit at the oracle basis + oracle-forced "
                "route: A_unpen (penalty -> 0; per-iteration lstsq "
                "minimum-norm guard against the exact intercept-aliasing "
                "singularity, fallback counts persisted) and A_lam1n "
                "(penalty = hazard_ridge * I, intercept exempt -- the V2 "
                "penalty divided by len(y), an effective lambda ~ 1/n); "
                "e_orc_true at natural {1x, 4x}"
            ),
            "arm_b": (
                "one-step family enlargement at the oracle basis: append "
                "ALL pairwise interaction products (i<j, non-intercept) of "
                "the forced-route hazard design columns; V2 penalty "
                "semantics; e_orc_true at natural {1x, 4x}; companion "
                "AB_enlarged_unpen (enlargement + penalty -> 0) at 1x -- "
                "the registered pivot's 'A and B together' arm"
            ),
            "arm_c": (
                "DIAGNOSTIC subspace alignment: orthogonal Procrustes of "
                "the discovered frame onto the oracle frame (three roles "
                "stacked, one column-orthonormal W per world-rep); refit D "
                "at the aligned width-7 frame with V2 estimator semantics "
                "at the forced route; gap_aligned = e_aligned_true - "
                "e_orc_true at author level vs the ~.136 comparator; the "
                "oracle frame is consumed, so this lever is NOT "
                "operationally available"
            ),
            "arm_d": (
                "stacks: (1) every lever refit on the Leg-6 C3.3-excited 1x "
                "panels at the oracle basis (amplitude 1.0, scales "
                "persisted); (2) two_stage_lever full battery -- stage 1 = "
                "Leg 5 penalized route selection (lambda=.125, asserted), "
                "stage 2 = the registered-selected composition "
                f"(estimator={composition['estimator_lever']}, "
                f"frame={composition['frame']}), loop = D_lever @ G_v2 @ "
                "C_v2, vs Leg 5's persisted .7605"
            ),
            "registered_selection_rule": composition["rule"],
            "budgets": list(NATURAL_BUDGETS),
            "lever_arms": list(LEVER_ARMS),
            "lever_natural_budgets": {
                arm: list(values)
                for arm, values in LEVER_NATURAL_BUDGETS.items()
            },
        },
        "faithfulness": {
            "baseline_replay_vs_leg4": {
                "reference": "results/m4_d_dleg_floor/dleg_budget_rows.csv "
                "(budgets 1x/4x)",
                "world_reps_checked": int(len(baseline_checks)),
                "rows_compared": int(baseline_checks["rows_compared"].sum()),
                "max_abs_difference": baseline_max,
                "all_flags_equal": bool(baseline_checks["flags_equal"].all()),
                "pooled_1x_e_orc_true_equals_persisted": True,
                "pooled_4x_e_orc_true_equals_persisted": True,
            },
            "excited_replay_vs_leg6": {
                "reference": "results/m4_d_excitation_floor/"
                "floor_budget_rows.csv (excitation 1x rows)",
                "world_reps_checked": int(len(excited_checks)),
                "rows_compared": int(excited_checks["rows_compared"].sum()),
                "max_abs_difference": excited_max,
                "all_flags_equal": bool(excited_checks["flags_equal"].all()),
                "pooled_excited_1x_e_orc_true_equals_persisted": True,
            },
            "gap_v2_equals_leg7_r1_gap": {
                "mine": gap_pooled_v2,
                "leg7_persisted": leg7_gap,
                "abs_difference": float(abs(gap_pooled_v2 - leg7_gap)),
            },
            "flex_fit_identity_gates": {
                "world_reps_gated": len(fit_gates),
                "max_flex_v2_identity_gap": float(
                    max(g["flex_v2_identity_max_gap"] for g in fit_gates)
                ),
                "max_enlarged_zero_identity_gap": float(
                    max(
                        g["enlarged_zero_identity_max_gap"]
                        for g in fit_gates
                    )
                ),
            },
            "leg4_fit_gates": {
                "max_orc_refit_identity_gap_1x": float(
                    max(
                        g["orc_refit_identity_max_gap_1x"] for g in fit_gates
                    )
                ),
                "max_true_d_unit_check_gap": float(
                    max(g["true_d_unit_check_max_gap"] for g in fit_gates)
                ),
            },
            "amplitude0_identity_gates": {
                "worlds_gated": len(amp0_gates),
                "all_hold": bool(
                    all(g["identity_holds"] for g in amp0_gates)
                ),
            },
            "stage1_reproduction_vs_leg4": {
                "world_reps_checked": int(len(stack_stage1_checks)),
                "max_scaled_difference": stage1_max,
                "all_flags_equal": bool(
                    stack_stage1_checks["flags_equal"].all()
                ),
                "flips_total_equals_73": bool(
                    stage1_flips == leg5.STAGE1_EXPECTED_FLIPS
                ),
            },
            "two_stage_reproduction_vs_leg5": {
                "world_reps_checked": int(len(stack_two_stage_checks)),
                "max_scaled_difference": two_stage_max,
                "all_flags_equal": bool(
                    stack_two_stage_checks["flags_equal"].all()
                ),
            },
            "v2_validation_max_abs_difference": (
                float(validation["abs_difference"].max())
                if len(validation)
                else float("nan")
            ),
            "degenerate_reference_author_views": n_degenerate,
        },
        "law_level_table": law_table,
        "alignment": {
            "gap_pooled_v2": gap_pooled_v2,
            "gap_pooled_aligned": gap_pooled_aligned,
            "closed_fraction": gap_closed_fraction,
            "per_world_gap_v2": gap_per_world_v2,
            "per_world_gap_aligned": gap_per_world_aligned,
            "e_d_paired_aligned_pooled": float(
                _author_level_stats(alignment, "e_d_paired_aligned", [])[
                    "e_d_paired_aligned"
                ].median()
            ),
            "procrustes_relative_residual_range": [
                float(alignment["procrustes_relative_residual"].min()),
                float(alignment["procrustes_relative_residual"].max()),
            ],
            "principal_cos_min_range": [
                float(alignment["principal_cos_min"].min()),
                float(alignment["principal_cos_min"].max()),
            ],
            "label": "DIAGNOSTIC (oracle frame consumed; not operational)",
        },
        "stack_composition": composition,
        "stacking": {
            "arms": arm_summaries,
            "leg5_two_stage_persisted": {
                "pooled_loop_geometry": float(
                    leg5_two_stage["pooled_loop_geometry"]
                ),
                "per_world_loop_geometry": leg5_per_world,
            },
            "two_stage_lever_vs_leg5": {
                "pooled_gain": float(
                    pooled_lever
                    - float(leg5_two_stage["pooled_loop_geometry"])
                ),
                "per_world_gain": per_world_gain,
            },
            "identity_composition_all_world_reps": identity_composition,
            "stage2_lstsq_fallbacks_total": int(
                sum(
                    structure["stage2_lstsq_fallbacks"]
                    for structure in stack_structures
                )
            ),
        },
        "conditioning_profile": {
            "instrument": (
                "information-operator conditioning of the creation "
                "estimand at the oracle basis (first look): I_n = X^T "
                "diag(p(1-p)) X / n at the V2 forced-route fit; estimand "
                "Jacobian J from the probe construction; CR-style relative "
                "sd proxy sqrt(tr(J I_n^+ J^T)/n)/||D_true||; near-null cut "
                f"{NULL_RELATIVE_TOLERANCE:g} relative -- the intercept-"
                "aliasing null direction is structural and excluded from "
                "effective statistics"
            ),
            "per_scope": conditioning_summary,
        },
        "bias_ledger": bias_ledger,
        "lean_a": {
            "registered": (
                "de-biasing (A) alone cuts oracle-own-error from ~.376 to "
                "<= .25 at 1x in >= 3/5 worlds"
            ),
            "bar": LEAN_A_BAR,
            "min_worlds": LEAN_A_MIN_WORLDS,
            "worlds_passing_by_variant": lean_a_counts,
            "passing_worlds": lean_a_worlds,
            "per_world_A_unpen": law_table["natural"]["A_unpen"]["1x"][
                "per_world_median"
            ],
            "per_world_A_lam1n": law_table["natural"]["A_lam1n"]["1x"][
                "per_world_median"
            ],
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": (
                "A or B combined with excitation reaches pooled e_orc_true "
                "<= .18 at 1x"
            ),
            "bar": LEAN_B_BAR,
            "candidates_excited_1x": lean_b_candidates,
            "winner": lean_b_winner,
            "value": lean_b_value,
            "ab_excited_1x_reported": law_table["excited"][
                "AB_enlarged_unpen"
            ]["1x"]["pooled_median"],
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered": (
                "alignment (C) closes >= half the .136 gap (aligned gap "
                "<= .068)"
            ),
            "bar": LEAN_C_BAR,
            "gap_v2": gap_pooled_v2,
            "gap_aligned": gap_pooled_aligned,
            "closed_fraction": gap_closed_fraction,
            "hold": lean_c_hold,
        },
        "lean_d": {
            "registered": (
                "the full stack (D) lifts two-stage pooled loop geometry "
                "to >= .80"
            ),
            "bar": LEAN_D_BAR,
            "value": pooled_lever,
            "leg5_reference": float(
                leg5_two_stage["pooled_loop_geometry"]
            ),
            "hold": lean_d_hold,
        },
        "pivot_if": {
            "registered": (
                "A and B together move oracle-own-error < .05 -> the "
                "law-level bias is neither regularization nor one-step "
                "family enlargement; verdict WORLD-IDENTIFIABILITY LIMIT; "
                "next instrument = information-operator conditioning "
                "analysis of the creation estimand (profiled in-run above)"
            ),
            "baseline_pooled_natural_1x": baseline_pooled_1x,
            "lever_pooled_natural_1x": lever_pooled_1x,
            "best_lever": best_lever,
            "best_move": pivot_move,
            "bar": PIVOT_MOVE_BAR,
            "triggered": pivot_triggered,
            "declaration": (
                "WORLD_IDENTIFIABILITY_LIMIT"
                if pivot_triggered
                else "not triggered"
            ),
        },
        "anomalies": anomalies,
        "lstsq_fallback_totals": fallback_totals,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "estimator diagnostics throughout (oracle basis, oracle-forced "
            "routes, generator-law derivatives, and C3.3 generator-"
            "privileged excitation are consumed as references); the "
            "subspace-alignment lever consumes the oracle frame and is "
            "labeled DIAGNOSTIC -- nothing here is an operational rescue "
            "of chart transport or a reopened gate; the V1/V2 and C3.3 "
            "NO-GO decisions stand; no natural-text, personality, emotion, "
            "or clinical claim; EXPLORATORY tier under the 2026-08-01 "
            "open-exploration directive."
        ),
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "outcome": outcome,
                "baseline_1x": baseline_pooled_1x,
                "lever_pooled_natural_1x": lever_pooled_1x,
                "excited_pooled_1x": {
                    arm: law_table["excited"][arm]["1x"]["pooled_median"]
                    for arm in LEVER_ARMS
                },
                "gap_v2": gap_pooled_v2,
                "gap_aligned": gap_pooled_aligned,
                "stack_pooled": pooled_lever,
                "lean_a_hold": lean_a_hold,
                "lean_b_hold": lean_b_hold,
                "lean_c_hold": lean_c_hold,
                "lean_d_hold": lean_d_hold,
                "pivot_triggered": pivot_triggered,
                "pivot_best_move": pivot_move,
            },
            indent=2,
            sort_keys=True,
        )
    )


# ---------------------------------------------------------------------------
# entry point
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
        default=ROOT / "results" / "m4_d_bias_anatomy",
    )
    parser.add_argument("--chunk-start", type=int, default=None)
    parser.add_argument("--chunk-stop", type=int, default=None)
    parser.add_argument("--select-stack", action="store_true")
    parser.add_argument("--stack-chunk-start", type=int, default=None)
    parser.add_argument("--stack-chunk-stop", type=int, default=None)
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    started = time.time()
    config = leg3._load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.smoke:
        args.output = ROOT / "results" / "_smoke_m4_d_bias_anatomy"
        worlds = list(LOOP_WORLDS)[:2]
        _run_chunk(args, config, spec, (0,), worlds)
        smoke_composition = {
            "estimator_lever": "A_unpen",
            "frame": "aligned",
            "rule": "smoke-forced composition (not the registered rule)",
            "compute_guard_substituted_aligned_frame": False,
        }
        _run_stack_chunk(
            args, config, spec, (0,), worlds, composition=smoke_composition
        )
        print(
            f"[smoke done] partials under {args.output} "
            f"({time.time() - started:.0f}s)",
            flush=True,
        )
        return
    if args.select_stack:
        _select_stack(args, config)
        print(f"[selected] total {time.time() - started:.0f}s", flush=True)
        return
    if args.assemble:
        _assemble(args, config)
        print(f"[assembled] total {time.time() - started:.0f}s", flush=True)
        return
    if args.stack_chunk_start is not None or args.stack_chunk_stop is not None:
        if args.stack_chunk_start is None or args.stack_chunk_stop is None:
            raise SystemExit(
                "provide both --stack-chunk-start and --stack-chunk-stop"
            )
        repetitions = tuple(
            range(args.stack_chunk_start, args.stack_chunk_stop)
        )
        _run_stack_chunk(args, config, spec, repetitions, list(LOOP_WORLDS))
        print(f"[done] total {time.time() - started:.0f}s", flush=True)
        return
    if args.chunk_start is None or args.chunk_stop is None:
        raise SystemExit(
            "provide --chunk-start/--chunk-stop for a floor chunk, "
            "--select-stack, --stack-chunk-start/--stack-chunk-stop, "
            "--assemble, or --smoke"
        )
    repetitions = tuple(range(args.chunk_start, args.chunk_stop))
    _run_chunk(args, config, spec, repetitions, list(LOOP_WORLDS))
    print(f"[done] total {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
