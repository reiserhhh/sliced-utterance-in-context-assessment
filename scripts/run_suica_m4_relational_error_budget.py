#!/usr/bin/env python3
"""Run M4-C.3.1 relational error-budget discovery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
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
    fit_m4_physical_edge_route,
    inject_physical_edge_fault,
    mixed_physical_loops,
)
from suica_core.m4_relational_error_budget import (  # noqa: E402
    relational_invariance_error,
    relational_mobius_budget,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float)
    y = np.asarray(second, dtype=float)
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else 0.0


def _fault_diagnostics(
    oracle: Any,
    *,
    repetition: int,
    world: str,
    view: str,
    strength: float,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    for edge_index, edge in enumerate(EDGE_NAMES):
        fault = inject_physical_edge_fault(
            oracle,
            edge=edge,
            strength=strength,
            seed=seed + edge_index * 100_003,
        )
        result = relational_mobius_budget(
            mixed_physical_loops(oracle, fault)
        )
        values = {
            name: float(result[f"shapley_loss_{name}"])
            for name in EDGE_NAMES
        }
        predicted = max(values, key=values.get)
        rows.append(
            {
                "repetition": repetition,
                "world": world,
                "view": view,
                "planted_edge": edge,
                "predicted_edge": predicted,
                "correct": float(predicted == edge),
                "attribution_margin": (
                    values[edge]
                    - max(
                        values[name]
                        for name in EDGE_NAMES
                        if name != edge
                    )
                ),
                "third_order_relative_norm": result[
                    "third_order_relative_norm"
                ],
                **{
                    f"shapley_loss_{name}": value
                    for name, value in values.items()
                },
            }
        )
    null_result = relational_mobius_budget(
        mixed_physical_loops(oracle, oracle)
    )
    null_values = {
        name: abs(float(null_result[f"shapley_loss_{name}"]))
        for name in EDGE_NAMES
    }
    rows.append(
        {
            "repetition": repetition,
            "world": world,
            "view": view,
            "planted_edge": "null",
            "predicted_edge": (
                max(null_values, key=null_values.get)
                if max(null_values.values()) > 1e-8
                else "null"
            ),
            "correct": float(max(null_values.values()) <= 1e-8),
            "attribution_margin": float("nan"),
            "third_order_relative_norm": null_result[
                "third_order_relative_norm"
            ],
            **{
                f"shapley_loss_{name}": float(
                    null_result[f"shapley_loss_{name}"]
                )
                for name in EDGE_NAMES
            },
        }
    )
    return rows


def _cluster_bootstrap_lcb(
    metrics: pd.DataFrame,
    *,
    seed: int,
    repetitions: int,
) -> float:
    rng = np.random.default_rng(seed)
    cluster_names = metrics["cluster"].unique()
    values = []
    groups = {
        name: group
        for name, group in metrics.groupby("cluster")
    }
    for _ in range(repetitions):
        selected = rng.choice(
            cluster_names,
            size=len(cluster_names),
            replace=True,
        )
        actual = np.concatenate(
            [groups[name]["actual_loss"].to_numpy() for name in selected]
        )
        predicted = np.concatenate(
            [
                groups[name]["predicted_second_order_loss"].to_numpy()
                for name in selected
            ]
        )
        values.append(_safe_spearman(predicted, actual))
    return float(np.quantile(values, 0.025))


def _bootstrap_margin_lcb(
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
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    pooled = _safe_spearman(
        metrics["predicted_second_order_loss"],
        metrics["actual_loss"],
    )
    cluster_lcb = _cluster_bootstrap_lcb(
        metrics,
        seed=int(config["bootstrap_seed"]),
        repetitions=int(config["bootstrap_repetitions"]),
    )
    leave_one_out = []
    unique_repetitions = sorted(metrics["repetition"].unique())
    if len(unique_repetitions) > 1:
        for repetition in unique_repetitions:
            held = metrics[metrics["repetition"] != repetition]
            leave_one_out.append(
                _safe_spearman(
                    held["predicted_second_order_loss"],
                    held["actual_loss"],
                )
            )
    else:
        leave_one_out.append(0.0)
    iqr = float(
        np.subtract(
            *np.quantile(metrics["actual_loss"], [0.75, 0.25])
        )
    )
    normalized_mae = (
        float(
            np.mean(
                np.abs(
                    metrics["predicted_second_order_loss"]
                    - metrics["actual_loss"]
                )
            )
        )
        / max(iqr, 1e-12)
    )
    active_faults = faults[faults["planted_edge"] != "null"]
    null_faults = faults[faults["planted_edge"] == "null"]
    margin_lcb = _bootstrap_margin_lcb(
        active_faults["attribution_margin"].to_numpy(dtype=float),
        seed=int(config["bootstrap_seed"]) + 17,
        repetitions=int(config["bootstrap_repetitions"]),
    )
    third_order_reference = float(
        np.quantile(
            active_faults["third_order_relative_norm"],
            0.95,
        )
    )
    third_order_excess = (
        float(metrics["third_order_relative_norm"].median())
        - third_order_reference
    )
    diagnostics = {
        "pooled_second_order_loss_spearman": pooled,
        "cluster_bootstrap_spearman_lcb": cluster_lcb,
        "leave_one_repetition_out_min_spearman": min(leave_one_out),
        "normalized_loss_mae": normalized_mae,
        "maximum_spearman_identity_error": float(
            metrics["spearman_identity_error"].max()
        ),
        "maximum_mobius_reconstruction_error": float(
            metrics["mobius_reconstruction_error"].max()
        ),
        "maximum_shapley_efficiency_error": float(
            metrics["shapley_efficiency_error"].max()
        ),
        "maximum_similarity_invariance_error": float(
            metrics["similarity_invariance_error"].max()
        ),
        "fault_localization_accuracy": float(
            active_faults["correct"].mean()
        ),
        "fault_attribution_margin_lcb": margin_lcb,
        "null_false_attribution_rate": float(
            1.0 - null_faults["correct"].mean()
        ),
        "median_third_order_relative_norm": float(
            metrics["third_order_relative_norm"].median()
        ),
        "fault_third_order_95pct": third_order_reference,
        "third_order_excess": third_order_excess,
        "mean_actual_loss": float(metrics["actual_loss"].mean()),
        "mean_predicted_second_order_loss": float(
            metrics["predicted_second_order_loss"].mean()
        ),
        "mean_gram_cka": float(metrics["gram_cka"].mean()),
        "mean_shapley_loss": {
            edge: float(metrics[f"shapley_loss_{edge}"].mean())
            for edge in EDGE_NAMES
        },
    }
    checks = {
        "spearman_identity": (
            diagnostics["maximum_spearman_identity_error"]
            <= targets["maximum_identity_error"]
        ),
        "mobius_reconstruction": (
            diagnostics["maximum_mobius_reconstruction_error"]
            <= targets["maximum_mobius_error"]
        ),
        "similarity_invariance": (
            diagnostics["maximum_similarity_invariance_error"]
            <= targets["maximum_invariance_error"]
        ),
        "shapley_efficiency": (
            diagnostics["maximum_shapley_efficiency_error"]
            <= targets["maximum_shapley_error"]
        ),
        "pooled_prediction": (
            diagnostics["pooled_second_order_loss_spearman"]
            >= targets["minimum_pooled_spearman"]
        ),
        "cluster_stability": (
            diagnostics["cluster_bootstrap_spearman_lcb"]
            >= targets["minimum_cluster_lcb"]
        ),
        "leave_one_out_stability": (
            diagnostics["leave_one_repetition_out_min_spearman"]
            >= targets["minimum_leave_one_out_spearman"]
        ),
        "prediction_error": (
            diagnostics["normalized_loss_mae"]
            <= targets["maximum_normalized_mae"]
        ),
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
    }
    algebra = all(
        checks[name]
        for name in (
            "spearman_identity",
            "mobius_reconstruction",
            "similarity_invariance",
            "shapley_efficiency",
            "fault_localization",
            "fault_margin",
            "null_attribution",
        )
    )
    predictive = all(
        checks[name]
        for name in (
            "pooled_prediction",
            "cluster_stability",
            "leave_one_out_stability",
            "prediction_error",
        )
    )
    if algebra and predictive:
        decision = "M4_C31_GO_RELATIONAL_BUDGET"
    elif (
        algebra
        and diagnostics["third_order_excess"]
        >= targets["minimum_third_order_excess"]
    ):
        decision = "M4_C31_RELATIONAL_THIRD_ORDER_INTERACTION"
    else:
        decision = "M4_C31_NO_GO_RELATIONAL_BUDGET"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic relation-space accounting only. It can "
            "coordinate M4-C.2 loop loss in the same author-relation "
            "geometry, but cannot change prior NO-GO decisions, establish "
            "causality, identify personality, validate natural text, or "
            "authorize M4-D."
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
    return rf"""# SUICA M4-C.3.1 Relational Error Budget

