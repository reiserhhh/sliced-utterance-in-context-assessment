#!/usr/bin/env python3
"""Run the paired M4-C.3.5-R2 response-safe chart replacement experiment."""
from __future__ import annotations

import argparse
from dataclasses import replace
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
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
    subset_opportunity_budget,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)
from suica_core.m4_response_safe_chart_replacement import (  # noqa: E402
    basis_oracle_cka,
    build_current_pooled_attribution_route,
    linear_cka,
    match_nonmass_trace,
    nonmass_rank_and_trace,
    repeatability_projected_basis,
    rotate_spectral_block_basis,
    truncate_whitened_basis,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


ARM_NAMES = ("B0", "Br_var", "Br_rep", "R", "Oest")


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _rcca_parameters(config: dict[str, Any], *, seed: int) -> dict[str, Any]:
    values = dict(config["rcca"])
    values["gamma_grid"] = tuple(float(value) for value in values["gamma_grid"])
    values["seed"] = int(seed)
    return values


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(value) for value in values["ridge_grid"])
    return values


def _creation_parameters(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": str(config["creation_estimator"]["hazard_model"]),
        "ridge": float(config["route_estimator"]["hazard_ridge"]),
        "iterations": int(config["route_estimator"]["logistic_iterations"]),
        "epsilon_scale": float(config["creation_estimator"]["epsilon_scale"]),
    }


def _expanded_worlds(
    config: dict[str, Any],
) -> list[tuple[str, str, str]]:
    """Return world type, generator world, and unique output label."""
    worlds = [
        ("main", world, world) for world in config["main_worlds"]
    ]
    for world in config["null_worlds"]:
        repeats = int(config.get("null_repeats", {}).get(world, 1))
        worlds.extend(
            (
                "null",
                world,
                f"{world}__draw_{draw:02d}",
            )
            for draw in range(repeats)
        )
    return worlds


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


def _cluster_ucb(
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
    return float(np.quantile(np.mean(draws, axis=1), 0.975))


def _cluster_ratio_lcb(
    numerator: np.ndarray,
    denominator: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float]:
    top = np.asarray(numerator, dtype=float)
    bottom = np.asarray(denominator, dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(top), size=(repetitions, len(top)))
    denominator_mean = np.mean(bottom[indices], axis=1)
    valid = denominator_mean > 0.0
    valid_rate = float(np.mean(valid))
    if valid_rate < 0.975:
        return float("nan"), valid_rate
    values = np.mean(top[indices], axis=1)[valid] / denominator_mean[valid]
    return float(np.quantile(values, 0.025)), valid_rate


def _wilson_upper(successes: int, trials: int) -> float:
    if trials <= 0:
        return 1.0
    z = 1.959963984540054
    proportion = successes / trials
    denominator = 1.0 + z**2 / trials
    center = proportion + z**2 / (2.0 * trials)
    radius = z * np.sqrt(
        proportion * (1.0 - proportion) / trials
        + z**2 / (4.0 * trials**2)
    )
    return float((center + radius) / denominator)


def _map_condition(
    observed: M4ConditionObserved,
    function: Any,
) -> M4ConditionObserved:
    fields = (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    )
    return M4ConditionObserved(
        **{
            field: function(getattr(observed, field))
            for field in fields
        },
        design=dict(observed.design),
    )


def _shift_condition(
    observed: M4ConditionObserved,
    *,
    value: float,
) -> M4ConditionObserved:
    return _map_condition(
        observed,
        lambda panel: replace(
            panel,
            pre_context=panel.pre_context + value,
        ),
    )


def _alias_mechanism_conditions(
    observed: M4ConditionObserved,
) -> M4ConditionObserved:
    """Make two latent mechanism conditions observationally identical."""
    updates = {}
    for name in (
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        pre = panel.pre_context.copy()
        pre[:, :, 1] = pre[:, :, 0]
        updates[name] = replace(panel, pre_context=pre)
    return replace(observed, **updates)


def _loop(
    route: Any,
    anchor: Any,
    view_name: str,
) -> np.ndarray:
    return compose_creation_only_loop(
        getattr(route, view_name).creation,
        getattr(anchor, view_name),
    )


def _max_loop_difference(
    first: Any,
    second: Any,
    anchor: Any,
) -> float:
    return max(
        float(np.max(np.abs(
            _loop(first, anchor, view_name)
            - _loop(second, anchor, view_name)
        )))
        for view_name in ("train", "test")
    )


def _arm_metric_rows(
    *,
    repetition: int,
    world: str,
    world_type: str,
    routes: dict[str, Any],
    bases: dict[str, dict[str, np.ndarray]],
    anchor: Any,
    oracle: Any,
    old_rank: int,
    rcca: Any,
) -> list[dict[str, Any]]:
    cka = {
        arm: basis_oracle_cka(basis, {
            role: values
            for role, values in oracle["basis"].items()
        })
        for arm, basis in bases.items()
    }
    rows = []
    for view_name in ("train", "test"):
        anchor_view = getattr(anchor, view_name)
        oracle_view = getattr(oracle["route"], view_name)
        target = oracle_view.jacobian_loop
        oracle_swap = author_relation_geometry(
            compose_creation_only_loop(
                oracle_view.creation,
                anchor_view,
            ),
            target,
        )
        for arm in ARM_NAMES:
            view = getattr(routes[arm], view_name)
            geometry = author_relation_geometry(
                compose_creation_only_loop(
                    view.creation,
                    anchor_view,
                ),
                target,
            )
            rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "world_type": world_type,
                    "view": view_name,
                    "arm": arm,
                    "geometry": geometry,
                    "oracle_swap_geometry": oracle_swap,
                    "evaluation_loss": float(np.mean(view.evaluation_loss)),
                    "comparable_hazard_loss": float(
                        np.mean(view.comparable_hazard_loss)
                    ),
                    "oracle_cka_calibration": cka[arm]["calibration"],
                    "oracle_cka_selection": cka[arm]["selection"],
                    "oracle_cka_evaluation": cka[arm]["evaluation"],
                    "oracle_cka_mean": float(np.mean(list(cka[arm].values()))),
                    "old_rank": old_rank,
                    "rcca_support_rank_1": rcca.support_ranks[0],
                    "rcca_support_rank_2": rcca.support_ranks[1],
                    "rcca_shared_rank_lower": rcca.shared_rank_lower,
                    "rcca_shared_rank_upper": rcca.shared_rank_upper,
                    "rcca_shared_rank": rcca.shared_rank,
                    "rcca_refused": rcca.refused,
                    "rcca_refusal_reasons": "|".join(rcca.refusal_reasons),
                }
            )
    return rows


