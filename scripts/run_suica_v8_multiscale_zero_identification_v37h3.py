#!/usr/bin/env python3
"""Run the V3.7H.3 multiscale zero-identification discovery battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_multiscale_zero_identification import (  # noqa: E402
    ALL_COMPONENTS,
    STABLE_COMPONENTS,
    MultiscaleZeroSpec,
    coarse_graining_assay,
    decompose_balanced_panel,
    generate_multiscale_basis,
    measurement_energies,
    minority_near_kernel_assay,
    persistent_alias_assay,
    simulate_multiscale_panel,
    simulate_selection_assay,
    stable_recovery_metrics,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_multiscale_zero_identification_v37h3.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_multiscale_zero_identification"
    / "v37h3_discovery"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            allow_nan=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _spec(config: dict[str, Any]) -> MultiscaleZeroSpec:
    values = config["spec"]
    return MultiscaleZeroSpec(
        societies=int(values["societies"]),
        groups_per_society=int(values["groups_per_society"]),
        authors_per_group=int(values["authors_per_group"]),
        conditions=int(values["conditions"]),
        response_rank=int(values["response_rank"]),
        opportunities=int(values["opportunities"]),
        technical_streams=int(values["technical_streams"]),
        dimensions=int(values["dimensions"]),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )


def _scales(value: float = 0.0) -> dict[str, float]:
    return {component: float(value) for component in ALL_COMPONENTS}


def _zero_path_rows(
    *,
    repetition: int,
    noise_mode: str,
    basis: dict[str, np.ndarray],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    rows: list[dict[str, Any]] = []
    background_value = float(config["background_amplitude"])
    reconstruction_error = 0.0
    for target in ALL_COMPONENTS:
        zero_scales = _scales(background_value)
        zero_scales[target] = 0.0
        zero_panel = simulate_multiscale_panel(
            basis,
            scales=zero_scales,
        )
        zero_decomposition = decompose_balanced_panel(zero_panel)
        reconstruction_error = max(
            reconstruction_error,
            float(zero_decomposition["reconstruction_error"]),
        )
        zero_energy = measurement_energies(
            zero_panel,
            zero_decomposition,
        )
        for amplitude in map(float, config["zero_lambdas"]):
            plus_scales = zero_scales.copy()
            minus_scales = zero_scales.copy()
            plus_scales[target] = amplitude
            minus_scales[target] = -amplitude
            plus_panel = simulate_multiscale_panel(
                basis,
                scales=plus_scales,
            )
            minus_panel = simulate_multiscale_panel(
                basis,
                scales=minus_scales,
            )
            plus_decomposition = decompose_balanced_panel(plus_panel)
            minus_decomposition = decompose_balanced_panel(minus_panel)
            reconstruction_error = max(
                reconstruction_error,
                float(plus_decomposition["reconstruction_error"]),
                float(minus_decomposition["reconstruction_error"]),
            )
            plus_energy = measurement_energies(
                plus_panel,
                plus_decomposition,
            )
            minus_energy = measurement_energies(
                minus_panel,
                minus_decomposition,
            )
            for measured in ALL_COMPONENTS:
                even_excess = (
                    0.5
                    * (
                        float(plus_energy[measured])
                        + float(minus_energy[measured])
                    )
                    - float(zero_energy[measured])
                )
                rows.append({
                    "repetition": int(repetition),
                    "noise_mode": str(noise_mode),
                    "target_component": target,
                    "measured_component": measured,
                    "amplitude": amplitude,
                    "even_excess_energy": float(even_excess),
                    "expected_diagonal_energy": float(amplitude**2),
                    "diagonal": bool(target == measured),
                })
    return rows, reconstruction_error


def _recovery_rows(
    *,
    repetition: int,
    noise_mode: str,
    basis: dict[str, np.ndarray],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    rows: list[dict[str, Any]] = []
    stable_amplitude = float(config["full_stable_amplitude"])
    scales = _scales()
    for component in STABLE_COMPONENTS:
        scales[component] = stable_amplitude
    scales["opportunity"] = float(
        config["full_opportunity_amplitude"]
    )
    scales["technical"] = float(
        config["full_technical_amplitude"]
    )
    maximum_error = 0.0
    for opportunities in map(int, config["recovery_k"]):
        panel = simulate_multiscale_panel(
            basis,
            scales=scales,
            opportunities=opportunities,
        )
        decomposition = decompose_balanced_panel(panel)
        maximum_error = max(
            maximum_error,
            float(decomposition["reconstruction_error"]),
        )
        energy = measurement_energies(panel, decomposition)
        for item in stable_recovery_metrics(
            decomposition,
            basis,
            stable_amplitude=stable_amplitude,
        ):
            rows.append({
                "repetition": int(repetition),
                "noise_mode": str(noise_mode),
                "opportunities": opportunities,
                **item,
                "estimated_energy": float(
                    energy[str(item["component"])]
                ),
                "truth_energy": float(stable_amplitude**2),
                "energy_error": float(
                    energy[str(item["component"])]
                    - stable_amplitude**2
                ),
            })
        for component, truth in (
            (
                "opportunity",
                float(config["full_opportunity_amplitude"]) ** 2,
            ),
            (
                "technical",
                float(config["full_technical_amplitude"]) ** 2,
            ),
        ):
            rows.append({
                "repetition": int(repetition),
                "noise_mode": str(noise_mode),
                "opportunities": opportunities,
                "component": component,
                "recovery_r2_panel_a": float("nan"),
                "recovery_r2_panel_b": float("nan"),
                "recovery_r2_mean": float("nan"),
                "truth_correlation_mean": float("nan"),
                "split_panel_correlation": float("nan"),
                "estimated_energy": float(energy[component]),
                "truth_energy": truth,
                "energy_error": float(energy[component] - truth),
            })
    return rows, maximum_error


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> dict[str, Any]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    streams = root.spawn(len(config["noise_modes"]) + 4)
    seeds = [_uint64(stream) for stream in streams]
    spec = _spec(config)

    zero_rows: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    reconstruction_error = 0.0
    for noise_mode, seed in zip(
        config["noise_modes"],
        seeds[:len(config["noise_modes"])],
        strict=True,
    ):
        basis = generate_multiscale_basis(
            seed=seed,
            spec=spec,
            noise_mode=str(noise_mode),
        )
        zero_part, zero_error = _zero_path_rows(
            repetition=repetition,
            noise_mode=str(noise_mode),
            basis=basis,
            config=config,
        )
        recovery_part, recovery_error = _recovery_rows(
            repetition=repetition,
            noise_mode=str(noise_mode),
            basis=basis,
            config=config,
        )
        zero_rows.extend(zero_part)
        recovery_rows.extend(recovery_part)
        reconstruction_error = max(
            reconstruction_error,
            zero_error,
            recovery_error,
        )

    offset = len(config["noise_modes"])
    coarse_rows = coarse_graining_assay(
        seed=seeds[offset],
        sizes=tuple(map(int, config["coarse_sizes"])),
        units=int(config["coarse_units"]),
        dimensions=int(config["coarse_dimensions"]),
    )
    for row in coarse_rows:
        row["repetition"] = int(repetition)

    selection = simulate_selection_assay(
        seed=seeds[offset + 1],
        authors=int(config["selection_authors"]),
        conditions=int(spec.conditions),
        forced_per_condition=int(
            config["selection_forced_per_condition"]
        ),
        extra_draws=int(config["selection_extra_draws"]),
        selection_strength=float(config["selection_strength"]),
        author_effect=float(config["selection_author_effect"]),
        condition_effect=float(config["selection_condition_effect"]),
        noise_sd=float(config["selection_noise_sd"]),
    )
    selection["repetition"] = int(repetition)

    alias = persistent_alias_assay(
        seed=seeds[offset + 2],
        shape=(
            int(config["selection_authors"]),
            int(spec.conditions),
            int(spec.dimensions),
        ),
    )
    alias["repetition"] = int(repetition)

    near_rows = minority_near_kernel_assay(
        seed=seeds[offset + 3],
        authors=int(config["near_kernel_authors"]),
        dimensions=int(spec.dimensions),
        prevalence=tuple(map(
            float,
            config["near_kernel_prevalence"],
        )),
        observable_fraction=tuple(map(
            float,
            config["near_kernel_observable_fraction"],
        )),
        individual_energy=float(
            config["near_kernel_individual_energy"]
        ),
    )
    for row in near_rows:
        row["repetition"] = int(repetition)
    return {
        "zero": zero_rows,
        "recovery": recovery_rows,
        "coarse": coarse_rows,
        "selection": selection,
        "alias": alias,
        "near": near_rows,
        "seeds": seeds,
        "reconstruction_error": reconstruction_error,
    }


def _zero_summary(
    metrics: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = (
        metrics.groupby(
            [
                "noise_mode",
                "target_component",
                "measured_component",
                "amplitude",
                "diagonal",
            ],
            sort=True,
            observed=True,
        )["even_excess_energy"]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
    )
    rows: list[dict[str, Any]] = []
    for (noise_mode, target), group in summary[
        summary["diagonal"]
    ].groupby(
        ["noise_mode", "target_component"],
        sort=True,
        observed=True,
    ):
        amplitude = group["amplitude"].to_numpy(dtype=float)
        energy = group["mean"].to_numpy(dtype=float)
        valid = energy > 0.0
        slope = (
            float(np.polyfit(
                np.log(amplitude[valid]),
                np.log(energy[valid]),
                1,
            )[0])
            if valid.sum() >= 2
            else float("nan")
        )
        endpoint = summary[
            (summary["noise_mode"] == noise_mode)
            & (summary["target_component"] == target)
            & np.isclose(summary["amplitude"], 1.0)
        ]
        diagonal = endpoint[
            endpoint["measured_component"] == target
        ]
        denominator = max(
            abs(float(diagonal.iloc[0]["mean"])),
            1e-12,
        )
        off = endpoint[
            endpoint["measured_component"] != target
        ]
        maximum_leakage = (
            float(np.max(np.abs(off["mean"].to_numpy(dtype=float)))
                  / denominator)
            if len(off)
            else 0.0
        )
        rows.append({
            "noise_mode": str(noise_mode),
            "target_component": str(target),
            "zero_path_slope": slope,
            "endpoint_diagonal_energy": float(
                diagonal.iloc[0]["mean"]
            ),
            "maximum_off_diagonal_leakage": maximum_leakage,
        })
    return summary, pd.DataFrame(rows)


def _coarse_summary(
    metrics: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = (
        metrics.groupby(["family", "size"], sort=True, observed=True)[
            "energy"
        ]
        .agg(["mean", "std"])
        .reset_index()
    )
    rows = []
    for family, group in summary.groupby(
        "family",
        sort=True,
        observed=True,
    ):
        rows.append({
            "family": str(family),
            "log_log_slope": float(np.polyfit(
                np.log(group["size"].to_numpy(dtype=float)),
                np.log(group["mean"].to_numpy(dtype=float)),
                1,
            )[0]),
            "minimum_mean_energy": float(group["mean"].min()),
            "maximum_mean_energy": float(group["mean"].max()),
        })
    return summary, pd.DataFrame(rows)


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.3 Multiscale Zero Identification

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Extrema

```json
{json.dumps(decision["extrema"], indent=2)}
```

## Interpretation

This run tests a planted multiscale score-space decomposition. A passing
zero-path or aggregation law means that the registered synthetic estimator
separates the registered components. It does not establish that a component
exists in real text, that it is personality, or that a persistent response
has a psychological cause.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    if args.mode == "smoke":
        config["_active_seed"] = int(config["smoke_seed"])
        config["_active_repetitions"] = int(
            config["smoke_repetitions"]
        )
    else:
        config["_active_seed"] = int(config["seed"])
        config["_active_repetitions"] = int(
            config["discovery_repetitions"]
        )

    root = np.random.SeedSequence(int(config["_active_seed"]))
    payloads = [
        (config, repetition, tuple(child.spawn_key))
        for repetition, child in enumerate(
            root.spawn(int(config["_active_repetitions"]))
        )
    ]
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))

    zero = pd.DataFrame([
        row for part in nested for row in part["zero"]
    ])
    recovery = pd.DataFrame([
        row for part in nested for row in part["recovery"]
    ])
    coarse = pd.DataFrame([
        row for part in nested for row in part["coarse"]
    ])
    selection = pd.DataFrame([
        part["selection"] for part in nested
    ])
    alias = pd.DataFrame([part["alias"] for part in nested])
    near = pd.DataFrame([
        row for part in nested for row in part["near"]
    ])
    seeds = [seed for part in nested for seed in part["seeds"]]

    zero_summary, zero_signature = _zero_summary(zero)
    recovery_summary = (
        recovery.groupby(
            ["noise_mode", "opportunities", "component"],
            sort=True,
            observed=True,
        )
        .agg({
            "recovery_r2_mean": "mean",
            "truth_correlation_mean": "mean",
            "split_panel_correlation": "mean",
            "estimated_energy": "mean",
            "truth_energy": "mean",
            "energy_error": ["mean", "std"],
        })
    )
    recovery_summary.columns = [
        "_".join(filter(None, column))
        for column in recovery_summary.columns.to_flat_index()
    ]
    recovery_summary = recovery_summary.reset_index()
    coarse_summary, coarse_slopes = _coarse_summary(coarse)

    k4_stable = recovery_summary[
        (recovery_summary["opportunities"] == 4)
        & recovery_summary["component"].isin(STABLE_COMPONENTS)
    ]
    gates = config["gates"]
    slope_map = {
        str(row["family"]): float(row["log_log_slope"])
        for _, row in coarse_slopes.iterrows()
    }
    selection_reversal_rate = float(
        (selection["naive_author_correlation"] < 0.0).mean()
    )
    selection_recovery_rate = float(
        (selection["standardized_author_correlation"] > 0.0).mean()
    )
    maximum_reconstruction_error = max(
        float(part["reconstruction_error"]) for part in nested
    )
    maximum_near_kernel_relative_error = float(
        near["relative_error"].max()
    )
    checks = {
        "numeric_integrity": bool(
            len(zero)
            and len(recovery)
            and len(coarse)
            and len(selection)
            and len(alias)
            and len(near)
            and np.isfinite(
                zero["even_excess_energy"].to_numpy(dtype=float)
            ).all()
            and np.isfinite(
                coarse["energy"].to_numpy(dtype=float)
            ).all()
        ),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "algebraic_reconstruction": bool(
            maximum_reconstruction_error
            <= float(gates["maximum_reconstruction_error"])
        ),
        "k4_stable_recovery": bool(
            len(k4_stable)
            and k4_stable["recovery_r2_mean_mean"].min()
            >= float(gates["minimum_k4_recovery_r2"])
        ),
        "k4_split_panel_stability": bool(
            len(k4_stable)
            and k4_stable["split_panel_correlation_mean"].min()
            >= float(
                gates["minimum_k4_split_panel_correlation"]
            )
        ),
        "zero_path_quadratic": bool(
            zero_signature["zero_path_slope"].min()
            >= float(gates["minimum_zero_slope"])
            and zero_signature["zero_path_slope"].max()
            <= float(gates["maximum_zero_slope"])
        ),
        "zero_path_separation": bool(
            zero_signature["maximum_off_diagonal_leakage"].max()
            <= float(gates["maximum_off_diagonal_leakage"])
        ),
        "author_independent_decay": bool(
            float(gates["minimum_independent_decay_slope"])
            <= slope_map["author_independent_to_group_mean"]
            <= float(gates["maximum_independent_decay_slope"])
        ),
        "group_common_persistence": bool(
            float(gates["minimum_common_persistence_slope"])
            <= slope_map["group_common_across_authors"]
            <= float(gates["maximum_common_persistence_slope"])
        ),
        "group_independent_decay": bool(
            float(gates["minimum_independent_decay_slope"])
            <= slope_map["group_independent_to_society_mean"]
            <= float(gates["maximum_independent_decay_slope"])
        ),
        "society_common_persistence": bool(
            float(gates["minimum_common_persistence_slope"])
            <= slope_map["society_common_across_groups"]
            <= float(gates["maximum_common_persistence_slope"])
        ),
        "selection_reversal": bool(
            selection_reversal_rate
            >= float(gates["minimum_selection_reversal_rate"])
        ),
        "selection_standardization_recovery": bool(
            selection_recovery_rate
            >= float(gates["minimum_selection_recovery_rate"])
        ),
        "projection_commutator_repair": bool(
            selection["balanced_to_raw_ratio"].mean()
            <= float(
                gates["maximum_balanced_to_raw_commutator_ratio"]
            )
        ),
        "persistent_alias_refusal": bool(
            alias["identity_error"].max()
            <= float(gates["maximum_alias_identity_error"])
            and (alias["classification"] == "CAUSE_UNIDENTIFIED").all()
        ),
        "minority_near_kernel_identity": bool(
            maximum_near_kernel_relative_error
            <= float(gates["maximum_near_kernel_relative_error"])
        ),
    }
    integrity_pass = bool(
        checks["numeric_integrity"]
        and checks["seed_uniqueness"]
        and checks["algebraic_reconstruction"]
    )
    if not integrity_pass:
        status = "V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_STOP_INTEGRITY"
    elif args.mode == "smoke":
        status = "V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_SMOKE_COMPLETE"
    else:
        status = (
            "V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_DISCOVERY_PASS"
            if all(checks.values())
            else "V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_DISCOVERY_REFUTED"
        )
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "checks": checks,
        "extrema": {
            "maximum_reconstruction_error": maximum_reconstruction_error,
            "minimum_k4_stable_recovery_r2": float(
                k4_stable["recovery_r2_mean_mean"].min()
            ),
            "minimum_k4_split_panel_correlation": float(
                k4_stable["split_panel_correlation_mean"].min()
            ),
            "minimum_zero_path_slope": float(
                zero_signature["zero_path_slope"].min()
            ),
            "maximum_zero_path_slope": float(
                zero_signature["zero_path_slope"].max()
            ),
            "maximum_off_diagonal_leakage": float(
                zero_signature[
                    "maximum_off_diagonal_leakage"
                ].max()
            ),
            "selection_reversal_rate": selection_reversal_rate,
            "selection_recovery_rate": selection_recovery_rate,
            "mean_raw_projection_commutator": float(
                selection["raw_commutator"].mean()
            ),
            "mean_balanced_projection_commutator": float(
                selection["balanced_commutator"].mean()
            ),
            "maximum_alias_identity_error": float(
                alias["identity_error"].max()
            ),
            "maximum_near_kernel_relative_error": (
                maximum_near_kernel_relative_error
            ),
        },
        "coarse_graining_slopes": slope_map,
        "row_counts": {
            "zero_path": int(len(zero)),
            "recovery": int(len(recovery)),
            "coarse": int(len(coarse)),
            "selection": int(len(selection)),
            "alias": int(len(alias)),
            "near_kernel": int(len(near)),
        },
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    zero.to_csv(args.output_dir / "zero_path_metrics.csv", index=False)
    zero_summary.to_csv(
        args.output_dir / "zero_path_summary.csv",
        index=False,
    )
    zero_signature.to_csv(
        args.output_dir / "zero_signature.csv",
        index=False,
    )
    recovery.to_csv(
        args.output_dir / "recovery_metrics.csv",
        index=False,
    )
    recovery_summary.to_csv(
        args.output_dir / "recovery_summary.csv",
        index=False,
    )
    coarse.to_csv(
        args.output_dir / "coarse_graining_metrics.csv",
        index=False,
    )
    coarse_summary.to_csv(
        args.output_dir / "coarse_graining_summary.csv",
        index=False,
    )
    coarse_slopes.to_csv(
        args.output_dir / "coarse_graining_slopes.csv",
        index=False,
    )
    selection.to_csv(
        args.output_dir / "selection_commutator_metrics.csv",
        index=False,
    )
    alias.to_csv(
        args.output_dir / "persistent_alias_metrics.csv",
        index=False,
    )
    near.to_csv(
        args.output_dir / "minority_near_kernel_metrics.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (args.output_dir / "report.md").write_text(
        _report(decision),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT
            / "suica_core/v8_multiscale_zero_identification.py",
            Path(__file__),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": status,
        "repetitions": int(config["_active_repetitions"]),
        "output_dir": str(args.output_dir),
        "checks": checks,
    }, indent=2))
    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

