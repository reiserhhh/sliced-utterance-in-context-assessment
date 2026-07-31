#!/usr/bin/env python3
"""Confirm M4-C.3.2 cross-fitted Fisher-Wiener creation estimation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
    fit_m4_chart_ecology,
    rotate_whitened_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
    compose_creation_only_loop,
    relative_headroom_recovery,
)
from suica_core.m4_fisher_wiener_creation import (  # noqa: E402
    build_fisher_wiener_route,
    fit_fixed_hazard_route,
    fit_selected_hazard_route,
    split_opportunity_occasions,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _fixed_parameters(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": str(config["fisher_wiener"]["hazard_model"]),
        "ridge": float(config["route_estimator"]["hazard_ridge"]),
        "iterations": int(
            config["route_estimator"]["logistic_iterations"]
        ),
    }


def _cluster_lcb(
    frame: pd.DataFrame,
    column: str,
    *,
    seed: int,
    repetitions: int,
) -> float:
    clusters = (
        frame.groupby("repetition", sort=True)[column]
        .mean()
        .to_numpy(dtype=float)
    )
    rng = np.random.default_rng(seed)
    draws = rng.choice(
        clusters,
        size=(repetitions, len(clusters)),
        replace=True,
    )
    return float(np.quantile(np.mean(draws, axis=1), 0.025))


def _fit_routes(
    observed: Any,
    basis: dict[str, np.ndarray],
    config: dict[str, Any],
    *,
    permutation: np.ndarray,
) -> dict[str, Any]:
    route_parameters = _route_parameters(config)
    fixed_parameters = _fixed_parameters(config)
    baseline = fit_m4_physical_edge_route(
        observed.ecology,
        basis,
        basis_name="chart_plugin",
        **route_parameters,
    )
    selected = fit_selected_hazard_route(
        observed.ecology,
        basis,
        ridge=fixed_parameters["ridge"],
        iterations=fixed_parameters["iterations"],
        complexity_penalty=float(
            config["route_estimator"]["complexity_penalty"]
        ),
    )
    full = fit_fixed_hazard_route(
        observed.ecology,
        basis,
        **fixed_parameters,
    )
    first_ecology, second_ecology = split_opportunity_occasions(
        observed.ecology
    )
    first = fit_fixed_hazard_route(
        first_ecology,
        basis,
        **fixed_parameters,
    )
    second = fit_fixed_hazard_route(
        second_ecology,
        basis,
        **fixed_parameters,
    )
    fisher = build_fisher_wiener_route(
        observed.ecology,
        basis,
        full,
        first,
        second,
        epsilon_scale=float(
            config["fisher_wiener"]["epsilon_scale"]
        ),
    )
    permuted = build_fisher_wiener_route(
        observed.ecology,
        basis,
        full,
        first,
        second,
        epsilon_scale=float(
            config["fisher_wiener"]["epsilon_scale"]
        ),
        second_permutation=permutation,
    )
    return {
        "baseline": baseline,
        "selected": selected,
        "full": full,
        "first": first,
        "second": second,
        "fisher": fisher,
        "permuted": permuted,
        "first_ecology": first_ecology,
        "second_ecology": second_ecology,
    }


def _metric_row(
    *,
    repetition: int,
    world: str,
    world_type: str,
    view_name: str,
    oracle: Any,
    routes: dict[str, Any],
) -> dict[str, Any]:
    oracle_view = getattr(oracle, view_name)
    baseline = getattr(routes["baseline"], view_name)
    selected = getattr(routes["selected"], view_name)
    full = getattr(routes["full"], view_name)
    fisher = getattr(routes["fisher"], view_name)
    permuted = getattr(routes["permuted"], view_name)
    oracle_target = oracle_view.jacobian_loop
    baseline_geometry = author_relation_geometry(
        baseline.jacobian_loop,
        oracle_target,
    )
    oracle_swap_geometry = author_relation_geometry(
        compose_creation_only_loop(oracle_view.creation, baseline),
        oracle_target,
    )
    fisher_loop = compose_creation_only_loop(
        fisher.creation,
        baseline,
    )
    permuted_loop = compose_creation_only_loop(
        permuted.creation,
        baseline,
    )
    fisher_geometry = author_relation_geometry(
        fisher_loop,
        oracle_target,
    )
    permutation_geometry = author_relation_geometry(
        permuted_loop,
        oracle_target,
    )
    shift = np.linspace(
        -0.05,
        0.05,
        fisher.creation.shape[1] * fisher.creation.shape[2],
    ).reshape(fisher.creation.shape[1:])
    replay_difference = float(
        np.max(np.abs(selected.creation - baseline.creation))
    )
    return {
        "repetition": repetition,
        "world": world,
        "world_type": world_type,
        "view": view_name,
        "baseline_geometry": baseline_geometry,
        "oracle_swap_geometry": oracle_swap_geometry,
        "creation_headroom": (
            oracle_swap_geometry - baseline_geometry
        ),
        "fisher_geometry": fisher_geometry,
        "fisher_gain": fisher_geometry - baseline_geometry,
        "recovered_headroom": relative_headroom_recovery(
            baseline_geometry,
            fisher_geometry,
            oracle_swap_geometry,
        ),
        "permutation_geometry": permutation_geometry,
        "permutation_gain": (
            permutation_geometry - baseline_geometry
        ),
        "baseline_creation_geometry": author_relation_geometry(
            baseline.creation,
            oracle_view.creation,
        ),
        "fixed_creation_geometry": author_relation_geometry(
            full.creation,
            oracle_view.creation,
        ),
        "fisher_creation_geometry": author_relation_geometry(
            fisher.creation,
            oracle_view.creation,
        ),
        "selected_hazard_loss": float(
            np.mean(selected.evaluation_loss)
        ),
        "fixed_hazard_loss": float(
            np.mean(full.evaluation_loss)
        ),
        "fisher_hazard_loss": float(
            np.mean(fisher.evaluation_loss)
        ),
        "hazard_relative_degradation": float(
            np.mean(fisher.evaluation_loss)
            / max(float(np.mean(selected.evaluation_loss)), 1e-12)
            - 1.0
        ),
        "selected_physical_replay_max_difference": replay_difference,
        "common_creation_shift_geometry_error": abs(
            1.0
            - author_relation_geometry(
                fisher.creation,
                fisher.creation + shift[None],
            )
        ),
    }


def _gauge_difference(
    observed: Any,
    basis: dict[str, np.ndarray],
    routes: dict[str, Any],
    config: dict[str, Any],
    *,
    seed: int,
    permutation: np.ndarray,
) -> float:
    rotated_basis = rotate_whitened_basis(basis, seed=seed)
    rotated = _fit_routes(
        observed,
        rotated_basis,
        config,
        permutation=permutation,
    )
    differences = []
    for view_name in ("train", "test"):
        original_baseline = getattr(routes["baseline"], view_name)
        rotated_baseline = getattr(rotated["baseline"], view_name)
        original_fisher = getattr(routes["fisher"], view_name)
        rotated_fisher = getattr(rotated["fisher"], view_name)
        original_loop = compose_creation_only_loop(
            original_fisher.creation,
            original_baseline,
        )
        rotated_loop = compose_creation_only_loop(
            rotated_fisher.creation,
            rotated_baseline,
        )
        differences.extend(
            [
                float(
                    np.max(
                        np.abs(
                            original_fisher.creation
                            - rotated_fisher.creation
                        )
                    )
                ),
                float(np.max(np.abs(original_loop - rotated_loop))),
            ]
        )
    return max(differences)


def _confirmation_decision(
    metrics: pd.DataFrame,
    refusals: pd.DataFrame,
    *,
    gauge_difference: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    main = metrics[
        (metrics["world_type"] == "main")
        & (metrics["view"] == "test")
    ].copy()
    null = metrics[
        (metrics["world_type"] == "null")
        & (metrics["view"] == "test")
    ].copy()
    headroom_lcb = _cluster_lcb(
        main,
        "creation_headroom",
        seed=int(config["bootstrap_seed"]),
        repetitions=int(config["bootstrap_repetitions"]),
    )
    gain_lcb = _cluster_lcb(
        main,
        "fisher_gain",
        seed=int(config["bootstrap_seed"]) + 1,
        repetitions=int(config["bootstrap_repetitions"]),
    )
    mean_headroom = float(main["creation_headroom"].mean())
    mean_gain = float(main["fisher_gain"].mean())
    mean_geometry = float(main["fisher_geometry"].mean())
    recovered = (
        mean_gain / mean_headroom
        if mean_headroom > 1e-12
        else float("nan")
    )
    repetition = main.groupby("repetition", sort=True).agg(
        gain=("fisher_gain", "mean"),
        geometry=("fisher_geometry", "mean"),
    )
    positive_repetitions = int(
        (
            (repetition["gain"] > 0)
            & (
                repetition["geometry"]
                >= targets["minimum_fisher_geometry"]
            )
        ).sum()
    )
    null_false_rate = float(
        (
            (null["fisher_gain"] >= targets["minimum_fisher_gain"])
            & (
                null["fisher_geometry"]
                >= targets["minimum_fisher_geometry"]
            )
        ).mean()
    )
    hazard_degradation = float(
        main["fisher_hazard_loss"].mean()
        / max(main["selected_hazard_loss"].mean(), 1e-12)
        - 1.0
    )
    diagnostics = {
        "baseline_geometry": float(main["baseline_geometry"].mean()),
        "oracle_swap_geometry": float(
            main["oracle_swap_geometry"].mean()
        ),
        "creation_headroom": mean_headroom,
        "creation_headroom_lcb": headroom_lcb,
        "fisher_geometry": mean_geometry,
        "fisher_gain": mean_gain,
        "fisher_gain_lcb": gain_lcb,
        "recovered_headroom": recovered,
        "positive_repetitions": positive_repetitions,
        "permutation_gain": float(main["permutation_gain"].mean()),
        "null_false_success_rate": null_false_rate,
        "hazard_relative_degradation": hazard_degradation,
        "gauge_max_difference": gauge_difference,
        "refusal_rate": float(refusals["refused"].mean()),
        "selected_physical_replay_max_difference": float(
            metrics["selected_physical_replay_max_difference"].max()
        ),
        "common_creation_shift_geometry_error": float(
            metrics["common_creation_shift_geometry_error"].max()
        ),
        "baseline_creation_geometry": float(
            main["baseline_creation_geometry"].mean()
        ),
        "fisher_creation_geometry": float(
            main["fisher_creation_geometry"].mean()
        ),
    }
    checks = {
        "oracle_headroom": (
            diagnostics["creation_headroom"]
            >= targets["minimum_creation_headroom"]
            and diagnostics["creation_headroom_lcb"] > 0.0
        ),
        "fisher_gain": (
            diagnostics["fisher_gain"]
            >= targets["minimum_fisher_gain"]
            and diagnostics["fisher_gain_lcb"] > 0.0
        ),
        "absolute_geometry": (
            diagnostics["fisher_geometry"]
            >= targets["minimum_fisher_geometry"]
        ),
        "headroom_recovery": (
            diagnostics["recovered_headroom"]
            >= targets["minimum_recovered_headroom"]
        ),
        "repetition_stability": (
            diagnostics["positive_repetitions"]
            >= targets["minimum_positive_repetitions"]
        ),
        "hazard_noninferiority": (
            diagnostics["hazard_relative_degradation"]
            <= targets["maximum_hazard_relative_degradation"]
        ),
        "permutation_null": (
            diagnostics["permutation_gain"]
            <= targets["maximum_permutation_gain"]
        ),
        "no_creation_specificity": (
            diagnostics["null_false_success_rate"]
            <= targets["maximum_null_false_success_rate"]
        ),
        "gauge_invariance": (
            diagnostics["gauge_max_difference"]
            <= targets["maximum_gauge_difference"]
        ),
        "refusal_control": (
            diagnostics["refusal_rate"]
            >= targets["minimum_refusal_rate"]
        ),
        "implementation_replay": (
            diagnostics["selected_physical_replay_max_difference"]
            <= targets["maximum_replay_difference"]
        ),
        "common_shift_invariance": (
            diagnostics["common_creation_shift_geometry_error"]
            <= targets["maximum_common_shift_error"]
        ),
    }
    if all(checks.values()):
        decision_name = "M4_C32_GO_FISHER_WIENER_CREATION"
    elif checks["oracle_headroom"] and not checks["fisher_gain"]:
        decision_name = "M4_C32_NO_GO_OPPORTUNITY_BUDGET"
    elif checks["fisher_gain"] and not checks["hazard_noninferiority"]:
        decision_name = "M4_C32_RELATIONAL_GAIN_PREDICTIVE_RISK"
    else:
        decision_name = "M4_C32_NO_GO_FISHER_WIENER_CREATION"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision_name,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic, response-safe creation-estimator "
            "intervention only. A pass would identify recoverable stable "
            "author derivative structure under the registered opportunity "
            "budget. It would not identify personality, validate natural "
            "text, reopen M4-C.2, or authorize M4-D."
        ),
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> str:
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    world_table = (
        metrics[
            (metrics["world_type"] == "main")
            & (metrics["view"] == "test")
        ]
        .groupby("world", sort=True)[
            [
                "baseline_geometry",
                "fisher_geometry",
                "fisher_gain",
                "creation_headroom",
                "hazard_relative_degradation",
            ]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    return f"""# SUICA M4-C.3.2 Fisher-Wiener Creation Confirmation

