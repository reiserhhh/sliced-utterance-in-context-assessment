#!/usr/bin/env python3
"""Run M4-C.3 physical-edge composition discovery."""
from __future__ import annotations

import argparse
from itertools import combinations
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    EDGE_NAMES,
    M4PhysicalEdgeRoute,
    M4PhysicalEdgeView,
    edge_error_budget,
    fit_m4_physical_edge_route,
    inject_physical_edge_fault,
    mixed_physical_loops,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float).ravel()
    y = np.asarray(second, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else 0.0


def _geometry(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float).reshape(len(first), -1)
    y = np.asarray(second, dtype=float).reshape(len(second), -1)
    return _safe_spearman(pdist(x), pdist(y))


def _subset_key(subset: frozenset[str]) -> str:
    return "".join(
        "D" if edge in subset else "O"
        for edge in EDGE_NAMES
    )


def _shapley_loss(
    geometry_by_key: dict[str, float],
) -> dict[str, float]:
    edges = tuple(EDGE_NAMES)
    count = len(edges)
    values = {}
    for size in range(count + 1):
        for subset_tuple in combinations(edges, size):
            subset = frozenset(subset_tuple)
            values[subset] = 1.0 - geometry_by_key[_subset_key(subset)]
    output = {}
    for edge in edges:
        contribution = 0.0
        remaining = [value for value in edges if value != edge]
        for size in range(count):
            for subset_tuple in combinations(remaining, size):
                subset = frozenset(subset_tuple)
                weight = (
                    math.factorial(size)
                    * math.factorial(count - size - 1)
                    / math.factorial(count)
                )
                contribution += weight * (
                    values[subset | {edge}] - values[subset]
                )
        output[edge] = float(contribution)
    return output


def _view_diagnostics(
    oracle: M4PhysicalEdgeView,
    discovered: M4PhysicalEdgeView,
    query_bank: np.ndarray,
) -> dict[str, Any]:
    loops = mixed_physical_loops(oracle, discovered)
    geometry = {
        key: _geometry(values, oracle.jacobian_loop)
        for key, values in loops.items()
    }
    shapley = _shapley_loss(geometry)
    budget = edge_error_budget(
        oracle,
        discovered,
        query_bank,
    )
    return {
        **{
            f"mixed_loop_geometry_{key}": value
            for key, value in geometry.items()
        },
        **{
            f"shapley_loss_{edge}": value
            for edge, value in shapley.items()
        },
        **{
            f"path_error_{edge}": float(np.mean(values))
            for edge, values in budget.items()
        },
        "oracle_jacobian_finite_geometry": _geometry(
            oracle.jacobian_loop,
            oracle.finite_loop,
        ),
        "discovered_jacobian_finite_geometry": _geometry(
            discovered.jacobian_loop,
            discovered.finite_loop,
        ),
        "finite_loop_transport_geometry": _geometry(
            discovered.finite_loop,
            oracle.finite_loop,
        ),
        "projection_error_max": float(
            np.max(discovered.projection_error)
        ),
        "legacy_loop_difference_max": float(
            np.max(discovered.legacy_loop_difference)
        ),
    }


def _fault_rows(
    oracle: M4PhysicalEdgeRoute,
    *,
    repetition: int,
    world: str,
    strength: float,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    for view_index, view_name in enumerate(("train", "test")):
        view = getattr(oracle, view_name)
        for edge_index, edge in enumerate(EDGE_NAMES):
            fault = inject_physical_edge_fault(
                view,
                edge=edge,
                strength=strength,
                seed=seed + view_index * 1009 + edge_index * 100_003,
            )
            loops = mixed_physical_loops(view, fault)
            geometry = {
                key: _geometry(values, view.jacobian_loop)
                for key, values in loops.items()
            }
            shapley = _shapley_loss(geometry)
            ranked = sorted(
                shapley,
                key=lambda name: shapley[name],
                reverse=True,
            )
            rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "view": view_name,
                    "planted_edge": edge,
                    "predicted_edge": ranked[0],
                    "correct": float(ranked[0] == edge),
                    "attribution_margin": (
                        shapley[edge]
                        - max(
                            shapley[name]
                            for name in EDGE_NAMES
                            if name != edge
                        )
                    ),
                    **{
                        f"shapley_loss_{name}": value
                        for name, value in shapley.items()
                    },
                }
            )
        null_geometry = {
            key: _geometry(values, view.jacobian_loop)
            for key, values in mixed_physical_loops(view, view).items()
        }
        null_shapley = _shapley_loss(null_geometry)
        rows.append(
            {
                "repetition": repetition,
                "world": world,
                "view": view_name,
                "planted_edge": "null",
                "predicted_edge": (
                    max(null_shapley, key=null_shapley.get)
                    if max(abs(value) for value in null_shapley.values())
                    > 1e-8
                    else "null"
                ),
                "correct": float(
                    max(abs(value) for value in null_shapley.values())
                    <= 1e-8
                ),
                "attribution_margin": float("nan"),
                **{
                    f"shapley_loss_{name}": value
                    for name, value in null_shapley.items()
                },
            }
        )
    return rows


