#!/usr/bin/env python3
"""M4-D Leg 3: overspan-controlled route identification on the M4-C.2 V2 wall.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 3 -- overspan-controlled route identification", before this run).

Target (Leg 1 pivot profile): the composite-loop wall is estimator-side --
discovered charts OVERSPAN the oracle frame (widths 12-13 vs 7), inflating the
hazard feedback parameterization, degrading the D leg and flipping hazard
model selection to `return` (D = 0, e_loop = 1). Existence proof that low
overspan passes: history_gated (width 8, 5 flips, loop geometry .915).

Arms (independent modifications of the baseline; never stacked; every arm
modifies the DISCOVERED-side estimation only -- the oracle reference fits are
frozen V2 semantics and shared bit-for-bit across arms):

- Arm 0 (arm0_v2): exact V2 replay. Must reproduce the archived numbers
  (pooled loop geometry .6519, 196 D-zero model-selection flips) and is
  asserted per world-repetition against the archived
  results/m4_chart_ecology/metrics.csv values (the same values Leg 1's
  v2_validation.csv certified at 1.1e-16) BEFORE the treatment arms run, and
  per-row against Leg 1's per_loop_metrics.csv after the battery.
- Arm 1 (arm1_width): chart-frame rank selection by the negative-spectrum
  noise-floor rule of suica_core/m4_relation_bridge.spectral_profile
  (eigenvalue > 2x |most negative|), applied to the chart estimation step.
  Implementation note (stated in the report): the V2 whitening consumes the
  covariance of source-AVERAGED chart features, which is PSD by construction
  and has no negative spectrum; the literal bridge object is therefore built
  from the symmetrized CROSS-SOURCE squared-distance relation of the
  reference-calibration chart features (R[i,j] = .5(||x_i^0 - x_j^1||^2 +
  ||x_j^0 - x_i^1||^2)), whose doubly centered Gram is indefinite exactly
  because the two sources disagree -- the negative spectrum IS the chart
  estimation noise. The selected rank is applied as `maximum_rank` to the
  frozen whitening (it can only shrink the V2 frame, never grow it);
  everything else identical to V2.
- Arm 2 (arm2_penalized): keep V2 charts; add an extra ridge (single global
  lambda) on the hazard feedback_*/gate_* coefficients in every hazard fit on
  the discovered side (candidates and final refit). Lambda is chosen by
  out-of-fold likelihood (calibration-fit -> selection-panel logloss of the
  penalized feedback/gate candidates) on discovery repetitions {0, 1} only,
  before the battery; the V2 selection rule (held-out logloss +
  complexity_penalty x n_parameters) is unchanged.
- Arm 3 (arm3_oof): keep V2 charts and fits; select the hazard route by a
  symmetric two-fold out-of-fold predictive score, .5 x (logloss(selection |
  fit on calibration) + logloss(calibration | fit on selection)), with NO
  parameter-count penalty (out-of-fold error absorbs complexity); the V2
  rule's calibration->selection loss is reused as one fold. Final refit on
  the combined panels is V2's own.

Measured per arm x world x repetition x author x view: D-zero model-selection
flip vs the oracle route (Leg 1's definition: exactly one side of the
discovered/oracle pair has a zero D leg), route-name mismatch, loop error
e_loop, chart-free D-leg error e_d_atom, chart-free GC-composite error, the
two chart-free leg-swap errors, and chart width. Loop transport geometry is
V2's own statistic (_geometry on author-mean kernels, train/test averaged).

Registered leans: (a) flips halved in the best single arm (196 -> <= 98);
(b) per-world mean loop geometry >= .75 in >= 3 of 5 worlds (currently 1/5);
(c) mediation: within-(world x rep) Spearman between D-leg error improvement
and loop-error improvement (vs Arm 0), median across cells >= .5 -- the plan
registers (c) on the width arm; the orchestrator restatement says winning
arm; both are computed and both adjudications are recorded. Pivot-if: flips
drop but pooled geometry stays < .70 -- then the D-leg error is not
selection-driven and the third layer is profiled.
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
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scipy.special import expit  # noqa: E402

from suica_core.m4_chart_ecology_audit import _geometry  # noqa: E402
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    HAZARD_MODELS,
    _choice_action,
    _choice_delta,
    _choice_logloss,
    _creation_action,
    _feedback_derivative,
    _fit_choice,
    _fit_hazard_candidate,
    _fit_response,
    _flatten_events,
    _hazard_design,
    _hazard_logloss,
    _query_masks,
    _response_loss,
    build_m4_discovered_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    _candidate_features,
    _fit_candidate,
    _panel_prototypes,
    fit_m4_condition_chart,
)
from suica_core.m4_relation_bridge import (  # noqa: E402
    gram_from_relation,
    spectral_profile,
)

LOOP_WORLDS = (
    "endogenous_source_partition_matched",
    "endogenous_creation_expansion",
    "source_rotated_feedback",
    "history_gated_ecology",
    "selection_creation_compensation",
)
ARMS = ("arm0_v2", "arm1_width", "arm2_penalized", "arm3_oof")
DISCOVERY_REPS = (0, 1)
LAMBDA_GRID = (0.005, 0.025, 0.125, 0.625)
EPS = 1e-12
FLIP_TOLERANCE = 1e-10


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _world_seed(
    base: int,
    repetition: int,
    world: str,
    world_index: int,
) -> int:
    """Exact copy of the V2 runner seed rule (world_index in the full list)."""
    matched_groups = {
        "linear_exogenous_selection": 101,
        "endogenous_source_partition_matched": 101,
        "fast_return_equal_marginal": 211,
        "slow_hysteresis_equal_marginal": 211,
    }
    offset = matched_groups.get(world, 1_009 + world_index * 10_003)
    return int(base + repetition * 1_000_003 + offset)


def _relative_error(estimate: np.ndarray, reference: np.ndarray) -> float:
    return float(
        np.linalg.norm(estimate - reference)
        / max(np.linalg.norm(reference), EPS)
    )


def _pooled_spearman(frame: pd.DataFrame, x: str, y: str) -> float:
    if len(frame) < 3:
        return float("nan")
    value = spearmanr(frame[x], frame[y]).statistic
    return float(value) if np.isfinite(value) else float("nan")


# ---------------------------------------------------------------------------
# hazard fitting variants
# ---------------------------------------------------------------------------


def _fit_logistic_penalized(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge: float,
    iterations: int,
    extra_ridge: float,
    extra_mask: np.ndarray,
) -> np.ndarray:
    """V2's _fit_logistic with an extra ridge on masked coefficients.

    With extra_ridge = 0 the penalty matrix is bit-identical to V2's, so the
    same IRLS path is followed exactly.
    """
    y = np.asarray(target, dtype=float).reshape(-1)
    penalty = ridge * len(y) * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    if extra_ridge > 0.0:
        index = np.flatnonzero(extra_mask)
        penalty[index, index] += extra_ridge * len(y)
    coefficient = np.zeros(design.shape[1])
    probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
    coefficient[0] = np.log(probability / (1.0 - probability))
    for _ in range(iterations):
        fitted = expit(np.clip(design @ coefficient, -20.0, 20.0))
        weight = np.clip(fitted * (1.0 - fitted), 1e-4, None)
        adjusted = design @ coefficient + (y - fitted) / weight
        system = design.T @ (weight[:, None] * design) + penalty
        updated = np.linalg.solve(system, design.T @ (weight * adjusted))
        if np.max(np.abs(updated - coefficient)) < 1e-10:
            coefficient = updated
            break
        coefficient = updated
    return coefficient


def _fit_hazard_penalized(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    model: str,
    ridge: float,
    iterations: int,
    extra_ridge: float,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Hazard candidate fit with extra ridge on feedback_*/gate_* coords."""
    designs = []
    targets = []
    names: tuple[str, ...] | None = None
    for rows, basis in datasets:
        design, current_names = _hazard_design(rows, basis, model=model)
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
        names = current_names
    names = names or ()
    mask = np.asarray(
        [
            name.startswith("feedback_") or name.startswith("gate_")
            for name in names
        ],
        dtype=bool,
    )
    coefficient = _fit_logistic_penalized(
        np.vstack(designs),
        np.concatenate(targets),
        ridge=ridge,
        iterations=iterations,
        extra_ridge=extra_ridge,
        extra_mask=mask,
    )
    return coefficient, names