def _paired_frame(metrics: pd.DataFrame, *, world_type: str) -> pd.DataFrame:
    frame = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == world_type)
    ]
    keys = ["repetition", "world"]
    geometry = frame.pivot(index=keys, columns="arm", values="geometry")
    cka = frame.pivot(
        index=keys,
        columns="arm",
        values="oracle_cka_evaluation",
    )
    loss = frame.pivot(
        index=keys,
        columns="arm",
        values="comparable_hazard_loss",
    )
    oracle_swap = frame.groupby(keys)["oracle_swap_geometry"].first()
    output = pd.DataFrame(index=geometry.index)
    for arm in ARM_NAMES:
        output[f"geometry_{arm}"] = geometry[arm]
        output[f"cka_{arm}"] = cka[arm]
        output[f"loss_{arm}"] = loss[arm]
    output["oracle_swap_geometry"] = oracle_swap
    output["headroom"] = output["oracle_swap_geometry"] - output["geometry_B0"]
    output["gain_R_B0"] = output["geometry_R"] - output["geometry_B0"]
    output["gain_R_Br_var"] = (
        output["geometry_R"] - output["geometry_Br_var"]
    )
    output["gain_R_Br_rep"] = (
        output["geometry_R"] - output["geometry_Br_rep"]
    )
    output["gain_Oest_B0"] = output["geometry_Oest"] - output["geometry_B0"]
    output["gain_R_Oest"] = output["geometry_R"] - output["geometry_Oest"]
    output["cka_gain_R_B0"] = output["cka_R"] - output["cka_B0"]
    output["cka_gain_R_Br_var"] = output["cka_R"] - output["cka_Br_var"]
    output["cka_gain_R_Br_rep"] = output["cka_R"] - output["cka_Br_rep"]
    return output.reset_index()


