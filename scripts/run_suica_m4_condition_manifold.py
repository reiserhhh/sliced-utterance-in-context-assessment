#!/usr/bin/env python3
"""Run M4-C response-safe condition-manifold discovery."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_condition_manifold_audit import (  # noqa: E402
    audit_m4_condition_manifold,
)
from suica_core.m4_condition_manifold_contracts import (  # noqa: E402
    M4ConditionObserved,
    M4ConditionPanel,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    PANEL_NAMES,
    fit_m4_condition_chart,
    fit_m4_condition_manifold,
)
from suica_core.m4_condition_manifold_generator import (  # noqa: E402
    M4ConditionSpec,
    generate_m4_condition_world,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _candidate_grid(config: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(candidate) for candidate in config["candidates"])


def _permuted_responses(
    observed: M4ConditionObserved,
    *,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    panels: dict[str, M4ConditionPanel] = {}
    for name in PANEL_NAMES:
        panel = getattr(observed, name)
        flattened = panel.response.reshape(-1, panel.response.shape[-1]).copy()
        rng.shuffle(flattened, axis=0)
        panels[name] = replace(
            panel,
            response=flattened.reshape(panel.response.shape),
        )
    return M4ConditionObserved(
        **panels,
        design=dict(observed.design),
    )


def _response_invariance(
    observed: M4ConditionObserved,
    *,
    config: dict[str, Any],
    seed: int,
) -> bool:
    chart = fit_m4_condition_chart(
        observed,
        candidates=_candidate_grid(config),
        **config["chart_thresholds"],
    )
    permuted = fit_m4_condition_chart(
        _permuted_responses(observed, seed=seed),
        candidates=_candidate_grid(config),
        **config["chart_thresholds"],
    )
    if chart.selected_family != permuted.selected_family:
        return False
    if chart.selected_parameters != permuted.selected_parameters:
        return False
    return all(
        np.allclose(
            chart.panel_features[name],
            permuted.panel_features[name],
            atol=1e-12,
            rtol=0.0,
        )
        for name in PANEL_NAMES
    )


def _summary(metrics: pd.DataFrame) -> pd.DataFrame:
    excluded = {
        "world",
        "expected_chart_status",
        "expected_topology",
        "selected_family",
        "topology_detected",
        "refusal_reasons",
        "repetition",
        "seed",
    }
    numeric = [
        column
        for column in metrics.columns
        if column not in excluded
        and pd.api.types.is_numeric_dtype(metrics[column])
    ]
    rows = []
    for world, group in metrics.groupby("world", sort=False):
        row: dict[str, Any] = {"world": world}
        for column in numeric:
            values = group[column].dropna().to_numpy(dtype=float)
            row[f"{column}_mean"] = (
                float(np.mean(values)) if len(values) else float("nan")
            )
            row[f"{column}_lower"] = (
                float(np.quantile(values, 0.025))
                if len(values)
                else float("nan")
            )
            row[f"{column}_upper"] = (
                float(np.quantile(values, 0.975))
                if len(values)
                else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _decision(
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["discovery_targets"]
    identifiable = metrics[metrics["expected_chart_status"] == "IDENTIFIABLE"]
    refusal = metrics[metrics["expected_chart_status"] == "REFUSE"]
    topology = metrics[metrics["world"] == "topology_mismatch"]
    alias = metrics[metrics["world"] == "condition_alias"]
    diagnostics = {
        "identifiable_resolution_rate": float(
            identifiable["expected_resolution"].mean()
        ),
        "identifiable_geometry": float(
            identifiable["geometry_spearman"].mean()
        ),
        "identifiable_neighbor_jaccard": float(
            identifiable["neighbor_jaccard"].mean()
        ),
        "identifiable_response_retention": float(
            identifiable["response_retention"].mean()
        ),
        "identifiable_response_geometry": float(
            identifiable["response_geometry"].mean()
        ),
        "refusal_world_resolution_rate": float(
            refusal["expected_resolution"].mean()
        ),
        "topology_resolution_rate": float(
            topology["expected_resolution"].mean()
        ),
        "alias_refusal_rate": float(
            alias["mechanism_alias_refused"].mean()
        ),
        "response_perturbation_invariance_rate": float(
            metrics["response_perturbation_invariant"].mean()
        ),
        "identifiable_cross_source_geometry": float(
            identifiable["cross_source_geometry_evaluation"].mean()
        ),
        "identifiable_topology_match_rate": float(
            identifiable["topology_match"].mean()
        ),
    }
    checks = {
        "identifiable_worlds": (
            diagnostics["identifiable_resolution_rate"]
            >= targets["minimum_identifiable_resolution_rate"]
        ),
        "geodesic_geometry": (
            diagnostics["identifiable_geometry"]
            >= targets["minimum_geometry_spearman"]
        ),
        "local_neighborhoods": (
            diagnostics["identifiable_neighbor_jaccard"]
            >= targets["minimum_neighbor_jaccard"]
        ),
        "cross_source_transport": (
            diagnostics["identifiable_cross_source_geometry"]
            >= targets["minimum_cross_source_geometry"]
        ),
        "refusal_attacks": (
            diagnostics["refusal_world_resolution_rate"]
            >= targets["minimum_refusal_resolution_rate"]
        ),
        "condition_alias": (
            diagnostics["alias_refusal_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
        "response_safety": (
            diagnostics["response_perturbation_invariance_rate"]
            >= targets["minimum_response_invariance_rate"]
        ),
        "topology_or_refusal": (
            diagnostics["topology_resolution_rate"]
            >= targets["minimum_topology_resolution_rate"]
        ),
        "registered_topology": (
            diagnostics["identifiable_topology_match_rate"]
            >= targets["minimum_topology_match_rate"]
        ),
        "conditional_response_retention": (
            diagnostics["identifiable_response_retention"]
            >= targets["minimum_response_retention"]
        ),
        "response_operator_geometry": (
            diagnostics["identifiable_response_geometry"]
            >= targets["minimum_response_geometry"]
        ),
    }
    identification_core = all(
        checks[name]
        for name in (
            "identifiable_worlds",
            "geodesic_geometry",
            "local_neighborhoods",
            "cross_source_transport",
            "refusal_attacks",
            "condition_alias",
            "response_safety",
        )
    )
    if all(checks.values()):
        decision = "M4_C_CONDITION_MANIFOLD_DISCOVERY_PASS"
    elif identification_core:
        decision = (
            "M4_C_CONDITION_MANIFOLD_DISCOVERY_"
            "PASS_WITH_SCOPE_CORRECTION"
        )
    else:
        decision = "M4_C_CONDITION_MANIFOLD_DISCOVERY_NO_GO"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite response-safe synthetic condition geometry only. "
            "A pass may recover registered condition neighborhoods and "
            "preserve a frozen conditional-response mechanism. It does not "
            "identify topic names, personality, emotion, cognition, "
            "diagnosis, or natural-text validity. Full M4-B opportunity "
            "selection/creation/return/gate transport remains separate."
        ),
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> str:
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {value:.6f}"
        for name, value in decision["diagnostics"].items()
    )
    family_counts = (
        metrics.groupby(["world", "selected_family"])
        .size()
        .rename("count")
        .reset_index()
        .to_markdown(index=False)
    )
    return f"""# SUICA M4-C Condition-Manifold Discovery