# ---------------------------------------------------------------------------
# per-author fitting stacks
# ---------------------------------------------------------------------------


def _fit_v2_stack(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    evaluation: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    ridge_grid: tuple[float, ...],
    hazard_ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
    query_masks: np.ndarray,
) -> dict[str, Any]:
    """Verbatim V2 `_one_author` fitting flow (as replayed in Leg 1).

    Returns the loop legs plus the intermediate candidate fits and losses the
    treatment arms need. The numerical path up to the returned kernels is
    identical to Leg 1's `_fit_author_legs`.
    """
    calibration_pair = (calibration, basis["calibration"])
    selection_pair = (selection, basis["selection"])
    combined = [calibration_pair, selection_pair]

    choice_candidates = [
        _fit_choice([calibration_pair], ridge=ridge) for ridge in ridge_grid
    ]
    choice_losses = [
        _choice_logloss(coefficient, selection, basis["selection"])
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
        _fit_response([calibration_pair], ridge=ridge) for ridge in ridge_grid
    ]
    response_losses = [
        _response_loss(coefficient, selection, basis["selection"])
        for coefficient in response_candidates
    ]
    minimum_response_loss = float(np.min(response_losses))
    response_ridge = next(
        ridge
        for ridge, loss in zip(ridge_grid, response_losses, strict=True)
        if loss <= minimum_response_loss + 1e-10
    )
    response_coefficient = _fit_response(combined, ridge=response_ridge)

    candidate_fits: dict[str, tuple[np.ndarray, tuple[str, ...]]] = {}
    candidate_losses: dict[str, float] = {}
    hazard_scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        fit = _fit_hazard_candidate(
            [calibration_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
        )
        design, _ = _hazard_design(selection, basis["selection"], model=model)
        loss = _hazard_logloss(fit[0], design, selection["generated_next"])
        candidate_fits[model] = fit
        candidate_losses[model] = loss
        hazard_scores[model] = loss + complexity_penalty * len(fit[1])
    minimum_hazard_score = min(hazard_scores.values())
    selected_model = next(
        model
        for model in HAZARD_MODELS
        if hazard_scores[model] <= minimum_hazard_score + 1e-10
    )
    hazard_coefficient, hazard_names = _fit_hazard_candidate(
        combined,
        model=selected_model,
        ridge=hazard_ridge,
        iterations=logistic_iterations,
    )

    eval_basis = basis["evaluation"]
    dimensions = evaluation["response_next"].shape[1]
    width = eval_basis.shape[1]
    derivative = _feedback_derivative(
        hazard_coefficient,
        hazard_names,
        eval_basis,
        dimensions,
    )
    response_choice = response_coefficient[dimensions : dimensions + width].T
    choice_delta = _choice_delta(choice_coefficient, eval_basis)
    return {
        "C": choice_delta,
        "G": response_choice,
        "D": derivative,
        "loop": derivative @ response_choice @ choice_delta,
        "choice_action": _choice_action(
            choice_coefficient,
            eval_basis,
            query_masks,
        ),
        "creation_action": _creation_action(
            hazard_coefficient,
            hazard_names,
            eval_basis,
            dimensions,
        ),
        "selected_model": selected_model,
        "choice_coefficient": choice_coefficient,
        "response_coefficient": response_coefficient,
        "candidate_fits": candidate_fits,
        "candidate_losses": candidate_losses,
        "hazard_scores": hazard_scores,
        "final_hazard": (hazard_coefficient, hazard_names),
    }


def _derived_from_hazard(
    base_stack: dict[str, Any],
    hazard_fit: tuple[np.ndarray, tuple[str, ...]],
    selected_model: str,
    evaluation: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Arm stack sharing C/G/choice with the base; only the D leg differs."""
    eval_basis = basis["evaluation"]
    dimensions = evaluation["response_next"].shape[1]
    coefficient, names = hazard_fit
    derivative = _feedback_derivative(
        coefficient,
        names,
        eval_basis,
        dimensions,
    )
    return {
        "C": base_stack["C"],
        "G": base_stack["G"],
        "D": derivative,
        "loop": derivative @ base_stack["G"] @ base_stack["C"],
        "choice_action": base_stack["choice_action"],
        "creation_action": _creation_action(
            coefficient,
            names,
            eval_basis,
            dimensions,
        ),
        "selected_model": selected_model,
    }


def _arm2_stack(
    base_stack: dict[str, Any],
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    evaluation: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    hazard_ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
    extra_ridge: float,
) -> dict[str, Any]:
    """Penalized-hazard arm: extra ridge on feedback/gate coords everywhere."""
    calibration_pair = (calibration, basis["calibration"])
    selection_pair = (selection, basis["selection"])
    scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        if model in ("base", "return"):
            scores[model] = base_stack["hazard_scores"][model]
            continue
        fit = _fit_hazard_penalized(
            [calibration_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
            extra_ridge=extra_ridge,
        )
        design, _ = _hazard_design(selection, basis["selection"], model=model)
        loss = _hazard_logloss(fit[0], design, selection["generated_next"])
        scores[model] = loss + complexity_penalty * len(fit[1])
    minimum = min(scores.values())
    selected = next(
        model for model in HAZARD_MODELS if scores[model] <= minimum + 1e-10
    )
    if selected == base_stack["selected_model"] and selected in (
        "base",
        "return",
    ):
        final = base_stack["final_hazard"]
    else:
        final = _fit_hazard_penalized(
            [calibration_pair, selection_pair],
            model=selected,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
            extra_ridge=extra_ridge,
        )
    return _derived_from_hazard(base_stack, final, selected, evaluation, basis)


def _arm3_stack(
    base_stack: dict[str, Any],
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    evaluation: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    hazard_ridge: float,
    logistic_iterations: int,
) -> dict[str, Any]:
    """Out-of-fold route selection arm: symmetric two-fold predictive score."""
    calibration_pair = (calibration, basis["calibration"])
    selection_pair = (selection, basis["selection"])
    scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        reverse_fit = _fit_hazard_candidate(
            [selection_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
        )
        design, _ = _hazard_design(
            calibration,
            basis["calibration"],
            model=model,
        )
        reverse_loss = _hazard_logloss(
            reverse_fit[0],
            design,
            calibration["generated_next"],
        )
        scores[model] = 0.5 * (
            base_stack["candidate_losses"][model] + reverse_loss
        )
    minimum = min(scores.values())
    selected = next(
        model for model in HAZARD_MODELS if scores[model] <= minimum + 1e-10
    )
    if selected == base_stack["selected_model"]:
        final = base_stack["final_hazard"]
    else:
        final = _fit_hazard_candidate(
            [calibration_pair, selection_pair],
            model=selected,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
        )
    return _derived_from_hazard(base_stack, final, selected, evaluation, basis)


# ---------------------------------------------------------------------------
# arm 1 chart-frame rank rule
# ---------------------------------------------------------------------------


def _bridge_chart_rank(
    observed: Any,
    chart: Any,
    *,
    rank_cap: int,
) -> dict[str, Any]:
    """Negative-spectrum noise-floor rank for the chart frame (arm 1).

    The bridge rule needs an indefinite Gram; the symmetrized cross-source
    squared-distance relation of the reference-calibration chart features
    supplies it (its negative spectrum is the cross-source disagreement,
    i.e. the chart estimation noise the whitened frame should not span).
    """
    parameters = chart.selected_parameters
    candidate = _fit_candidate(
        observed.condition.reference_calibration,
        family=chart.selected_family,
        dimensions=int(parameters["dimensions"]),
        neighbors=int(parameters["neighbors"]),
        landmarks=int(parameters["landmarks"]),
    )
    prototypes = _panel_prototypes(observed.condition.reference_calibration)
    features = _candidate_features(candidate, prototypes)
    cross = cdist(features[0], features[1], "sqeuclidean")
    relation = 0.5 * (cross + cross.T)
    profile = spectral_profile(
        gram_from_relation(relation),
        rank_cap=rank_cap,
        floor_multiplier=2.0,
    )
    return {
        "selected_rank": max(int(profile["selected_rank"]), 1),
        "noise_floor": float(profile["noise_floor"]),
        "spectral_margin": float(profile["spectral_margin"]),
    }


# ---------------------------------------------------------------------------
# battery
# ---------------------------------------------------------------------------


def _loop_row(
    keys: dict[str, Any],
    arm: str,
    stack: dict[str, Any],
    oracle: dict[str, Any],
) -> dict[str, Any]:
    d_norm_disc = float(np.linalg.norm(stack["D"]))
    d_norm_oracle = float(np.linalg.norm(oracle["D"]))
    loop_norm_oracle = float(np.linalg.norm(oracle["loop"]))
    gc_disc = stack["G"] @ stack["C"]
    gc_oracle = oracle["G"] @ oracle["C"]
    return {
        **keys,
        "arm": arm,
        "width_discovered": int(stack["C"].shape[0]),
        "width_oracle": int(oracle["C"].shape[0]),
        "selected_model_arm": stack["selected_model"],
        "selected_model_oracle": oracle["selected_model"],
        "model_flip": bool(
            (d_norm_disc < FLIP_TOLERANCE) != (d_norm_oracle < FLIP_TOLERANCE)
        ),
        "route_mismatch": bool(
            stack["selected_model"] != oracle["selected_model"]
        ),
        "e_loop": _relative_error(stack["loop"], oracle["loop"]),
        "e_d_atom": _relative_error(stack["D"], oracle["D"]),
        "e_gc_composite": _relative_error(gc_disc, gc_oracle),
        "e_swap_d_oracle": _relative_error(
            oracle["D"] @ gc_disc,
            oracle["loop"],
        ),
        "e_swap_gc_oracle": _relative_error(
            stack["D"] @ gc_oracle,
            oracle["loop"],
        ),
        "d_norm_discovered": d_norm_disc,
        "d_norm_oracle": d_norm_oracle,
        "loop_norm_discovered": float(np.linalg.norm(stack["loop"])),
        "loop_norm_oracle": loop_norm_oracle,
        "degenerate": bool(
            loop_norm_oracle < FLIP_TOLERANCE
            or d_norm_disc < FLIP_TOLERANCE
            or d_norm_oracle < FLIP_TOLERANCE
        ),
    }


def _arm_geometries(
    stacks: dict[str, list[dict[str, Any]]],
    oracle: dict[str, list[dict[str, Any]]],
) -> dict[str, float]:
    output = {}
    for label, name in (
        ("loop_action_geometry", "loop"),
        ("choice_action_geometry", "choice_action"),
        ("creation_action_geometry", "creation_action"),
    ):
        disc = 0.5 * (
            np.stack([fit[name] for fit in stacks["train"]])
            + np.stack([fit[name] for fit in stacks["test"]])
        )
        orac = 0.5 * (
            np.stack([fit[name] for fit in oracle["train"]])
            + np.stack([fit[name] for fit in oracle["test"]])
        )
        output[label] = _geometry(
            disc.reshape(len(disc), -1),
            orac.reshape(len(orac), -1),
        )
    return output


def _run_world_rep(
    world: str,
    repetition: int,
    seed: int,
    *,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
    arm2_lambda: float,
    expected_geometries: dict[str, float] | None,
    faithfulness_tolerance: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
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
    bridge = _bridge_chart_rank(
        observed,
        chart,
        rank_cap=int(config["maximum_rank"]),
    )
    arm1_transform, arm1_basis = build_m4_discovered_basis(
        observed,
        chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=bridge["selected_rank"],
    )
    arm1_is_noop = (
        arm1_transform.effective_rank == v2_transform.effective_rank
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
    arm_stacks: dict[str, dict[str, list[dict[str, Any]]]] = {
        arm: {"train": [], "test": []} for arm in ARMS
    }
    for view in ("train", "test"):
        panels = (
            getattr(observed.ecology, f"{view}_calibration"),
            getattr(observed.ecology, f"{view}_selection"),
            getattr(observed.ecology, f"{view}_evaluation"),
        )
        for author in range(authors):
            events = tuple(
                _flatten_events(panel, author) for panel in panels
            )
            flat[(view, author)] = events
            oracle_stacks[view].append(
                _fit_v2_stack(
                    *events,
                    truth.oracle_basis,
                    **fit_kwargs,
                    query_masks=query_masks,
                )
            )
            arm_stacks["arm0_v2"][view].append(
                _fit_v2_stack(
                    *events,
                    v2_basis,
                    **fit_kwargs,
                    query_masks=query_masks,
                )
            )

    # faithfulness gate BEFORE the treatment arms run on this world-rep
    arm0_geometries = _arm_geometries(arm_stacks["arm0_v2"], oracle_stacks)
    if expected_geometries is not None:
        for name, expected in expected_geometries.items():
            difference = abs(arm0_geometries[name] - expected)
            if difference > faithfulness_tolerance:
                raise RuntimeError(
                    f"V2 replay unfaithful on {world} rep {repetition}: "
                    f"{name} recomputed {arm0_geometries[name]:.12f} vs "
                    f"archived {expected:.12f} (|diff| {difference:.3e})"
                )

    for view in ("train", "test"):
        for author in range(authors):
            events = flat[(view, author)]
            base = arm_stacks["arm0_v2"][view][author]
            if arm1_is_noop:
                arm_stacks["arm1_width"][view].append(base)
            else:
                arm_stacks["arm1_width"][view].append(
                    _fit_v2_stack(
                        *events,
                        arm1_basis,
                        **fit_kwargs,
                        query_masks=query_masks,
                    )
                )
            arm_stacks["arm2_penalized"][view].append(
                _arm2_stack(
                    base,
                    *events,
                    v2_basis,
                    hazard_ridge=fit_kwargs["hazard_ridge"],
                    logistic_iterations=fit_kwargs["logistic_iterations"],
                    complexity_penalty=fit_kwargs["complexity_penalty"],
                    extra_ridge=arm2_lambda,
                )
            )
            arm_stacks["arm3_oof"][view].append(
                _arm3_stack(
                    base,
                    *events,
                    v2_basis,
                    hazard_ridge=fit_kwargs["hazard_ridge"],
                    logistic_iterations=fit_kwargs["logistic_iterations"],
                )
            )

    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    keys_base = {"world": world, "repetition": repetition, "seed": seed}
    for arm in ARMS:
        for view in ("train", "test"):
            for author in range(authors):
                loop_rows.append(
                    _loop_row(
                        {**keys_base, "author": author, "view": view},
                        arm,
                        arm_stacks[arm][view][author],
                        oracle_stacks[view][author],
                    )
                )
        geometries = (
            arm0_geometries
            if arm == "arm0_v2"
            else _arm_geometries(arm_stacks[arm], oracle_stacks)
        )
        arm_rows = [
            row for row in loop_rows if row["arm"] == arm
        ]
        world_rows.append(
            {
                **keys_base,
                "arm": arm,
                "chart_family": chart.selected_family,
                "v2_transform_rank": int(v2_transform.effective_rank),
                "arm_transform_rank": int(
                    arm1_transform.effective_rank
                    if arm == "arm1_width"
                    else v2_transform.effective_rank
                ),
                "width_basis": int(
                    arm1_basis["evaluation"].shape[1]
                    if arm == "arm1_width"
                    else v2_basis["evaluation"].shape[1]
                ),
                "oracle_width": int(
                    truth.oracle_basis["evaluation"].shape[1]
                ),
                "bridge_selected_rank": (
                    int(bridge["selected_rank"])
                    if arm == "arm1_width"
                    else np.nan
                ),
                "bridge_noise_floor": (
                    bridge["noise_floor"] if arm == "arm1_width" else np.nan
                ),
                "bridge_spectral_margin": (
                    bridge["spectral_margin"]
                    if arm == "arm1_width"
                    else np.nan
                ),
                "arm1_noop": bool(arm1_is_noop) if arm == "arm1_width" else False,
                "arm2_lambda": arm2_lambda if arm == "arm2_penalized" else np.nan,
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
    if expected_geometries is not None:
        for name, expected in expected_geometries.items():
            validation_rows.append(
                {
                    **keys_base,
                    "metric": name,
                    "recomputed": arm0_geometries[name],
                    "archived": expected,
                    "abs_difference": abs(arm0_geometries[name] - expected),
                }
            )
    return loop_rows, world_rows, validation_rows


# ---------------------------------------------------------------------------
# arm 2 lambda selection (discovery reps only)
# ---------------------------------------------------------------------------


def _select_arm2_lambda(
    worlds: list[str],
    *,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
    world_index: dict[str, int],
) -> tuple[float, pd.DataFrame]:
    route = dict(config["route_estimator"])
    route.pop("alias_match_threshold", None)
    hazard_ridge = float(route["hazard_ridge"])
    iterations = int(route["logistic_iterations"])
    rows = []
    for world in worlds:
        for repetition in DISCOVERY_REPS:
            seed = _world_seed(
                int(config["seed"]),
                repetition,
                world,
                world_index[world],
            )
            observed, _ = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            chart = fit_m4_condition_chart(
                observed.condition,
                candidates=tuple(dict(v) for v in config["candidates"]),
                **config["chart_thresholds"],
            )
            if chart.refused:
                raise RuntimeError(f"chart refused in lambda pass: {world}")
            _, basis = build_m4_discovered_basis(
                observed,
                chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=config.get("maximum_rank"),
            )
            authors = observed.ecology.train_calibration.menu.shape[0]
            for view in ("train", "test"):
                panels = (
                    getattr(observed.ecology, f"{view}_calibration"),
                    getattr(observed.ecology, f"{view}_selection"),
                )
                for author in range(authors):
                    calibration = _flatten_events(panels[0], author)
                    selection = _flatten_events(panels[1], author)
                    calibration_pair = (calibration, basis["calibration"])
                    for model in ("feedback", "gate"):
                        design, _ = _hazard_design(
                            selection,
                            basis["selection"],
                            model=model,
                        )
                        for lam in LAMBDA_GRID:
                            fit = _fit_hazard_penalized(
                                [calibration_pair],
                                model=model,
                                ridge=hazard_ridge,
                                iterations=iterations,
                                extra_ridge=lam,
                            )
                            rows.append(
                                {
                                    "world": world,
                                    "repetition": repetition,
                                    "view": view,
                                    "author": author,
                                    "model": model,
                                    "lam": lam,
                                    "oof_logloss": _hazard_logloss(
                                        fit[0],
                                        design,
                                        selection["generated_next"],
                                    ),
                                }
                            )
            print(
                f"[lambda] {world} rep={repetition} done",
                flush=True,
            )
    frame = pd.DataFrame(rows)
    by_lambda = (
        frame.groupby("lam")["oof_logloss"].mean().sort_index()
    )
    best = float(by_lambda.idxmin())
    return best, frame


# ---------------------------------------------------------------------------
# adjudication
# ---------------------------------------------------------------------------


def _author_level(frame: pd.DataFrame) -> pd.DataFrame:
    """Author-level loops (train/test mean) on oracle-nondegenerate rows."""
    usable = frame[frame["loop_norm_oracle"] > FLIP_TOLERANCE]
    return (
        usable.groupby(["arm", "world", "repetition", "author"])
        .agg(
            e_loop=("e_loop", "mean"),
            e_d_atom=("e_d_atom", "mean"),
            e_gc_composite=("e_gc_composite", "mean"),
            e_swap_d_oracle=("e_swap_d_oracle", "mean"),
            e_swap_gc_oracle=("e_swap_gc_oracle", "mean"),
        )
        .reset_index()
    )


def _mediation(
    per_author: pd.DataFrame,
    arm: str,
) -> dict[str, Any]:
    """Within-(world x rep) Spearman of D-leg vs loop improvement vs arm 0."""
    baseline = per_author[per_author["arm"] == "arm0_v2"]
    treated = per_author[per_author["arm"] == arm]
    merged = baseline.merge(
        treated,
        on=["world", "repetition", "author"],
        suffixes=("_base", "_arm"),
    )
    merged["delta_e_d"] = merged["e_d_atom_base"] - merged["e_d_atom_arm"]
    merged["delta_e_loop"] = merged["e_loop_base"] - merged["e_loop_arm"]
    cells = []
    for (world, repetition), group in merged.groupby(
        ["world", "repetition"]
    ):
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
                "rho": _pooled_spearman(group, "delta_e_d", "delta_e_loop"),
                "degenerate_cell": False,
            }
        )
    cell_frame = pd.DataFrame(cells)
    valid = cell_frame[~cell_frame["degenerate_cell"]]["rho"].dropna()
    return {
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
        "pooled_rho": _pooled_spearman(merged, "delta_e_d", "delta_e_loop"),
    }


def _adjudicate(
    loops: pd.DataFrame,
    worlds_frame: pd.DataFrame,
    validation: pd.DataFrame,
    lambda_frame: pd.DataFrame,
    arm2_lambda: float,
    config_seed: int,
    leg1_check: dict[str, Any],
) -> dict[str, Any]:
    per_author = _author_level(loops)
    arm_summaries: dict[str, Any] = {}
    for arm in ARMS:
        arm_loops = loops[loops["arm"] == arm]
        arm_worlds = worlds_frame[worlds_frame["arm"] == arm]
        per_world_geometry = {
            world: float(group["loop_action_geometry"].mean())
            for world, group in arm_worlds.groupby("world")
        }
        nonflip = arm_loops[~arm_loops["model_flip"]]
        arm_author = per_author[per_author["arm"] == arm]
        arm_summaries[arm] = {
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
            "mean_width_by_world": {
                world: float(group["width_discovered"].mean())
                for world, group in arm_loops.groupby("world")
            },
            "median_e_d": float(arm_author["e_d_atom"].median()),
            "median_e_loop": float(arm_author["e_loop"].median()),
            "median_e_gc": float(arm_author["e_gc_composite"].median()),
            "median_e_swap_d_oracle": float(
                arm_author["e_swap_d_oracle"].median()
            ),
            "median_e_swap_gc_oracle": float(
                arm_author["e_swap_gc_oracle"].median()
            ),
            "nonflip_mean_e_loop": float(nonflip["e_loop"].mean()),
            "within_cell_rho_e_d_vs_e_loop": float(
                np.nanmedian(
                    [
                        _pooled_spearman(group, "e_d_atom", "e_loop")
                        for _, group in arm_author.groupby(
                            ["world", "repetition"]
                        )
                        if len(group) >= 8
                    ]
                )
            ),
        }
        if arm != "arm0_v2":
            arm_summaries[arm]["mediation_vs_arm0"] = _mediation(
                per_author,
                arm,
            )

    treatment_arms = [arm for arm in ARMS if arm != "arm0_v2"]
    winning = min(
        treatment_arms,
        key=lambda arm: (
            arm_summaries[arm]["flips_total"],
            -arm_summaries[arm]["pooled_loop_geometry"],
        ),
    )
    lean_a_hold = bool(arm_summaries[winning]["flips_total"] <= 98)
    lean_b_hold = bool(arm_summaries[winning]["worlds_at_or_above_075"] >= 3)
    width_mediation = arm_summaries["arm1_width"]["mediation_vs_arm0"][
        "median_within_cell_rho"
    ]
    winning_mediation = arm_summaries[winning]["mediation_vs_arm0"][
        "median_within_cell_rho"
    ]
    lean_c_plan_hold = bool(
        np.isfinite(width_mediation) and width_mediation >= 0.5
    )
    lean_c_task_hold = bool(
        np.isfinite(winning_mediation) and winning_mediation >= 0.5
    )
    pivot_triggered = bool(
        lean_a_hold
        and arm_summaries[winning]["pooled_loop_geometry"] < 0.70
    )

    lambda_table = (
        lambda_frame.groupby("lam")["oof_logloss"].mean().to_dict()
        if len(lambda_frame)
        else {}
    )
    return {
        "estimand_id": "SUICA_M4_D_LEG3_OVERSPAN_CONTROLLED_ROUTE_IDENTIFICATION",
        "tier": "EXPLORATORY",
        "config_seed": config_seed,
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
        "arm2_lambda": {
            "grid": list(LAMBDA_GRID),
            "chosen": arm2_lambda,
            "discovery_repetitions": list(DISCOVERY_REPS),
            "mean_oof_logloss_by_lambda": {
                str(key): float(value)
                for key, value in sorted(lambda_table.items())
            },
        },
        "arms": arm_summaries,
        "winning_arm": winning,
        "lean_a": {
            "registered": "flips halved in the best single arm (196 -> <= 98)",
            "winning_arm_flips": arm_summaries[winning]["flips_total"],
            "flips_by_arm": {
                arm: arm_summaries[arm]["flips_total"] for arm in ARMS
            },
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": (
                "per-world mean loop geometry >= .75 in >= 3 of 5 worlds "
                "(currently 1/5)"
            ),
            "winning_arm_worlds_at_or_above_075": arm_summaries[winning][
                "worlds_at_or_above_075"
            ],
            "by_arm": {
                arm: arm_summaries[arm]["worlds_at_or_above_075"]
                for arm in ARMS
            },
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered_plan_wording": (
                "width-arm D-leg improvement mediates loop improvement: "
                "within-cell rho >= .5"
            ),
            "width_arm_median_within_cell_rho": width_mediation,
            "winning_arm_median_within_cell_rho": winning_mediation,
            "hold_plan_wording_width_arm": lean_c_plan_hold,
            "hold_task_wording_winning_arm": lean_c_task_hold,
            "readings_agree": bool(lean_c_plan_hold == lean_c_task_hold),
        },
        "pivot_if": {
            "registered": (
                "flips drop but pooled geometry stays < .70 -> D-leg error "
                "is not selection-driven; profile the third layer"
            ),
            "winning_arm_pooled_geometry": arm_summaries[winning][
                "pooled_loop_geometry"
            ],
            "triggered": pivot_triggered,
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; the loop-transport statistic "
            "still compares against oracle-basis fits, so this is a "
            "truth-referenced diagnostic of the estimator, not an operational "
            "rescue of chart transport and not a reopened gate; the V1/V2 "
            "NO-GO decisions stand; no natural-text, personality, emotion, or "
            "clinical claim; EXPLORATORY tier under the 2026-08-01 "
            "open-exploration directive."
        ),
    }


def _leg1_per_row_check(loops: pd.DataFrame) -> dict[str, Any]:
    """Assert arm-0 rows equal Leg 1's stored per-loop rows."""
    leg1_path = ROOT / "results" / "m4_d_curvature" / "per_loop_metrics.csv"
    if not leg1_path.exists():
        return {"leg1_per_row_available": False}
    leg1 = pd.read_csv(leg1_path)
    leg1 = leg1[leg1["family"] == "main"][
        [
            "world",
            "repetition",
            "author",
            "view",
            "e_loop",
            "e_d_atom",
            "selected_model_discovered",
            "selected_model_oracle",
            "model_flip",
        ]
    ]
    arm0 = loops[loops["arm"] == "arm0_v2"][
        [
            "world",
            "repetition",
            "author",
            "view",
            "e_loop",
            "e_d_atom",
            "selected_model_arm",
            "selected_model_oracle",
            "model_flip",
        ]
    ]
    merged = leg1.merge(
        arm0,
        on=["world", "repetition", "author", "view"],
        suffixes=("_leg1", "_leg3"),
    )
    if len(merged) != len(leg1) or len(merged) != len(arm0):
        raise RuntimeError(
            f"arm0 rows do not align with leg1 rows: {len(merged)} matches "
            f"vs leg1 {len(leg1)} / arm0 {len(arm0)}"
        )
    max_e_loop = float(
        np.max(np.abs(merged["e_loop_leg1"] - merged["e_loop_leg3"]))
    )
    max_e_d = float(
        np.max(np.abs(merged["e_d_atom_leg1"] - merged["e_d_atom_leg3"]))
    )
    models_equal = bool(
        (
            merged["selected_model_discovered"]
            == merged["selected_model_arm"]
        ).all()
        and (
            merged["selected_model_oracle_leg1"]
            == merged["selected_model_oracle_leg3"]
        ).all()
        and (merged["model_flip_leg1"] == merged["model_flip_leg3"]).all()
    )
    if max_e_loop > 1e-9 or max_e_d > 1e-9 or not models_equal:
        raise RuntimeError(
            "arm0 per-row replay diverges from leg1: "
            f"max|e_loop diff|={max_e_loop:.3e} "
            f"max|e_d diff|={max_e_d:.3e} models_equal={models_equal}"
        )
    return {
        "leg1_per_row_available": True,
        "leg1_per_row_max_abs_e_loop_difference": max_e_loop,
        "leg1_per_row_max_abs_e_d_difference": max_e_d,
        "leg1_per_row_models_equal": models_equal,
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
        default=ROOT / "results" / "m4_d_overspan_control",
    )
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument(
        "--arm2-lambda",
        type=float,
        default=None,
        help="skip the lambda pre-pass and use this value (smoke only)",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    config = _load(args.config)
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

    if args.arm2_lambda is not None:
        arm2_lambda = float(args.arm2_lambda)
        lambda_frame = pd.DataFrame()
        print(f"[lambda] fixed by flag: {arm2_lambda}", flush=True)
    else:
        started = time.time()
        arm2_lambda, lambda_frame = _select_arm2_lambda(
            worlds,
            spec=spec,
            config=config,
            world_index=world_index,
        )
        print(
            f"[lambda] chosen {arm2_lambda} by OOF likelihood on discovery "
            f"reps {DISCOVERY_REPS} ({time.time() - started:.0f}s)",
            flush=True,
        )

    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    for repetition in range(repetitions):
        for world in worlds:
            seed = _world_seed(
                int(config["seed"]),
                repetition,
                world,
                world_index[world],
            )
            expected = None
            if archived is not None:
                match = archived[
                    (archived["world"] == world)
                    & (archived["repetition"] == repetition)
                    & (archived["seed"] == seed)
                ]
                if len(match) == 1:
                    expected = {
                        name: float(match[name].iloc[0])
                        for name in (
                            "loop_action_geometry",
                            "choice_action_geometry",
                            "creation_action_geometry",
                        )
                    }
            started = time.time()
            rows, wrows, vrows = _run_world_rep(
                world,
                repetition,
                seed,
                spec=spec,
                config=config,
                arm2_lambda=arm2_lambda,
                expected_geometries=expected,
                faithfulness_tolerance=1e-6,
            )
            loop_rows.extend(rows)
            world_rows.extend(wrows)
            validation_rows.extend(vrows)
            by_arm = {
                row["arm"]: (
                    round(row["loop_action_geometry"], 3),
                    row["flips"],
                )
                for row in wrows
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

    args.output.mkdir(parents=True, exist_ok=True)
    loops.to_csv(args.output / "per_loop_metrics.csv", index=False)
    worlds_frame.to_csv(args.output / "world_rep_metrics.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    if len(lambda_frame):
        lambda_frame.to_csv(
            args.output / "arm2_lambda_selection.csv",
            index=False,
        )

    leg1_check = (
        _leg1_per_row_check(loops)
        if not args.smoke
        else {"leg1_per_row_available": False}
    )
    decision = _adjudicate(
        loops,
        worlds_frame,
        validation,
        lambda_frame,
        arm2_lambda,
        int(config["seed"]),
        leg1_check,
    )
    with (args.output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