## Decision

`{decision["decision"]}`

The M4-C.3 author-wise Frobenius budget did not share the estimand of the
author-relation loop gate. M4-C.3.1 first quotients common author mode, then
works on the upper-triangle distance vector of all eight mixed physical loops.

For midrank vectors \(z_S\), the registered loss has the exact form

\\[
1-\\rho_S(d_O,d_S)=\\frac12\\|z_O-z_S\\|_2^2.
\\]

Single-edge and pairwise Harsanyi terms predict the DDD distance vector without
using DDD. The residual is the irreducible three-edge interaction.

## Frozen design

- version: `{config["version"]}`
- repetitions: `{config["repetitions"]}`
- worlds: `{", ".join(config["worlds"])}`
- common-mode quotient: author centering
- primary endpoint: pairwise-distance midrank loss
- secondary endpoint: normalized centered Gram/CKA

## Diagnostics

{diagnostics}

## Gates

{checks}

## Boundary

{decision["claim_boundary"]}

M4-C.2 and M4-C.3 remain frozen NO-GO results. M4-D remains blocked.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_relational_error_budget.json",
    )
    args = parser.parse_args()
    config = _load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    candidates = tuple(dict(value) for value in config["candidates"])
    route_parameters = _route_parameters(config)
    rows = []
    faults = []

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
                maximum_rank=int(config["maximum_rank"]),
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
            for view_index, view_name in enumerate(("train", "test")):
                oracle_view = getattr(oracle, view_name)
                discovered_view = getattr(discovered, view_name)
                result = relational_mobius_budget(
                    mixed_physical_loops(
                        oracle_view,
                        discovered_view,
                    )
                )
                rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "view": view_name,
                        "cluster": f"{repetition}:{world}",
                        "similarity_invariance_error": (
                            relational_invariance_error(
                                discovered_view.jacobian_loop,
                                seed=seed + view_index * 1009 + 700_001,
                            )
                        ),
                        **result,
                    }
                )
                faults.extend(
                    _fault_diagnostics(
                        oracle_view,
                        repetition=repetition,
                        world=world,
                        view=view_name,
                        strength=float(config["fault_strength"]),
                        seed=seed + view_index * 1009 + 900_001,
                    )
                )

    metrics = pd.DataFrame(rows)
    fault_frame = pd.DataFrame(faults)
    decision = _decision(metrics, fault_frame, config)
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    fault_frame.to_csv(output / "fault_attribution.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, config), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