## Decision

`{decision["decision"]}`

## Question

Can SUICA discover a condition representation from author-independent,
pre-response environment/context variables, transport it across two numeric
sources, and retain conditional-response structure without using the response
to select the chart?

The formal object is an atlas or relation geometry

\\[
\\widehat{{\\mathcal M}}
=
\\{{(\\mathcal U_a,\\zeta_a),T_{{ab}}\\}},
\\]

not a named topic axis. Chart fitting sees neither response nor external
psychological labels. Response is opened only after chart selection and is
evaluated once on the untouched mechanism-evaluation panel.

## Frozen design

- config version: `{config["version"]}`
- repetitions: `{config["repetitions"]}`
- worlds: `{", ".join(config["worlds"])}`
- chart families: linear PCA, global Isomap, landmark geodesic atlas
- role split: reference calibration -> reference selection -> mechanism
  calibration/selection -> untouched mechanism evaluation

## Diagnostics

{diagnostics}

## Gates

{checks}

## Selected families

{family_counts}

## Scope correction

This V1 route tests condition-chart recovery and frozen conditional-response
retention. It does **not** yet re-estimate all M4-B opportunity-selection,
opportunity-creation, return, recovery, and history-gate operators in the
discovered atlas. Those ecology operators remain valid M4-B objects and require
a separate chart-covariant adapter rather than being inferred from this
response-only result.

