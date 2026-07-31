#!/usr/bin/env python3
"""Run the M4-C.3.3 opportunity-excitation information frontier."""
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

from suica_core.m4_chart_ecology_audit import (  # noqa: E402
    audit_m4_chart_ecology,
)
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
    fit_m4_chart_ecology,
    fit_m4_chart_ecology_route,
    rotate_whitened_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)
from suica_core.m4_creation_information import (  # noqa: E402
    creation_information_route,
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


def _fixed_parameters(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": str(config["fisher_wiener"]["hazard_model"]),
        "ridge": float(config["route_estimator"]["hazard_ridge"]),
        "iterations": int(
            config["route_estimator"]["logistic_iterations"]
        ),
    }


def _fit_arm(
    observed: Any,
    basis: dict[str, np.ndarray],
    config: dict[str, Any],
    *,
    permutation: np.ndarray,
) -> dict[str, Any]:
    fixed_parameters = _fixed_parameters(config)
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
    information = creation_information_route(
        observed.ecology,
        basis,
        full,
    )
    return {
        "selected": selected,
        "full": full,
        "fisher": fisher,
        "permuted": permuted,
        "information": information,
    }


def _metric_row(
    *,
    repetition: int,
    world: str,
    world_type: str,
    intervention: str,
    budget: dict[str, int],
    view_name: str,
    arm: dict[str, Any],
    anchor: Any,
    oracle: Any,
) -> dict[str, Any]:
    selected = getattr(arm["selected"], view_name)
    fisher = getattr(arm["fisher"], view_name)
    permuted = getattr(arm["permuted"], view_name)
    information = getattr(arm["information"], view_name)
    anchor_view = getattr(anchor, view_name)
    oracle_view = getattr(oracle, view_name)
    target = oracle_view.jacobian_loop
    baseline_loop = compose_creation_only_loop(
        selected.creation,
        anchor_view,
    )
    fisher_loop = compose_creation_only_loop(
        fisher.creation,
        anchor_view,
    )
    permuted_loop = compose_creation_only_loop(
        permuted.creation,
        anchor_view,
    )
    oracle_swap = compose_creation_only_loop(
        oracle_view.creation,
        anchor_view,
    )
    baseline_geometry = author_relation_geometry(baseline_loop, target)
    fisher_geometry = author_relation_geometry(fisher_loop, target)
    permutation_geometry = author_relation_geometry(
        permuted_loop,
        target,
    )
    creation_headroom = (
        author_relation_geometry(oracle_swap, target)
        - baseline_geometry
    )
    shift = np.linspace(
        -0.05,
        0.05,
        fisher.creation.shape[1] * fisher.creation.shape[2],
    ).reshape(1, -1)
    flattened = fisher.creation.reshape(len(fisher.creation), -1)
    shift_error = float(
        np.max(
            np.abs(
                pdist(flattened + shift) - pdist(flattened)
            )
        )
    )
    return {
        "repetition": repetition,
        "world": world,
        "world_type": world_type,
        "view": view_name,
        "intervention": intervention,
        "k": int(budget["k"]),
        "calibration_occasions": int(budget["calibration"]),
        "selection_occasions": int(budget["selection"]),
        "baseline_geometry": baseline_geometry,
        "oracle_swap_geometry": author_relation_geometry(
            oracle_swap,
            target,
        ),
        "creation_headroom": creation_headroom,
        "fisher_geometry": fisher_geometry,
        "fisher_gain": fisher_geometry - baseline_geometry,
        "recovered_headroom": relative_headroom_recovery(
            baseline_geometry,
            fisher_geometry,
            author_relation_geometry(oracle_swap, target),
        ),
        "permutation_gain": (
            permutation_geometry - baseline_geometry
        ),
        "selected_hazard_loss": float(
            np.mean(selected.evaluation_loss)
        ),
        "fisher_hazard_loss": float(
            np.mean(fisher.evaluation_loss)
        ),
        "hazard_relative_degradation": float(
            np.mean(fisher.evaluation_loss)
            / max(float(np.mean(selected.evaluation_loss)), 1e-12)
            - 1.0
        ),
        "fisher_minimum_information": float(
            np.median(information.minimum_positive_eigenvalue)
        ),
        "fisher_information_trace": float(
            np.median(information.trace)
        ),
        "fisher_information_effective_rank": float(
            np.median(information.effective_rank)
        ),
        "fisher_information_condition_number": float(
            np.median(information.condition_number)
        ),
        "common_shift_distance_error": shift_error,
    }


def _cluster_lcb(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> float:
    vector = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(
        vector,
        size=(repetitions, len(vector)),
        replace=True,
    )
    return float(np.quantile(np.mean(draws, axis=1), 0.025))


def _dose_slopes(frame: pd.DataFrame) -> np.ndarray:
    rows = []
    for repetition, repeated in frame.groupby("repetition", sort=True):
        numerator = 0.0
        denominator = 0.0
        for _, values in repeated.groupby("world", sort=True):
            x = np.log(
                np.maximum(
                    values["fisher_minimum_information"].to_numpy(
                        dtype=float
                    ),
                    1e-12,
                )
            )
            y = values["fisher_geometry"].to_numpy(dtype=float)
            x = x - np.mean(x)
            y = y - np.mean(y)
            numerator += float(x @ y)
            denominator += float(x @ x)
        rows.append(
            {
                "repetition": int(repetition),
                "slope": numerator / max(denominator, 1e-12),
            }
        )
    return pd.DataFrame(rows)["slope"].to_numpy(dtype=float)


def _paired_endpoint_values(
    frame: pd.DataFrame,
    column: str,
    *,
    low: tuple[int, str],
    high: tuple[int, str],
    ratio: bool = False,
) -> np.ndarray:
    index = ["repetition", "world"]
    pivot = frame.pivot_table(
        index=index,
        columns=["k", "intervention"],
        values=column,
        aggfunc="mean",
    )
    left = pivot[low].to_numpy(dtype=float)
    right = pivot[high].to_numpy(dtype=float)
    values = (
        right / np.maximum(left, 1e-12)
        if ratio
        else right - left
    )
    repeated = pd.DataFrame(
        {
            "repetition": pivot.index.get_level_values("repetition"),
            "value": values,
        }
    )
    return (
        repeated.groupby("repetition", sort=True)["value"]
        .mean()
        .to_numpy(dtype=float)
    )


def _alias_audit(
    *,
    repetition: int,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    candidates: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    seed = int(config["alias_seed"] + repetition * 1_000_003)
    observed, truth = generate_m4_chart_ecology_world(
        world="condition_alias_ecology",
        spec=spec,
        seed=seed,
    )
    route_parameters = _route_parameters(config)
    estimate = fit_m4_chart_ecology(
        observed,
        candidates=candidates,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=int(config["maximum_rank"]),
        minimum_evaluation_coverage=float(
            config["minimum_evaluation_coverage"]
        ),
        route_parameters=route_parameters,
        **config["chart_thresholds"],
    )
    oracle = fit_m4_chart_ecology_route(
        observed.ecology,
        truth.oracle_basis,
        basis_name="oracle",
        **route_parameters,
    )
    audit = audit_m4_chart_ecology(
        estimate,
        oracle,
        truth,
        basis_action_invariant=True,
        response_perturbation_invariant=True,
        alias_bootstrap_seed=seed + 900_001,
        **config["alias_audit"],
    )
    return {
        "repetition": repetition,
        "truth_open_alias_information_loss": audit[
            "truth_open_alias_information_loss"
        ],
        "alias_oracle_skill": audit["alias_oracle_skill"],
        "alias_skill_gap": audit["alias_skill_gap"],
        "alias_retained_ratio": audit["alias_retained_ratio"],
        "alias_gap_lcb": audit["alias_skill_gap_lcb"],
    }


def _decision(
    metrics: pd.DataFrame,
    aliases: pd.DataFrame,
    *,
    gauge_difference: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    test_main = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
    ].copy()
    test_null = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "null")
    ].copy()
    low_key = (
        int(config["budget_grid"][0]["k"]),
        "passive",
    )
    high_key = (
        int(config["budget_grid"][-1]["k"]),
        "excitation",
    )
    information_ratios = _paired_endpoint_values(
        test_main,
        "fisher_minimum_information",
        low=low_key,
        high=high_key,
        ratio=True,
    )
    geometry_deltas = _paired_endpoint_values(
        test_main,
        "fisher_geometry",
        low=low_key,
        high=high_key,
    )
    slopes = _dose_slopes(test_main)
    high = test_main[
        (test_main["k"] == high_key[0])
        & (test_main["intervention"] == high_key[1])
    ]
    high_headroom = float(high["creation_headroom"].mean())
    high_gain = float(high["fisher_gain"].mean())
    recovered = (
        high_gain / high_headroom
        if high_headroom > 1e-12
        else float("nan")
    )
    repetition = high.groupby("repetition", sort=True).agg(
        gain=("fisher_gain", "mean"),
        geometry=("fisher_geometry", "mean"),
    )
    positive_repetitions = int(
        (
            (repetition["gain"] > 0)
            & (
                repetition["geometry"]
                >= targets["minimum_endpoint_geometry"]
            )
        ).sum()
    )
    null_endpoint = test_null[
        (test_null["k"] == high_key[0])
        & (test_null["intervention"] == high_key[1])
    ]
    null_false_rate = float(
        (
            (null_endpoint["fisher_gain"] >= 0.03)
            & (
                null_endpoint["fisher_geometry"]
                >= targets["minimum_endpoint_geometry"]
            )
        ).mean()
    )
    hazard_degradation = float(
        high["fisher_hazard_loss"].mean()
        / max(high["selected_hazard_loss"].mean(), 1e-12)
        - 1.0
    )
    diagnostics = {
        "information_ratio": float(np.mean(information_ratios)),
        "information_ratio_lcb": _cluster_lcb(
            information_ratios,
            seed=int(config["bootstrap_seed"]),
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "geometry_log_information_slope": float(np.mean(slopes)),
        "geometry_log_information_slope_lcb": _cluster_lcb(
            slopes,
            seed=int(config["bootstrap_seed"]) + 1,
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "endpoint_geometry_delta": float(np.mean(geometry_deltas)),
        "endpoint_geometry_delta_lcb": _cluster_lcb(
            geometry_deltas,
            seed=int(config["bootstrap_seed"]) + 2,
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "high_endpoint_geometry": float(high["fisher_geometry"].mean()),
        "high_endpoint_gain": high_gain,
        "high_recovered_headroom": recovered,
        "positive_repetitions": positive_repetitions,
        "hazard_relative_degradation": hazard_degradation,
        "permutation_gain": float(high["permutation_gain"].mean()),
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
        "information_amplification": (
            diagnostics["information_ratio"]
            >= targets["minimum_information_ratio"]
            and diagnostics["information_ratio_lcb"] > 1.0
        ),
        "dose_response": (
            diagnostics["geometry_log_information_slope_lcb"] > 0.0
        ),
        "endpoint_gain": (
            diagnostics["endpoint_geometry_delta"]
            >= targets["minimum_endpoint_delta"]
            and diagnostics["endpoint_geometry_delta_lcb"] > 0.0
        ),
        "headroom_recovery": (
            diagnostics["high_recovered_headroom"]
            >= targets["minimum_recovered_headroom"]
        ),
        "absolute_geometry": (
            diagnostics["high_endpoint_geometry"]
            >= targets["minimum_endpoint_geometry"]
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
        decision_name = "M4_C33_GO_INFORMATION_LIMITED_CREATION"
    elif (
        checks["information_amplification"]
        and (
            not checks["dose_response"]
            or not checks["headroom_recovery"]
        )
    ):
        decision_name = "M4_C33_NO_GO_INFORMATION_LIMIT"
    else:
        decision_name = "M4_C33_UNDERPOWERED_EXCITATION"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision_name,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic creation-information frontier only. It can "
            "distinguish an opportunity/excitation information limit from "
            "persistent chart, model, or author-heterogeneity error. It "
            "cannot identify personality, validate natural text, reopen "
            "M4-C.2, or authorize M4-D."
        ),
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> str:
    test = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
    ]
    table = (
        test.groupby(["k", "intervention"], sort=True)[
            [
                "fisher_minimum_information",
                "baseline_geometry",
                "fisher_geometry",
                "fisher_gain",
                "recovered_headroom",
                "hazard_relative_degradation",
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
    return f"""# SUICA M4-C.3.3 Opportunity-Excitation Information Frontier

## Decision

`{decision["decision"]}`

The chart, Fisher-Wiener formula, author population, frozen response/choice
edge, and natural evaluation endpoint were held constant. Calibration
information followed the preregistered grid

\\[
K\\in\\{{1,2,4,8\\}},\\qquad
I\\in\\{{passive, orthogonal\\ excitation\\}}.
\\]

Each excitation path used balanced zero-mean signed response probes inside the
generator; creation outcomes and downstream paths were regenerated by the
same planted mechanism. Evaluation remained natural.

## Arm summary

{table}

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
            / "m4_opportunity_excitation_frontier.json"
        ),
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
    max_budget = config["budget_grid"][-1]
    spec = M4ChartEcologySpec(
        **{
            **config["base_spec"],
            "calibration_occasions": int(max_budget["calibration"]),
            "selection_occasions": int(max_budget["selection"]),
        }
    )
    candidates = tuple(
        dict(value) for value in config["chart_candidates"]
    )
    route_parameters = _route_parameters(config)
    rows = []
    alias_rows = []
    gauge_difference = 0.0
    worlds = [
        ("main", world) for world in config["main_worlds"]
    ] + [
        ("null", world) for world in config["null_worlds"]
    ]

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
            _, basis = build_m4_discovered_basis(
                passive,
                chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["maximum_rank"]),
            )
            oracle = fit_m4_physical_edge_route(
                passive.ecology,
                truth.oracle_basis,
                basis_name="oracle_max_passive",
                **route_parameters,
            )
            anchor_observed = subset_opportunity_budget(
                passive,
                calibration_occasions=int(
                    config["budget_grid"][0]["calibration"]
                ),
                selection_occasions=int(
                    config["budget_grid"][0]["selection"]
                ),
            )
            anchor = fit_m4_physical_edge_route(
                anchor_observed.ecology,
                basis,
                basis_name="anchor_k1_passive",
                **route_parameters,
            )
            rng = np.random.default_rng(
                int(config["permutation_seed"]) + seed
            )
            permutation = rng.permutation(spec.mechanism_authors)
            arm_cache: dict[tuple[int, str], tuple[Any, dict[str, Any]]] = {}
            arm_specs = (
                [
                    (intervention, source, budget)
                    for intervention, source in (
                        ("passive", passive),
                        ("excitation", excited),
                    )
                    for budget in config["budget_grid"]
                ]
                if world_type == "main"
                else [
                    (
                        "excitation",
                        excited,
                        config["budget_grid"][-1],
                    )
                ]
            )
            for intervention, source, budget in arm_specs:
                    observed = subset_opportunity_budget(
                        source,
                        calibration_occasions=int(budget["calibration"]),
                        selection_occasions=int(budget["selection"]),
                    )
                    arm = _fit_arm(
                        observed,
                        basis,
                        config,
                        permutation=permutation,
                    )
                    arm_cache[(int(budget["k"]), intervention)] = (
                        observed,
                        arm,
                    )
                    for view_name in ("train", "test"):
                        rows.append(
                            _metric_row(
                                repetition=repetition,
                                world=world,
                                world_type=world_type,
                                intervention=intervention,
                                budget=budget,
                                view_name=view_name,
                                arm=arm,
                                anchor=anchor,
                                oracle=oracle,
                            )
                        )
            if repetition == 0 and world_index == 0:
                high_key = (
                    int(config["budget_grid"][-1]["k"]),
                    "excitation",
                )
                high_observed, high_arm = arm_cache[high_key]
                rotated_basis = rotate_whitened_basis(
                    basis,
                    seed=seed + 800_009,
                )
                rotated_anchor = fit_m4_physical_edge_route(
                    anchor_observed.ecology,
                    rotated_basis,
                    basis_name="rotated_anchor",
                    **route_parameters,
                )
                rotated_high = _fit_arm(
                    high_observed,
                    rotated_basis,
                    config,
                    permutation=permutation,
                )
                differences = []
                for view_name in ("train", "test"):
                    original_fisher = getattr(
                        high_arm["fisher"],
                        view_name,
                    )
                    rotated_fisher = getattr(
                        rotated_high["fisher"],
                        view_name,
                    )
                    original_loop = compose_creation_only_loop(
                        original_fisher.creation,
                        getattr(anchor, view_name),
                    )
                    rotated_loop = compose_creation_only_loop(
                        rotated_fisher.creation,
                        getattr(rotated_anchor, view_name),
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
                            float(
                                np.max(
                                    np.abs(
                                        original_loop - rotated_loop
                                    )
                                )
                            ),
                        ]
                    )
                gauge_difference = max(differences)
        alias_spec = M4ChartEcologySpec(**config["alias_spec"])
        alias_rows.append(
            _alias_audit(
                repetition=repetition,
                config=config,
                spec=alias_spec,
                candidates=candidates,
            )
        )

    metrics = pd.DataFrame(rows)
    aliases = pd.DataFrame(alias_rows)
    decision = _decision(
        metrics,
        aliases,
        gauge_difference=gauge_difference,
        config=config,
    )
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    aliases.to_csv(output / "alias_audit.csv", index=False)
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
