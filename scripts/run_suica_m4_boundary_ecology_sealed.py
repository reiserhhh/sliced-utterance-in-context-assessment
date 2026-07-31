#!/usr/bin/env python3
"""Open outcomes for the sealed M4-C.3.5 boundary-ecology development."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _cluster_lcb,
    _cluster_ucb,
    _creation_parameters,
    _load,
    _loop,
    _rcca_parameters,
    _route_parameters,
)
from suica_core.m4_boundary_ecology import (  # noqa: E402
    intervene_evaluation_support,
    support_geometry,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
    freeze_m4_condition_transform,
)
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
    compose_creation_only_loop,
)
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
    subset_opportunity_budget,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    pre_response_digest,
    read_basis_bundle,
    runtime_fingerprint,
    sanitize_pre_response,
    verify_source_hash_manifest,
)
from suica_core.m4_response_safe_chart_replacement import (  # noqa: E402
    build_current_pooled_attribution_route,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def _old_basis(transform, observed):
    return {
        role: transform.transform_prototypes(
            getattr(observed, f"mechanism_{role}").pre_context
        )
        for role in ("calibration", "selection", "evaluation")
    }


def _stratum(config: dict[str, Any], world: str, world_type: str) -> str:
    if world_type == "null":
        return "null"
    for name in ("eligible", "sentinel", "boundary"):
        if world in config.get(f"{name}_worlds", []):
            return name
    raise ValueError(f"unregistered boundary-ecology world: {world}")


def _replay_variant(observed, rcca, metadata, config):
    if metadata["target_count"] is None:
        current = observed
        selected = ()
        geometry = support_geometry(rcca, observed)
    else:
        intervention = intervene_evaluation_support(
            observed,
            rcca,
            target_count=int(metadata["target_count"]),
            amplitude_multiplier=float(
                config["support_intervention_amplitude"]
            ),
        )
        current = intervention.observed
        selected = intervention.selected_conditions
        geometry = intervention.geometry
    if list(selected) != list(metadata["selected_conditions"]):
        raise ValueError("intervention selection does not replay Phase A")
    if pre_response_digest(current) != metadata["pre_response_digest"]:
        raise ValueError("intervention digest does not replay Phase A")
    if not np.isclose(
        geometry.minimum_coverage,
        float(metadata["minimum_coverage"]),
    ):
        raise ValueError("coverage does not replay Phase A")
    accepted = (
        geometry.minimum_coverage >= float(config["coverage_threshold"])
    )
    if accepted != bool(metadata["accepted"]):
        raise ValueError("acceptance decision does not replay Phase A")
    return current, geometry


def _maximum_basis_error(expected, actual) -> float:
    return max(
        float(np.max(np.abs(
            np.asarray(expected[arm][role])
            - np.asarray(actual[arm][role])
        )))
        for arm in ("B0", "R")
        for role in ("calibration", "selection", "evaluation")
    )


def _cluster_auc_lcb(
    frame: pd.DataFrame,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float, float]:
    labels = frame["harmful"].astype(int).to_numpy()
    scores = (-frame["minimum_margin"]).to_numpy()
    if len(np.unique(labels)) < 2:
        return float("nan"), float("nan"), 0.0
    observed = float(roc_auc_score(labels, scores))
    clusters = np.asarray(sorted(frame["repetition"].unique()))
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repetitions):
        selected = rng.choice(clusters, size=len(clusters), replace=True)
        sample = pd.concat(
            [frame[frame["repetition"].eq(value)] for value in selected],
            ignore_index=True,
        )
        current = sample["harmful"].astype(int).to_numpy()
        if len(np.unique(current)) < 2:
            continue
        values.append(
            roc_auc_score(current, -sample["minimum_margin"])
        )
    valid_rate = len(values) / max(repetitions, 1)
    lcb = (
        float(np.quantile(values, 0.025))
        if values
        else float("nan")
    )
    return observed, lcb, valid_rate


def _oracle_error_relation(
    frame: pd.DataFrame,
    *,
    seed: int,
    repetitions: int,
) -> dict[str, float]:
    native = frame[frame["variant"].eq("native")][
        ["repetition", "world", "minimum_coverage", "oracle_error"]
    ].rename(
        columns={
            "minimum_coverage": "native_coverage",
            "oracle_error": "native_oracle_error",
        }
    )
    values = frame.merge(
        native,
        on=["repetition", "world"],
        validate="many_to_one",
    )
    values["support_deficit"] = (
        values["native_coverage"] - values["minimum_coverage"]
    )
    values["oracle_error_delta"] = (
        values["oracle_error"] - values["native_oracle_error"]
    )
    x = values["support_deficit"].to_numpy(dtype=float)
    y = values["oracle_error_delta"].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    fitted = design @ coefficients
    total = float(np.sum((y - np.mean(y)) ** 2))
    r2 = (
        1.0 - float(np.sum((y - fitted) ** 2)) / total
        if total > 1e-12
        else 0.0
    )
    rho = float(spearmanr(x, y).statistic)
    rng = np.random.default_rng(seed)
    exceedances = 0
    groups = [
        indices.to_numpy()
        for _, indices in values.groupby(
            ["repetition", "world"],
            sort=True,
        ).groups.items()
    ]
    for _ in range(repetitions):
        permuted = y.copy()
        for indices in groups:
            permuted[indices] = permuted[
                indices[rng.permutation(len(indices))]
            ]
        current = float(spearmanr(x, permuted).statistic)
        exceedances += int(current >= rho)
    p_value = (exceedances + 1) / (repetitions + 1)
    return {
        "slope": float(coefficients[1]),
        "r2": r2,
        "spearman_rho": rho,
        "permutation_p": float(p_value),
    }


def _analyze(metrics: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    eligible = metrics[metrics["stratum"].eq("eligible")].copy()
    seed = int(config["bootstrap_seed"])
    repetitions = int(config["bootstrap_repetitions"])
    by_repetition = eligible.groupby(
        "repetition",
        sort=True,
    ).mean(numeric_only=True)
    policy_value = float(eligible["policy_value"].mean())
    routing_value = float(eligible["routing_value"].mean())
    accepted = eligible[eligible["accepted"]]
    refused = eligible[~eligible["accepted"]]
    auc, auc_lcb, auc_valid = _cluster_auc_lcb(
        eligible,
        seed=seed + 3,
        repetitions=repetitions,
    )
    relation = _oracle_error_relation(
        eligible,
        seed=int(config["permutation_seed"]),
        repetitions=int(config["permutation_repetitions"]),
    )
    policy_lcb = _cluster_lcb(
        by_repetition["policy_value"].to_numpy(),
        seed=seed,
        repetitions=repetitions,
    )
    routing_lcb = _cluster_lcb(
        by_repetition["routing_value"].to_numpy(),
        seed=seed + 1,
        repetitions=repetitions,
    )
    diagnostics = {
        "policy_value": policy_value,
        "policy_value_lcb": policy_lcb,
        "routing_value_over_forced_r": routing_value,
        "routing_value_lcb": routing_lcb,
        "routing_value_ucb": _cluster_ucb(
            by_repetition["routing_value"].to_numpy(),
            seed=seed + 2,
            repetitions=repetitions,
        ),
        "accepted_forced_r_gain": float(
            accepted["forced_r_gain"].mean()
        ),
        "refused_forced_r_gain": float(
            refused["forced_r_gain"].mean()
        ),
        "harmful_cells": int(eligible["harmful"].sum()),
        "eligible_cells": int(len(eligible)),
        "harm_auc": auc,
        "harm_auc_lcb": auc_lcb,
        "harm_auc_bootstrap_valid_rate": auc_valid,
        "oracle_error_relation": relation,
        "acceptance_rate": float(eligible["accepted"].mean()),
        "maximum_basis_replay_error": float(
            metrics["basis_replay_error"].max()
        ),
        "null_maximum_absolute_forced_gain": float(
            metrics[metrics["stratum"].eq("null")][
                "forced_r_gain"
            ].abs().max()
        ),
    }
    targets = config["candidate_targets"]
    useful = (
        policy_lcb > targets["minimum_policy_value_lcb"]
        and routing_lcb > targets["minimum_routing_value_lcb"]
        and np.isfinite(auc_lcb)
        and auc_lcb >= targets["minimum_harm_auc_lcb"]
    )
    proxy = (
        relation["r2"] >= targets["minimum_oracle_error_r2"]
        and relation["permutation_p"]
        <= targets["maximum_oracle_error_permutation_p"]
        and routing_lcb <= 0.0
    )
    false_refusal = (
        routing_value < 0.0
        and diagnostics["refused_forced_r_gain"] >= 0.0
    )
    if useful:
        classification = "USEFUL_SAFETY_GATE_CANDIDATE"
    elif proxy:
        classification = "SUPPORT_BOUNDARY_PROXY_CANDIDATE"
    elif false_refusal:
        classification = "FALSE_REFUSAL_RISK"
    else:
        classification = "INCONCLUSIVE"
    return {
        "estimand_id": config["estimand_id"],
        "phase": "development",
        "decision": "M4_C35_R2C_BOUNDARY_ECOLOGY_DEVELOPMENT_COMPLETE",
        "mechanism_classification": classification,
        "diagnostics": diagnostics,
        "confirmation_status": "NOT_AUTHORIZED",
        "claim_boundary": (
            "Finite-synthetic support-boundary development only. It "
            "identifies neither natural-text transport nor personality, "
            "behavioral, clinical, or M4-D validity."
        ),
    }


def _report(decision: dict[str, Any], metrics: pd.DataFrame) -> str:
    eligible = metrics[metrics["stratum"].eq("eligible")]
    by_coverage = (
        eligible.groupby(
            ["variant", "minimum_coverage", "accepted"],
            sort=False,
        )[
            [
                "forced_r_gain",
                "oracle_error",
                "policy_value",
                "routing_value",
            ]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    by_world = (
        eligible.groupby(["world", "accepted"], sort=True)[
            ["forced_r_gain", "oracle_error", "routing_value"]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    diagnostics = "\n".join(
        f"- `{key}`: {json.dumps(value, sort_keys=True)}"
        for key, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4-C.3.5-R2C Boundary Ecology Development

## Decision

`{decision["decision"]}`

Mechanism classification:
`{decision["mechanism_classification"]}`

The same response truth is scored across native and outcome-blind
pre-response support interventions. `Pi` uses `R` above the frozen `.80`
coverage boundary and `B0` below it.

## Eligible worlds by coverage

{by_coverage}

## Eligible worlds by boundary side

{by_world}

## Diagnostics

{diagnostics}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()
    config = _load(args.config)
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    manifest_path = bundle_root / "stage_a_manifest.json"
    if file_sha256(manifest_path) != args.expected_manifest_sha256:
        raise ValueError("Stage-A boundary manifest hash mismatch")
    manifest = _load(manifest_path)
    if manifest["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after boundary sealing")
    protocol = ROOT / manifest["protocol_path"]
    if manifest["protocol_sha256"] != file_sha256(protocol):
        raise ValueError("protocol changed after boundary sealing")
    r1_path = ROOT / manifest["r1_decision_path"]
    if manifest["r1_decision_sha256"] != file_sha256(r1_path):
        raise ValueError("R1 decision changed after boundary sealing")
    verify_source_hash_manifest(ROOT, manifest["source_sha256"])
    if manifest["runtime"] != runtime_fingerprint():
        raise ValueError("runtime changed after boundary sealing")

    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    route_parameters = _route_parameters(config)
    creation_parameters = _creation_parameters(config)
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for cell in manifest["cells"]:
        key = (int(cell["repetition"]), str(cell["world"]))
        grouped.setdefault(key, []).append(cell)
    rows = []
    for _, cells in sorted(grouped.items()):
        first = cells[0]
        passive, truth = generate_m4_chart_ecology_world(
            world=first["generator_world"],
            spec=spec,
            seed=int(first["seed"]),
        )
        observed = sanitize_pre_response(passive.condition)
        old_chart = fit_m4_condition_chart(
            observed,
            candidates=candidates,
            **config["chart_thresholds"],
        )
        old_transform = freeze_m4_condition_transform(
            observed,
            old_chart,
            rank_tolerance=float(config["rank_tolerance"]),
            maximum_rank=int(config["maximum_rank"]),
        )
        rcca = fit_response_safe_rcca_chart(
            observed,
            **_rcca_parameters(config, seed=int(first["seed"])),
        )
        excited = build_excited_observed(
            passive,
            truth,
            spec,
            seed=int(first["seed"]),
            amplitude=float(config["excitation_amplitude"]),
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
        oracle_route = fit_m4_physical_edge_route(
            passive.ecology,
            truth.oracle_basis,
            basis_name="oracle_max_passive",
            **route_parameters,
        )
        for metadata in sorted(cells, key=lambda value: value["variant"]):
            current, geometry = _replay_variant(
                observed,
                rcca,
                metadata,
                config,
            )
            actual = {
                "B0": _old_basis(old_transform, current),
                "R": build_response_safe_rcca_basis(rcca, current),
            }
            loaded = read_basis_bundle(
                bundle_root / metadata["bundle"],
                expected_sha256=metadata["bundle_sha256"],
            )
            basis_error = _maximum_basis_error(loaded, actual)
            if basis_error > 1e-12:
                raise ValueError("boundary basis does not replay Phase A")
            bases = {
                "B0": loaded["B0"],
                "R": loaded["R"],
                "Oest": truth.oracle_basis,
            }
            anchor = fit_m4_physical_edge_route(
                anchor_observed.ecology,
                bases["B0"],
                basis_name="anchor_old_response_safe",
                **route_parameters,
            )
            routes = {
                arm: build_current_pooled_attribution_route(
                    excited.ecology,
                    basis,
                    **creation_parameters,
                )
                for arm, basis in bases.items()
            }
            target = oracle_route.test.jacobian_loop
            geometry_by_arm = {
                arm: author_relation_geometry(
                    _loop(route, anchor, "test"),
                    target,
                )
                for arm, route in routes.items()
            }
            accepted = bool(metadata["accepted"])
            policy = (
                geometry_by_arm["R"]
                if accepted
                else geometry_by_arm["B0"]
            )
            forced_gain = (
                geometry_by_arm["R"] - geometry_by_arm["B0"]
            )
            oracle_error = (
                geometry_by_arm["Oest"] - geometry_by_arm["R"]
            )
            rows.append(
                {
                    "repetition": int(metadata["repetition"]),
                    "world": str(metadata["world"]),
                    "world_type": str(metadata["world_type"]),
                    "stratum": _stratum(
                        config,
                        str(metadata["world"]),
                        str(metadata["world_type"]),
                    ),
                    "variant": str(metadata["variant"]),
                    "target_count": metadata["target_count"],
                    "evaluation_count": int(
                        metadata["evaluation_count"]
                    ),
                    "minimum_coverage": float(
                        geometry.minimum_coverage
                    ),
                    "minimum_margin": float(
                        geometry.minimum_coverage
                        - config["coverage_threshold"]
                    ),
                    "accepted": accepted,
                    "geometry_B0": geometry_by_arm["B0"],
                    "geometry_R": geometry_by_arm["R"],
                    "geometry_Oest": geometry_by_arm["Oest"],
                    "geometry_Pi": policy,
                    "forced_r_gain": forced_gain,
                    "oracle_error": oracle_error,
                    "policy_value": policy - geometry_by_arm["B0"],
                    "routing_value": policy - geometry_by_arm["R"],
                    "harmful": forced_gain < float(
                        config["harm_threshold"]
                    ),
                    "hazard_B0": float(np.mean(
                        routes["B0"].test.comparable_hazard_loss
                    )),
                    "hazard_R": float(np.mean(
                        routes["R"].test.comparable_hazard_loss
                    )),
                    "basis_replay_error": basis_error,
                }
            )

    metrics = pd.DataFrame(rows)
    decision = _analyze(metrics, config)
    output = (
        args.output_directory
        if args.output_directory is not None
        else Path(config["output_directory"])
    )
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = (
        args.report_path
        if args.report_path is not None
        else Path(config["report_path"])
    )
    if not report.is_absolute():
        report = ROOT / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, metrics), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