Coordinate axes and individual matrix elements are diagnostics. The licensed
objects are held-out neighborhoods, chart-invariant relation geometry,
response prediction on registered support, and explicit refusal under
leakage, no-manifold, topology conflict, or condition alias.

The condition-alias refusal is operationally triggered by the predeclared
untouched-response rule
`conditional_response_r2 < {config["discovery_targets"]["minimum_conditional_response_r2"]:.2f}`.
Synthetic oracle retention is used only in the truth-open audit to verify the
cause of the planted alias; it is not available to the runtime refusal.
Response-permutation invariance is executed once per world (8/8), then
recorded on that world's repetition rows.

## Artifacts

- cell metrics: `results/m4_condition_manifold/metrics.csv`
- world summary: `results/m4_condition_manifold/world_summary.csv`
- decision: `results/m4_condition_manifold/decision.json`

## Claim boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    """Run the registered M4-C synthetic discovery battery."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/m4_condition_manifold.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/m4_condition_manifold",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "reports/SUICA_M4_CONDITION_MANIFOLD_DISCOVERY.md",
    )
    args = parser.parse_args()
    config = _load(args.config)
    spec = M4ConditionSpec(**config["base_spec"])
    rows: list[dict[str, Any]] = []
    invariance: dict[str, bool] = {}
    for repetition in range(int(config["repetitions"])):
        for world_index, world in enumerate(config["worlds"]):
            seed = int(
                config["seed"]
                + 100_003 * repetition
                + 10_007 * world_index
            )
            observed, truth = generate_m4_condition_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            estimate = fit_m4_condition_manifold(
                observed,
                candidates=_candidate_grid(config),
                ridge_grid=tuple(config["ridge_grid"]),
                **config["chart_thresholds"],
            )
            if world not in invariance:
                invariance[world] = _response_invariance(
                    observed,
                    config=config,
                    seed=seed + 991,
                )
            row = audit_m4_condition_manifold(
                estimate,
                observed,
                truth,
                minimum_geometry=config["discovery_targets"][
                    "minimum_geometry_spearman"
                ],
                minimum_neighbor_jaccard=config["discovery_targets"][
                    "minimum_neighbor_jaccard"
                ],
                minimum_response_retention=config["discovery_targets"][
                    "minimum_response_retention"
                ],
                minimum_conditional_response_r2=config["discovery_targets"][
                    "minimum_conditional_response_r2"
                ],
                response_perturbation_invariant=invariance[world],
            )
            rows.append(
                {
                    "repetition": repetition,
                    "seed": seed,
                    **row,
                }
            )
            print(
                f"repetition={repetition} world={world} "
                f"family={row['selected_family']} "
                f"geometry={row['geometry_spearman']:.3f} "
                f"resolution={int(row['expected_resolution'])}"
            )
    metrics = pd.DataFrame(rows)
    summary = _summary(metrics)
    decision = _decision(metrics, config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    summary.to_csv(args.output_dir / "world_summary.csv", index=False)
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.report.write_text(
        _report(decision, metrics, summary, config),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
