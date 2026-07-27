#!/usr/bin/env python3
"""Run the SUICA M3 basis-blinded two-phase microkernel discovery."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_kernel_audit import (  # noqa: E402
    audit_m3_kernel_invariance,
    audit_m3_kernel_truth,
    audit_same_occupancy_different_transition,
    audit_single_occasion_state_alias,
    packet_has_hidden_kernel_fields,
)
from suica_core.m3_kernel_estimator import fit_m3_kernel  # noqa: E402
from suica_core.m3_kernel_generator import (  # noqa: E402
    M3KernelWorldSpec,
    generate_m3_kernel_world,
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
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _bootstrap(
    values: np.ndarray,
    *,
    seed: int,
    draws: int = 3000,
) -> dict[str, float | int]:
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
    samples = vector[
        rng.integers(0, len(vector), size=(draws, len(vector)))
    ].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(samples, 0.025)),
        "upper95": float(np.quantile(samples, 0.975)),
        "n": int(len(vector)),
    }


def _summarize(metrics: pd.DataFrame, *, seed: int) -> pd.DataFrame:
    excluded = {
        "world",
        "repetition",
        "seed",
        "response_status",
        "state_status",
        "reliability_status",
        "coarse_status",
        "packet_isolated",
    }
    rows: list[dict[str, Any]] = []
    for world, group in metrics.groupby("world", sort=True):
        for column in metrics.columns:
            if (
                column in excluded
                or not pd.api.types.is_numeric_dtype(metrics[column])
            ):
                continue
            rows.append({
                "world": world,
                "metric": column,
                **_bootstrap(
                    group[column].to_numpy(dtype=float),
                    seed=seed + 7919 * len(rows),
                ),
            })
    return pd.DataFrame(rows)


def _summary_value(
    summary: pd.DataFrame,
    world: str,
    metric: str,
    statistic: str = "mean",
) -> float:
    selected = summary[
        (summary["world"] == world)
        & (summary["metric"] == metric)
    ]
    if len(selected) != 1:
        return float("nan")
    return float(selected.iloc[0][statistic])


def _finite_minimum(values: list[float]) -> float:
    if not values or not all(np.isfinite(values)):
        return float("nan")
    return float(min(values))


def _decision(
    config: dict[str, Any],
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
    invariance: pd.DataFrame,
    aliases: pd.DataFrame,
    state_aliases: pd.DataFrame,
) -> dict[str, Any]:
    gates = config["discovery_gates"]
    positives = [
        name
        for name in config["worlds"]
        if name.startswith("P")
    ]
    positive = metrics[metrics["world"].isin(positives)]
    refusal_expectations = {
        "N1_no_common_support": (
            "response_status",
            "RESPONSE_REFUSED_NO_COMMON_SUPPORT",
        ),
        "N2_single_occasion": (
            "state_status",
            "STATE_REFUSED_SINGLE_OCCASION",
        ),
        "N3_fixed_not_randomized": (
            "response_status",
            "RESPONSE_OBSERVATIONAL_ONLY",
        ),
        "N4_rank_deficient": (
            "response_status",
            "RESPONSE_REFUSED_RANK_DEFICIENT",
        ),
        "N5_representation_drift": (
            "response_status",
            "RESPONSE_REFUSED_REPRESENTATION_VERSION",
        ),
        "N6_unknown_missingness": (
            "response_status",
            "RESPONSE_REFUSED_UNKNOWN_MISSINGNESS",
        ),
        "N7_dependent_technical_streams": (
            "reliability_status",
            "RELIABILITY_REFUSED_TECHNICAL_DEPENDENCE",
        ),
        "N8_mixed_coarse_blocks": (
            "coarse_status",
            "COARSE_INVARIANCE_REFUSED_MIXED_CONDITIONS",
        ),
        "N9_reference_mismatch": (
            "response_status",
            "RESPONSE_REFUSED_REFERENCE_VERSION",
        ),
    }
    refusal_rates = {
        world: float(np.mean(
            metrics[metrics["world"] == world][column] == expected
        ))
        for world, (column, expected) in refusal_expectations.items()
    }

    def positive_minimum(
        metric: str,
        statistic: str = "mean",
    ) -> float:
        return _finite_minimum([
            _summary_value(summary, world, metric, statistic)
            for world in positives
        ])

    def positive_seed_fraction(metric: str) -> float:
        return _finite_minimum([
            float(np.mean(
                metrics[metrics["world"] == world][metric] > 0.0
            ))
            for world in positives
        ])

    invariance_error = float(invariance[[
        column
        for column in invariance
        if column.endswith("_max_abs")
    ]].max().max())
    invariance_geometry = float(invariance[[
        column
        for column in invariance
        if column.endswith("_geometry")
    ]].min().min())
    null_auc = _summary_value(
        summary,
        "N10_null_authors",
        "same_author_response_auc",
    )
    checks = {
        "input_contract_isolation": bool(metrics["packet_isolated"].all()),
        "positive_protocol_identification": bool(
            (positive["response_status"] == "RESPONSE_OK").all()
            and (
                positive["state_status"]
                == "STATE_WITHIN_AUTHOR_RELATIVE_OK"
            ).all()
        ),
        "occupancy_recovery": (
            positive_minimum("occupancy_correlation")
            >= float(gates["minimum_occupancy_correlation_mean"])
        ),
        "ordered_transition_information": (
            positive_minimum("transition_order_gain")
            >= float(gates["minimum_transition_order_gain_mean"])
        ),
        "personal_transition_information": (
            positive_minimum("heldout_personal_transition_skill")
            >= float(gates["minimum_personal_transition_skill_mean"])
            and positive_minimum(
                "heldout_personal_transition_skill",
                "lower95",
            )
            > float(
                gates["minimum_personal_transition_skill_lower95"]
            )
        ),
        "shared_transition_information": (
            positive_minimum("heldout_shared_transition_skill")
            >= float(gates["minimum_shared_transition_skill_mean"])
        ),
        "unseen_condition_field_recovery": (
            positive_minimum("heldout_field_r2")
            >= float(gates["minimum_heldout_field_r2_mean"])
        ),
        "public_projection_recovery": (
            positive_minimum("projection_correlation")
            >= float(gates["minimum_projection_correlation_mean"])
        ),
        "nonlinear_remainder_recovery": (
            positive_minimum("nonlinear_heldout_correlation")
            >= float(
                gates["minimum_nonlinear_heldout_correlation_mean"]
            )
        ),
        "nonlinear_predictive_increment": (
            positive_minimum(
                "heldout_nonlinear_increment",
                "lower95",
            )
            > float(gates["minimum_nonlinear_increment_lower95"])
            and positive_seed_fraction("heldout_nonlinear_increment")
            >= float(
                gates["minimum_nonlinear_positive_seed_fraction"]
            )
        ),
        "relative_occasion_state_recovery": (
            positive_minimum("state_relative_correlation")
            >= float(gates["minimum_state_relative_correlation_mean"])
        ),
        "same_author_response_reidentification": (
            positive_minimum("same_author_response_auc")
            >= float(gates["minimum_same_author_auc_mean"])
        ),
        "null_author_calibration": (
            float(gates["null_same_author_auc_lower"])
            <= null_auc
            <= float(gates["null_same_author_auc_upper"])
        ),
        "null_personal_transition_calibration": (
            abs(_summary_value(
                summary,
                "N10_null_authors",
                "heldout_personal_transition_skill",
            ))
            <= float(
                gates["maximum_null_personal_transition_skill_abs"]
            )
        ),
        "design_refusals": (
            min(refusal_rates.values())
            >= float(gates["minimum_refusal_rate"])
        ),
        "response_space_invariance": (
            invariance_error
            <= float(gates["maximum_invariance_error"])
            and invariance_geometry
            >= float(gates["minimum_invariance_geometry"])
        ),
        "occupancy_transition_nonidentification": (
            float(aliases["occupancy_group_accuracy"].mean())
            <= float(gates["maximum_alias_occupancy_accuracy"])
            and float(aliases["transition_group_accuracy"].mean())
            >= float(gates["minimum_alias_transition_accuracy"])
        ),
        "stable_state_nonidentification": (
            float(state_aliases["alias_observable_error"].max())
            <= float(gates["maximum_state_alias_observable_error"])
            and min(
                float(
                    state_aliases["alias_stable_truth_difference"].min()
                ),
                float(
                    state_aliases["alias_state_truth_difference"].min()
                ),
            )
            >= float(gates["minimum_state_alias_truth_difference"])
            and bool(
                (
                    state_aliases["state_status_a"]
                    == "STATE_REFUSED_SINGLE_OCCASION"
                ).all()
                and (
                    state_aliases["state_status_b"]
                    == "STATE_REFUSED_SINGLE_OCCASION"
                ).all()
            )
        ),
    }
    supported = bool(all(checks.values()))
    return {
        "status": (
            "M3_TWO_PHASE_MICROKERNEL_DISCOVERY_SUPPORTED"
            if supported
            else "M3_TWO_PHASE_MICROKERNEL_DISCOVERY_PARTIAL"
        ),
        "supported": supported,
        "license_level": (
            "BASIS_BLINDED_NEAR_FAMILY_SYNTHETIC_DISCOVERY"
        ),
        "checks": checks,
        "refusal_rates": refusal_rates,
        "diagnostics": {
            "minimum_positive_occupancy_correlation": (
                positive_minimum("occupancy_correlation")
            ),
            "minimum_positive_transition_order_gain": (
                positive_minimum("transition_order_gain")
            ),
            "minimum_positive_personal_transition_skill": (
                positive_minimum("heldout_personal_transition_skill")
            ),
            "minimum_positive_shared_transition_skill": (
                positive_minimum("heldout_shared_transition_skill")
            ),
            "minimum_positive_heldout_field_r2": (
                positive_minimum("heldout_field_r2")
            ),
            "minimum_positive_projection_correlation": (
                positive_minimum("projection_correlation")
            ),
            "minimum_positive_nonlinear_correlation": (
                positive_minimum("nonlinear_heldout_correlation")
            ),
            "minimum_nonlinear_increment_lower95": (
                positive_minimum(
                    "heldout_nonlinear_increment",
                    "lower95",
                )
            ),
            "minimum_nonlinear_positive_seed_fraction": (
                positive_seed_fraction("heldout_nonlinear_increment")
            ),
            "minimum_positive_state_correlation": (
                positive_minimum("state_relative_correlation")
            ),
            "minimum_positive_same_author_auc": (
                positive_minimum("same_author_response_auc")
            ),
            "null_same_author_auc": null_auc,
            "null_personal_transition_skill": _summary_value(
                summary,
                "N10_null_authors",
                "heldout_personal_transition_skill",
            ),
            "maximum_invariance_error": invariance_error,
            "minimum_invariance_geometry": invariance_geometry,
            "alias_occupancy_accuracy": float(
                aliases["occupancy_group_accuracy"].mean()
            ),
            "alias_transition_accuracy": float(
                aliases["transition_group_accuracy"].mean()
            ),
            "maximum_state_alias_observable_error": float(
                state_aliases["alias_observable_error"].max()
            ),
            "minimum_state_alias_truth_difference": float(min(
                state_aliases["alias_stable_truth_difference"].min(),
                state_aliases["alias_state_truth_difference"].min(),
            )),
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
            "occupancy_correlation",
            "transition_order_gain",
            "heldout_personal_transition_skill",
            "heldout_shared_transition_skill",
            "transition_prior_strength",
            "heldout_field_r2",
            "projection_correlation",
            "nonlinear_heldout_correlation",
            "heldout_nonlinear_increment",
            "same_author_response_auc",
            "state_relative_correlation",
        ])
    ]
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA M3 Two-Phase Microkernel Discovery

Decision: `{decision["status"]}`

## What changed from V1

The free phase produces an event-level joint state-choice chain. The fixed
phase samples vector responses from the same conditional emission family under
assigned conditions and occasion-level states. Hidden discrete codes and
random-Fourier features are not exposed to the estimator. The estimator uses
ordered counts, training-occasion-selected hierarchical shrinkage, and a
cross-validated RBF surface on public condition coordinates.

This is basis-blinded but not fully out-of-family: random Fourier functions and
Gaussian RBF regression are members of the same kernel family. Shared sequence
information and author-specific transition information are scored separately.
Response metrics use unseen conditions and independent test occasions.

## Discovery checks

{checks}

## World-by-world estimates

{selected.to_markdown(index=False, floatfmt=".4f")}

## Refusal audit

```json
{json.dumps(decision["refusal_rates"], indent=2)}
```

## Diagnostic extrema

```json
{json.dumps(decision["diagnostics"], indent=2)}
```

## Interpretation boundary

This is a discovery run, not a frozen confirmation. A partial result may
support specific components even when the conjunction fails. The recovered
axes are public-coordinate projections, not generator coefficients and not
psychological traits. Correlation with a planted nonlinear remainder is not
enough to claim nonlinear predictive benefit; that requires positive held-out
incremental R2 across worlds and seeds.

{config["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/m3_kernel_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/m3_kernel_discovery",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=ROOT / "reports/SUICA_M3_EVENT_KERNEL_DISCOVERY.md",
    )
    args = parser.parse_args()
    config = _read(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    roots = np.random.SeedSequence(
        int(config["seed"])
    ).spawn(int(config["repetitions"]))
    metric_rows: list[dict[str, Any]] = []
    invariance_rows: list[dict[str, Any]] = []
    alias_rows: list[dict[str, Any]] = []
    state_alias_rows: list[dict[str, Any]] = []
    for repetition, root in enumerate(roots):
        children = root.spawn(len(config["worlds"]) + 1)
        for index, (world, override) in enumerate(
            config["worlds"].items()
        ):
            seed = int(children[index].generate_state(
                1,
                dtype=np.uint64,
            )[0])
            spec = M3KernelWorldSpec(**{
                **config["base_spec"],
                **override,
            })
            observed, truth, design = generate_m3_kernel_world(
                spec=spec,
                seed=seed,
            )
            estimate = fit_m3_kernel(observed, design)
            audit = audit_m3_kernel_truth(
                estimate,
                truth,
                observed,
                design,
            )
            audit.update({
                "world": world,
                "repetition": int(repetition),
                "seed": seed,
                "packet_isolated": bool(
                    not packet_has_hidden_kernel_fields(observed)
                    and not packet_has_hidden_kernel_fields(design)
                ),
            })
            metric_rows.append(audit)
            if world == "P3_nonlinear_t5":
                invariance = audit_m3_kernel_invariance(
                    observed,
                    design,
                    seed=seed + 1_000_003,
                )
                invariance.update({
                    "repetition": int(repetition),
                    "seed": seed,
                })
                invariance_rows.append(invariance)
            if world == "N2_single_occasion":
                state_alias_rows.append({
                    "repetition": int(repetition),
                    "seed": seed,
                    **audit_single_occasion_state_alias(
                        observed,
                        design,
                        seed=seed + 2_000_003,
                    ),
                })
        alias_seed = int(children[-1].generate_state(
            1,
            dtype=np.uint64,
        )[0])
        alias_rows.append({
            "repetition": int(repetition),
            "seed": alias_seed,
            **audit_same_occupancy_different_transition(
                seed=alias_seed,
            ),
        })

    metrics = pd.DataFrame(metric_rows)
    invariance = pd.DataFrame(invariance_rows)
    aliases = pd.DataFrame(alias_rows)
    state_aliases = pd.DataFrame(state_alias_rows)
    summary = _summarize(metrics, seed=int(config["seed"]) + 41)
    decision = _decision(
        config,
        metrics,
        summary,
        invariance,
        aliases,
        state_aliases,
    )

    metrics.to_csv(args.output_dir / "seed_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    invariance.to_csv(
        args.output_dir / "invariance_metrics.csv",
        index=False,
    )
    aliases.to_csv(
        args.output_dir / "transition_alias_metrics.csv",
        index=False,
    )
    state_aliases.to_csv(
        args.output_dir / "state_alias_metrics.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "resolved_config.json", config)
    report = _report(config, decision, summary)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report, encoding="utf-8")
    (args.output_dir / "report.md").write_text(
        report,
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/m3_kernel_contracts.py",
            ROOT / "suica_core/m3_kernel_generator.py",
            ROOT / "suica_core/m3_kernel_estimator.py",
            ROOT / "suica_core/m3_kernel_audit.py",
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