def _decision(
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    conditional = config.get("estimand_variant") == "conditional"
    main = _paired_frame(metrics, world_type="main")
    null = _paired_frame(metrics, world_type="null")
    eligible = main[main["world"].isin(config["eligible_worlds"])].copy()
    sentinel = main[main["world"].isin(config["sentinel_worlds"])].copy()
    boundary = main[
        main["world"].isin(config.get("boundary_worlds", []))
    ].copy()
    by_repetition = main.groupby("repetition", sort=True).mean(numeric_only=True)
    eligible_by_repetition = (
        eligible.groupby("repetition", sort=True).mean(numeric_only=True)
    )
    effect = eligible if conditional else main
    effect_by_repetition = (
        effect.groupby("repetition", sort=True).mean(numeric_only=True)
    )
    seed = int(config["bootstrap_seed"])
    boot = int(config["bootstrap_repetitions"])
    global_headroom = float(main["headroom"].mean())
    headroom = float(eligible["headroom"].mean())
    global_gain = float(main["gain_R_B0"].mean())
    eligible_gain = float(eligible["gain_R_B0"].mean())
    gain = eligible_gain if conditional else global_gain
    variance_rank_gain = float(main["gain_R_Br_var"].mean())
    repeatability_rank_gain = float(main["gain_R_Br_rep"].mean())
    oracle_gain = float(eligible["gain_Oest_B0"].mean())
    recovered = eligible_gain / headroom if headroom > 0.0 else float("nan")
    oracle_recovered = (
        oracle_gain / headroom if headroom > 0.0 else float("nan")
    )
    accessible = (
        eligible_gain / oracle_gain if oracle_gain > 0.0 else float("nan")
    )
    recovery_lcb, recovery_valid = _cluster_ratio_lcb(
        eligible_by_repetition["gain_R_B0"].to_numpy(),
        eligible_by_repetition["headroom"].to_numpy(),
        seed=seed + 4,
        repetitions=boot,
    )
    accessible_lcb, accessible_valid = _cluster_ratio_lcb(
        eligible_by_repetition["gain_R_B0"].to_numpy(),
        eligible_by_repetition["gain_Oest_B0"].to_numpy(),
        seed=seed + 5,
        repetitions=boot,
    )
    world_gain = main.groupby("world", sort=True)["gain_R_B0"].mean()
    eligible_worlds = {}
    for index, (world, values) in enumerate(
        eligible.groupby("world", sort=True)
    ):
        repeated = values.groupby(
            "repetition",
            sort=True,
        ).mean(numeric_only=True)
        ratio_lcb, ratio_valid = _cluster_ratio_lcb(
            repeated["gain_R_B0"].to_numpy(),
            repeated["headroom"].to_numpy(),
            seed=seed + 100 + index,
            repetitions=boot,
        )
        eligible_worlds[str(world)] = {
            "headroom": float(values["headroom"].mean()),
            "headroom_lcb": _cluster_lcb(
                repeated["headroom"].to_numpy(),
                seed=seed + 200 + index,
                repetitions=boot,
            ),
            "gain": float(values["gain_R_B0"].mean()),
            "recovery": float(
                values["gain_R_B0"].mean()
                / values["headroom"].mean()
            ),
            "recovery_lcb": ratio_lcb,
            "ratio_valid_bootstrap_rate": ratio_valid,
            "positive_repetitions": int(
                np.sum(repeated["gain_R_B0"] > 0.0)
            ),
        }
    sentinel_worlds = {}
    for index, (world, values) in enumerate(
        sentinel.groupby("world", sort=True)
    ):
        repeated = values.groupby(
            "repetition",
            sort=True,
        )["gain_R_B0"].mean().to_numpy()
        sentinel_worlds[str(world)] = {
            "gain": float(values["gain_R_B0"].mean()),
            "gain_lcb": _cluster_lcb(
                repeated,
                seed=seed + 300 + index,
                repetitions=boot,
            ),
        }
    boundary_worlds = {}
    for index, (world, values) in enumerate(
        boundary.groupby("world", sort=True)
    ):
        repeated = values.groupby(
            "repetition",
            sort=True,
        )["gain_R_Oest"].mean().to_numpy()
        boundary_worlds[str(world)] = {
            "oracle_fidelity": float(values["gain_R_Oest"].mean()),
            "oracle_fidelity_lcb": _cluster_lcb(
                repeated,
                seed=seed + 400 + index,
                repetitions=boot,
            ),
        }
    permutation = controls[controls["control"] == "author_permutation"]
    gauge = controls[controls["control"] == "block_gauge"]
    shift = controls[controls["control"] == "common_shift"]
    shuffle = controls[controls["control"] == "source_shuffle"]
    support = controls[controls["control"] == "support_shift"]
    alias = controls[controls["control"] == "latent_alias"]
    basis_contract = controls[controls["control"] == "basis_contract"]
    cka_permutation = controls[controls["control"] == "cka_permutation"]
    native_cells = metrics.drop_duplicates(
        ["repetition", "world", "world_type"]
    )
    null_false = null["gain_R_B0"] >= targets["null_gain_threshold"]
    null_successes = int(np.sum(null_false))
    null_trials = int(len(null_false))
    effect_gain_lcb = _cluster_lcb(
        effect_by_repetition["gain_R_B0"].to_numpy(),
        seed=seed + 2,
        repetitions=boot,
    )
    hazard_by_repetition = (
        by_repetition["loss_R"]
        / np.maximum(by_repetition["loss_B0"], 1e-12)
        - 1.0
    )
    diagnostics = {
        "global_oracle_headroom": global_headroom,
        "eligible_oracle_headroom": headroom,
        "oracle_headroom_lcb": _cluster_lcb(
            eligible_by_repetition["headroom"].to_numpy(),
            seed=seed,
            repetitions=boot,
        ),
        "oracle_estimator_gain": oracle_gain,
        "oracle_estimator_gain_lcb": _cluster_lcb(
            eligible_by_repetition["gain_Oest_B0"].to_numpy(),
            seed=seed + 1,
            repetitions=boot,
        ),
        "oracle_estimator_recovered_headroom": oracle_recovered,
        "global_rcca_gain": global_gain,
        "rcca_gain": gain,
        "rcca_gain_lcb": effect_gain_lcb,
        "rcca_variance_rank_gain": variance_rank_gain,
        "rcca_variance_rank_gain_lcb": _cluster_lcb(
            by_repetition["gain_R_Br_var"].to_numpy(),
            seed=seed + 3,
            repetitions=boot,
        ),
        "rcca_repeatability_rank_gain": repeatability_rank_gain,
        "rcca_repeatability_rank_gain_lcb": _cluster_lcb(
            by_repetition["gain_R_Br_rep"].to_numpy(),
            seed=seed + 11,
            repetitions=boot,
        ),
        "rcca_recovered_headroom": recovered,
        "rcca_recovered_headroom_lcb": recovery_lcb,
        "rcca_recovery_ratio_valid_bootstrap_rate": recovery_valid,
        "rcca_accessible_efficiency": accessible,
        "rcca_accessible_efficiency_lcb": accessible_lcb,
        "rcca_accessible_ratio_valid_bootstrap_rate": accessible_valid,
        "rcca_oracle_noninferiority_lcb": _cluster_lcb(
            eligible_by_repetition["gain_R_B0"].to_numpy()
            - eligible_by_repetition["gain_Oest_B0"].to_numpy(),
            seed=seed + 12,
            repetitions=boot,
        ),
        "positive_repetitions": int(
            np.sum(effect_by_repetition["gain_R_B0"] > 0.0)
        ),
        "positive_worlds": int(
            np.sum(
                (
                    eligible.groupby("world", sort=True)["gain_R_B0"].mean()
                    if conditional
                    else world_gain
                )
                > 0.0
            )
        ),
        "minimum_world_gain": float(world_gain.min()),
        "eligible_worlds": eligible_worlds,
        "sentinel_worlds": sentinel_worlds,
        "boundary_worlds": boundary_worlds,
        "cka_gain_rcca_baseline": float(main["cka_gain_R_B0"].mean()),
        "cka_gain_rcca_baseline_lcb": _cluster_lcb(
            by_repetition["cka_gain_R_B0"].to_numpy(),
            seed=seed + 6,
            repetitions=boot,
        ),
        "cka_gain_rcca_variance_rank": float(
            main["cka_gain_R_Br_var"].mean()
        ),
        "cka_gain_rcca_variance_rank_lcb": _cluster_lcb(
            by_repetition["cka_gain_R_Br_var"].to_numpy(),
            seed=seed + 7,
            repetitions=boot,
        ),
        "cka_gain_rcca_repeatability_rank": float(
            main["cka_gain_R_Br_rep"].mean()
        ),
        "cka_gain_rcca_repeatability_rank_lcb": _cluster_lcb(
            by_repetition["cka_gain_R_Br_rep"].to_numpy(),
            seed=seed + 13,
            repetitions=boot,
        ),
        "cka_permutation_p_maximum": float(cka_permutation["value"].max()),
        "hazard_relative_degradation": float(
            main["loss_R"].mean() / max(main["loss_B0"].mean(), 1e-12)
            - 1.0
        ),
        "hazard_relative_degradation_ucb": _cluster_ucb(
            hazard_by_repetition.to_numpy(),
            seed=seed + 14,
            repetitions=boot,
        ),
        "author_permutation_gain": float(permutation["value"].mean()),
        "null_false_successes": null_successes,
        "null_trials": null_trials,
        "null_false_success_rate": float(null_false.mean()),
        "null_false_success_wilson_upper": _wilson_upper(
            null_successes,
            null_trials,
        ),
        "native_rcca_refusal_rate": float(native_cells["rcca_refused"].mean()),
        "same_rank_control_coverage": float(
            (native_cells["old_rank"] >= native_cells["rcca_shared_rank"]).mean()
        ),
        "basis_contract_pass_rate": float(basis_contract["passed"].mean()),
        "source_shuffle_zero_rank_or_refusal_rate": float(
            shuffle["passed"].mean()
        ),
        "support_shift_refusal_rate": float(support["passed"].mean()),
        "alias_false_recovery_rate": float((~alias["passed"]).mean()),
        "downstream_gauge_max_error": float(gauge["value"].max()),
        "downstream_common_shift_max_error": float(shift["value"].max()),
    }
    checks = {
        "oracle_headroom": (
            diagnostics["eligible_oracle_headroom"]
            >= targets["minimum_oracle_headroom"]
            and diagnostics["oracle_headroom_lcb"] > 0.0
        ),
        "oracle_estimator_ceiling": (
            diagnostics["oracle_estimator_gain_lcb"] > 0.0
            and diagnostics["oracle_estimator_recovered_headroom"]
            >= targets["minimum_oracle_estimator_recovery"]
        ),
        "rcca_absolute_gain": (
            diagnostics["rcca_gain"] >= targets["minimum_rcca_gain"]
            and diagnostics["rcca_gain_lcb"] > 0.0
        ),
        "same_rank_superiority": (
            diagnostics["rcca_variance_rank_gain_lcb"] > 0.0
            and diagnostics["rcca_repeatability_rank_gain_lcb"] > 0.0
            and diagnostics["same_rank_control_coverage"]
            >= targets["minimum_same_rank_control_coverage"]
            and diagnostics["basis_contract_pass_rate"] >= 1.0
        ),
        "headroom_recovery": (
            diagnostics["rcca_recovered_headroom"]
            >= targets["minimum_rcca_recovery"]
            and diagnostics["rcca_recovered_headroom_lcb"]
            >= targets["minimum_rcca_recovery_lcb"]
            and diagnostics["rcca_recovery_ratio_valid_bootstrap_rate"]
            >= targets["minimum_ratio_valid_bootstrap_rate"]
        ),
        "accessible_efficiency": (
            diagnostics["rcca_accessible_efficiency"]
            >= targets["minimum_accessible_efficiency"]
            and diagnostics["rcca_accessible_efficiency_lcb"]
            >= targets["minimum_accessible_efficiency_lcb"]
            and diagnostics["rcca_accessible_ratio_valid_bootstrap_rate"]
            >= targets["minimum_ratio_valid_bootstrap_rate"]
            and diagnostics["rcca_oracle_noninferiority_lcb"]
            >= -targets["maximum_oracle_noninferiority_margin"]
        ),
        "repetition_consistency": (
            diagnostics["positive_repetitions"]
            >= targets["minimum_positive_repetitions"]
        ),
        "world_consistency": (
            all(
                values["headroom_lcb"] > 0.0
                and values["recovery_lcb"]
                >= targets["minimum_high_headroom_world_recovery"]
                and values["ratio_valid_bootstrap_rate"]
                >= targets["minimum_ratio_valid_bootstrap_rate"]
                and values["positive_repetitions"]
                >= targets.get(
                    "minimum_positive_repetitions_per_eligible_world",
                    0,
                )
                for values in eligible_worlds.values()
            )
            and all(
                values["gain_lcb"]
                >= -targets["maximum_sentinel_world_degradation"]
                for values in sentinel_worlds.values()
            )
            and all(
                values["oracle_fidelity_lcb"]
                >= -targets.get(
                    "maximum_boundary_oracle_degradation",
                    float("inf"),
                )
                for values in boundary_worlds.values()
            )
        ),
        "oracle_gram_alignment": (
            diagnostics["cka_gain_rcca_baseline_lcb"] > 0.0
            and diagnostics["cka_gain_rcca_variance_rank_lcb"] > 0.0
            and diagnostics["cka_gain_rcca_repeatability_rank_lcb"] > 0.0
            and diagnostics["cka_permutation_p_maximum"]
            <= targets["maximum_cka_permutation_p"]
        ),
        "hazard_noninferiority": (
            diagnostics["hazard_relative_degradation_ucb"]
            <= targets["maximum_hazard_relative_degradation"]
        ),
        "author_permutation_null": (
            diagnostics["author_permutation_gain"]
            <= targets["maximum_author_permutation_gain"]
        ),
        "null_specificity": (
            diagnostics["null_false_success_wilson_upper"]
            <= targets["maximum_null_false_success_wilson_upper"]
        ),
        "chart_native_acceptance": (
            diagnostics["native_rcca_refusal_rate"]
            <= targets["maximum_native_rcca_refusal_rate"]
        ),
        "source_shuffle": (
            diagnostics["source_shuffle_zero_rank_or_refusal_rate"]
            >= targets["minimum_source_shuffle_rate"]
        ),
        "support_shift": (
            diagnostics["support_shift_refusal_rate"]
            >= targets["minimum_support_shift_refusal_rate"]
        ),
        "observable_alias": (
            diagnostics["alias_false_recovery_rate"]
            <= targets["maximum_alias_false_recovery_rate"]
        ),
        "downstream_invariance": (
            diagnostics["downstream_gauge_max_error"]
            <= targets["maximum_downstream_gauge_error"]
            and diagnostics["downstream_common_shift_max_error"]
            <= targets["maximum_downstream_common_shift_error"]
        ),
    }
    if config["phase"] == "smoke":
        smoke_keys = (
            "same_rank_superiority",
            "chart_native_acceptance",
            "source_shuffle",
            "support_shift",
            "observable_alias",
            "downstream_invariance",
        )
        smoke_integrity = (
            diagnostics["same_rank_control_coverage"] >= 1.0
            and diagnostics["basis_contract_pass_rate"] >= 1.0
            and all(
                checks[name]
                for name in smoke_keys
                if name != "same_rank_superiority"
            )
        )
        decision = (
            "M4_C35_R2_SMOKE_COMPLETE"
            if smoke_integrity
            else "M4_C35_R2_SMOKE_STOP"
        )
    elif all(checks.values()):
        if config["phase"] == "confirmation":
            decision = (
                "M4_C35_R2B_CONDITIONAL_CHART_EFFECT_GO"
                if conditional
                else "M4_C35_R2_CHART_REPLACEMENT_GO"
            )
        else:
            decision = (
                "M4_C35_R2B_READY_TO_FREEZE"
                if conditional
                else "M4_C35_R2_READY_TO_FREEZE"
            )
    elif (
        diagnostics["rcca_gain_lcb"] > 0.0
        and diagnostics["rcca_variance_rank_gain_lcb"] > 0.0
        and diagnostics["rcca_repeatability_rank_gain_lcb"] > 0.0
    ):
        decision = (
            "M4_C35_R2B_PARTIAL_CONDITIONAL_EFFECT"
            if conditional
            else "M4_C35_R2_PARTIAL_CHART_EFFECT"
        )
    else:
        decision = "M4_C35_R2_NO_GO_CHART_REPLACEMENT"
    return {
        "estimand_id": config["estimand_id"],
        "phase": config["phase"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite-synthetic conditional paired chart effect only. "
            if conditional
            else "Finite-synthetic paired chart replacement only. "
        ) + (
            "RCCA saw "
            "pre-response condition tensors only; response and oracle truth "
            "were opened only after every chart arm was frozen for scoring. "
            "No personality, natural-text, clinical, or M4-D claim follows."
        ),
    }


def _report(decision: dict[str, Any], metrics: pd.DataFrame) -> str:
    pairs = _paired_frame(metrics, world_type="main")
    worlds = (
        pairs.groupby("world", sort=True)[
            [
                "geometry_B0",
                "geometry_Br_var",
                "geometry_Br_rep",
                "geometry_R",
                "geometry_Oest",
                "headroom",
                "gain_R_B0",
                "gain_R_Br_var",
                "gain_R_Br_rep",
                "gain_R_Oest",
                "cka_gain_R_B0",
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
    return f"""# SUICA M4-C.3.5-R2 Response-Safe Chart Replacement

## Decision

`{decision["decision"]}`

This paired experiment holds the C3.4 gate-zero estimand, physical anchor,
current observation law, and Fisher-Wiener pooling fixed. It compares the old
response-safe chart (`B0`), its top-variance rank match (`Br_var`), its
repeatability-selected rank match (`Br_rep`), the frozen RCCA spectral-block
chart (`R`), and the truth-open oracle chart with the same estimator (`Oest`).
The oracle creation swap remains only the scoring denominator.

## Main-world means

{worlds}

## Diagnostics

{diagnostics}

## Gates

{checks}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_response_safe_chart_replacement.json",
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
        config["main_worlds"] = config["main_worlds"][: args.main_world_limit]
    if args.null_world_limit is not None:
        config["null_worlds"] = config["null_worlds"][: args.null_world_limit]
    if args.output_directory is not None:
        config["output_directory"] = args.output_directory
    if args.report_path is not None:
        config["report_path"] = args.report_path

    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    route_parameters = _route_parameters(config)
    creation_parameters = _creation_parameters(config)
    rows: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    worlds = _expanded_worlds(config)
    start = int(args.repetition_start)
    stop = start + int(config["repetitions"])

    for repetition in range(start, stop):
        for world_index, (world_type, generator_world, world) in enumerate(
            worlds
        ):
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            passive, truth = generate_m4_chart_ecology_world(
                world=generator_world,
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
            old_chart = fit_m4_condition_chart(
                passive.condition,
                candidates=candidates,
                **config["chart_thresholds"],
            )
            old_transform, old_basis = build_m4_discovered_basis(
                passive,
                old_chart,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=int(config["maximum_rank"]),
            )
            rcca = fit_response_safe_rcca_chart(
                passive.condition,
                **_rcca_parameters(config, seed=seed),
            )
            rcca_basis = build_response_safe_rcca_basis(
                rcca,
                passive.condition,
            )
            variance_basis = match_nonmass_trace(
                truncate_whitened_basis(
                    old_basis,
                    rank=rcca.shared_rank,
                ),
                rcca_basis,
            )
            repeatability_basis = match_nonmass_trace(
                repeatability_projected_basis(
                    old_transform,
                    passive.condition,
                    old_basis,
                    rank=rcca.shared_rank,
                    author_blocks=int(config["rcca"]["author_blocks"]),
                ),
                rcca_basis,
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
                old_basis,
                basis_name="anchor_old_response_safe",
                **route_parameters,
            )
            oracle_route = fit_m4_physical_edge_route(
                passive.ecology,
                truth.oracle_basis,
                basis_name="oracle_max_passive",
                **route_parameters,
            )
            bases = {
                "B0": old_basis,
                "Br_var": variance_basis,
                "Br_rep": repeatability_basis,
                "R": rcca_basis,
                "Oest": truth.oracle_basis,
            }
            basis_stats = {
                arm: nonmass_rank_and_trace(bases[arm])
                for arm in ("Br_var", "Br_rep", "R")
            }
            trace_error = max(
                abs(
                    basis_stats[arm][role][1]
                    - basis_stats["R"][role][1]
                )
                / max(basis_stats["R"][role][1], 1e-12)
                for arm in ("Br_var", "Br_rep")
                for role in ("calibration", "selection", "evaluation")
            )
            rank_contract = all(
                basis_stats[arm][role][0] == rcca.shared_rank
                for arm in ("Br_var", "Br_rep", "R")
                for role in ("calibration", "selection", "evaluation")
            )
            controls.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "control": "basis_contract",
                    "value": trace_error,
                    "passed": bool(rank_contract and trace_error <= 1e-10),
                    "details": json.dumps(
                        {
                            arm: {
                                role: [int(values[0]), float(values[1])]
                                for role, values in roles.items()
                            }
                            for arm, roles in basis_stats.items()
                        },
                        sort_keys=True,
                    ),
                }
            )
            routes = {
                arm: build_current_pooled_attribution_route(
                    excited.ecology,
                    basis,
                    **creation_parameters,
                )
                for arm, basis in bases.items()
            }
            rows.extend(
                _arm_metric_rows(
                    repetition=repetition,
                    world=world,
                    world_type=world_type,
                    routes=routes,
                    bases=bases,
                    anchor=anchor,
                    oracle={
                        "route": oracle_route,
                        "basis": truth.oracle_basis,
                    },
                    old_rank=old_transform.effective_rank,
                    rcca=rcca,
                )
            )

            if world_type == "main":
                cka_rng = np.random.default_rng(
                    int(config["cka_permutation_seed"]) + seed
                )
                observed_cka = linear_cka(
                    rcca_basis["evaluation"][:, 1:],
                    truth.oracle_basis["evaluation"][:, 1:],
                )
                exceedances = 0
                for _ in range(int(config["cka_permutation_repetitions"])):
                    permutation = cka_rng.permutation(spec.categories)
                    null_cka = linear_cka(
                        rcca_basis["evaluation"][:, 1:],
                        truth.oracle_basis["evaluation"][permutation, 1:],
                    )
                    exceedances += int(null_cka >= observed_cka)
                cka_p = (
                    exceedances + 1
                ) / (
                    int(config["cka_permutation_repetitions"]) + 1
                )
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "cka_permutation",
                        "value": cka_p,
                        "passed": bool(
                            cka_p
                            <= config["targets"][
                                "maximum_cka_permutation_p"
                            ]
                        ),
                        "details": "",
                    }
                )
                rng = np.random.default_rng(
                    int(config["permutation_seed"]) + seed
                )
                permutation = rng.permutation(spec.mechanism_authors)
                permuted = build_current_pooled_attribution_route(
                    excited.ecology,
                    rcca_basis,
                    **creation_parameters,
                    second_permutation=permutation,
                )
                native_geometry = author_relation_geometry(
                    _loop(routes["R"], anchor, "test"),
                    oracle_route.test.jacobian_loop,
                )
                permuted_geometry = author_relation_geometry(
                    _loop(permuted, anchor, "test"),
                    oracle_route.test.jacobian_loop,
                )
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "author_permutation",
                        "value": permuted_geometry - native_geometry,
                        "passed": bool(
                            permuted_geometry - native_geometry
                            <= config["targets"][
                                "maximum_author_permutation_gain"
                            ]
                        ),
                        "details": "",
                    }
                )
                shuffled = fit_response_safe_rcca_chart(
                    passive.condition,
                    shuffle_source_two=True,
                    **_rcca_parameters(config, seed=seed + 500_009),
                )
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "source_shuffle",
                        "value": float(shuffled.shared_rank_lower),
                        "passed": bool(
                            shuffled.shared_rank_lower == 0 or shuffled.refused
                        ),
                        "details": "|".join(shuffled.refusal_reasons),
                    }
                )

            if world_index == 0:
                rotated_basis = rotate_spectral_block_basis(
                    rcca_basis,
                    rcca.spectral_blocks,
                    seed=seed + 700_001,
                )
                rotated_route = build_current_pooled_attribution_route(
                    excited.ecology,
                    rotated_basis,
                    **creation_parameters,
                )
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "block_gauge",
                        "value": _max_loop_difference(
                            routes["R"],
                            rotated_route,
                            anchor,
                        ),
                        "passed": True,
                        "details": "",
                    }
                )
                shifted_condition = _shift_condition(
                    passive.condition,
                    value=23.75,
                )
                shifted_chart = fit_response_safe_rcca_chart(
                    shifted_condition,
                    **_rcca_parameters(config, seed=seed),
                )
                shifted_basis = build_response_safe_rcca_basis(
                    shifted_chart,
                    shifted_condition,
                )
                shifted_route = build_current_pooled_attribution_route(
                    excited.ecology,
                    shifted_basis,
                    **creation_parameters,
                )
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "common_shift",
                        "value": _max_loop_difference(
                            routes["R"],
                            shifted_route,
                            anchor,
                        ),
                        "passed": True,
                        "details": "",
                    }
                )

        support_seed = int(
            config["seed"] + repetition * 1_000_003 + 80_000_009
        )
        support_observed, _ = generate_m4_chart_ecology_world(
            world="evaluation_support_shift",
            spec=spec,
            seed=support_seed,
        )
        support_chart = fit_response_safe_rcca_chart(
            support_observed.condition,
            **_rcca_parameters(config, seed=support_seed),
        )
        controls.append(
            {
                "repetition": repetition,
                "world": "evaluation_support_shift",
                "control": "support_shift",
                "value": float(support_chart.refused),
                "passed": bool(support_chart.refused),
                "details": "|".join(support_chart.refusal_reasons),
            }
        )
        alias_seed = int(
            config["seed"] + repetition * 1_000_003 + 90_000_011
        )
        alias_observed, alias_truth = generate_m4_chart_ecology_world(
            world="condition_alias_ecology",
            spec=spec,
            seed=alias_seed,
        )
        aliased = _alias_mechanism_conditions(alias_observed.condition)
        alias_observed = replace(alias_observed, condition=aliased)
        alias_chart = fit_response_safe_rcca_chart(
            aliased,
            **_rcca_parameters(config, seed=alias_seed),
        )
        alias_basis = build_response_safe_rcca_basis(alias_chart, aliased)
        alias_excited = build_excited_observed(
            alias_observed,
            alias_truth,
            spec,
            seed=alias_seed,
            amplitude=float(config["excitation_amplitude"]),
        )
        alias_route = build_current_pooled_attribution_route(
            alias_excited.ecology,
            alias_basis,
            **creation_parameters,
        )
        alias_distance = float(np.max(np.linalg.norm(
            alias_route.test.creation[:, 0]
            - alias_route.test.creation[:, 1],
            axis=1,
        )))
        latent_distance = float(np.linalg.norm(
            alias_truth.oracle_basis["evaluation"][0, 1:]
            - alias_truth.oracle_basis["evaluation"][1, 1:]
        ))
        controls.append(
            {
                "repetition": repetition,
                "world": "condition_alias_ecology",
                "control": "latent_alias",
                "value": alias_distance,
                "passed": bool(
                    alias_chart.refused
                    or (
                        latent_distance
                        >= config["targets"]["minimum_latent_alias_distance"]
                        and alias_distance
                        <= config["targets"][
                            "maximum_latent_alias_recovery"
                        ]
                    )
                ),
                "details": json.dumps(
                    {
                        "latent_distance": latent_distance,
                        "refusal_reasons": alias_chart.refusal_reasons,
                    },
                    sort_keys=True,
                ),
            }
        )

    metrics = pd.DataFrame(rows)
    control_frame = pd.DataFrame(controls)
    decision = _decision(metrics, control_frame, config=config)
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    control_frame.to_csv(output / "controls.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, metrics), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
