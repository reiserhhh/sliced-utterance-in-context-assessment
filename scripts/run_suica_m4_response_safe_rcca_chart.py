#!/usr/bin/env python3
"""Run the response-only-blind M4-C.3.5-R1 RCCA chart gate."""
from __future__ import annotations

import argparse
from collections import Counter
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

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_contracts import (  # noqa: E402
    M4ConditionObserved,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _parameters(
    config: dict[str, Any],
    *,
    seed: int,
) -> dict[str, Any]:
    values = dict(config["rcca"])
    values["gamma_grid"] = tuple(
        float(value) for value in values["gamma_grid"]
    )
    values["seed"] = int(seed)
    return values


def _map_panels(
    observed: M4ConditionObserved,
    function: Any,
) -> M4ConditionObserved:
    values = {
        name: function(getattr(observed, name))
        for name in (
            "reference_calibration",
            "reference_selection",
            "mechanism_calibration",
            "mechanism_selection",
            "mechanism_evaluation",
        )
    }
    return M4ConditionObserved(**values, design=dict(observed.design))


def _mutate_responses(
    observed: M4ConditionObserved,
    *,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    return _map_panels(
        observed,
        lambda panel: replace(
            panel,
            response=rng.normal(size=panel.response.shape),
        ),
    )


def _rotate(
    observed: M4ConditionObserved,
    *,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    width = observed.reference_calibration.pre_context.shape[-1]
    rotations = [
        np.linalg.qr(rng.normal(size=(width, width)))[0]
        for _ in range(2)
    ]

    def rotate_panel(panel: Any) -> Any:
        pre = panel.pre_context.copy()
        for source in range(2):
            pre[source] = pre[source] @ rotations[source]
        return replace(panel, pre_context=pre)

    return _map_panels(observed, rotate_panel)


def _shift(
    observed: M4ConditionObserved,
    *,
    value: float,
) -> M4ConditionObserved:
    return _map_panels(
        observed,
        lambda panel: replace(
            panel,
            pre_context=panel.pre_context + value,
        ),
    )


def _distance_error(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    return float(np.max(np.abs(
        pdist(np.asarray(first, dtype=float))
        - pdist(np.asarray(second, dtype=float))
    )))


def _metric_row(
    *,
    repetition: int,
    world: str,
    chart: Any,
) -> dict[str, Any]:
    block_pattern = ",".join(
        f"{start}:{stop}" for start, stop in chart.spectral_blocks
    )
    return {
        "repetition": repetition,
        "world": world,
        "support_rank_source_1": chart.support_ranks[0],
        "support_rank_source_2": chart.support_ranks[1],
        "shared_rank_lower": chart.shared_rank_lower,
        "shared_rank_upper": chart.shared_rank_upper,
        "shared_rank": chart.shared_rank,
        "spectral_block_pattern": block_pattern,
        "support_selection_minimum": min(
            chart.consensus_concentration
        ),
        "support_stability_minimum": min(chart.support_stability),
        "support_stability_lcb_minimum": min(
            chart.support_stability_lcb
        ),
        "consensus_minimum_eigenvalue": min(
            chart.consensus_minimum_eigenvalue
        ),
        "consensus_eigengap_lcb_minimum": min(
            chart.consensus_eigengap_lcb
        ),
        "rank_boundary_lcb_minimum": min(
            chart.support_rank_boundary_lcb
        ),
        "next_boundary_ucb_maximum": max(
            chart.support_next_boundary_ucb
        ),
        "native_consensus_affinity_minimum": min(
            chart.native_consensus_affinity
        ),
        "projector_affinity_minimum": min(
            chart.projector_affinities
        ),
        "heldout_source_cka": chart.heldout_source_cka,
        "canonical_singular_maximum": float(
            np.max(chart.canonical_singular_values)
        ),
        "canonical_singular_minimum_retained": float(
            chart.canonical_singular_values[
                max(chart.shared_rank - 1, 0)
            ]
        ),
        "canonical_null_threshold": chart.canonical_null_threshold,
        "condition_number_maximum": max(chart.condition_numbers),
        "negative_spectral_mass_maximum": max(
            chart.negative_spectral_mass
        ),
        "asymmetric_mass_maximum": max(chart.asymmetric_mass),
        "coverage": chart.coverage,
        "null_false_positive_rate": chart.null_false_positive_rate,
        "null_trials": chart.null_trials,
        "refused": chart.refused,
        "refusal_reasons": "|".join(chart.refusal_reasons),
    }


def _invariance_rows(
    *,
    repetition: int,
    observed: M4ConditionObserved,
    config: dict[str, Any],
    seed: int,
) -> list[dict[str, Any]]:
    parameters = _parameters(config, seed=seed)
    native = fit_response_safe_rcca_chart(observed, **parameters)
    native_basis = build_response_safe_rcca_basis(
        native,
        observed,
    )["evaluation"][:, 1:]
    mutated = _mutate_responses(observed, seed=seed + 101)
    response_chart = fit_response_safe_rcca_chart(
        mutated,
        **parameters,
    )
    rotated = _rotate(observed, seed=seed + 103)
    rotated_chart = fit_response_safe_rcca_chart(
        rotated,
        **parameters,
    )
    rotated_basis = build_response_safe_rcca_basis(
        rotated_chart,
        rotated,
    )["evaluation"][:, 1:]
    shifted = _shift(observed, value=23.75)
    shifted_chart = fit_response_safe_rcca_chart(
        shifted,
        **parameters,
    )
    shifted_basis = build_response_safe_rcca_basis(
        shifted_chart,
        shifted,
    )["evaluation"][:, 1:]
    return [
        {
            "repetition": repetition,
            "world": "invariance",
            "control": "response_hash",
            "value": float(
                native.provenance_hash
                != response_chart.provenance_hash
            ),
            "passed": bool(
                native.provenance_hash
                == response_chart.provenance_hash
            ),
            "details": "",
        },
        {
            "repetition": repetition,
            "world": "invariance",
            "control": "orthogonal_gauge",
            "value": _distance_error(native_basis, rotated_basis),
            "passed": True,
            "details": "",
        },
        {
            "repetition": repetition,
            "world": "invariance",
            "control": "common_shift",
            "value": _distance_error(native_basis, shifted_basis),
            "passed": True,
            "details": "",
        },
    ]


def _alias_row(
    *,
    repetition: int,
    observed: M4ConditionObserved,
    config: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    panel = observed.mechanism_evaluation
    pre = panel.pre_context.copy()
    pre[:, :, 1] = pre[:, :, 0]
    aliased = replace(
        observed,
        mechanism_evaluation=replace(panel, pre_context=pre),
    )
    chart = fit_response_safe_rcca_chart(
        aliased,
        **_parameters(config, seed=seed),
    )
    basis = build_response_safe_rcca_basis(chart, aliased)["evaluation"]
    distance = float(np.linalg.norm(basis[0] - basis[1]))
    return {
        "repetition": repetition,
        "observable_alias_distance": distance,
        "false_latent_recovery": bool(distance > 1e-12),
        "refused": chart.refused,
        "refusal_reasons": "|".join(chart.refusal_reasons),
    }


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


def _cluster_lcb(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> float:
    """Bootstrap the lower bound while resampling whole repetitions."""
    vector = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(
        vector,
        size=(repetitions, len(vector)),
        replace=True,
    )
    return float(np.quantile(np.mean(draws, axis=1), 0.025))


def _pattern_frequency(metrics: pd.DataFrame) -> float:
    frequencies = []
    for _, frame in metrics.groupby("world", sort=True):
        patterns = [
            (
                int(row.support_rank_source_1),
                int(row.support_rank_source_2),
                int(row.shared_rank),
                str(row.spectral_block_pattern),
            )
            for row in frame.itertuples()
        ]
        frequencies.append(max(Counter(patterns).values()) / len(patterns))
    return float(min(frequencies)) if frequencies else 0.0


def _decision(
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
    aliases: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["targets"]
    affinity_by_repetition = (
        metrics.groupby("repetition", sort=True)[
            "projector_affinity_minimum"
        ]
        .mean()
        .to_numpy(dtype=float)
    )
    cka_by_repetition = (
        metrics.groupby("repetition", sort=True)["heldout_source_cka"]
        .mean()
        .to_numpy(dtype=float)
    )
    null_false = int(np.round(np.sum(
        metrics["null_false_positive_rate"]
        * metrics["null_trials"]
    )))
    null_trials = int(metrics["null_trials"].sum())
    shuffle = controls[controls["control"] == "source_shuffle"]
    refusal = controls[controls["control"] == "refusal"]
    forbidden = refusal[
        refusal["world"].isin(
            ["author_leakage", "response_leakage_circular"]
        )
    ]
    support_shift = refusal[
        refusal["world"] == "evaluation_support_shift"
    ]
    diagnostics = {
        "projector_affinity_mean": float(
            metrics["projector_affinity_minimum"].mean()
        ),
        "projector_affinity_lcb": _cluster_lcb(
            affinity_by_repetition,
            seed=int(config["bootstrap_seed"]),
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "heldout_source_cka_mean": float(
            metrics["heldout_source_cka"].mean()
        ),
        "heldout_source_cka_lcb": _cluster_lcb(
            cka_by_repetition,
            seed=int(config["bootstrap_seed"]) + 1,
            repetitions=int(config["bootstrap_repetitions"]),
        ),
        "rank_resolved_rate": float(
            (
                metrics["shared_rank_lower"]
                == metrics["shared_rank_upper"]
            ).mean()
        ),
        "rank_pattern_frequency": _pattern_frequency(metrics),
        "support_stability_minimum": float(
            metrics["support_stability_minimum"].min()
        ),
        "support_stability_lcb_minimum": float(
            metrics["support_stability_lcb_minimum"].min()
        ),
        "consensus_concentration_minimum": float(
            metrics["support_selection_minimum"].min()
        ),
        "consensus_minimum_eigenvalue": float(
            metrics["consensus_minimum_eigenvalue"].min()
        ),
        "consensus_eigengap_lcb_minimum": float(
            metrics["consensus_eigengap_lcb_minimum"].min()
        ),
        "rank_boundary_lcb_minimum": float(
            metrics["rank_boundary_lcb_minimum"].min()
        ),
        "next_boundary_ucb_maximum": float(
            metrics["next_boundary_ucb_maximum"].max()
        ),
        "native_consensus_affinity_minimum": float(
            metrics["native_consensus_affinity_minimum"].min()
        ),
        "condition_number_maximum": float(
            metrics["condition_number_maximum"].max()
        ),
        "canonical_singular_maximum": float(
            metrics["canonical_singular_maximum"].max()
        ),
        "negative_spectral_mass_maximum": float(
            metrics["negative_spectral_mass_maximum"].max()
        ),
        "asymmetric_mass_maximum": float(
            metrics["asymmetric_mass_maximum"].max()
        ),
        "coverage_minimum": float(metrics["coverage"].min()),
        "native_refusal_rate": float(metrics["refused"].mean()),
        "null_false_positives": null_false,
        "null_trials": null_trials,
        "null_fpr_upper": _wilson_upper(null_false, null_trials),
        "source_shuffle_zero_rank_rate": float(
            (shuffle["value"] == 0.0).mean()
        ),
        "response_hash_failures": int(
            controls.loc[
                controls["control"] == "response_hash",
                "value",
            ].sum()
        ),
        "gauge_max_error": float(
            controls.loc[
                controls["control"] == "orthogonal_gauge",
                "value",
            ].max()
        ),
        "common_shift_max_error": float(
            controls.loc[
                controls["control"] == "common_shift",
                "value",
            ].max()
        ),
        "alias_false_recovery_rate": float(
            aliases["false_latent_recovery"].mean()
        ),
        "forbidden_refusal_rate": float(forbidden["passed"].mean()),
        "support_shift_refusal_rate": float(
            support_shift["passed"].mean()
        ),
        "topology_refusal_rate": float(
            refusal.loc[
                refusal["world"] == "topology_mismatch",
                "passed",
            ].mean()
        ),
    }
    checks = {
        "projector_stability": (
            diagnostics["projector_affinity_mean"]
            >= targets["minimum_projector_affinity"]
            and diagnostics["projector_affinity_lcb"]
            >= targets["minimum_projector_affinity_lcb"]
        ),
        "heldout_gram_stability": (
            diagnostics["heldout_source_cka_mean"]
            >= targets["minimum_heldout_cka"]
            and diagnostics["heldout_source_cka_lcb"]
            >= targets["minimum_heldout_cka_lcb"]
        ),
        "rank_identification": (
            diagnostics["rank_resolved_rate"]
            >= targets["minimum_rank_resolved_rate"]
            and diagnostics["rank_pattern_frequency"]
            >= targets["minimum_rank_pattern_frequency"]
        ),
        "support_consensus": (
            diagnostics["support_stability_minimum"]
            >= targets["minimum_support_stability"]
            and diagnostics["support_stability_lcb_minimum"]
            >= targets["minimum_support_stability_lcb"]
            and diagnostics["consensus_concentration_minimum"]
            >= targets["minimum_consensus_concentration"]
            and diagnostics["consensus_minimum_eigenvalue"]
            >= targets["minimum_consensus_eigenvalue"]
            and diagnostics["consensus_eigengap_lcb_minimum"]
            > targets["minimum_consensus_eigengap_lcb"]
            and diagnostics["rank_boundary_lcb_minimum"] > 0.0
            and diagnostics["next_boundary_ucb_maximum"] < 0.0
            and diagnostics["native_consensus_affinity_minimum"]
            >= targets["minimum_native_consensus_affinity"]
            and diagnostics["native_refusal_rate"]
            <= targets["maximum_native_refusal_rate"]
        ),
        "numerical_contract": (
            diagnostics["condition_number_maximum"]
            <= targets["maximum_condition_number"]
            and diagnostics["canonical_singular_maximum"]
            <= targets["maximum_canonical_singular"]
        ),
        "replicate_model": (
            diagnostics["negative_spectral_mass_maximum"]
            <= targets["maximum_negative_mass"]
            and diagnostics["asymmetric_mass_maximum"]
            <= targets["maximum_asymmetric_mass"]
        ),
        "coverage": (
            diagnostics["coverage_minimum"]
            >= targets.get(
                "minimum_coverage",
                config["rcca"]["minimum_coverage"],
            )
        ),
        "null_specificity": (
            diagnostics["null_fpr_upper"]
            <= targets["maximum_null_fpr_upper"]
        ),
        "source_shuffle": (
            diagnostics["source_shuffle_zero_rank_rate"]
            >= targets["minimum_source_shuffle_zero_rank_rate"]
        ),
        "response_safety": (
            diagnostics["response_hash_failures"]
            <= targets["maximum_response_hash_failures"]
        ),
        "gauge_invariance": (
            diagnostics["gauge_max_error"]
            <= targets["maximum_gauge_error"]
        ),
        "common_shift_invariance": (
            diagnostics["common_shift_max_error"]
            <= targets["maximum_common_shift_error"]
        ),
        "alias_safety": (
            diagnostics["alias_false_recovery_rate"]
            <= targets["maximum_alias_false_recovery_rate"]
        ),
        "forbidden_refusal": (
            diagnostics["forbidden_refusal_rate"]
            >= targets["minimum_forbidden_refusal_rate"]
        ),
        "support_shift_refusal": (
            diagnostics["support_shift_refusal_rate"]
            >= targets["minimum_support_shift_refusal_rate"]
        ),
    }
    if not checks["alias_safety"]:
        decision = "M4_C35_R1_STOP_ALIAS_UNSAFE"
    elif all(checks.values()):
        if config["phase"] == "smoke":
            decision = "M4_C35_R1_SMOKE_COMPLETE"
        elif config["phase"] == "confirmation":
            decision = "M4_C35_R1_CONFIRMATION_GO"
        else:
            decision = "M4_C35_R1_READY_TO_FREEZE"
    else:
        decision = (
            "M4_C35_R1_CONFIRMATION_NO_GO"
            if config["phase"] == "confirmation"
            else "M4_C35_R1_STOP_PURE_CHART_GATE"
        )
    boundary = (
        "Pure finite-synthetic pre-response chart evidence only. No response, "
        "mechanism endpoint, truth, personality label, or downstream "
        "headroom selected this chart. "
    )
    if config["phase"] == "confirmation":
        boundary += (
            "CONFIRMATION_GO licenses the frozen chart only as a candidate "
            "observable replacement in a separate downstream experiment; "
            "it does not establish mechanism recovery or personality meaning."
        )
    else:
        boundary += (
            "READY_TO_FREEZE means only that a separate confirmation "
            "protocol may be sealed."
        )
    return {
        "estimand_id": config["estimand_id"],
        "phase": config["phase"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": boundary,
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
) -> str:
    metrics_table = (
        metrics.groupby("world", sort=True)[
            [
                "support_rank_source_1",
                "support_rank_source_2",
                "shared_rank",
                "projector_affinity_minimum",
                "heldout_source_cka",
                "condition_number_maximum",
                "coverage",
            ]
        ]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    control_table = (
        controls.groupby(["control", "world"], sort=True)
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
    return f"""# SUICA M4-C.3.5-R1 Response-Safe RCCA Chart

## Decision

`{decision["decision"]}`

This gate sees only replicated pre-response condition tensors. It estimates
within-source repeatable supports from four fixed author blocks, freezes
regularized whiteners, identifies cross-source spectral blocks, and evaluates
projector/Gram objects rather than named canonical axes.

## World diagnostics

{metrics_table}

## Controls

{control_table}

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
        default=(
            ROOT
            / "configs"
            / "m4_response_safe_rcca_chart.development.json"
        ),
    )
    parser.add_argument("--repetition-limit", type=int)
    parser.add_argument("--repetition-start", type=int, default=0)
    parser.add_argument("--world-limit", type=int)
    parser.add_argument("--output-directory")
    parser.add_argument("--report-path")
    args = parser.parse_args()
    config = _load(args.config)
    if args.repetition_limit is not None:
        config["repetitions"] = int(args.repetition_limit)
    if args.world_limit is not None:
        config["worlds"] = config["worlds"][: args.world_limit]
    if args.output_directory is not None:
        config["output_directory"] = args.output_directory
    if args.report_path is not None:
        config["report_path"] = args.report_path
    spec = M4ChartEcologySpec(**config["spec"])
    metric_rows = []
    control_rows = []
    alias_rows = []
    start = int(args.repetition_start)
    stop = start + int(config["repetitions"])
    for repetition in range(start, stop):
        first_condition = None
        for world_index, world in enumerate(config["worlds"]):
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            observed, _ = generate_m4_chart_ecology_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            chart = fit_response_safe_rcca_chart(
                observed.condition,
                **_parameters(config, seed=seed),
            )
            metric_rows.append(
                _metric_row(
                    repetition=repetition,
                    world=world,
                    chart=chart,
                )
            )
            shuffled = fit_response_safe_rcca_chart(
                observed.condition,
                shuffle_source_two=True,
                **_parameters(config, seed=seed + 500_009),
            )
            control_rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "control": "source_shuffle",
                    "value": float(shuffled.shared_rank_lower),
                    "passed": bool(shuffled.shared_rank_lower == 0),
                    "details": "|".join(shuffled.refusal_reasons),
                }
            )
            if first_condition is None:
                first_condition = observed.condition
        if first_condition is None:
            raise ValueError("at least one chart world is required")
        control_rows.extend(
            _invariance_rows(
                repetition=repetition,
                observed=first_condition,
                config=config,
                seed=int(config["seed"]) + repetition * 1_000_003,
            )
        )
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
            chart = fit_response_safe_rcca_chart(
                observed.condition,
                **_parameters(config, seed=seed),
            )
            control_rows.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "control": "refusal",
                    "value": float(chart.refused),
                    "passed": bool(chart.refused),
                    "details": "|".join(chart.refusal_reasons),
                }
            )
        alias_seed = int(
            config["seed"] + repetition * 1_000_003 + 90_000_011
        )
        alias_observed, _ = generate_m4_chart_ecology_world(
            world="condition_alias_ecology",
            spec=spec,
            seed=alias_seed,
        )
        alias_rows.append(
            _alias_row(
                repetition=repetition,
                observed=alias_observed.condition,
                config=config,
                seed=alias_seed,
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
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
