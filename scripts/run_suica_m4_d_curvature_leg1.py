#!/usr/bin/env python3
"""M4-D Leg 1: composition-curvature conjecture on the M4-C.2 V2 wall.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01).

Conjecture under test (registered in
docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md): per-atom transports
T_i are chart-consistent up to gauge; a composed loop accumulates a holonomy
defect. Law: per-loop transport failure increases with accumulated atom-pair
non-commutation sum_ij ||[T_i, T_j]||_F along the loop; near-zero-commutator
loops transport at atom-level rates.

Operationalization on the V2 loop kernel L = D @ G @ C (categories x
categories, physical on both axes):

- C := choice delta (chart x categories) -- chart-indexed rows;
- G := response-choice operator (response x chart) -- chart-indexed columns;
- D := creation feedback derivative (categories x response) -- chart-free.

The loop has exactly one gauged seam (Phi, between C and G). Per-atom
transports (oracle frame -> discovered frame), gauge group diag(1, O):

- T_C = diag(1, O_C), O_C = UV' from SVD(C_d[1:,:] @ C_o[1:,:]');
- T_G = diag(1, O_G), O_G = UV' from rank-restricted
  SVD(G_d[:,1:]' @ G_o[:,1:]) (G has only `response_dimensions` rows, so
  O_G is a rank<=d partial isometry on its identified plane);
- T_D = I (no chart index), hence ||[T_C,T_D]|| = ||[T_G,T_D]|| = 0 exactly.

Registered predictor (the computable form of the pair commutator for
rectangular partial isometries):

    kappa := || T_C T_G' - T_G T_C' ||_F

which vanishes iff the relative discovered-frame gauge T_C T_G' is symmetric
(no net rotation between the legs' preferred gauges on the identified plane)
and reduces to the skew norm of T_C when T_G = I.

Companions (persisted per loop, not the registered lean):
- seam_defect := ||G_d (Omega - I) C_d||_F / ||G_d C_d||_F with
  Omega = T_G T_C' -- the seam holonomy as the loop actually sees it;
- delta_joint := excess alignment cost of forcing one shared gauge for both
  legs versus per-leg gauges (joint-vs-separate Procrustes).

Lean (b) path-ordered correction: L_corr := D_d @ G_d @ Omega @ C_d
(parallel-transport across the single gauged seam before composing).

Lean (c) commuting family: monkeypatched creation loading interpolates
(lambda) between the registered rank-1 outer(direction, [1,-0.72]) and a
norm-matched full-rank random loading; lambda=0 reproduces the registered
world bit-for-bit. Full-rank loading identifies the seam gauge in every
direction, driving kappa toward zero -- the near-zero-commutator family.

Faithfulness gate: the audit-level loop/choice/creation action geometries
recomputed here must match results/m4_chart_ecology/metrics.csv (the archived
V2 confirmation) per world x repetition.
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
from scipy.stats import spearmanr, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core import m4_chart_ecology_generator as generator_module  # noqa: E402
from suica_core.m4_chart_ecology_audit import _geometry  # noqa: E402
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    HAZARD_MODELS,
    _choice_delta,
    _choice_logloss,
    _creation_action,
    _choice_action,
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
    fit_m4_condition_chart,
)

LOOP_WORLDS = (
    "endogenous_source_partition_matched",
    "endogenous_creation_expansion",
    "source_rotated_feedback",
    "history_gated_ecology",
    "selection_creation_compensation",
)
COMMUTING_BASE_WORLD = "endogenous_creation_expansion"
EPS = 1e-12


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


def _fit_author_legs(
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
    query_masks: np.ndarray,
) -> dict[str, Any]:
    """Replicate the exact `_one_author` fitting flow; return the loop legs.

    Fitting order, ridge/model selection, and refits are copied verbatim from
    suica_core.m4_chart_ecology_estimator._one_author so that D @ G @ C equals
    the V2 loop kernel bit-for-bit.
    """
    calibration = _flatten_events(calibration_panel, author)
    selection = _flatten_events(selection_panel, author)
    evaluation = _flatten_events(evaluation_panel, author)
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

    hazard_fits: dict[str, tuple[np.ndarray, tuple[str, ...]]] = {}
    hazard_scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        fit = _fit_hazard_candidate(
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
        loss = _hazard_logloss(fit[0], design, selection["generated_next"])
        hazard_fits[model] = fit
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
    response_choice = response_coefficient[
        dimensions : dimensions + width
    ].T
    choice_delta = _choice_delta(choice_coefficient, eval_basis)
    loop_kernel = derivative @ response_choice @ choice_delta
    return {
        "C": choice_delta,
        "G": response_choice,
        "D": derivative,
        "loop": loop_kernel,
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
    }


def _fit_route_legs(
    ecology: Any,
    basis: dict[str, np.ndarray],
    *,
    route_parameters: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    categories = ecology.train_calibration.menu.shape[-1]
    query_masks = _query_masks(categories)
    authors = ecology.train_calibration.menu.shape[0]
    output: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
    for view in ("train", "test"):
        panels = (
            getattr(ecology, f"{view}_calibration"),
            getattr(ecology, f"{view}_selection"),
            getattr(ecology, f"{view}_evaluation"),
        )
        for author in range(authors):
            output[view].append(
                _fit_author_legs(
                    *panels,
                    basis,
                    author,
                    ridge_grid=tuple(
                        float(x) for x in route_parameters["ridge_grid"]
                    ),
                    hazard_ridge=float(route_parameters["hazard_ridge"]),
                    logistic_iterations=int(
                        route_parameters["logistic_iterations"]
                    ),
                    complexity_penalty=float(
                        route_parameters["complexity_penalty"]
                    ),
                    query_masks=query_masks,
                )
            )
    return output


def _procrustes_c(
    c_disc: np.ndarray,
    c_oracle: np.ndarray,
) -> np.ndarray:
    """O_C minimizing ||C_d[1:,:] - O C_o[1:,:]||_F over partial isometries."""
    cross = c_disc[1:, :] @ c_oracle[1:, :].T
    u, _, vt = np.linalg.svd(cross, full_matrices=False)
    return u @ vt


def _procrustes_g(
    g_disc: np.ndarray,
    g_oracle: np.ndarray,
    *,
    rank_tolerance: float = 1e-8,
) -> tuple[np.ndarray, int]:
    """O_G minimizing ||G_d[:,1:] O - G_o[:,1:]||_F, rank-restricted.

    G has only `response_dimensions` rows, so the gauge is identified only on
    a rank<=d plane; singular directions below tolerance are dropped rather
    than filled with arbitrary rotations.
    """
    cross = g_disc[:, 1:].T @ g_oracle[:, 1:]
    u, s, vt = np.linalg.svd(cross, full_matrices=False)
    keep = s > rank_tolerance * max(float(s[0]), EPS)
    rank = int(np.sum(keep))
    if rank == 0:
        return np.zeros((cross.shape[0], cross.shape[1])), 0
    return u[:, keep] @ vt[keep], rank


def _embed_gauge(o_block: np.ndarray) -> np.ndarray:
    """diag(1, O): fix the mass coordinate, gauge the whitened block."""
    rows, cols = o_block.shape
    t = np.zeros((rows + 1, cols + 1))
    t[0, 0] = 1.0
    t[1:, 1:] = o_block
    return t


def _relative_error(
    estimate: np.ndarray,
    reference: np.ndarray,
) -> float:
    return float(
        np.linalg.norm(estimate - reference)
        / max(np.linalg.norm(reference), EPS)
    )


def _joint_gauge_excess(
    c_disc: np.ndarray,
    c_oracle: np.ndarray,
    g_disc: np.ndarray,
    g_oracle: np.ndarray,
) -> float:
    """Excess cost of one shared gauge versus per-leg gauges (>= ~0)."""
    c_norm = max(np.linalg.norm(c_oracle[1:, :]), EPS)
    g_norm = max(np.linalg.norm(g_oracle[:, 1:]), EPS)
    cross = (
        c_disc[1:, :] @ c_oracle[1:, :].T / (c_norm**2)
        + g_disc[:, 1:].T @ g_oracle[:, 1:] / (g_norm**2)
    )
    u, _, vt = np.linalg.svd(cross, full_matrices=False)
    shared = u @ vt
    o_c = _procrustes_c(c_disc, c_oracle)
    o_g, _ = _procrustes_g(g_disc, g_oracle)

    def cost(o_for_c: np.ndarray, o_for_g: np.ndarray) -> float:
        c_term = (
            np.linalg.norm(c_disc[1:, :] - o_for_c @ c_oracle[1:, :])
            / c_norm
        ) ** 2
        g_term = (
            np.linalg.norm(g_disc[:, 1:] @ o_for_g - g_oracle[:, 1:])
            / g_norm
        ) ** 2
        return float(c_term + g_term)

    return cost(shared, shared) - cost(o_c, o_g)


def _loop_rows(
    world: str,
    family: str,
    lam: float,
    repetition: int,
    seed: int,
    discovered: dict[str, list[dict[str, Any]]],
    oracle: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    authors = len(discovered["train"])
    for author in range(authors):
        for view in ("train", "test"):
            d_fit = discovered[view][author]
            o_fit = oracle[view][author]
            c_d, g_d, dd = d_fit["C"], d_fit["G"], d_fit["D"]
            c_o, g_o, do = o_fit["C"], o_fit["G"], o_fit["D"]
            l_d, l_o = d_fit["loop"], o_fit["loop"]
            o_c = _procrustes_c(c_d, c_o)
            o_g, rank_g = _procrustes_g(g_d, g_o)
            t_c = _embed_gauge(o_c)
            t_g = _embed_gauge(o_g)
            kappa = float(
                np.linalg.norm(t_c @ t_g.T - t_g @ t_c.T)
            )
            omega = t_g @ t_c.T
            gc_d = g_d @ c_d
            seam_defect = float(
                np.linalg.norm(g_d @ (omega - np.eye(len(omega))) @ c_d)
                / max(np.linalg.norm(gc_d), EPS)
            )
            delta_joint = _joint_gauge_excess(c_d, c_o, g_d, g_o)
            loop_norm_oracle = float(np.linalg.norm(l_o))
            d_norm_disc = float(np.linalg.norm(dd))
            d_norm_oracle = float(np.linalg.norm(do))
            model_flip = bool(
                (d_norm_disc < 1e-10) != (d_norm_oracle < 1e-10)
            )
            degenerate = bool(
                loop_norm_oracle < 1e-10
                or d_norm_disc < 1e-10
                or d_norm_oracle < 1e-10
                or rank_g == 0
            )
            l_corr = dd @ g_d @ omega @ c_d
            aligned_c = t_c @ c_o
            aligned_g = g_o @ t_g.T
            rows.append(
                {
                    "world": world,
                    "family": family,
                    "lam": lam,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "width_discovered": int(c_d.shape[0]),
                    "width_oracle": int(c_o.shape[0]),
                    "rank_g": rank_g,
                    "selected_model_discovered": d_fit["selected_model"],
                    "selected_model_oracle": o_fit["selected_model"],
                    "kappa_commutator": kappa,
                    "seam_defect": seam_defect,
                    "delta_joint_gauge": delta_joint,
                    "e_loop": _relative_error(l_d, l_o),
                    "e_loop_corrected": _relative_error(l_corr, l_o),
                    "e_gc_composite": _relative_error(gc_d, g_o @ c_o),
                    "e_c_atom": _relative_error(c_d, aligned_c),
                    "e_g_atom": _relative_error(g_d @ t_g, g_o),
                    "e_d_atom": _relative_error(dd, do),
                    "e_loop_swap_c": _relative_error(
                        dd @ (g_d @ t_g) @ c_o,
                        l_o,
                    ),
                    "e_loop_swap_g": _relative_error(
                        dd @ g_o @ (t_c.T @ c_d),
                        l_o,
                    ),
                    "e_loop_swap_d": _relative_error(
                        do @ g_d @ omega @ c_d,
                        l_o,
                    ),
                    "loop_norm_oracle": loop_norm_oracle,
                    "loop_norm_discovered": float(np.linalg.norm(l_d)),
                    "d_norm_discovered": d_norm_disc,
                    "d_norm_oracle": d_norm_oracle,
                    "model_flip": model_flip,
                    "degenerate": degenerate,
                }
            )
    return rows


def _mean_kernel(fits: dict[str, list[dict[str, Any]]], name: str) -> np.ndarray:
    train = np.stack([fit[name] for fit in fits["train"]])
    test = np.stack([fit[name] for fit in fits["test"]])
    return 0.5 * (train + test)


def _route_geometries(
    discovered: dict[str, list[dict[str, Any]]],
    oracle: dict[str, list[dict[str, Any]]],
) -> dict[str, float]:
    output = {}
    for label, name in (
        ("loop_action_geometry", "loop"),
        ("choice_action_geometry", "choice_action"),
        ("creation_action_geometry", "creation_action"),
    ):
        disc = _mean_kernel(discovered, name)
        orac = _mean_kernel(oracle, name)
        output[label] = _geometry(
            disc.reshape(len(disc), -1),
            orac.reshape(len(orac), -1),
        )
    return output


def _corrected_loop_geometry(
    rows: list[dict[str, Any]],
    discovered: dict[str, list[dict[str, Any]]],
    oracle: dict[str, list[dict[str, Any]]],
) -> float:
    """Recompute the V2 loop geometry with seam-corrected discovered kernels."""
    authors = len(discovered["train"])
    corrected = []
    for author in range(authors):
        kernels = []
        for view in ("train", "test"):
            d_fit = discovered[view][author]
            o_fit = oracle[view][author]
            o_c = _procrustes_c(d_fit["C"], o_fit["C"])
            o_g, _ = _procrustes_g(d_fit["G"], o_fit["G"])
            omega = _embed_gauge(o_g) @ _embed_gauge(o_c).T
            kernels.append(d_fit["D"] @ d_fit["G"] @ omega @ d_fit["C"])
        corrected.append(0.5 * (kernels[0] + kernels[1]))
    corrected_stack = np.stack(corrected)
    oracle_stack = _mean_kernel(oracle, "loop")
    return _geometry(
        corrected_stack.reshape(authors, -1),
        oracle_stack.reshape(authors, -1),
    )


def _commuting_parameter_wrapper(lam: float, base_seed_note: str):
    """Wrap _mechanism_parameters: interpolate creation loading to full rank.

    lambda=0 returns the registered parameters untouched (bit-for-bit).
    lambda>0 mixes the rank-1 outer(direction,[1,-0.72]) loading with a
    norm-matched full-rank random loading (mass row zero), renormalized per
    author to the original Frobenius norm so total feedback strength -- and
    hence the menu marginal calibration -- is preserved.
    """
    original = generator_module._mechanism_parameters

    def wrapped(*, world, oracle_width, spec, seed):
        parameters = original(
            world=world,
            oracle_width=oracle_width,
            spec=spec,
            seed=seed,
        )
        if lam <= 0.0:
            return parameters
        creation = parameters["creation"].copy()
        for author in range(creation.shape[0]):
            block = creation[author]
            norm = float(np.linalg.norm(block))
            if norm < EPS:
                continue
            rng = np.random.default_rng(
                (int(seed) * 1_000_003 + author * 9_176 + 733) % (2**63)
            )
            full = rng.normal(size=block.shape)
            full[0, :] = 0.0
            full *= norm / max(float(np.linalg.norm(full)), EPS)
            mixed = (1.0 - lam) * block + lam * full
            mixed_norm = float(np.linalg.norm(mixed))
            if mixed_norm > EPS:
                mixed *= norm / mixed_norm
            creation[author] = mixed
        parameters["creation"] = creation
        return parameters

    wrapped.__name__ = f"_mechanism_parameters_commuting_{base_seed_note}"
    return wrapped


def _run_world_rep(
    world: str,
    repetition: int,
    seed: int,
    *,
    family: str,
    lam: float,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
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
        return [], {
            "world": world,
            "family": family,
            "lam": lam,
            "repetition": repetition,
            "seed": seed,
            "chart_refused": True,
        }
    transform, discovered_basis = build_m4_discovered_basis(
        observed,
        chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=config.get("maximum_rank"),
    )
    route_parameters = dict(config["route_estimator"])
    route_parameters.pop("alias_match_threshold", None)
    discovered = _fit_route_legs(
        observed.ecology,
        discovered_basis,
        route_parameters=route_parameters,
    )
    oracle = _fit_route_legs(
        observed.ecology,
        truth.oracle_basis,
        route_parameters=route_parameters,
    )
    rows = _loop_rows(
        world,
        family,
        lam,
        repetition,
        seed,
        discovered,
        oracle,
    )
    geometries = _route_geometries(discovered, oracle)
    generated_rate = float(
        np.mean(observed.ecology.train_evaluation.generated_menu)
    )
    menu_rate = float(np.mean(observed.ecology.train_evaluation.menu))
    world_row = {
        "world": world,
        "family": family,
        "lam": lam,
        "repetition": repetition,
        "seed": seed,
        "chart_refused": False,
        "transform_rank": int(transform.effective_rank),
        "oracle_width": int(truth.oracle_basis["evaluation"].shape[1]),
        **geometries,
        "loop_action_geometry_corrected": _corrected_loop_geometry(
            rows,
            discovered,
            oracle,
        ),
        "mean_kappa": float(np.mean([row["kappa_commutator"] for row in rows])),
        "mean_e_loop": float(np.mean([row["e_loop"] for row in rows])),
        "mean_e_loop_corrected": float(
            np.mean([row["e_loop_corrected"] for row in rows])
        ),
        "generated_menu_rate": generated_rate,
        "union_menu_rate": menu_rate,
    }
    return rows, world_row


def _pooled_spearman(
    frame: pd.DataFrame,
    x: str,
    y: str,
) -> float:
    if len(frame) < 3:
        return float("nan")
    value = spearmanr(frame[x], frame[y]).statistic
    return float(value) if np.isfinite(value) else float("nan")


def _adjudicate(
    loops: pd.DataFrame,
    worlds: pd.DataFrame,
    validation: pd.DataFrame,
    config_seed: int,
) -> dict[str, Any]:
    main = loops[(loops["family"] == "main") & (~loops["degenerate"])]
    main_all = loops[loops["family"] == "main"]
    per_author = (
        main.groupby(["world", "repetition", "author"])
        .agg(
            kappa_commutator=("kappa_commutator", "mean"),
            seam_defect=("seam_defect", "mean"),
            delta_joint_gauge=("delta_joint_gauge", "mean"),
            e_loop=("e_loop", "mean"),
            e_loop_corrected=("e_loop_corrected", "mean"),
            e_gc_composite=("e_gc_composite", "mean"),
            e_c_atom=("e_c_atom", "mean"),
            e_g_atom=("e_g_atom", "mean"),
            e_d_atom=("e_d_atom", "mean"),
        )
        .reset_index()
    )
    lean_a_primary = _pooled_spearman(
        per_author,
        "kappa_commutator",
        "e_loop",
    )
    lean_a_view_level = _pooled_spearman(main, "kappa_commutator", "e_loop")
    within = []
    for (world, repetition), group in per_author.groupby(
        ["world", "repetition"]
    ):
        if len(group) >= 8:
            within.append(
                {
                    "world": world,
                    "repetition": repetition,
                    "rho": _pooled_spearman(
                        group,
                        "kappa_commutator",
                        "e_loop",
                    ),
                }
            )
    within_frame = pd.DataFrame(within)
    per_world = {
        world: _pooled_spearman(group, "kappa_commutator", "e_loop")
        for world, group in per_author.groupby("world")
    }
    atom_error_sum = (
        per_author["e_c_atom"]
        + per_author["e_g_atom"]
        + per_author["e_d_atom"]
    )
    residual_kappa = per_author["kappa_commutator"].rank() - pd.Series(
        np.poly1d(
            np.polyfit(
                atom_error_sum.rank(),
                per_author["kappa_commutator"].rank(),
                1,
            )
        )(atom_error_sum.rank())
    )
    residual_e = per_author["e_loop"].rank() - pd.Series(
        np.poly1d(
            np.polyfit(atom_error_sum.rank(), per_author["e_loop"].rank(), 1)
        )(atom_error_sum.rank())
    )
    partial = (
        float(np.corrcoef(residual_kappa, residual_e)[0, 1])
        if len(per_author) > 4
        else float("nan")
    )

    world_level = worlds[worlds["family"] == "main"]
    lean_a_worldrep_geometry = _pooled_spearman(
        world_level,
        "mean_kappa",
        "loop_action_geometry",
    )
    lean_a_worldrep_error = _pooled_spearman(
        world_level,
        "mean_kappa",
        "mean_e_loop",
    )

    lean_a_hold = bool(lean_a_primary >= 0.7)
    lean_a_pivot = bool(lean_a_primary < 0.3)

    holding_worlds = [
        world for world, rho in per_world.items() if np.isfinite(rho) and rho >= 0.7
    ]
    reduction_frame = per_author[
        per_author["world"].isin(holding_worlds)
    ] if holding_worlds else per_author
    reduction = (
        reduction_frame["e_loop"] - reduction_frame["e_loop_corrected"]
    ) / np.maximum(reduction_frame["e_loop"], EPS)
    try:
        wilcoxon_p = float(
            wilcoxon(
                reduction_frame["e_loop"],
                reduction_frame["e_loop_corrected"],
                alternative="greater",
            ).pvalue
        )
    except ValueError:
        wilcoxon_p = float("nan")
    corrected_geometry = world_level["loop_action_geometry_corrected"]
    uncorrected_geometry = world_level["loop_action_geometry"]
    lean_b_hold = bool(
        np.median(reduction) > 0.0 and wilcoxon_p < 0.05
    )

    commuting = worlds[worlds["family"] == "commuting"]
    commuting_loops = loops[
        (loops["family"] == "commuting") & (~loops["degenerate"])
    ]
    lean_c: dict[str, Any] = {"available": bool(len(commuting) > 0)}
    if len(commuting) > 0:
        by_lambda = (
            commuting.groupby("lam")
            .agg(
                loop_geometry=("loop_action_geometry", "mean"),
                choice_geometry=("choice_action_geometry", "mean"),
                creation_geometry=("creation_action_geometry", "mean"),
                mean_kappa=("mean_kappa", "mean"),
                mean_e_loop=("mean_e_loop", "mean"),
                generated_rate=("generated_menu_rate", "mean"),
                union_rate=("union_menu_rate", "mean"),
            )
            .reset_index()
        )
        lean_c["by_lambda"] = by_lambda.to_dict(orient="records")
        top = by_lambda[by_lambda["lam"] == by_lambda["lam"].max()].iloc[0]
        base = by_lambda[by_lambda["lam"] == by_lambda["lam"].min()].iloc[0]
        atom_floor = float(
            min(top["choice_geometry"], top["creation_geometry"])
        )
        lean_c["kappa_drop"] = float(base["mean_kappa"] - top["mean_kappa"])
        lean_c["loop_geometry_at_max_lambda"] = float(top["loop_geometry"])
        lean_c["atom_floor_at_max_lambda"] = atom_floor
        lean_c["hold"] = bool(
            top["mean_kappa"] < base["mean_kappa"]
            and (
                top["loop_geometry"] >= atom_floor - 0.05
                or top["loop_geometry"] >= 0.70
            )
        )
        lean_c["commuting_lambda_spearman_kappa_e_loop"] = _pooled_spearman(
            commuting_loops,
            "kappa_commutator",
            "e_loop",
        )

    faithful = bool(
        len(validation) > 0
        and validation["abs_difference"].max() <= 1e-6
    )
    flip_rows = main_all[main_all["model_flip"]]
    swap_profile = {
        "seam_only_correction_median_e_loop": float(
            per_author["e_loop_corrected"].median()
        ),
        "uncorrected_median_e_loop": float(per_author["e_loop"].median()),
        "swap_c_median": float(
            main.groupby(["world", "repetition", "author"])["e_loop_swap_c"]
            .mean()
            .median()
        ),
        "swap_g_median": float(
            main.groupby(["world", "repetition", "author"])["e_loop_swap_g"]
            .mean()
            .median()
        ),
        "swap_d_median": float(
            main.groupby(["world", "repetition", "author"])["e_loop_swap_d"]
            .mean()
            .median()
        ),
        "median_e_c_atom": float(per_author["e_c_atom"].median()),
        "median_e_g_atom": float(per_author["e_g_atom"].median()),
        "median_e_d_atom": float(per_author["e_d_atom"].median()),
        "median_e_gc_composite": float(
            per_author["e_gc_composite"].median()
        ),
        "spearman_e_d_atom_vs_e_loop": _pooled_spearman(
            per_author,
            "e_d_atom",
            "e_loop",
        ),
        "spearman_e_gc_composite_vs_e_loop": _pooled_spearman(
            per_author,
            "e_gc_composite",
            "e_loop",
        ),
        "spearman_e_c_atom_vs_e_loop": _pooled_spearman(
            per_author,
            "e_c_atom",
            "e_loop",
        ),
        "spearman_e_g_atom_vs_e_loop": _pooled_spearman(
            per_author,
            "e_g_atom",
            "e_loop",
        ),
        "model_flip_view_rows": int(len(flip_rows)),
        "model_flip_view_row_share": float(
            len(flip_rows) / max(len(main_all), 1)
        ),
        "model_flip_by_world": {
            world: int(count)
            for world, count in flip_rows.groupby("world")
            .size()
            .items()
        },
        "model_flip_direction": {
            f"{disc}->{orac}": int(count)
            for (disc, orac), count in flip_rows.groupby(
                ["selected_model_discovered", "selected_model_oracle"]
            )
            .size()
            .items()
        },
        "sensitivity_spearman_including_flips": _pooled_spearman(
            main_all[main_all["loop_norm_oracle"] > 1e-10]
            .groupby(["world", "repetition", "author"])
            .agg(
                kappa_commutator=("kappa_commutator", "mean"),
                e_loop=("e_loop", "mean"),
            )
            .reset_index(),
            "kappa_commutator",
            "e_loop",
        ),
    }
    return {
        "estimand_id": "SUICA_M4_D_LEG1_COMPOSITION_CURVATURE",
        "tier": "EXPLORATORY",
        "config_seed": config_seed,
        "extraction_faithful_to_v2": faithful,
        "validation_max_abs_difference": (
            float(validation["abs_difference"].max())
            if len(validation)
            else float("nan")
        ),
        "n_loops_primary": int(len(per_author)),
        "n_loops_degenerate_excluded": int(
            len(
                loops[(loops["family"] == "main") & (loops["degenerate"])]
            )
        ),
        "lean_a": {
            "registered": "Spearman(kappa, e_loop) >= .7 holds; < .3 pivots",
            "primary_spearman_per_author_loops": lean_a_primary,
            "view_level_spearman": lean_a_view_level,
            "partial_rank_correlation_given_atom_errors": partial,
            "within_world_rep_median_rho": (
                float(within_frame["rho"].median())
                if len(within_frame)
                else float("nan")
            ),
            "within_world_rep_iqr": (
                [
                    float(within_frame["rho"].quantile(0.25)),
                    float(within_frame["rho"].quantile(0.75)),
                ]
                if len(within_frame)
                else [float("nan"), float("nan")]
            ),
            "per_world_spearman": per_world,
            "world_rep_level_spearman_vs_loop_geometry": (
                lean_a_worldrep_geometry
            ),
            "world_rep_level_spearman_vs_mean_e_loop": lean_a_worldrep_error,
            "companion_seam_defect_spearman": _pooled_spearman(
                per_author,
                "seam_defect",
                "e_loop",
            ),
            "companion_delta_joint_spearman": _pooled_spearman(
                per_author,
                "delta_joint_gauge",
                "e_loop",
            ),
            "hold": lean_a_hold,
            "pivot": lean_a_pivot,
        },
        "lean_b": {
            "registered": (
                "path-ordered seam correction reduces loop error in worlds "
                "where (a) holds"
            ),
            "worlds_where_a_holds": holding_worlds,
            "median_relative_reduction": float(np.median(reduction)),
            "wilcoxon_p_one_sided": wilcoxon_p,
            "mean_loop_geometry_uncorrected": float(
                uncorrected_geometry.mean()
            ),
            "mean_loop_geometry_corrected": float(corrected_geometry.mean()),
            "corrected_geometry_by_world": {
                world: float(group["loop_action_geometry_corrected"].mean())
                for world, group in world_level.groupby("world")
            },
            "uncorrected_geometry_by_world": {
                world: float(group["loop_action_geometry"].mean())
                for world, group in world_level.groupby("world")
            },
            "hold": lean_b_hold,
        },
        "lean_c": lean_c,
        "error_concentration_profile": swap_profile,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-open diagnostic "
            "(oracle legs are consumed by the transports), so nothing here "
            "is an operational rescue of chart transport; no natural-text, "
            "personality, or clinical claim; EXPLORATORY tier under the "
            "2026-08-01 open-exploration directive."
        ),
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
        default=ROOT / "results" / "m4_d_curvature",
    )
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--commuting-repetitions", type=int, default=4)
    parser.add_argument(
        "--lambdas",
        type=float,
        nargs="*",
        default=(0.0, 0.5, 1.0),
    )
    parser.add_argument("--skip-commuting", action="store_true")
    parser.add_argument(
        "--worlds",
        nargs="*",
        default=list(LOOP_WORLDS),
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
    worlds = list(args.worlds)
    if args.smoke:
        repetitions = 1
        worlds = worlds[:2]
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }

    archived_path = ROOT / "results" / "m4_chart_ecology" / "metrics.csv"
    archived = (
        pd.read_csv(archived_path) if archived_path.exists() else None
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
            started = time.time()
            rows, world_row = _run_world_rep(
                world,
                repetition,
                seed,
                family="main",
                lam=0.0,
                spec=spec,
                config=config,
            )
            loop_rows.extend(rows)
            world_rows.append(world_row)
            if archived is not None and not world_row.get("chart_refused"):
                match = archived[
                    (archived["world"] == world)
                    & (archived["repetition"] == repetition)
                    & (archived["seed"] == seed)
                ]
                if len(match) == 1:
                    for name in (
                        "loop_action_geometry",
                        "choice_action_geometry",
                        "creation_action_geometry",
                    ):
                        validation_rows.append(
                            {
                                "world": world,
                                "repetition": repetition,
                                "metric": name,
                                "recomputed": world_row[name],
                                "archived": float(match[name].iloc[0]),
                                "abs_difference": abs(
                                    world_row[name]
                                    - float(match[name].iloc[0])
                                ),
                            }
                        )
            print(
                f"[main] rep={repetition} world={world} "
                f"seed={seed} loops={len(rows)} "
                f"loop_geo={world_row.get('loop_action_geometry', 'refused')}"
                f" ({time.time() - started:.1f}s)",
                flush=True,
            )

    if not args.skip_commuting and not args.smoke:
        commuting_reps = min(int(args.commuting_repetitions), repetitions)
        for lam in args.lambdas:
            for repetition in range(commuting_reps):
                seed = _world_seed(
                    int(config["seed"]),
                    repetition,
                    COMMUTING_BASE_WORLD,
                    world_index[COMMUTING_BASE_WORLD],
                )
                if lam <= 0.0:
                    # lambda=0 is bit-identical to the registered world:
                    # reuse the main-battery rows instead of recomputing.
                    for row in loop_rows:
                        if (
                            row["family"] == "main"
                            and row["world"] == COMMUTING_BASE_WORLD
                            and row["repetition"] == repetition
                        ):
                            copied = dict(row)
                            copied["family"] = "commuting"
                            copied["lam"] = 0.0
                            loop_rows.append(copied)
                    for row in world_rows:
                        if (
                            row["family"] == "main"
                            and row["world"] == COMMUTING_BASE_WORLD
                            and row["repetition"] == repetition
                        ):
                            copied = dict(row)
                            copied["family"] = "commuting"
                            copied["lam"] = 0.0
                            world_rows.append(copied)
                    continue
                original = generator_module._mechanism_parameters
                generator_module._mechanism_parameters = (
                    _commuting_parameter_wrapper(lam, f"lam{lam}")
                )
                try:
                    started = time.time()
                    rows, world_row = _run_world_rep(
                        COMMUTING_BASE_WORLD,
                        repetition,
                        seed,
                        family="commuting",
                        lam=float(lam),
                        spec=spec,
                        config=config,
                    )
                finally:
                    generator_module._mechanism_parameters = original
                loop_rows.extend(rows)
                world_rows.append(world_row)
                print(
                    f"[commuting] lam={lam} rep={repetition} "
                    f"loop_geo={world_row.get('loop_action_geometry')}"
                    f" kappa={world_row.get('mean_kappa'):.4f}"
                    f" ({time.time() - started:.1f}s)",
                    flush=True,
                )

    loops = pd.DataFrame(loop_rows)
    worlds_frame = pd.DataFrame(world_rows)
    validation = pd.DataFrame(validation_rows)

    args.output.mkdir(parents=True, exist_ok=True)
    loops.to_csv(args.output / "per_loop_metrics.csv", index=False)
    worlds_frame.to_csv(args.output / "world_rep_metrics.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)

    decision = _adjudicate(
        loops,
        worlds_frame,
        validation,
        int(config["seed"]),
    )
    with (args.output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
