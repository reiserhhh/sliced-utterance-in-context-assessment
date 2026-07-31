#!/usr/bin/env python3
"""Develop M4-C.3.2 creation-only relation-kernel interventions."""
from __future__ import annotations

import argparse
from itertools import product
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
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)
from suica_core.m4_relation_kernel_basis import (  # noqa: E402
    build_relation_kernel_bases,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _cluster_lcb(
    values: pd.DataFrame,
    column: str,
    *,
    seed: int,
    repetitions: int,
) -> float:
    """Bootstrap repetition clusters after averaging worlds within cluster."""
    clusters = (
        values.groupby("repetition", sort=True)[column]
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


def _metric_row(
    *,
    repetition: int,
    world: str,
    view_name: str,
    rank: int,
    realized_rank: int,
    bandwidth_scale: float,
    bandwidth: float,
    oracle: Any,
    baseline: Any,
    candidate: Any,
) -> dict[str, Any]:
    oracle_view = getattr(oracle, view_name)
    baseline_view = getattr(baseline, view_name)
    candidate_view = getattr(candidate, view_name)
    oracle_target = oracle_view.jacobian_loop
    baseline_loop = baseline_view.jacobian_loop
    oracle_swap = compose_creation_only_loop(
        oracle_view.creation,
        baseline_view,
    )
    candidate_swap = compose_creation_only_loop(
        candidate_view.creation,
        baseline_view,
    )
    baseline_geometry = author_relation_geometry(
        baseline_loop,
        oracle_target,
    )
    oracle_swap_geometry = author_relation_geometry(
        oracle_swap,
        oracle_target,
    )
    candidate_geometry = author_relation_geometry(
        candidate_swap,
        oracle_target,
    )
    headroom = oracle_swap_geometry - baseline_geometry
    gain = candidate_geometry - baseline_geometry
    baseline_creation_geometry = author_relation_geometry(
        baseline_view.creation,
        oracle_view.creation,
    )
    candidate_creation_geometry = author_relation_geometry(
        candidate_view.creation,
        oracle_view.creation,
    )
    return {
        "repetition": repetition,
        "world": world,
        "view": view_name,
        "arm": f"kernel_r{rank}_bw{bandwidth_scale:g}",
        "requested_rank": rank,
        "realized_rank": realized_rank,
        "bandwidth_scale": bandwidth_scale,
        "bandwidth": bandwidth,
        "baseline_geometry": baseline_geometry,
        "oracle_swap_geometry": oracle_swap_geometry,
        "creation_headroom": headroom,
        "candidate_creation_only_geometry": candidate_geometry,
        "candidate_gain": gain,
        "recovered_headroom": relative_headroom_recovery(
            baseline_geometry,
            candidate_geometry,
            oracle_swap_geometry,
        ),
        "candidate_full_route_geometry": author_relation_geometry(
            candidate_view.jacobian_loop,
            oracle_target,
        ),
        "baseline_creation_geometry": baseline_creation_geometry,
        "candidate_creation_geometry": candidate_creation_geometry,
        "candidate_creation_gain": (
            candidate_creation_geometry - baseline_creation_geometry
        ),
    }


def _summarize(
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    test = metrics[metrics["view"] == "test"].copy()
    targets = config["targets"]
    rows = []
    for arm_index, (arm, values) in enumerate(
        test.groupby("arm", sort=True)
    ):
        repetition = values.groupby("repetition", sort=True).agg(
            candidate_gain=("candidate_gain", "mean"),
            candidate_geometry=(
                "candidate_creation_only_geometry",
                "mean",
            ),
        )
        gain_lcb = _cluster_lcb(
            values,
            "candidate_gain",
            seed=int(config["bootstrap_seed"]) + arm_index * 10_007,
            repetitions=int(config["bootstrap_repetitions"]),
        )
        headroom_lcb = _cluster_lcb(
            values,
            "creation_headroom",
            seed=int(config["bootstrap_seed"]) + arm_index * 10_007 + 1,
            repetitions=int(config["bootstrap_repetitions"]),
        )
        mean_headroom = float(values["creation_headroom"].mean())
        mean_gain = float(values["candidate_gain"].mean())
        recovered = (
            mean_gain / mean_headroom
            if mean_headroom > 1e-12
            else float("nan")
        )
        positive_repetitions = int(
            (
                (repetition["candidate_gain"] > 0)
                & (
                    repetition["candidate_geometry"]
                    >= targets["minimum_candidate_geometry"]
                )
            ).sum()
        )
        checks = {
            "headroom": (
                mean_headroom
                >= targets["minimum_creation_headroom"]
                and headroom_lcb > targets["minimum_headroom_lcb"]
            ),
            "gain": (
                mean_gain >= targets["minimum_candidate_gain"]
                and gain_lcb > targets["minimum_candidate_gain_lcb"]
            ),
            "geometry": (
                float(
                    values["candidate_creation_only_geometry"].mean()
                )
                >= targets["minimum_candidate_geometry"]
            ),
            "recovered_headroom": (
                recovered >= targets["minimum_recovered_headroom"]
            ),
            "repetition_stability": (
                positive_repetitions
                >= targets["minimum_positive_repetitions"]
            ),
        }
        rows.append(
            {
                "arm": arm,
                "requested_rank": int(values["requested_rank"].iloc[0]),
                "mean_realized_rank": float(
                    values["realized_rank"].mean()
                ),
                "bandwidth_scale": float(
                    values["bandwidth_scale"].iloc[0]
                ),
                "baseline_geometry": float(
                    values["baseline_geometry"].mean()
                ),
                "oracle_swap_geometry": float(
                    values["oracle_swap_geometry"].mean()
                ),
                "creation_headroom": mean_headroom,
                "creation_headroom_lcb": headroom_lcb,
                "candidate_creation_only_geometry": float(
                    values["candidate_creation_only_geometry"].mean()
                ),
                "candidate_gain": mean_gain,
                "candidate_gain_lcb": gain_lcb,
                "recovered_headroom": recovered,
                "candidate_full_route_geometry": float(
                    values["candidate_full_route_geometry"].mean()
                ),
                "baseline_creation_geometry": float(
                    values["baseline_creation_geometry"].mean()
                ),
                "candidate_creation_geometry": float(
                    values["candidate_creation_geometry"].mean()
                ),
                "candidate_creation_gain": float(
                    values["candidate_creation_gain"].mean()
                ),
                "positive_repetitions": positive_repetitions,
                **{
                    f"check_{name}": passed
                    for name, passed in checks.items()
                },
                "development_candidate": bool(all(checks.values())),
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["development_candidate", "candidate_creation_only_geometry"],
        ascending=[False, False],
    )
    eligible = summary[summary["development_candidate"]]
    if len(eligible):
        best = eligible.iloc[0].to_dict()
        decision_name = (
            "M4_C32_KERNEL_CANDIDATE_FOUND_NEEDS_CONFIRMATION"
        )
    else:
        best = summary.iloc[0].to_dict()
        decision_name = "M4_C32_KERNEL_PATH_STOP"
    decision = {
        "estimand_id": config["estimand_id"],
        "decision": decision_name,
        "best_development_arm": best,
        "candidate_count": int(summary["development_candidate"].sum()),
        "arm_count": int(len(summary)),
        "formal_confirmation_complete": False,
        "missing_confirmation_controls": [
            "independent frozen seed",
            "selection-risk noninferiority guard",
            "response-only and choice-only specificity worlds",
            "support-alias refusal control",
            "family-selection multiplicity control",
        ],
        "claim_boundary": (
            "Development-only synthetic intervention. Candidate creation "
            "estimators are fitted without response outcomes in their basis, "
            "then inserted into frozen discovered response and choice edges. "
            "A candidate can justify an independent confirmation but cannot "
            "reopen M4-C.2, establish personality, validate natural text, or "
            "authorize M4-D."
        ),
    }
    return summary, decision


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> str:
    best = decision["best_development_arm"]
    table = summary[
        [
            "arm",
            "candidate_creation_only_geometry",
            "candidate_gain",
            "candidate_gain_lcb",
            "creation_headroom",
            "recovered_headroom",
            "baseline_creation_geometry",
            "candidate_creation_geometry",
            "positive_repetitions",
            "development_candidate",
        ]
    ].to_markdown(index=False, floatfmt=".4f")
    return f"""# SUICA M4-C.3.2 Creation Intervention Development

## Decision

`{decision["decision"]}`

The C3.1 relational budget identified creation as the largest symmetric loss
allocation. This development experiment tests that diagnosis by changing only
the creation estimator. Response and choice edges remain frozen at their
discovered-route estimates:

\\[
L^{{(j)}}_u=A^{{(j)}}_uR^D_uD^D_u.
\\]

The candidate basis is a calibration-only centered RBF relation kernel,
transported to selection and evaluation conditions by Nyström extension.
Ranks and bandwidths are development arms, not confirmed hyperparameters.

## Design

- repetitions: `{config["repetitions"]}`
- worlds: `{", ".join(config["worlds"])}`
- kernel ranks: `{config["kernel_ranks"]}`
- bandwidth scales: `{config["bandwidth_scales"]}`
- response/choice intervention status: frozen
- endpoint: author-pair geometry of the physical loop

## Arm results

{table}

## Best development arm

- arm: `{best["arm"]}`
- creation-only geometry: `{best["candidate_creation_only_geometry"]:.4f}`
- gain over chart baseline: `{best["candidate_gain"]:.4f}`
- clustered gain LCB: `{best["candidate_gain_lcb"]:.4f}`
- oracle creation headroom: `{best["creation_headroom"]:.4f}`
- recovered headroom: `{best["recovered_headroom"]:.4f}`
- baseline/candidate creation geometry: `{best["baseline_creation_geometry"]:.4f}` / `{best["candidate_creation_geometry"]:.4f}`
- positive repetitions: `{int(best["positive_repetitions"])}/{config["repetitions"]}`

## Boundary

{decision["claim_boundary"]}

Even a passing development arm still lacks an independent frozen seed,
selection-risk noninferiority, specificity worlds, alias refusal, and
multiplicity protection. Therefore this run can only choose whether an
independent C3.2 confirmation is warranted.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            ROOT
            / "configs"
            / "m4_creation_intervention.development.json"
        ),
    )
    args = parser.parse_args()
    config = _load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])
    candidates = tuple(
        dict(value) for value in config["chart_candidates"]
    )
    route_parameters = _route_parameters(config)
    rows = []

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
            baseline = fit_m4_physical_edge_route(
                observed.ecology,
                discovered_basis,
                basis_name="chart_plugin",
                **route_parameters,
            )
            for rank, bandwidth_scale in product(
                config["kernel_ranks"],
                config["bandwidth_scales"],
            ):
                frozen_kernel, kernel_basis = (
                    build_relation_kernel_bases(
                        discovered_basis,
                        rank=int(rank),
                        bandwidth_scale=float(bandwidth_scale),
                    )
                )
                candidate = fit_m4_physical_edge_route(
                    observed.ecology,
                    kernel_basis,
                    basis_name=(
                        f"kernel_r{rank}_bw{bandwidth_scale:g}"
                    ),
                    **route_parameters,
                )
                for view_name in ("train", "test"):
                    rows.append(
                        _metric_row(
                            repetition=repetition,
                            world=world,
                            view_name=view_name,
                            rank=int(rank),
                            realized_rank=len(
                                frozen_kernel.eigenvalues
                            ),
                            bandwidth_scale=float(bandwidth_scale),
                            bandwidth=frozen_kernel.bandwidth,
                            oracle=oracle,
                            baseline=baseline,
                            candidate=candidate,
                        )
                    )

    metrics = pd.DataFrame(rows)
    summary, decision = _summarize(metrics, config)
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "arm_metrics.csv", index=False)
    summary.to_csv(output / "arm_summary.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _report(decision, summary, config),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
