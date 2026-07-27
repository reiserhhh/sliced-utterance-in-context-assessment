#!/usr/bin/env python3
"""Run the SUICA M3 V1 matched-family engineering baseline."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_meso_estimator import fit_m3_meso  # noqa: E402
from suica_core.m3_micro_generator import (  # noqa: E402
    M3WorldSpec,
    generate_m3_world,
    same_occupancy_different_transition,
    stable_state_alias_counterexample,
)
from suica_core.m3_truth_audit import (  # noqa: E402
    audit_m3_invariance,
    audit_m3_truth,
    packet_has_truth_leakage,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _bootstrap_interval(
    values: np.ndarray,
    *,
    seed: int,
    draws: int = 4000,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return {
            "mean": float("nan"),
            "lower95": float("nan"),
            "upper95": float("nan"),
            "n": 0,
        }
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(vector), size=(draws, len(vector)))
    means = vector[indices].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
        "n": int(len(vector)),
    }


def _run_one(
    *,
    world: str,
    repetition: int,
    seed: int,
    spec_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, float] | None]:
    observed, truth, manifest = generate_m3_world(
        spec=M3WorldSpec(**spec_payload),
        seed=seed,
    )
    estimate = fit_m3_meso(observed, manifest)
    metrics = audit_m3_truth(estimate, truth)
    metrics.update({
        "world": world,
        "repetition": int(repetition),
        "seed": int(seed),
        "observed_truth_leakage": bool(
            packet_has_truth_leakage(observed)
        ),
        "support_rank": int(estimate.support_rank),
        "common_condition_count": int(len(estimate.common_conditions)),
    })
    invariance = None
    if world == "positive_nonlinear_t5":
        invariance = audit_m3_invariance(
            observed,
            manifest,
            seed=seed + 1_000_003,
        )
        invariance.update({
            "world": world,
            "repetition": int(repetition),
            "seed": int(seed),
        })
    return metrics, invariance


def _counterexamples(seed: int, repetition: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    stationary = rng.dirichlet(np.ones(6))
    first, second = same_occupancy_different_transition(
        stationary,
        first_inertia=0.10,
        second_inertia=0.80,
    )
    alias = stable_state_alias_counterexample(
        seed=seed + 17,
        authors=48,
        dimensions=6,
    )
    return {
        "repetition": int(repetition),
        "seed": int(seed),
        "occupancy_error_first": float(np.max(np.abs(
            stationary @ first - stationary
        ))),
        "occupancy_error_second": float(np.max(np.abs(
            stationary @ second - stationary
        ))),
        "transition_micro_difference": float(np.linalg.norm(first - second)),
        "alias_observable_error": float(np.max(np.abs(
            alias["observed_world_a"] - alias["observed_world_b"]
        ))),
        "alias_position_truth_difference": float(np.sqrt(np.mean(
            (
                alias["position_world_a"]
                - alias["position_world_b"]
            ) ** 2
        ))),
        "alias_state_truth_difference": float(np.sqrt(np.mean(
            (
                alias["state_world_a"]
                - alias["state_world_b"]
            ) ** 2
        ))),
    }


def _summarize(
    metrics: pd.DataFrame,
    *,
    seed: int,
) -> pd.DataFrame:
    excluded = {
        "world",
        "repetition",
        "seed",
        "response_status",
        "state_status",
        "observed_truth_leakage",
    }
    rows: list[dict[str, Any]] = []
    for world, group in metrics.groupby("world", sort=True):
        for column in metrics.columns:
            if column in excluded or not pd.api.types.is_numeric_dtype(
                metrics[column]
            ):
                continue
            interval = _bootstrap_interval(
                group[column].to_numpy(dtype=float),
                seed=seed + len(rows) * 7919,
            )
            rows.append({
                "world": world,
                "metric": column,
                **interval,
            })
    return pd.DataFrame(rows)


def _summary_value(
    summary: pd.DataFrame,
    *,
    world: str,
    metric: str,
    statistic: str,
) -> float:
    match = summary[
        (summary["world"] == world)
        & (summary["metric"] == metric)
    ]
    if len(match) != 1:
        return float("nan")
    return float(match.iloc[0][statistic])


def _minimum(
    summary: pd.DataFrame,
    worlds: list[str],
    metric: str,
    statistic: str,
) -> float:
    values = [
        _summary_value(
            summary,
            world=world,
            metric=metric,
            statistic=statistic,
        )
        for world in worlds
    ]
    if len(values) != len(worlds) or not all(np.isfinite(values)):
        return float("nan")
    return min(values)


def _maximum(
    summary: pd.DataFrame,
    worlds: list[str],
    metric: str,
    statistic: str,
) -> float:
    values = [
        _summary_value(
            summary,
            world=world,
            metric=metric,
            statistic=statistic,
        )
        for world in worlds
    ]
    if len(values) != len(worlds) or not all(np.isfinite(values)):
        return float("nan")
    return max(values)


def _decision(
    config: dict[str, Any],
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
    invariance: pd.DataFrame,
    counterexamples: pd.DataFrame,
) -> dict[str, Any]:
    gates = config["gates"]
    positives = [
        name
        for name in config["worlds"]
        if name.startswith("positive_")
    ]
    nonlinear = [
        name
        for name in positives
        if bool(config["worlds"][name].get("nonlinear", True))
    ]

    refusal_expectations = {
        "negative_no_common_support": (
            "response_status",
            "RESPONSE_REFUSED_NO_COMMON_SUPPORT",
        ),
        "negative_single_occasion": (
            "state_status",
            "STATE_REFUSED_SINGLE_OCCASION",
        ),
        "negative_rank_deficient": (
            "response_status",
            "RESPONSE_REFUSED_RANK_DEFICIENT",
        ),
    }
    refusal_rates: dict[str, float] = {}
    for world, (column, expected) in refusal_expectations.items():
        group = metrics[metrics["world"] == world]
        refusal_rates[world] = float(np.mean(group[column] == expected))

    invariance_error_columns = [
        column
        for column in invariance.columns
        if column.endswith("_max_abs")
    ]
    maximum_invariance_error = float(
        invariance[invariance_error_columns].max().max()
    )
    minimum_invariance_geometry = float(min(
        invariance["rotation_position_geometry"].min(),
        invariance["rotation_operator_geometry"].min(),
    ))
    maximum_equivalent_observable_error = float(max(
        counterexamples["occupancy_error_first"].max(),
        counterexamples["occupancy_error_second"].max(),
        counterexamples["alias_observable_error"].max(),
    ))
    minimum_micro_difference = float(min(
        counterexamples["transition_micro_difference"].min(),
        counterexamples["alias_position_truth_difference"].min(),
        counterexamples["alias_state_truth_difference"].min(),
    ))

    checks = {
        "packet_isolation": not bool(
            metrics["observed_truth_leakage"].any()
        ),
        "positive_response_identified": bool(
            (
                metrics[metrics["world"].isin(positives)]["response_status"]
                == "RESPONSE_OK"
            ).all()
        ),
        "positive_state_identified": bool(
            (
                metrics[metrics["world"].isin(positives)]["state_status"]
                == "STATE_OK"
            ).all()
        ),
        "choice_js": _maximum(
            summary,
            positives,
            "choice_js_median",
            "upper95",
        ) <= float(gates["maximum_choice_js_upper"]),
        "choice_heldout_skill": _minimum(
            summary,
            positives,
            "heldout_choice_log_skill",
            "lower95",
        ) >= float(gates["minimum_choice_skill_lower"]),
        "position_geometry": _minimum(
            summary,
            positives,
            "position_distance_spearman",
            "lower95",
        ) >= float(gates["minimum_position_geometry_lower"]),
        "position_nrmse": _maximum(
            summary,
            positives,
            "position_nrmse",
            "upper95",
        ) <= float(gates["maximum_position_nrmse_upper"]),
        "operator_recovery": _minimum(
            summary,
            positives,
            "operator_correlation",
            "lower95",
        ) >= float(gates["minimum_operator_correlation_lower"]),
        "nonlinear_recovery": _minimum(
            summary,
            nonlinear,
            "nonlinear_correlation",
            "lower95",
        ) >= float(gates["minimum_nonlinear_correlation_lower"]),
        "nonlinear_heldout_increment": _minimum(
            summary,
            nonlinear,
            "heldout_nonlinear_incremental_r2",
            "lower95",
        ) >= float(gates["minimum_nonlinear_increment_lower"]),
        "state_recovery": _minimum(
            summary,
            positives,
            "state_correlation",
            "lower95",
        ) >= float(gates["minimum_state_correlation_lower"]),
        "refusal_worlds": min(refusal_rates.values()) >= float(
            gates["minimum_refusal_rate"]
        ),
        "affine_and_coarse_invariance": (
            maximum_invariance_error
            <= float(gates["maximum_affine_or_coarse_error"])
            and minimum_invariance_geometry
            >= float(gates["minimum_invariance_geometry"])
        ),
        "observational_equivalence": (
            maximum_equivalent_observable_error
            <= float(gates["maximum_equivalent_observable_error"])
            and minimum_micro_difference
            >= float(gates["minimum_equivalent_micro_difference"])
        ),
    }
    passed = bool(all(checks.values()))
    return {
        "status": (
            "M3_MATCHED_FAMILY_RECOVERY_WITH_BASIC_REFUSAL_CHECKS"
            if passed
            else "M3_MATCHED_FAMILY_PARTIAL"
        ),
        "passed": passed,
        "license_level": "MATCHED_FAMILY_ENGINEERING_BASELINE",
        "checks": checks,
        "refusal_rates": refusal_rates,
        "extrema": {
            "maximum_invariance_error": maximum_invariance_error,
            "minimum_invariance_geometry": minimum_invariance_geometry,
            "maximum_equivalent_observable_error": (
                maximum_equivalent_observable_error
            ),
            "minimum_micro_difference": minimum_micro_difference,
        },
        "repetitions": int(config["repetitions"]),
        "claim_boundary": config["claim_boundary"],
    }


def _report(
    config: dict[str, Any],
    decision: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    selected = summary[
        summary["metric"].isin([
            "choice_js_median",
            "heldout_choice_log_skill",
            "position_distance_spearman",
            "position_nrmse",
            "operator_correlation",
            "nonlinear_correlation",
            "heldout_nonlinear_incremental_r2",
            "state_correlation",
        ])
    ].copy()
    table = selected.to_markdown(index=False, floatfmt=".4f")
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA M3 Micro-Meso-Macro Foundation V1

Decision: `{decision["status"]}`

## Scope

This battery tests a declared synthetic microscopic choice/response process,
its mesoscopic projections, transformation invariants, and required refusals.
It does not read real text or psychological labels.

## Checks

{checks}

## Recovery summary

{table}

## Refusal rates

```json
{json.dumps(decision["refusal_rates"], indent=2)}
```

## Invariance and equivalence extrema

```json
{json.dumps(decision["extrema"], indent=2)}
```

## Interpretation

The generator and estimator are separated at the Python-module and packet
interface, and observed packets contain no explicit truth or world label.
However, the public design manifest exposes the condition basis used by this
matched additive generator. Nonlinear recovery uses saturated observed
condition means, and state recovery uses the same additive zero-sum gauge as
the generator. The result is therefore an engineering baseline for known-basis
projection, simple refusals, and algebraic invariants, not a micro-to-meso
theory closure. The equivalence constructions are algebraic demonstrations;
they do not yet pass through the estimator as blinded classification tests.

## Claim boundary

{config["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/m3_micro_meso_foundation_smoke.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/m3_micro_meso_foundation",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=ROOT / "reports/SUICA_M3_MICRO_MESO_FOUNDATION_REPORT.md",
    )
    args = parser.parse_args()
    config = _read(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    root_sequences = np.random.SeedSequence(
        int(config["seed"])
    ).spawn(int(config["repetitions"]))
    metric_rows: list[dict[str, Any]] = []
    invariance_rows: list[dict[str, Any]] = []
    counterexample_rows: list[dict[str, float | int]] = []
    for repetition, root_sequence in enumerate(root_sequences):
        world_sequences = root_sequence.spawn(len(config["worlds"]) + 1)
        for world_index, (world, override) in enumerate(
            config["worlds"].items()
        ):
            seed = int(world_sequences[world_index].generate_state(
                1,
                dtype=np.uint64,
            )[0])
            spec_payload = {
                **config["base_spec"],
                **override,
            }
            metrics, invariance = _run_one(
                world=world,
                repetition=repetition,
                seed=seed,
                spec_payload=spec_payload,
            )
            metric_rows.append(metrics)
            if invariance is not None:
                invariance_rows.append(invariance)
        counter_seed = int(world_sequences[-1].generate_state(
            1,
            dtype=np.uint64,
        )[0])
        counterexample_rows.append(
            _counterexamples(counter_seed, repetition)
        )

    metrics = pd.DataFrame(metric_rows)
    invariance = pd.DataFrame(invariance_rows)
    counterexamples = pd.DataFrame(counterexample_rows)
    summary = _summarize(metrics, seed=int(config["seed"]) + 31)
    decision = _decision(
        config,
        metrics,
        summary,
        invariance,
        counterexamples,
    )

    metrics.to_csv(args.output_dir / "seed_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    invariance.to_csv(
        args.output_dir / "invariance_metrics.csv",
        index=False,
    )
    counterexamples.to_csv(
        args.output_dir / "counterexample_metrics.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "resolved_config.json", config)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        _report(config, decision, summary),
        encoding="utf-8",
    )
    (args.output_dir / "report.md").write_text(
        _report(config, decision, summary),
        encoding="utf-8",
    )

    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/m3_contracts.py",
            ROOT / "suica_core/m3_micro_generator.py",
            ROOT / "suica_core/m3_meso_estimator.py",
            ROOT / "suica_core/m3_truth_audit.py",
            Path(__file__).resolve(),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
