#!/usr/bin/env python3
"""Run M4-C.2 chart-covariant opportunity-ecology discovery."""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_chart_ecology_audit import (  # noqa: E402
    MECHANISMS,
    audit_m4_chart_ecology,
)
from suica_core.m4_chart_ecology_contracts import (  # noqa: E402
    M4ChartEcologyObserved,
)
from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    build_m4_discovered_basis,
    fit_m4_chart_ecology,
    fit_m4_chart_ecology_route,
    rotate_whitened_basis,
    route_action_max_difference,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_contracts import (  # noqa: E402
    M4ConditionObserved,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    PANEL_NAMES,
    fit_m4_condition_chart,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _route_parameters(config: dict[str, Any]) -> dict[str, Any]:
    values = dict(config["route_estimator"])
    values["ridge_grid"] = tuple(float(x) for x in values["ridge_grid"])
    return values


def _permuted_condition_responses(
    observed: M4ChartEcologyObserved,
    *,
    seed: int,
) -> M4ChartEcologyObserved:
    rng = np.random.default_rng(seed)
    panels = {}
    for name in PANEL_NAMES:
        panel = getattr(observed.condition, name)
        response = panel.response.reshape(-1, panel.response.shape[-1]).copy()
        rng.shuffle(response, axis=0)
        panels[name] = replace(
            panel,
            response=response.reshape(panel.response.shape),
        )
    condition = M4ConditionObserved(
        **panels,
        design=dict(observed.condition.design),
    )
    return replace(observed, condition=condition)


def _response_invariance(
    observed: M4ChartEcologyObserved,
    *,
    candidates: tuple[dict[str, Any], ...],
    chart_thresholds: dict[str, float],
    seed: int,
) -> bool:
    first = fit_m4_condition_chart(
        observed.condition,
        candidates=candidates,
        **chart_thresholds,
    )
    second = fit_m4_condition_chart(
        _permuted_condition_responses(
            observed,
            seed=seed,
        ).condition,
        candidates=candidates,
        **chart_thresholds,
    )
    if first.selected_family != second.selected_family:
        return False
    if first.selected_parameters != second.selected_parameters:
        return False
    return all(
        np.allclose(
            first.panel_features[name],
            second.panel_features[name],
            atol=1e-12,
            rtol=0.0,
        )
        for name in PANEL_NAMES
    )


def _basis_invariance(
    observed: M4ChartEcologyObserved,
    estimate: Any,
    *,
    config: dict[str, Any],
    seed: int,
) -> tuple[bool, float]:
    if (
        estimate.chart.refused
        or "evaluation_support_shift" in estimate.refusal_reasons
    ):
        return True, 0.0
    _, basis = build_m4_discovered_basis(
        observed,
        estimate.chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=config.get("maximum_rank"),
    )
    rotated = fit_m4_chart_ecology_route(
        observed.ecology,
        rotate_whitened_basis(basis, seed=seed),
        basis_name="rotated_discovered",
        **_route_parameters(config),
    )
    difference = route_action_max_difference(
        estimate.discovered,
        rotated,
    )
    selected_equal = (
        np.array_equal(
            estimate.discovered.train_selected_model,
            rotated.train_selected_model,
        )
        and np.array_equal(
            estimate.discovered.test_selected_model,
            rotated.test_selected_model,
        )
    )
    return (
        bool(
            selected_equal
            and difference
            <= float(config["basis_invariance_tolerance"])
        ),
        difference,
    )


def _world_seed(
    base: int,
    repetition: int,
    world: str,
    world_index: int,
) -> int:
    matched_groups = {
        "linear_exogenous_selection": 101,
        "endogenous_source_partition_matched": 101,
        "fast_return_equal_marginal": 211,
        "slow_hysteresis_equal_marginal": 211,
    }
    offset = matched_groups.get(world, 1_009 + world_index * 10_003)
    return int(base + repetition * 1_000_003 + offset)


def _serialize_nested(row: dict[str, Any]) -> dict[str, Any]:
    output = dict(row)
    for name, value in output.items():
        if isinstance(value, (list, dict, tuple)):
            output[name] = json.dumps(
                value,
                ensure_ascii=True,
                sort_keys=isinstance(value, dict),
            )
    return output


def _rbf_mmd(first: np.ndarray, second: np.ndarray) -> float:
    x, x_count = np.unique(
        np.asarray(first, dtype=float),
        return_counts=True,
    )
    y, y_count = np.unique(
        np.asarray(second, dtype=float),
        return_counts=True,
    )
    x_weight = x_count / np.sum(x_count)
    y_weight = y_count / np.sum(y_count)
    joined = np.concatenate([x, y])
    distances = np.abs(joined[:, None] - joined[None]).reshape(-1)
    positive = distances[distances > 1e-12]
    bandwidth = float(np.median(positive)) if len(positive) else 1.0

    def kernel(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return np.exp(
            -0.5
            * ((a[:, None] - b[None]) / max(bandwidth, 1e-8)) ** 2
        )

    value = (
        float(x_weight @ kernel(x, x) @ x_weight)
        + float(y_weight @ kernel(y, y) @ y_weight)
        - 2.0 * float(x_weight @ kernel(x, y) @ y_weight)
    )
    return float(np.sqrt(max(value, 0.0)))


def _path_marginals(observed: M4ChartEcologyObserved) -> dict[str, np.ndarray]:
    panels = (
        observed.ecology.train_evaluation,
        observed.ecology.test_evaluation,
    )
    menu_mass = np.concatenate(
        [np.mean(panel.menu, axis=-1).ravel() for panel in panels]
    )
    outside = np.concatenate(
        [(panel.choice == 0).astype(float).ravel() for panel in panels]
    )
    available = np.concatenate(
        [np.sum(panel.menu, axis=-1).ravel() for panel in panels]
    )
    entropy_proxy = np.log1p(available)
    return {
        "menu_mass": menu_mass,
        "outside": outside,
        "choice_entropy_proxy": entropy_proxy,
    }


def _matched_union_max_difference(
    first: M4ChartEcologyObserved,
    second: M4ChartEcologyObserved,
) -> float:
    names = (
        "train_calibration",
        "train_selection",
        "train_evaluation",
        "test_calibration",
        "test_selection",
        "test_evaluation",
    )
    return float(
        max(
            np.max(
                np.abs(
                    getattr(first.ecology, name).menu.astype(float)
                    - getattr(second.ecology, name).menu.astype(float)
                )
            )
            for name in names
        )
    )


def _matched_environment_max_difference(
    first: M4ChartEcologyObserved,
    second: M4ChartEcologyObserved,
) -> float:
    names = (
        "train_calibration",
        "train_selection",
        "train_evaluation",
        "test_calibration",
        "test_selection",
        "test_evaluation",
    )
    return float(
        max(
            np.max(
                np.abs(
                    getattr(first.ecology, name).environment
                    - getattr(second.ecology, name).environment
                )
            )
            for name in names
        )
    )


def _matched_condition_max_difference(
    first: M4ChartEcologyObserved,
    second: M4ChartEcologyObserved,
) -> float:
    return float(
        max(
            np.max(
                np.abs(
                    getattr(first.condition, name).pre_context
                    - getattr(second.condition, name).pre_context
                )
            )
            for name in PANEL_NAMES
        )
    )


def _selected_condition_tv(
    first: M4ChartEcologyObserved,
    second: M4ChartEcologyObserved,
) -> float:
    categories = first.ecology.train_evaluation.menu.shape[-1]

    def distribution(observed: M4ChartEcologyObserved) -> np.ndarray:
        choice = np.concatenate(
            [
                observed.ecology.train_evaluation.choice.ravel(),
                observed.ecology.test_evaluation.choice.ravel(),
            ]
        )
        count = np.bincount(choice, minlength=categories + 1).astype(float)
        return count / np.sum(count)

    return float(
        0.5 * np.sum(np.abs(distribution(first) - distribution(second)))
    )


def _matched_metrics(
    observed: dict[str, M4ChartEcologyObserved],
) -> dict[str, float]:
    selection_observed = observed["linear_exogenous_selection"]
    creation_observed = observed["endogenous_source_partition_matched"]
    selection = _path_marginals(selection_observed)
    creation = _path_marginals(creation_observed)
    fast = _path_marginals(observed["fast_return_equal_marginal"])
    slow = _path_marginals(observed["slow_hysteresis_equal_marginal"])
    return {
        "selection_creation_union_max_difference": (
            _matched_union_max_difference(
                selection_observed,
                creation_observed,
            )
        ),
        "selection_creation_environment_max_difference": (
            _matched_environment_max_difference(
                selection_observed,
                creation_observed,
            )
        ),
        "selection_creation_condition_max_difference": (
            _matched_condition_max_difference(
                selection_observed,
                creation_observed,
            )
        ),
        "selection_creation_menu_mmd": _rbf_mmd(
            selection["menu_mass"],
            creation["menu_mass"],
        ),
        "selection_creation_entropy_mmd": _rbf_mmd(
            selection["choice_entropy_proxy"],
            creation["choice_entropy_proxy"],
        ),
        "selection_creation_outside_gap": abs(
            float(np.mean(selection["outside"]))
            - float(np.mean(creation["outside"]))
        ),
        "selection_creation_selected_condition_tv": (
            _selected_condition_tv(
                selection_observed,
                creation_observed,
            )
        ),
        "fast_slow_menu_mmd": _rbf_mmd(
            fast["menu_mass"],
            slow["menu_mass"],
        ),
        "fast_slow_outside_gap": abs(
            float(np.mean(fast["outside"]))
            - float(np.mean(slow["outside"]))
        ),
    }


def _support_macro_f1(
    metrics: pd.DataFrame,
    *,
    prefix: str,
    authors: int,
) -> float:
    scores = []
    for mechanism in MECHANISMS:
        truth = metrics[f"truth_{mechanism}"].to_numpy(dtype=int)
        rate = metrics[
            f"{prefix}predicted_{mechanism}_rate"
        ].to_numpy(dtype=float)
        true_positive = float(np.sum(rate[truth == 1]) * authors)
        false_negative = float(np.sum(1.0 - rate[truth == 1]) * authors)
        false_positive = float(np.sum(rate[truth == 0]) * authors)
        denominator = (
            2.0 * true_positive + false_positive + false_negative
        )
        scores.append(
            2.0 * true_positive / denominator
            if denominator > 1e-12
            else 1.0
        )
    return float(np.mean(scores))


def _summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    excluded = {
        "world",
        "expected_status",
        "active_mechanisms",
        "refusal_reasons",
        "predicted_labels",
        "oracle_predicted_labels",
        "selected_models",
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


def _aggregate_decision(
    metrics: pd.DataFrame,
    repetitions: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["discovery_targets"]
    authors = int(config["base_spec"]["mechanism_authors"])
    identifiable = metrics[metrics["expected_status"] == "IDENTIFIABLE"]
    active = identifiable[identifiable["active_mechanisms"] != ""]
    selection_worlds = active[
        active["active_mechanisms"].str.contains("selection")
    ]
    loop = active[active["active_mechanisms"].str.contains("creation")]
    return_worlds = identifiable[
        identifiable["active_mechanisms"].str.contains("return")
    ]
    gate = metrics[metrics["world"] == "history_gated_ecology"]
    alias = metrics[metrics["world"] == "condition_alias_ecology"]
    source_alias = metrics[
        metrics["world"] == "hidden_opportunity_source_alias"
    ]
    null = metrics[metrics["world"] == "linear_null_ecology"]
    discovered_f1 = _support_macro_f1(
        identifiable,
        prefix="",
        authors=authors,
    )
    oracle_f1 = _support_macro_f1(
        identifiable,
        prefix="oracle_",
        authors=authors,
    )
    diagnostics = {
        "oracle_mechanism_macro_f1": oracle_f1,
        "discovered_mechanism_macro_f1": discovered_f1,
        "mechanism_macro_f1_drop": oracle_f1 - discovered_f1,
        "active_support_f1": float(active["support_f1"].mean()),
        "active_sign_accuracy": float(active["sign_accuracy"].mean()),
        "choice_action_geometry": float(
            selection_worlds["choice_action_geometry"].mean()
        ),
        "creation_action_geometry": float(
            loop["creation_action_geometry"].mean()
        ),
        "loop_action_geometry": float(loop["loop_action_geometry"].mean()),
        "return_spearman": float(
            return_worlds["return_spearman"].mean()
        ),
        "recovery_spearman": float(active["recovery_spearman"].mean()),
        "history_gate_margin": float(
            gate["gate_direction_margin"].mean()
        ),
        "expected_resolution_rate": float(
            metrics["expected_resolution"].mean()
        ),
        "condition_alias_information_loss_rate": float(
            alias["truth_open_alias_information_loss"].mean()
        ),
        "source_alias_refusal_rate": float(
            source_alias["source_alias_refusal_rate"].mean()
        ),
        "null_false_positive_rate": float(
            null["null_false_positive_rate"].mean()
        ),
        "basis_action_invariance_rate": float(
            metrics["basis_action_invariant"].mean()
        ),
        "response_invariance_rate": float(
            metrics["response_perturbation_invariant"].mean()
        ),
        "maximum_basis_action_difference": float(
            metrics["basis_action_max_difference"].max()
        ),
        "matched_menu_mmd": float(
            repetitions["selection_creation_menu_mmd"].mean()
        ),
        "matched_entropy_mmd": float(
            repetitions["selection_creation_entropy_mmd"].mean()
        ),
        "matched_outside_gap": float(
            repetitions["selection_creation_outside_gap"].mean()
        ),
        "matched_union_max_difference": float(
            repetitions[
                "selection_creation_union_max_difference"
            ].max()
        ),
        "matched_environment_max_difference": float(
            repetitions[
                "selection_creation_environment_max_difference"
            ].max()
        ),
        "matched_condition_max_difference": float(
            repetitions[
                "selection_creation_condition_max_difference"
            ].max()
        ),
        "matched_selected_condition_tv": float(
            repetitions[
                "selection_creation_selected_condition_tv"
            ].mean()
        ),
        "fast_slow_menu_mmd": float(
            repetitions["fast_slow_menu_mmd"].mean()
        ),
        "fast_slow_outside_gap": float(
            repetitions["fast_slow_outside_gap"].mean()
        ),
    }
    checks = {
        "oracle_route_valid": (
            diagnostics["oracle_mechanism_macro_f1"]
            >= targets["minimum_oracle_mechanism_macro_f1"]
        ),
        "discovered_mechanism_recovery": (
            diagnostics["discovered_mechanism_macro_f1"]
            >= targets["minimum_discovered_mechanism_macro_f1"]
        ),
        "oracle_relative_mechanism_loss": (
            diagnostics["mechanism_macro_f1_drop"]
            <= targets["maximum_mechanism_macro_f1_drop"]
        ),
        "active_support": (
            diagnostics["active_support_f1"]
            >= targets["minimum_active_support_f1"]
        ),
        "action_signs": (
            diagnostics["active_sign_accuracy"]
            >= targets["minimum_sign_accuracy"]
        ),
        "choice_action": (
            diagnostics["choice_action_geometry"]
            >= targets["minimum_choice_action_geometry"]
        ),
        "creation_action": (
            diagnostics["creation_action_geometry"]
            >= targets["minimum_creation_action_geometry"]
        ),
        "loop_action": (
            diagnostics["loop_action_geometry"]
            >= targets["minimum_loop_action_geometry"]
        ),
        "return_geometry": (
            diagnostics["return_spearman"]
            >= targets["minimum_return_spearman"]
        ),
        "recovery_geometry": (
            diagnostics["recovery_spearman"]
            >= targets["minimum_recovery_spearman"]
        ),
        "history_gate": (
            diagnostics["history_gate_margin"]
            >= targets["minimum_history_gate_margin"]
        ),
        "refusal_worlds": (
            diagnostics["expected_resolution_rate"]
            >= targets["minimum_expected_resolution_rate"]
        ),
        "condition_alias": (
            diagnostics["condition_alias_information_loss_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
        "source_alias": (
            diagnostics["source_alias_refusal_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
        "null_calibration": (
            diagnostics["null_false_positive_rate"]
            <= targets["maximum_null_false_positive_rate"]
        ),
        "response_safety": (
            diagnostics["response_invariance_rate"] == 1.0
        ),
        "basis_covariance": (
            diagnostics["basis_action_invariance_rate"] == 1.0
        ),
        "matched_marginals": (
            diagnostics["matched_union_max_difference"]
            <= targets["maximum_matched_union_difference"]
            and diagnostics["matched_environment_max_difference"]
            <= targets["maximum_matched_environment_difference"]
            and diagnostics["matched_condition_max_difference"]
            <= targets["maximum_matched_condition_difference"]
            and
            diagnostics["matched_menu_mmd"]
            <= targets["maximum_matched_mmd"]
            and diagnostics["matched_entropy_mmd"]
            <= targets["maximum_matched_mmd"]
            and diagnostics["matched_outside_gap"]
            <= targets["maximum_matched_outside_gap"]
            and diagnostics["fast_slow_menu_mmd"]
            <= targets["maximum_fast_slow_mmd"]
            and diagnostics["fast_slow_outside_gap"]
            <= targets["maximum_fast_slow_outside_gap"]
        ),
    }
    identification = all(
        checks[name]
        for name in (
            "oracle_route_valid",
            "refusal_worlds",
            "condition_alias",
            "source_alias",
            "null_calibration",
            "response_safety",
            "basis_covariance",
        )
    )
    if not checks["oracle_route_valid"]:
        decision = "M4_C2_INVALID_WORLD_OR_ESTIMATOR"
    elif not identification:
        decision = "M4_C2_NO_GO_IDENTIFICATION"
    elif not all(
        checks[name]
        for name in (
            "discovered_mechanism_recovery",
            "oracle_relative_mechanism_loss",
            "choice_action",
            "creation_action",
            "loop_action",
        )
    ):
        decision = "M4_C2_NO_GO_CHART_TRANSPORT"
    elif all(checks.values()):
        decision = "M4_C2_CHART_COVARIANT_ECOLOGY_TRANSPORT_PASS"
    else:
        decision = (
            "M4_C2_CHART_COVARIANT_ECOLOGY_TRANSPORT_"
            "PASS_WITH_SCOPE_CORRECTION"
        )
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Finite synthetic chart-covariant opportunity ecology only. "
            "The result concerns response-safe condition measures and "
            "physical operator actions. It does not identify coordinate "
            "axes, topic names, personality, emotion, diagnosis, natural "
            "text validity, or clinical use."
        ),
    }


def _repetition_decisions(
    metrics: pd.DataFrame,
    repetitions: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Recompute every substantive gate independently within each repetition."""
    excluded = {"response_safety", "basis_covariance"}
    rows = []
    for repetition in sorted(metrics["repetition"].unique()):
        repeated_metrics = metrics[metrics["repetition"] == repetition]
        repeated_marginals = repetitions[
            repetitions["repetition"] == repetition
        ]
        result = _aggregate_decision(
            repeated_metrics,
            repeated_marginals,
            config,
        )
        substantive = {
            name: passed
            for name, passed in result["checks"].items()
            if name not in excluded
        }
        rows.append(
            {
                "repetition": int(repetition),
                "core_pass": bool(all(substantive.values())),
                "decision": result["decision"],
                **{
                    f"check_{name}": bool(passed)
                    for name, passed in result["checks"].items()
                },
                **result["diagnostics"],
            }
        )
    return pd.DataFrame(rows)


def _decision(
    metrics: pd.DataFrame,
    repetitions: pd.DataFrame,
    repetition_decisions: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Apply aggregate gates plus a preregistered repetition-stability gate."""
    result = _aggregate_decision(metrics, repetitions, config)
    targets = config["discovery_targets"]
    passed = int(repetition_decisions["core_pass"].sum())
    total = int(len(repetition_decisions))
    required = int(
        targets.get(
            "minimum_passing_repetitions",
            int(np.ceil(0.75 * total)),
        )
    )
    stable = passed >= required
    result["diagnostics"].update(
        {
            "passing_repetitions": passed,
            "total_repetitions": total,
            "required_passing_repetitions": required,
        }
    )
    result["checks"]["repetition_stability"] = stable
    if (
        not stable
        and result["decision"]
        in {
            "M4_C2_CHART_COVARIANT_ECOLOGY_TRANSPORT_PASS",
            (
                "M4_C2_CHART_COVARIANT_ECOLOGY_TRANSPORT_"
                "PASS_WITH_SCOPE_CORRECTION"
            ),
        }
    ):
        result["decision"] = "M4_C2_NO_GO_REPETITION_STABILITY"
    return result


def _report(
    decision: dict[str, Any],
    config: dict[str, Any],
) -> str:
    diagnostics = "\n".join(
        f"- `{name}`: {value:.6f}"
        for name, value in decision["diagnostics"].items()
    )
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA M4-C.2 Chart-Covariant Ecology Discovery

## Decision

`{decision["decision"]}`

## Question

Can the complete M4-B ecology be re-expressed on a response-safe discovered
condition chart without comparing arbitrary coordinate axes or matrix cells?

The menu is a finite condition measure,

\\[
\\nu_{{u,t}}=J^{{-1}}\\sum_j M_{{u,t,j}}\\delta_{{z_j}},
\\qquad
o_{{u,t}}=\\int\\phi(z)d\\nu_{{u,t}}(z),
\\]

and the primary comparison is the action of selection, response, creation,
feedback, return, recovery, and history-gate operators on a frozen physical
query bank.

## Frozen design

- config version: `{config["version"]}`
- repetitions: `{config["repetitions"]}`
- worlds: `{", ".join(config["worlds"])}`
- reference calibration and selection authors: disjoint
- chart inputs: author-independent pre-response descriptors only
- chart basis: constant mass coordinate plus reference-whitened relation
  coordinates
- comparison: oracle versus discovered action, never coefficient cells
- repetition stability: at least
  `{config["discovery_targets"].get("minimum_passing_repetitions", "75%")}`
  independent repetitions must pass every substantive gate

## Diagnostics

{diagnostics}

## Gates

{checks}

## Scope

The chart is frozen before path responses are opened. Calibration fits model
candidates, mechanism selection chooses regularization/model family, and the
evaluation path is untouched until the final action audit. Source
nonidentifiability, support shift, author leakage, response leakage, and
topology conflict are operational refusal routes. Condition alias is different:
it is confirmed only in this truth-open synthetic audit by oracle information
loss and is not claimed as an operational detector.

Specific PCA/Isomap/landmark families, dimensions, axes, raw coefficients,
matrix elements, spectral radii, thresholds, and synthetic scores remain
engineering diagnostics. No psychological interpretation is licensed.

## Artifacts

- metrics: `results/m4_chart_ecology/metrics.csv`
- repetition metrics: `results/m4_chart_ecology/repetition_metrics.csv`
- repetition gates: `results/m4_chart_ecology/repetition_gate_metrics.csv`
- world summary: `results/m4_chart_ecology/world_summary.csv`
- decision: `results/m4_chart_ecology/decision.json`
"""


def _write_outputs(
    metrics: pd.DataFrame,
    repetitions: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    summary = _summarize(metrics)
    repetition_decisions = _repetition_decisions(
        metrics,
        repetitions,
        config,
    )
    decision = _decision(
        metrics,
        repetitions,
        repetition_decisions,
        config,
    )
    metrics.to_csv(output / "metrics.csv", index=False)
    repetitions.to_csv(output / "repetition_metrics.csv", index=False)
    repetition_decisions.to_csv(
        output / "repetition_gate_metrics.csv",
        index=False,
    )
    summary.to_csv(output / "world_summary.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, config), encoding="utf-8")
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_chart_ecology.json",
    )
    parser.add_argument(
        "--summarize-existing",
        action="store_true",
        help="Recompute summaries and gates from existing CSV artifacts.",
    )
    args = parser.parse_args()
    config = _load(args.config)
    output = ROOT / config["output_directory"]
    if args.summarize_existing:
        metrics = pd.read_csv(output / "metrics.csv")
        repetitions = pd.read_csv(output / "repetition_metrics.csv")
        decision = _write_outputs(metrics, repetitions, config)
        print(json.dumps(decision, indent=2, sort_keys=True))
        return

    spec = M4ChartEcologySpec(**config["base_spec"])
    candidates = tuple(dict(value) for value in config["candidates"])
    route_parameters = _route_parameters(config)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    repetition_rows = []
    for repetition in range(int(config["repetitions"])):
        observed_by_world: dict[str, M4ChartEcologyObserved] = {}
        repetition_metrics = []
        for world_index, world in enumerate(config["worlds"]):
            seed = _world_seed(
                int(config["seed"]),
                repetition,
                world,
                world_index,
            )
            observed, truth = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            observed_by_world[world] = observed
            estimate = fit_m4_chart_ecology(
                observed,
                candidates=candidates,
                rank_tolerance=float(config["rank_tolerance"]),
                maximum_rank=config.get("maximum_rank"),
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
            if repetition == 0:
                response_invariant = _response_invariance(
                    observed,
                    candidates=candidates,
                    chart_thresholds=config["chart_thresholds"],
                    seed=seed + 700_001,
                )
                basis_invariant, basis_difference = _basis_invariance(
                    observed,
                    estimate,
                    config=config,
                    seed=seed + 900_001,
                )
            else:
                response_invariant = True
                basis_invariant = True
                basis_difference = 0.0
            result = audit_m4_chart_ecology(
                estimate,
                oracle,
                truth,
                basis_action_invariant=basis_invariant,
                response_perturbation_invariant=response_invariant,
                **config["audit"],
            )
            result["basis_action_max_difference"] = basis_difference
            result["repetition"] = repetition
            result["seed"] = seed
            result["authors"] = spec.mechanism_authors
            rows.append(_serialize_nested(result))
            repetition_metrics.append(result)
        matched = _matched_metrics(observed_by_world)
        frame = pd.DataFrame(repetition_metrics)
        repeated = {
            "repetition": repetition,
            **matched,
            "expected_resolution_rate": float(
                frame["expected_resolution"].mean()
            ),
        }
        repetition_rows.append(repeated)
    metrics = pd.DataFrame(rows)
    repetitions = pd.DataFrame(repetition_rows)
    decision = _write_outputs(metrics, repetitions, config)
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
