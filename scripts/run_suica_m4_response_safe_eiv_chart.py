#!/usr/bin/env python3
"""Run the M4-C.3.5 response-safe cross-view EIV chart experiment."""
from __future__ import annotations

import argparse
from dataclasses import replace
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
    _cluster_lcb,
)
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_contracts import (  # noqa: E402
    M4ConditionObserved,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
)
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
    compose_creation_only_loop,
)
from suica_core.m4_fisher_wiener_creation import (  # noqa: E402
    build_fisher_wiener_route,
    fit_fixed_hazard_route,
    split_opportunity_occasions,
)
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
    subset_opportunity_budget,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)
from suica_core.m4_response_safe_eiv_chart import (  # noqa: E402
    build_response_safe_basis,
    fit_response_safe_eiv_chart,
    fit_single_view_pca_chart,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _eiv_parameters(
    config: dict[str, Any],
    *,
    seed: int,
) -> dict[str, Any]:
    values = dict(config["eiv_chart"])
    values["permutation_seed"] = (
        int(config["permutation_seed"]) + int(seed)
    )
    return values


def _fit_pooled_creation(
    ecology: Any,
    basis: dict[str, np.ndarray],
    config: dict[str, Any],
) -> Any:
    parameters = {
        "model": str(config["creation_estimator"]["hazard_model"]),
        "ridge": float(config["route_estimator"]["hazard_ridge"]),
        "iterations": int(
            config["route_estimator"]["logistic_iterations"]
        ),
    }
    full = fit_fixed_hazard_route(ecology, basis, **parameters)
    first_ecology, second_ecology = split_opportunity_occasions(ecology)
    first = fit_fixed_hazard_route(first_ecology, basis, **parameters)
    second = fit_fixed_hazard_route(second_ecology, basis, **parameters)
    return build_fisher_wiener_route(
        ecology,
        basis,
        full,
        first,
        second,
        epsilon_scale=float(
            config["creation_estimator"]["epsilon_scale"]
        ),
    )


def _mutate_responses(
    observed: M4ConditionObserved,
    *,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    values = {}
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        values[name] = replace(
            panel,
            response=rng.normal(size=panel.response.shape),
        )
    return M4ConditionObserved(**values, design=dict(observed.design))


def _rotate_pre_context(
    observed: M4ConditionObserved,
    *,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    width = observed.reference_calibration.pre_context.shape[-1]
    rotations = []
    for _ in range(2):
        rotation, _ = np.linalg.qr(rng.normal(size=(width, width)))
        rotations.append(rotation)
    values = {}
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        pre = panel.pre_context.copy()
        for source in range(2):
            pre[source] = pre[source] @ rotations[source]
        values[name] = replace(panel, pre_context=pre)
    return M4ConditionObserved(**values, design=dict(observed.design))


def _shift_pre_context(
    observed: M4ConditionObserved,
    *,
    shift: float,
) -> M4ConditionObserved:
    values = {
        name: replace(
            getattr(observed, name),
            pre_context=getattr(observed, name).pre_context + shift,
        )
        for name in (
            "reference_calibration",
            "reference_selection",
            "mechanism_calibration",
            "mechanism_selection",
            "mechanism_evaluation",
        )
    }
    return M4ConditionObserved(**values, design=dict(observed.design))


def _duplicate_evaluation_condition(
    observed: M4ConditionObserved,
) -> M4ConditionObserved:
    panel = observed.mechanism_evaluation
    pre = panel.pre_context.copy()
    pre[:, :, 1] = pre[:, :, 0]
    return replace(
        observed,
        mechanism_evaluation=replace(panel, pre_context=pre),
    )


def _distance_error(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    return float(np.max(np.abs(pdist(left) - pdist(right))))


def _chart_bundle(
    observed: Any,
    config: dict[str, Any],
    *,
    seed: int,
) -> dict[str, Any]:
    candidates = tuple(
        dict(value) for value in config["chart_candidates"]
    )
    chart = fit_m4_condition_chart(
        observed.condition,
        candidates=candidates,
        **config["chart_thresholds"],
    )
    _, baseline_basis = build_m4_discovered_basis(
        observed,
        chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=int(config["maximum_rank"]),
    )
    eiv = fit_response_safe_eiv_chart(
        observed.condition,
        **_eiv_parameters(config, seed=seed),
    )
    pca = fit_single_view_pca_chart(
        observed.condition,
        rank=eiv.effective_rank,
        whitening_tolerance=float(
            config["eiv_chart"]["whitening_tolerance"]
        ),
    )
    shuffled = fit_response_safe_eiv_chart(
        observed.condition,
        shuffle_source_two=True,
        **_eiv_parameters(config, seed=seed + 700_001),
    )
    return {
        "c0": baseline_basis,
        "pca": build_response_safe_basis(pca, observed.condition),
        "eiv": build_response_safe_basis(eiv, observed.condition),
        "shuffle_eiv": build_response_safe_basis(
            shuffled,
            observed.condition,
        ),
        "eiv_transform": eiv,
        "pca_transform": pca,
        "shuffle_transform": shuffled,
    }


def _world_rows(
    *,
    repetition: int,
    world: str,
    world_type: str,
    passive: Any,
    truth: Any,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    excited = build_excited_observed(
        passive,
        truth,
        spec,
        seed=seed,
        amplitude=float(config["excitation_amplitude"]),
    )
    bundle = _chart_bundle(passive, config, seed=seed)
    anchor_observed = subset_opportunity_budget(
        passive,
        calibration_occasions=int(
            config["anchor_budget"]["calibration"]
        ),
        selection_occasions=int(
            config["anchor_budget"]["selection"]
        ),
    )
    route_parameters = _route_parameters(config)
    anchor = fit_m4_physical_edge_route(
        anchor_observed.ecology,
        bundle["c0"],
        basis_name="c34_frozen_c0_anchor",
        **route_parameters,
    )
    oracle = fit_m4_physical_edge_route(
        passive.ecology,
        truth.oracle_basis,
        basis_name="truth_open_ceiling",
        **route_parameters,
    )
    routes = {
        name: _fit_pooled_creation(
            excited.ecology,
            bundle[name],
            config,
        )
        for name in ("c0", "pca", "eiv", "shuffle_eiv")
    }
    eiv = bundle["eiv_transform"]
    shuffled = bundle["shuffle_transform"]
    rows = []
    control_rows = []
    for view_name in ("train", "test"):
        anchor_view = getattr(anchor, view_name)
        oracle_view = getattr(oracle, view_name)
        target = oracle_view.jacobian_loop
        oracle_geometry = author_relation_geometry(
            compose_creation_only_loop(
                oracle_view.creation,
                anchor_view,
            ),
            target,
        )
        geometries = {
            name: author_relation_geometry(
                compose_creation_only_loop(
                    getattr(route, view_name).creation,
                    anchor_view,
                ),
                target,
            )
            for name, route in routes.items()
        }
        baseline_geometry = geometries["c0"]
        headroom = oracle_geometry - baseline_geometry
        for name, geometry in geometries.items():
            route_view = getattr(routes[name], view_name)
            gain = geometry - baseline_geometry
            rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "world_type": world_type,
                    "view": view_name,
                    "chart": name,
                    "geometry": geometry,
                    "baseline_geometry": baseline_geometry,
                    "oracle_geometry": oracle_geometry,
                    "oracle_headroom": headroom,
                    "geometry_gain": gain,
                    "recovered_headroom": (
                        gain / headroom
                        if headroom > 1e-12
                        else float("nan")
                    ),
                    "evaluation_loss": float(
                        np.mean(route_view.evaluation_loss)
                    ),
                    "selected_rank": eiv.selected_rank,
                    "effective_rank": eiv.effective_rank,
                    "permutation_threshold": (
                        eiv.permutation_threshold
                    ),
                    "retained_singular_minimum": float(
                        eiv.singular_values[eiv.selected_rank - 1]
                    ),
                    "singular_margin": float(
                        eiv.singular_values[eiv.selected_rank - 1]
                        - eiv.permutation_threshold
                    ),
                    "principal_angle_maximum": float(
                        np.max(eiv.principal_angles_degrees)
                    ),
                    "coverage": eiv.coverage,
                    "chart_refused": eiv.refused,
                    "chart_refusal_reasons": "|".join(
                        eiv.refusal_reasons
                    ),
                    "shuffle_refused": shuffled.refused,
                }
            )
        control_rows.append(
            {
                "repetition": repetition,
                "world": world,
                "world_type": world_type,
                "control": "source_condition_shuffle",
                "view": view_name,
                "value": (
                    geometries["shuffle_eiv"] - baseline_geometry
                ),
                "passed": bool(
                    geometries["shuffle_eiv"] - baseline_geometry
                    <= config["targets"]["maximum_shuffle_gain"]
                ),
                "details": "|".join(shuffled.refusal_reasons),
            }
        )
    return rows, control_rows


def _invariance_rows(
    *,
    repetition: int,
    observed: M4ConditionObserved,
    config: dict[str, Any],
    seed: int,
) -> list[dict[str, Any]]:
    parameters = _eiv_parameters(config, seed=seed)
    native = fit_response_safe_eiv_chart(observed, **parameters)
    native_basis = build_response_safe_basis(native, observed)["evaluation"]
    response_mutated = _mutate_responses(
        observed,
        seed=seed + 1_000_003,
    )
    response_chart = fit_response_safe_eiv_chart(
        response_mutated,
        **parameters,
    )
    rotated = _rotate_pre_context(observed, seed=seed + 2_000_003)
    rotated_chart = fit_response_safe_eiv_chart(rotated, **parameters)
    rotated_basis = build_response_safe_basis(
        rotated_chart,
        rotated,
    )["evaluation"]
    shifted = _shift_pre_context(observed, shift=17.125)
    shifted_chart = fit_response_safe_eiv_chart(shifted, **parameters)
    shifted_basis = build_response_safe_basis(
        shifted_chart,
        shifted,
    )["evaluation"]
    response_failure = native.provenance_hash != response_chart.provenance_hash
    gauge_error = _distance_error(
        native_basis[:, 1:],
        rotated_basis[:, 1:],
    )
    shift_error = _distance_error(
        native_basis[:, 1:],
        shifted_basis[:, 1:],
    )
    return [
        {
            "repetition": repetition,
            "world": "endogenous_source_partition_matched",
            "world_type": "invariance",
            "control": "response_bytes",
            "view": "chart",
            "value": float(response_failure),
            "passed": not response_failure,
            "details": "",
        },
        {
            "repetition": repetition,
            "world": "endogenous_source_partition_matched",
            "world_type": "invariance",
            "control": "orthogonal_gauge",
            "view": "chart",
            "value": gauge_error,
            "passed": bool(
                gauge_error
                <= config["targets"]["maximum_gauge_error"]
            ),
            "details": "",
        },
        {
            "repetition": repetition,
            "world": "endogenous_source_partition_matched",
            "world_type": "invariance",
            "control": "common_shift",
            "view": "chart",
            "value": shift_error,
            "passed": bool(
                shift_error
                <= config["targets"]["maximum_common_shift_error"]
            ),
            "details": "",
        },
    ]


def _refusal_rows(
    *,
    repetition: int,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for index, world in enumerate(config["refusal_worlds"]):
        seed = int(
            config["seed"]
            + repetition * 1_000_003
            + 80_000_009
            + index * 10_003
        )
        observed, _ = generate_m4_chart_ecology_world(
            world=world,
            spec=spec,
            seed=seed,
        )
        chart = fit_response_safe_eiv_chart(
            observed.condition,
            **_eiv_parameters(config, seed=seed),
        )
        rows.append(
            {
                "repetition": repetition,
                "world": world,
                "world_type": "refusal",
                "control": "chart_refusal",
                "view": "chart",
                "value": float(chart.refused),
                "passed": bool(chart.refused),
                "details": "|".join(chart.refusal_reasons),
            }
        )
    return rows


def _alias_row(
    *,
    repetition: int,
    spec: M4ChartEcologySpec,
    config: dict[str, Any],
) -> dict[str, Any]:
    seed = int(
        config["seed"] + repetition * 1_000_003 + 90_000_011
    )
    observed, _ = generate_m4_chart_ecology_world(
        world="condition_alias_ecology",
        spec=spec,
        seed=seed,
    )
    aliased = _duplicate_evaluation_condition(observed.condition)
    chart = fit_response_safe_eiv_chart(
        aliased,
        **_eiv_parameters(config, seed=seed),
    )
    basis = build_response_safe_basis(chart, aliased)["evaluation"]
    distance = float(np.linalg.norm(basis[0] - basis[1]))
    return {
        "repetition": repetition,
        "observable_alias_distance": distance,
        "false_latent_recovery": bool(distance > 1e-12),
        "chart_refused": chart.refused,
        "refusal_reasons": "|".join(chart.refusal_reasons),
    }


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
    controls: pd.DataFrame,
    aliases: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    test = metrics[metrics["view"] == "test"].copy()
    main = test[test["world_type"] == "main"]
    target = main[main["world"].isin(config["target_worlds"])]
    other = main[~main["world"].isin(config["target_worlds"])]
    null = test[test["world_type"] == "null"]
    eiv = target[target["chart"] == "eiv"].copy()
    c0 = target[target["chart"] == "c0"].copy()
    pca = target[target["chart"] == "pca"].copy()
    pivot = target.pivot_table(
        index=["repetition", "world"],
        columns="chart",
        values="recovered_headroom",
        aggfunc="mean",
    )
    advantage = (
        pivot["eiv"] - pivot["pca"]
    ).rename("value").reset_index()
    recovery_by_repetition = _cluster_values(
        eiv,
        "recovered_headroom",
    )
    advantage_by_repetition = _cluster_values(
        advantage,
        "value",
    )
    headroom_by_repetition = _cluster_values(
        eiv,
        "oracle_headroom",
    )
    mean_recovery = float(eiv["recovered_headroom"].mean())
    recovery_lcb = _cluster_lcb(
        recovery_by_repetition,
        seed=int(config["bootstrap_seed"]),
        repetitions=int(config["bootstrap_repetitions"]),
    )
    mean_advantage = float(advantage["value"].mean())
    advantage_lcb = _cluster_lcb(
        advantage_by_repetition,
        seed=int(config["bootstrap_seed"]) + 1,
        repetitions=int(config["bootstrap_repetitions"]),
    )
    oracle_headroom = float(eiv["oracle_headroom"].mean())
    oracle_headroom_lcb = _cluster_lcb(
        headroom_by_repetition,
        seed=int(config["bootstrap_seed"]) + 2,
        repetitions=int(config["bootstrap_repetitions"]),
    )
    target_world_recovery = {}
    for world, values in eiv.groupby("world", sort=True):
        eligible = values[
            values["oracle_headroom"]
            >= targets["minimum_oracle_headroom"]
        ]
        if len(eligible):
            target_world_recovery[str(world)] = float(
                eligible["recovered_headroom"].mean()
            )
    eiv_other = other[other["chart"] == "eiv"]
    eiv_null = null[null["chart"] == "eiv"]
    null_false_rate = float(
        (
            (eiv_null["geometry_gain"] >= 0.03)
            & (eiv_null["geometry"] >= 0.70)
        ).mean()
    ) if len(eiv_null) else 0.0
    hazard_degradation = float(
        eiv["evaluation_loss"].mean()
        / max(c0["evaluation_loss"].mean(), 1e-12)
        - 1.0
    )
    shuffle = controls[
        (controls["control"] == "source_condition_shuffle")
        & (controls["view"] == "test")
        & (controls["world"].isin(config["target_worlds"]))
    ]
    invariance = controls[controls["world_type"] == "invariance"]
    refusal = controls[controls["world_type"] == "refusal"]
    forbidden = refusal[
        refusal["world"].isin(
            ["author_leakage", "response_leakage_circular"]
        )
    ]
    support = refusal[
        refusal["world"] == "evaluation_support_shift"
    ]
    diagnostics = {
        "mean_recovered_headroom": mean_recovery,
        "recovered_headroom_lcb": recovery_lcb,
        "positive_repetitions": int(
            np.sum(recovery_by_repetition > 0.0)
        ),
        "mean_advantage_over_same_rank_pca": mean_advantage,
        "pca_advantage_lcb": advantage_lcb,
        "oracle_headroom": oracle_headroom,
        "oracle_headroom_lcb": oracle_headroom_lcb,
        "target_world_recovered_headroom": target_world_recovery,
        "other_world_gain": (
            float(eiv_other["geometry_gain"].mean())
            if len(eiv_other)
            else 0.0
        ),
        "hazard_relative_degradation": hazard_degradation,
        "shuffle_gain": (
            float(shuffle["value"].mean()) if len(shuffle) else 0.0
        ),
        "null_false_success_rate": null_false_rate,
        "selected_rank_mean": float(eiv["selected_rank"].mean()),
        "principal_angle_maximum": float(
            eiv["principal_angle_maximum"].max()
        ),
        "coverage_minimum": float(eiv["coverage"].min()),
        "singular_margin_minimum": float(
            eiv["singular_margin"].min()
        ),
        "target_chart_refusal_rate": float(
            eiv["chart_refused"].mean()
        ),
        "gauge_max_error": float(
            invariance.loc[
                invariance["control"] == "orthogonal_gauge",
                "value",
            ].max()
        ),
        "common_shift_max_error": float(
            invariance.loc[
                invariance["control"] == "common_shift",
                "value",
            ].max()
        ),
        "response_hash_failures": int(
            invariance.loc[
                invariance["control"] == "response_bytes",
                "value",
            ].sum()
        ),
        "alias_false_recovery_rate": float(
            aliases["false_latent_recovery"].mean()
        ),
        "forbidden_refusal_rate": float(forbidden["passed"].mean()),
        "support_refusal_rate": float(support["passed"].mean()),
        "topology_refusal_rate": float(
            refusal.loc[
                refusal["world"] == "topology_mismatch",
                "passed",
            ].mean()
        ),
    }
    checks = {
        "recovered_headroom": (
            diagnostics["mean_recovered_headroom"]
            >= targets["minimum_mean_recovered_headroom"]
            and diagnostics["recovered_headroom_lcb"]
            > targets["minimum_recovered_headroom_lcb"]
            and diagnostics["positive_repetitions"]
            >= targets["minimum_positive_repetitions"]
        ),
        "same_rank_pca_advantage": (
            diagnostics["mean_advantage_over_same_rank_pca"]
            >= targets["minimum_pca_advantage"]
            and diagnostics["pca_advantage_lcb"] > 0.0
        ),
        "oracle_headroom": (
            diagnostics["oracle_headroom"]
            >= targets["minimum_oracle_headroom"]
            and diagnostics["oracle_headroom_lcb"] > 0.0
        ),
        "target_world_recovery": (
            bool(diagnostics["target_world_recovered_headroom"])
            and min(
                diagnostics["target_world_recovered_headroom"].values()
            )
            >= targets["minimum_target_world_recovery"]
        ),
        "other_world_noninferiority": (
            diagnostics["other_world_gain"]
            >= -targets["maximum_other_world_degradation"]
        ),
        "hazard_noninferiority": (
            diagnostics["hazard_relative_degradation"]
            <= targets["maximum_hazard_relative_degradation"]
        ),
        "source_shuffle_null": (
            diagnostics["shuffle_gain"]
            <= targets["maximum_shuffle_gain"]
        ),
        "no_creation_specificity": (
            diagnostics["null_false_success_rate"]
            <= targets["maximum_null_false_success_rate"]
        ),
        "chart_stability": (
            diagnostics["target_chart_refusal_rate"] == 0.0
            and diagnostics["principal_angle_maximum"]
            <= targets["maximum_principal_angle_degrees"]
            and diagnostics["coverage_minimum"]
            >= targets["minimum_coverage"]
            and diagnostics["singular_margin_minimum"] > 0.0
        ),
        "gauge_invariance": (
            diagnostics["gauge_max_error"]
            <= targets["maximum_gauge_error"]
        ),
        "common_shift_invariance": (
            diagnostics["common_shift_max_error"]
            <= targets["maximum_common_shift_error"]
        ),
        "response_safety": (
            diagnostics["response_hash_failures"]
            <= targets["maximum_response_hash_failures"]
        ),
        "alias_safety": (
            diagnostics["alias_false_recovery_rate"]
            <= targets["maximum_alias_false_recovery_rate"]
        ),
        "forbidden_provenance_refusal": (
            diagnostics["forbidden_refusal_rate"]
            >= targets["minimum_forbidden_refusal_rate"]
        ),
        "support_shift_refusal": (
            diagnostics["support_refusal_rate"]
            >= targets["minimum_support_refusal_rate"]
        ),
    }
    if not checks["alias_safety"]:
        decision = "M4_C35_NO_GO_ALIAS_UNSAFE"
    elif all(checks.values()):
        decision = "M4_C35_GO_RESPONSE_SAFE_EIV_CHART"
    else:
        decision = "M4_C35_NO_GO_RESPONSE_SAFE_CHART_IDENTIFICATION"
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic response-safe condition-chart evidence only. "
            "The chart uses no response, author identity, mechanism label, "
            "synthetic truth, Big Five, or MBTI during fitting. A pass would "
            "still require a separately frozen C2 transport confirmation; "
            "it cannot identify personality, validate natural text, or "
            "authorize M4-D."
        ),
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
) -> str:
    test = metrics[metrics["view"] == "test"]
    chart_table = (
        test[test["world_type"] == "main"]
        .groupby("chart", sort=True)[
            [
                "geometry",
                "geometry_gain",
                "recovered_headroom",
                "evaluation_loss",
            ]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    world_table = (
        test[
            (test["world_type"] == "main")
            & (test["chart"].isin(["c0", "pca", "eiv"]))
        ]
        .pivot_table(
            index="world",
            columns="chart",
            values="recovered_headroom",
            aggfunc="mean",
        )
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    control_table = (
        controls.groupby(["world_type", "control"], sort=True)
        .agg(value=("value", "mean"), pass_rate=("passed", "mean"))
        .reset_index()
        .to_markdown(index=False, floatfmt=".6f")
    )
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4-C.3.5 Response-Safe Cross-View EIV Chart

## Decision

`{decision["decision"]}`

The C3.4 gate-zero direct-creation estimand, `K=8` excitation, discovered
`C0` response/choice anchor, and truth-open oracle ceiling were held fixed.
Only the condition basis supplied to the Fisher-Wiener creation estimator was
changed. The EIV chart was fitted from replicated pre-response condition
tensors and compared with same-rank source-1 PCA and a source-shuffled null.

## Chart comparison

{chart_table}

## Main-world recovered headroom

{world_table}

## Controls

{control_table}

## Diagnostics

{diagnostics}

## Gates

{checks}

## Boundary

{decision["claim_boundary"]}

M4-D remains blocked independently of this result.
"""


def _write_outputs(
    *,
    config: dict[str, Any],
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
    aliases: pd.DataFrame,
    decision: dict[str, Any],
) -> None:
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    controls.to_csv(output / "controls.csv", index=False)
    aliases.to_csv(output / "alias_audit.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _report(decision, metrics, controls),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_response_safe_eiv_chart.json",
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
        config["repetitions"] = int(args.repetition_limit)
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
    worlds = [
        ("main", world) for world in config["main_worlds"]
    ] + [
        ("null", world) for world in config["null_worlds"]
    ]
    metric_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    alias_rows: list[dict[str, Any]] = []
    start = int(args.repetition_start)
    stop = start + int(config["repetitions"])
    for repetition in range(start, stop):
        first_condition = None
        first_seed = None
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
            rows, controls = _world_rows(
                repetition=repetition,
                world=world,
                world_type=world_type,
                passive=passive,
                truth=truth,
                spec=spec,
                config=config,
                seed=seed,
            )
            metric_rows.extend(rows)
            control_rows.extend(controls)
            if first_condition is None:
                first_condition = passive.condition
                first_seed = seed
        if first_condition is None or first_seed is None:
            raise ValueError("at least one main or null world is required")
        control_rows.extend(
            _invariance_rows(
                repetition=repetition,
                observed=first_condition,
                config=config,
                seed=first_seed,
            )
        )
        control_rows.extend(
            _refusal_rows(
                repetition=repetition,
                spec=spec,
                config=config,
            )
        )
        alias_rows.append(
            _alias_row(
                repetition=repetition,
                spec=spec,
                config=config,
            )
        )

    metrics = pd.DataFrame(metric_rows)
    controls = pd.DataFrame(control_rows)
    aliases = pd.DataFrame(alias_rows)
    decision = _decision(
        metrics,
        controls,
        aliases,
        config=config,
    )
    _write_outputs(
        config=config,
        metrics=metrics,
        controls=controls,
        aliases=aliases,
        decision=decision,
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