## Decision

`{decision["decision"]}`

The discovered condition chart, physical response edge, physical choice edge,
and author-relation endpoint were frozen. Calibration occasions supplied two
technical creation estimates. A leave-one-author-out Fisher-Wiener operator
retained only their cross-half stable author covariance:

\\[
\\widehat L_u^{{FW}}=
\\widehat A_u^{{FW}}R_u^DD_u^D.
\\]

No oracle edge or final relation geometry was available to the estimator.

## Frozen design

- repetitions: `{config["repetitions"]}`
- main worlds: `{", ".join(config["main_worlds"])}`
- no-creation controls: `{", ".join(config["null_worlds"])}`
- refusal controls: `{", ".join(config["refusal_worlds"])}`
- hazard family: `{config["fisher_wiener"]["hazard_model"]}`
- epsilon scale: `{config["fisher_wiener"]["epsilon_scale"]}`

## Main-world results

{world_table}

## Diagnostics

{diagnostics}

## Gates

{checks}

## Boundary

{decision["claim_boundary"]}

M4-D remains blocked independently of this result.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            ROOT
            / "configs"
            / "m4_fisher_wiener_creation_confirmation.json"
        ),
    )
    args = parser.parse_args()
    config = _load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    chart_candidates = tuple(
        dict(value) for value in config["chart_candidates"]
    )
    route_parameters = _route_parameters(config)
    rows = []
    refusal_rows = []
    gauge_difference = 0.0

    worlds = [
        ("main", world) for world in config["main_worlds"]
    ] + [
        ("null", world) for world in config["null_worlds"]
    ]
    for repetition in range(int(config["repetitions"])):
        for world_index, (world_type, world) in enumerate(worlds):
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
                candidates=chart_candidates,
                **config["chart_thresholds"],
            )
            _, basis = build_m4_discovered_basis(
                observed,
                chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["maximum_rank"]),
            )
            rng = np.random.default_rng(
                int(config["permutation_seed"]) + seed
            )
            permutation = rng.permutation(spec.mechanism_authors)
            routes = _fit_routes(
                observed,
                basis,
                config,
                permutation=permutation,
            )
            oracle = fit_m4_physical_edge_route(
                observed.ecology,
                truth.oracle_basis,
                basis_name="oracle",
                **route_parameters,
            )
            for view_name in ("train", "test"):
                rows.append(
                    _metric_row(
                        repetition=repetition,
                        world=world,
                        world_type=world_type,
                        view_name=view_name,
                        oracle=oracle,
                        routes=routes,
                    )
                )
            if repetition == 0 and world_index == 0:
                gauge_difference = _gauge_difference(
                    observed,
                    basis,
                    routes,
                    config,
                    seed=seed + 800_009,
                    permutation=permutation,
                )

        for refusal_index, world in enumerate(
            config["refusal_worlds"]
        ):
            seed = int(
                config["refusal_seed"]
                + repetition * 1_000_003
                + refusal_index * 10_003
            )
            observed, _ = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            estimate = fit_m4_chart_ecology(
                observed,
                candidates=chart_candidates,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["maximum_rank"]),
                minimum_evaluation_coverage=float(
                    config["minimum_evaluation_coverage"]
                ),
                route_parameters=route_parameters,
                **config["chart_thresholds"],
            )
            refusal_rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "refused": bool(estimate.refused),
                    "reasons": "|".join(estimate.refusal_reasons),
                }
            )

    metrics = pd.DataFrame(rows)
    refusals = pd.DataFrame(refusal_rows)
    decision = _confirmation_decision(
        metrics,
        refusals,
        gauge_difference=gauge_difference,
        config=config,
    )
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    refusals.to_csv(output / "refusal_controls.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _report(decision, metrics, config),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