def _basis_invariance_difference(
    ecology: Any,
    basis: dict[str, np.ndarray],
    route: M4PhysicalEdgeRoute,
    *,
    route_parameters: dict[str, Any],
    seed: int,
) -> float:
    rotated = fit_m4_physical_edge_route(
        ecology,
        rotate_whitened_basis(basis, seed=seed),
        basis_name="rotated_discovered",
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


def _bootstrap_lcb(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> float:
    rng = np.random.default_rng(seed)
    draws = rng.choice(
        np.asarray(values, dtype=float),
        size=(repetitions, len(values)),
        replace=True,
    )
    return float(np.quantile(np.mean(draws, axis=1), 0.025))


def _decision(
    metrics: pd.DataFrame,
    faults: pd.DataFrame,
    ranks: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    active_faults = faults[faults["planted_edge"] != "null"]
    null_faults = faults[faults["planted_edge"] == "null"]
    loop_loss = 1.0 - metrics["mixed_loop_geometry_DDD"]
    error_spearman = _safe_spearman(
        metrics["path_error_total"],
        loop_loss,
    )
    margin_lcb = _bootstrap_lcb(
        active_faults["attribution_margin"].to_numpy(dtype=float),
        seed=int(config["bootstrap_seed"]),
        repetitions=int(config["bootstrap_repetitions"]),
    )
    repetition_rows = []
    for repetition, repeated in metrics.groupby("repetition"):
        repeated_faults = active_faults[
            active_faults["repetition"] == repetition
        ]
        repetition_rows.append(
            {
                "repetition": int(repetition),
                "fault_accuracy": float(
                    repeated_faults["correct"].mean()
                ),
                "error_spearman": _safe_spearman(
                    repeated["path_error_total"],
                    1.0 - repeated["mixed_loop_geometry_DDD"],
                ),
                "exact_reconstruction": bool(
                    repeated["legacy_loop_difference_max"].max()
                    <= targets["maximum_reconstruction_error"]
                ),
            }
        )
    repetition_metrics = pd.DataFrame(repetition_rows)
    repetition_metrics["pass"] = (
        (
            repetition_metrics["fault_accuracy"]
            >= targets["minimum_fault_localization_accuracy"]
        )
        & (
            repetition_metrics["error_spearman"]
            >= targets["minimum_error_loss_spearman"]
        )
        & repetition_metrics["exact_reconstruction"]
    )
    diagnostics = {
        "fault_localization_accuracy": float(
            active_faults["correct"].mean()
        ),
        "fault_attribution_margin_lcb": margin_lcb,
        "null_false_attribution_rate": float(
            1.0 - null_faults["correct"].mean()
        ),
        "error_budget_loss_spearman": error_spearman,
        "oracle_jacobian_finite_geometry": float(
            metrics["oracle_jacobian_finite_geometry"].mean()
        ),
        "discovered_jacobian_finite_geometry": float(
            metrics["discovered_jacobian_finite_geometry"].mean()
        ),
        "finite_loop_transport_geometry": float(
            metrics["finite_loop_transport_geometry"].mean()
        ),
        "jacobian_loop_transport_geometry": float(
            metrics["mixed_loop_geometry_DDD"].mean()
        ),
        "maximum_projection_error": float(
            metrics["projection_error_max"].max()
        ),
        "maximum_reconstruction_error": float(
            metrics["legacy_loop_difference_max"].max()
        ),
        "basis_invariance_max_difference": float(
            metrics["basis_invariance_max_difference"].max()
        ),
        "passing_repetitions": int(repetition_metrics["pass"].sum()),
        "required_passing_repetitions": int(
            targets["minimum_passing_repetitions"]
        ),
        "rank_loop_geometry": {
            str(int(rank)): float(group["loop_geometry"].mean())
            for rank, group in ranks.groupby("requested_rank")
        },
        "mean_shapley_loss": {
            edge: float(metrics[f"shapley_loss_{edge}"].mean())
            for edge in EDGE_NAMES
        },
    }
    checks = {
        "fault_localization": (
            diagnostics["fault_localization_accuracy"]
            >= targets["minimum_fault_localization_accuracy"]
        ),
        "fault_margin": (
            diagnostics["fault_attribution_margin_lcb"] > 0.0
        ),
        "null_attribution": (
            diagnostics["null_false_attribution_rate"]
            <= targets["maximum_null_false_attribution_rate"]
        ),
        "error_budget": (
            diagnostics["error_budget_loss_spearman"]
            >= targets["minimum_error_loss_spearman"]
        ),
        "linearization_control": (
            diagnostics["oracle_jacobian_finite_geometry"]
            >= targets["minimum_oracle_finite_geometry"]
        ),
        "physical_reconstruction": (
            diagnostics["maximum_projection_error"]
            <= targets["maximum_reconstruction_error"]
            and diagnostics["maximum_reconstruction_error"]
            <= targets["maximum_reconstruction_error"]
        ),
        "basis_invariance": (
            diagnostics["basis_invariance_max_difference"]
            <= targets["maximum_basis_invariance_difference"]
        ),
        "repetition_stability": (
            diagnostics["passing_repetitions"]
            >= diagnostics["required_passing_repetitions"]
        ),
    }
    if all(checks.values()):
        decision = "M4_C3_PHYSICAL_EDGE_COMPOSITION_LOSS_LOCALIZED"
    elif not checks["linearization_control"]:
        decision = "M4_C3_NONLINEAR_LOOP_DEFINITION_MISMATCH"
    else:
        decision = "M4_C3_NO_GO_ERROR_ATTRIBUTION"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "repetition_metrics": repetition_rows,
        "claim_boundary": (
            "Finite synthetic decomposition of physical choice, response, "
            "and creation edges only. It explains or localizes composite "
            "loop loss; it does not convert M4-C.2 to a pass, identify "
            "personality, validate natural text, or authorize M4-D."
        ),
    }


def _report(decision: dict[str, Any], config: dict[str, Any]) -> str:
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA M4-C.3 Physical-Edge Composition Audit

## Decision

`{decision["decision"]}`

M4-C.2 established strong atomic action transport but failed its composite
loop and repetition gates. M4-C.3 does not reopen that result. It maps each
estimated edge into the shared physical condition space and constructs all
eight products

\\[
L_{{ijk}}=A_iR_jD_k,\\qquad i,j,k\\in\\{{O,D\\}}.
\\]

A Shapley decomposition attributes oracle-to-discovered loop loss to the
creation, response, and choice edges and their order-independent interactions.
Path-conditioned error budgets are evaluated only on the registered query
bank. A finite nonlinear intervention is compared against the Jacobian
product so estimator error is not confused with linearization error.

## Frozen design

- version: `{config["version"]}`
- repetitions: `{config["repetitions"]}`
- worlds: `{", ".join(config["worlds"])}`
- primary rank: `{config["primary_rank"]}`
- rank diagnostic arms: `{config["rank_arms"]}`
- fault strength: `{config["fault_strength"]}`

## Diagnostics

{diagnostics}

## Gates

{checks}

## Boundary

{decision["claim_boundary"]}

This audit can localize why the M4-C.2 plug-in loop failed. It cannot turn the
frozen V2 NO-GO into a pass. M4-D remains blocked.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_physical_edge_audit.json",
    )
    args = parser.parse_args()
    config = _load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    candidates = tuple(dict(value) for value in config["candidates"])
    route_parameters = _route_parameters(config)
    query_bank = np.asarray(config["query_bank"], dtype=float).T
    rows = []
    fault_rows = []
    rank_rows = []

    for repetition in range(int(config["repetitions"])):
        for world_index, world in enumerate(config["worlds"]):
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
                _basis_invariance_difference(
                    observed.ecology,
                    discovered_basis,
                    discovered,
                    route_parameters=route_parameters,
                    seed=seed + 800_009,
                )
                if repetition == 0 and world_index == 0
                else 0.0
            )
            for view_name in ("train", "test"):
                values = _view_diagnostics(
                    getattr(oracle, view_name),
                    getattr(discovered, view_name),
                    query_bank,
                )
                rows.append(
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
            fault_rows.extend(
                _fault_rows(
                    oracle,
                    repetition=repetition,
                    world=world,
                    strength=float(config["fault_strength"]),
                    seed=seed + 900_001,
                )
            )

            if repetition < int(config["rank_diagnostic_repetitions"]):
                for requested_rank in config["rank_arms"]:
                    _, rank_basis = build_m4_discovered_basis(
                        observed,
                        chart,
                        rank_tolerance=float(config["rank_tolerance"]),
                        maximum_rank=int(requested_rank),
                    )
                    rank_route = fit_m4_physical_edge_route(
                        observed.ecology,
                        rank_basis,
                        basis_name=f"rank_{requested_rank}",
                        **route_parameters,
                    )
                    for view_name in ("train", "test"):
                        rank_rows.append(
                            {
                                "repetition": repetition,
                                "world": world,
                                "view": view_name,
                                "requested_rank": requested_rank,
                                "realized_rank": rank_basis[
                                    "evaluation"
                                ].shape[1],
                                "loop_geometry": _geometry(
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

    metrics = pd.DataFrame(rows)
    faults = pd.DataFrame(fault_rows)
    ranks = pd.DataFrame(rank_rows)
    decision = _decision(metrics, faults, ranks, config)
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    faults.to_csv(output / "fault_attribution.csv", index=False)
    ranks.to_csv(output / "rank_diagnostics.csv", index=False)
    pd.DataFrame(decision["repetition_metrics"]).to_csv(
        output / "repetition_metrics.csv",
        index=False,
    )
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, config), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
