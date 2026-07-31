#!/usr/bin/env python3
"""Run the M4-C.3.4 chart/observation/pooling attribution cube."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_opportunity_excitation_frontier import (  # noqa: E402
    _alias_audit,
    _cluster_lcb,
)
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
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
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
    compose_creation_only_loop,
)
from suica_core.m4_creation_residual_attribution import (  # noqa: E402
    M4CreationAttributionGrid,
    build_creation_attribution_grid,
    mobius_effects,
    shapley_effects,
)
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
    subset_opportunity_budget,
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


def _creation_parameters(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": str(config["creation_estimator"]["hazard_model"]),
        "ridge": float(config["route_estimator"]["hazard_ridge"]),
        "iterations": int(
            config["route_estimator"]["logistic_iterations"]
        ),
        "epsilon_scale": float(
            config["creation_estimator"]["epsilon_scale"]
        ),
        "maximum_source_overlap_rate": float(
            config["creation_estimator"]["maximum_source_overlap_rate"]
        ),
    }


def _select_route(
    grid: M4CreationAttributionGrid,
    s: int,
    p: int,
) -> Any:
    if s == 0 and p == 0:
        return grid.current_pooled
    if s == 0 and p == 1:
        return grid.current_local
    if s == 1 and p == 0:
        return grid.complete_pooled
    return grid.complete_local


def _metric_rows(
    *,
    repetition: int,
    world: str,
    world_type: str,
    grids: dict[int, M4CreationAttributionGrid],
    anchor: Any,
    oracle: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metric_rows = []
    decomposition_rows = []
    for view_name in ("train", "test"):
        anchor_view = getattr(anchor, view_name)
        oracle_view = getattr(oracle, view_name)
        target = oracle_view.jacobian_loop
        oracle_loop = compose_creation_only_loop(
            oracle_view.creation,
            anchor_view,
        )
        oracle_geometry = author_relation_geometry(oracle_loop, target)
        geometries: dict[tuple[int, int, int], float] = {}
        loops: dict[tuple[int, int, int], np.ndarray] = {}
        routes: dict[tuple[int, int, int], Any] = {}
        for c in (0, 1):
            for s in (0, 1):
                for p in (0, 1):
                    route = _select_route(grids[c], s, p)
                    view = getattr(route, view_name)
                    loop = compose_creation_only_loop(
                        view.creation,
                        anchor_view,
                    )
                    key = (c, s, p)
                    loops[key] = loop
                    routes[key] = route
                    geometries[key] = author_relation_geometry(loop, target)
        baseline_geometry = geometries[(0, 0, 0)]
        headroom = oracle_geometry - baseline_geometry
        for key, geometry in geometries.items():
            c, s, p = key
            route = routes[key]
            view = getattr(route, view_name)
            flattened = view.creation.reshape(len(view.creation), -1)
            shift = np.linspace(
                -0.05,
                0.05,
                flattened.shape[1],
            ).reshape(1, -1)
            shift_error = float(
                np.max(np.abs(
                    pdist(flattened + shift) - pdist(flattened)
                ))
            )
            metric_rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "world_type": world_type,
                    "view": view_name,
                    "c": c,
                    "s": s,
                    "p": p,
                    "geometry": geometry,
                    "baseline_geometry": baseline_geometry,
                    "oracle_swap_geometry": oracle_geometry,
                    "oracle_headroom": headroom,
                    "geometry_gain": geometry - baseline_geometry,
                    "recovered_headroom": (
                        (geometry - baseline_geometry) / headroom
                        if headroom > 1e-12
                        else float("nan")
                    ),
                    "evaluation_loss": float(
                        np.mean(view.evaluation_loss)
                    ),
                    "comparable_hazard_loss": float(
                        np.mean(view.comparable_hazard_loss)
                    ),
                    "joint_information_minimum": float(
                        np.median(view.joint_information_minimum)
                    ),
                    "joint_information_full_rank_coverage": float(
                        np.mean(view.joint_information_full_rank)
                    ),
                    "source_at_risk_coverage": float(
                        np.mean(view.source_at_risk_valid)
                    ),
                    "source_route_used": bool(route.source_route_used),
                    "common_shift_distance_error": shift_error,
                }
            )
        mobius = mobius_effects(geometries)
        shapley = shapley_effects(geometries)
        observation_effect = float(np.mean([
            geometries[(c, 1, p)] - geometries[(c, 0, p)]
            for c in (0, 1)
            for p in (0, 1)
        ]))
        decomposition_rows.append(
            {
                "repetition": repetition,
                "world": world,
                "world_type": world_type,
                "view": view_name,
                "baseline_geometry": baseline_geometry,
                "full_geometry": geometries[(1, 1, 1)],
                "oracle_swap_geometry": oracle_geometry,
                "oracle_headroom": headroom,
                "full_gain": geometries[(1, 1, 1)] - baseline_geometry,
                "full_recovered_headroom": (
                    (geometries[(1, 1, 1)] - baseline_geometry) / headroom
                    if headroom > 1e-12
                    else float("nan")
                ),
                "observation_main_effect": observation_effect,
                **{
                    f"mobius_{name}": value
                    for name, value in mobius.items()
                },
                **{
                    f"shapley_{name}": value
                    for name, value in shapley.items()
                },
            }
        )
    return metric_rows, decomposition_rows


def _cluster_values(
    frame: pd.DataFrame,
    column: str,
) -> np.ndarray:
    return (
        frame.groupby("repetition", sort=True)[column]
        .mean()
        .to_numpy(dtype=float)
    )


def _decision(
    metrics: pd.DataFrame,
    decomposition: pd.DataFrame,
    controls: pd.DataFrame,
    aliases: pd.DataFrame,
    *,
    gauge_difference: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    main = decomposition[
        (decomposition["view"] == "test")
        & (decomposition["world_type"] == "main")
    ].copy()
    target = main[main["world"].isin(config["target_worlds"])]
    other = main[~main["world"].isin(config["target_worlds"])]
    full = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
        & (metrics["c"] == 1)
        & (metrics["s"] == 1)
        & (metrics["p"] == 1)
    ]
    baseline = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
        & (metrics["c"] == 0)
        & (metrics["s"] == 0)
        & (metrics["p"] == 0)
    ]
    headroom_by_repetition = _cluster_values(main, "oracle_headroom")
    observation_by_repetition = _cluster_values(
        target,
        "observation_main_effect",
    )
    full_gain = float(main["full_gain"].mean())
    headroom = float(main["oracle_headroom"].mean())
    full_recovered = (
        full_gain / headroom if headroom > 1e-12 else float("nan")
    )
    target_recovery = {}
    for world, values in target.groupby("world", sort=True):
        denominator = float(values["oracle_headroom"].mean())
        target_recovery[str(world)] = (
            float(values["full_gain"].mean()) / denominator
            if denominator > 1e-12
            else float("nan")
        )
    shapley_means = {
        factor: float(main[f"shapley_{factor}"].mean())
        for factor in ("C", "S", "P")
    }
    leading_factor = max(shapley_means, key=shapley_means.get)
    runner_up = max(
        (factor for factor in shapley_means if factor != leading_factor),
        key=shapley_means.get,
    )
    margin_by_repetition = (
        main.groupby("repetition", sort=True)[
            [f"shapley_{leading_factor}", f"shapley_{runner_up}"]
        ]
        .mean()
    )
    margin = (
        margin_by_repetition[f"shapley_{leading_factor}"]
        - margin_by_repetition[f"shapley_{runner_up}"]
    ).to_numpy(dtype=float)
    source_rows = full[
        full["world"] == "endogenous_source_partition_matched"
    ]
    null = decomposition[
        (decomposition["view"] == "test")
        & (decomposition["world_type"] == "null")
    ]
    null_false_rate = float(
        (
            (null["full_gain"] >= 0.03)
            & (null["full_geometry"] >= 0.70)
        ).mean()
    )
    hazard_degradation = float(
        full["comparable_hazard_loss"].mean()
        / max(baseline["comparable_hazard_loss"].mean(), 1e-12)
        - 1.0
    )
    other_world_degradation = (
        float(other["full_gain"].mean())
        if len(other)
        else 0.0
    )
    diagnostics = {
        "oracle_headroom": headroom,
        "oracle_headroom_lcb": _cluster_lcb(
            headroom_by_repetition,
            seed=int(config["bootstrap_seed"]),
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "joint_information_full_rank_coverage": float(
            full["joint_information_full_rank_coverage"].mean()
        ),
        "source_at_risk_coverage": float(
            source_rows["source_at_risk_coverage"].mean()
        ),
        "observation_main_effect": float(
            target["observation_main_effect"].mean()
        ),
        "observation_main_effect_lcb": _cluster_lcb(
            observation_by_repetition,
            seed=int(config["bootstrap_seed"]) + 1,
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "observation_positive_repetitions": int(
            np.sum(observation_by_repetition > 0.0)
        ),
        "full_recovered_headroom": full_recovered,
        "target_world_recovered_headroom": target_recovery,
        "other_world_degradation": other_world_degradation,
        "shapley_means": shapley_means,
        "leading_shapley_factor": leading_factor,
        "shapley_leading_margin": float(np.mean(margin)),
        "shapley_leading_margin_lcb": _cluster_lcb(
            margin,
            seed=int(config["bootstrap_seed"]) + 2,
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "hazard_relative_degradation": hazard_degradation,
        "permutation_gain": float(
            controls["permutation_gain"].mean()
        ),
        "null_false_success_rate": null_false_rate,
        "gauge_max_difference": gauge_difference,
        "common_shift_distance_error": float(
            metrics["common_shift_distance_error"].max()
        ),
        "truth_open_alias_rate": float(
            aliases["truth_open_alias_information_loss"].mean()
        ),
    }
    checks = {
        "oracle_headroom": (
            diagnostics["oracle_headroom"]
            >= targets["minimum_oracle_headroom"]
            and diagnostics["oracle_headroom_lcb"] > 0.0
        ),
        "joint_information": (
            diagnostics["joint_information_full_rank_coverage"]
            >= targets["minimum_joint_information_coverage"]
        ),
        "source_at_risk": (
            diagnostics["source_at_risk_coverage"]
            >= targets["minimum_source_at_risk_coverage"]
        ),
        "observation_main_effect": (
            diagnostics["observation_main_effect"]
            >= targets["minimum_observation_main_effect"]
            and diagnostics["observation_main_effect_lcb"] > 0.0
            and diagnostics["observation_positive_repetitions"]
            >= targets["minimum_observation_positive_repetitions"]
        ),
        "full_recovery": (
            diagnostics["full_recovered_headroom"]
            >= targets["minimum_full_recovered_headroom"]
        ),
        "target_world_recovery": (
            min(diagnostics["target_world_recovered_headroom"].values())
            >= targets["minimum_target_world_recovered_headroom"]
        ),
        "other_world_noninferiority": (
            diagnostics["other_world_degradation"]
            >= -targets["maximum_other_world_degradation"]
        ),
        "shapley_identifiability": (
            diagnostics["shapley_leading_margin_lcb"] > 0.0
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
        "common_shift_invariance": (
            diagnostics["common_shift_distance_error"]
            <= targets["maximum_common_shift_error"]
        ),
        "truth_open_alias": (
            diagnostics["truth_open_alias_rate"]
            >= targets["minimum_alias_information_loss_rate"]
        ),
    }
    if all(checks.values()):
        decision = "M4_C34_GO_OBSERVATION_LAW_DOMINANT"
    elif not checks["full_recovery"]:
        decision = "M4_C34_NO_GO_THREE_FACTOR_INCOMPLETE"
    elif not checks["observation_main_effect"]:
        decision = "M4_C34_NO_GO_OBSERVATION_LAW"
    else:
        decision = "M4_C34_PARTIAL_ATTRIBUTION"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic chart/observation/pooling attribution only. "
            "Oracle-chart cells are diagnostic and nondeployable. The result "
            "cannot identify personality, validate natural text, close "
            "M4-C.2, or authorize M4-D."
        ),
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    decomposition: pd.DataFrame,
) -> str:
    test = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
    ]
    cells = (
        test.groupby(["c", "s", "p"], sort=True)[
            ["geometry", "geometry_gain", "recovered_headroom"]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    worlds = (
        decomposition[
            (decomposition["view"] == "test")
            & (decomposition["world_type"] == "main")
        ]
        .groupby("world", sort=True)[
            [
                "baseline_geometry",
                "full_geometry",
                "oracle_headroom",
                "full_recovered_headroom",
                "observation_main_effect",
                "shapley_C",
                "shapley_S",
                "shapley_P",
            ]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4-C.3.4 Creation Residual Attribution

## Decision

`{decision["decision"]}`

The high-information `K=8 excitation` endpoint was fixed. The diagnostic cube
crossed discovered/oracle chart (`C`), current joint/target-aligned
history-stratified hurdle likelihood (`S`), and Fisher-Wiener
pooled/author-local fit (`P`). Every cell estimates the same gate-zero direct
creation derivative. Oracle chart cells are truth-open attribution controls
and are not deployable.

## Cell means

{cells}

## World decomposition

{worlds}

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
        default=ROOT / "configs" / "m4_creation_residual_attribution.json",
    )
    parser.add_argument("--repetition-limit", type=int)
    parser.add_argument("--repetition-start", type=int, default=0)
    parser.add_argument("--main-world-limit", type=int)
    parser.add_argument("--null-world-limit", type=int)
    parser.add_argument("--output-directory")
    parser.add_argument("--report-path")
    args = parser.parse_args()
    config = _load(args.config)
    if args.repetition_limit is not None:
        config["repetitions"] = args.repetition_limit
    if args.main_world_limit is not None:
        config["main_worlds"] = config["main_worlds"][
            : args.main_world_limit
        ]
    if args.null_world_limit is not None:
        config["null_worlds"] = config["null_worlds"][
            : args.null_world_limit
        ]
    if args.output_directory is not None:
        config["output_directory"] = args.output_directory
    if args.report_path is not None:
        config["report_path"] = args.report_path

    spec = M4ChartEcologySpec(**config["base_spec"])
    alias_spec = M4ChartEcologySpec(**config["alias_spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    route_parameters = _route_parameters(config)
    creation_parameters = _creation_parameters(config)
    worlds = [
        ("main", world) for world in config["main_worlds"]
    ] + [
        ("null", world) for world in config["null_worlds"]
    ]
    rows: list[dict[str, Any]] = []
    decomposition_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    alias_rows: list[dict[str, Any]] = []
    gauge_difference = 0.0
    repetition_start = int(args.repetition_start)
    repetition_stop = repetition_start + int(config["repetitions"])

    for repetition in range(repetition_start, repetition_stop):
        for world_index, (world_type, world) in enumerate(worlds):
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            passive, truth = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            excited = build_excited_observed(
                passive,
                truth,
                spec,
                seed=seed,
                amplitude=float(config["excitation_amplitude"]),
            )
            chart = fit_m4_condition_chart(
                passive.condition,
                candidates=candidates,
                **config["chart_thresholds"],
            )
            _, discovered_basis = build_m4_discovered_basis(
                passive,
                chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["maximum_rank"]),
            )
            anchor_observed = subset_opportunity_budget(
                passive,
                calibration_occasions=int(
                    config["anchor_budget"]["calibration"]
                ),
                selection_occasions=int(
                    config["anchor_budget"]["selection"]
                ),
            )
            anchor = fit_m4_physical_edge_route(
                anchor_observed.ecology,
                discovered_basis,
                basis_name="anchor_discovered",
                **route_parameters,
            )
            oracle = fit_m4_physical_edge_route(
                passive.ecology,
                truth.oracle_basis,
                basis_name="oracle_max_passive",
                **route_parameters,
            )
            grids = {
                0: build_creation_attribution_grid(
                    excited.ecology,
                    discovered_basis,
                    **creation_parameters,
                ),
                1: build_creation_attribution_grid(
                    excited.ecology,
                    truth.oracle_basis,
                    **creation_parameters,
                ),
            }
            metric, decomposition = _metric_rows(
                repetition=repetition,
                world=world,
                world_type=world_type,
                grids=grids,
                anchor=anchor,
                oracle=oracle,
            )
            rows.extend(metric)
            decomposition_rows.extend(decomposition)

            rng = np.random.default_rng(
                int(config["permutation_seed"]) + seed
            )
            permutation = rng.permutation(spec.mechanism_authors)
            permuted_grid = build_creation_attribution_grid(
                excited.ecology,
                truth.oracle_basis,
                **creation_parameters,
                second_permutation=permutation,
            )
            for view_name in ("train", "test"):
                target = getattr(oracle, view_name).jacobian_loop
                anchor_view = getattr(anchor, view_name)
                permuted = getattr(
                    permuted_grid.complete_pooled,
                    view_name,
                )
                current = getattr(grids[1].current_pooled, view_name)
                permuted_geometry = author_relation_geometry(
                    compose_creation_only_loop(
                        permuted.creation,
                        anchor_view,
                    ),
                    target,
                )
                current_geometry = author_relation_geometry(
                    compose_creation_only_loop(
                        current.creation,
                        anchor_view,
                    ),
                    target,
                )
                control_rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "world_type": world_type,
                        "view": view_name,
                        "permutation_gain": (
                            permuted_geometry - current_geometry
                        ),
                    }
                )

            if repetition == repetition_start and world_index == 0:
                rotated_basis = rotate_whitened_basis(
                    discovered_basis,
                    seed=seed + 800_009,
                )
                rotated_anchor = fit_m4_physical_edge_route(
                    anchor_observed.ecology,
                    rotated_basis,
                    basis_name="rotated_anchor",
                    **route_parameters,
                )
                rotated_grid = build_creation_attribution_grid(
                    excited.ecology,
                    rotated_basis,
                    **creation_parameters,
                )
                differences = []
                for view_name in ("train", "test"):
                    original = getattr(
                        grids[0].complete_pooled,
                        view_name,
                    )
                    rotated = getattr(
                        rotated_grid.complete_pooled,
                        view_name,
                    )
                    original_loop = compose_creation_only_loop(
                        original.creation,
                        getattr(anchor, view_name),
                    )
                    rotated_loop = compose_creation_only_loop(
                        rotated.creation,
                        getattr(rotated_anchor, view_name),
                    )
                    differences.extend(
                        [
                            float(np.max(np.abs(
                                original.creation - rotated.creation
                            ))),
                            float(np.max(np.abs(
                                original_loop - rotated_loop
                            ))),
                        ]
                    )
                gauge_difference = max(differences)
        alias_rows.append(
            _alias_audit(
                repetition=repetition,
                config=config,
                spec=alias_spec,
                candidates=candidates,
            )
        )

    metrics = pd.DataFrame(rows)
    decomposition = pd.DataFrame(decomposition_rows)
    controls = pd.DataFrame(control_rows)
    aliases = pd.DataFrame(alias_rows)
    decision = _decision(
        metrics,
        decomposition,
        controls[
            (controls["view"] == "test")
            & (controls["world_type"] == "main")
        ],
        aliases,
        gauge_difference=gauge_difference,
        config=config,
    )
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    decomposition.to_csv(output / "decomposition.csv", index=False)
    controls.to_csv(output / "controls.csv", index=False)
    aliases.to_csv(output / "alias_audit.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _report(decision, metrics, decomposition),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
