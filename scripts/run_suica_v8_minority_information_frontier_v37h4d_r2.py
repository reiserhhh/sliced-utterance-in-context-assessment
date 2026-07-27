#!/usr/bin/env python3
"""Run the V3.7H.4D R2 minority information frontier."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _clopper,
    _read,
    _spec,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_minority_information_frontier import (  # noqa: E402
    plant_minority_interaction,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    additive_residual,
    simulate_reference_world,
    wild_residual_diagnostics,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_minority_information_frontier_v37h4d_r2.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_minority_information_frontier"
    / "v37h4d_r2_discovery"
)


def _cell_definitions(
    config: dict[str, Any],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    for noise_mode in config["noise_modes"]:
        w0_repetitions = (
            int(config["smoke_repetitions"])
            if mode == "smoke"
            else (
                int(config["w0_discovery_repetitions"])
                if mode == "discovery"
                else int(config["w0_confirmation_repetitions"])
            )
        )
        definitions.append({
            "cell_kind": "w0",
            "scaling_arm": "w0",
            "support_scheme": "none",
            "interaction_shape": "none",
            "noise_mode": str(noise_mode),
            "active_test_authors": 0,
            "repetitions": w0_repetitions,
        })
        repetitions = (
            int(config["smoke_repetitions"])
            if mode == "smoke"
            else (
                int(config["discovery_repetitions"])
                if mode == "discovery"
                else int(config["confirmation_repetitions"])
            )
        )
        support_schemes = (
            list(map(str, config["support_schemes"]))
            if mode != "confirmation"
            else ["fixed", "random"]
        )
        arms = (
            list(map(str, config["scaling_arms"]))
            if mode != "confirmation"
            else ["active_snr"]
        )
        for support_scheme in support_schemes:
            for arm in arms:
                for active_authors in config["active_test_author_grid"]:
                    definitions.append({
                        "cell_kind": mode,
                        "scaling_arm": arm,
                        "support_scheme": support_scheme,
                        "interaction_shape": str(
                            config["main_interaction_shape"]
                        ),
                        "noise_mode": str(noise_mode),
                        "active_test_authors": int(active_authors),
                        "repetitions": repetitions,
                    })
        if mode != "confirmation":
            intrinsic_repetitions = (
                int(config["smoke_repetitions"])
                if mode == "smoke"
                else int(config["intrinsic_discovery_repetitions"])
            )
            for active_authors in config[
                "intrinsic_active_test_author_grid"
            ]:
                definitions.append({
                    "cell_kind": "intrinsic_counterexample",
                    "scaling_arm": "active_snr",
                    "support_scheme": "fixed",
                    "interaction_shape": str(
                        config["intrinsic_interaction_shape"]
                    ),
                    "noise_mode": str(noise_mode),
                    "active_test_authors": int(active_authors),
                    "repetitions": intrinsic_repetitions,
                })
    return definitions


def _empty_plant_audit() -> dict[str, Any]:
    return {
        "support_scheme": "none",
        "interaction_shape": "none",
        "nominal_active_test_authors": 0,
        "realized_active_train_authors": 0,
        "realized_active_calibration_authors": 0,
        "realized_active_test_authors": 0,
        "active_conditions": 0,
        "realized_global_effect_share": 0.0,
        "realized_active_test_rms": 0.0,
        "registered_active_noise_rms": float("nan"),
        "realized_active_cell_snr": float("nan"),
        "registered_active_cell_snr": float("nan"),
        "interaction_effective_rank": 0.0,
        "intended_support_fraction": 0.0,
        "projection_grand_mean_compatibility_error": 0.0,
        "information_budget_active": 0.0,
        "information_budget_residual": 0.0,
        "information_budget_residual_per_active_author": 0.0,
        "centering_retention_ratio": 0.0,
        "centering_leakage_ratio": 0.0,
        "observed_active_cells_both_panels": 0.0,
        "active_cells_total": 0.0,
        "selected_test_authors": [],
        "selected_conditions": [],
    }


def _evaluate(
    *,
    definition: dict[str, Any],
    repetition: int,
    world_seed: int,
    plant_seed: int,
    diagnostic_seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one frozen-detector Monte Carlo cell."""
    spec = _spec(config)
    world = simulate_reference_world(
        seed=world_seed,
        world="additive",
        effect_share=0.0,
        reference_jsd=float(config["main_reference_jsd"]),
        support_coverage=1.0,
        near_kernel_fraction=0.02,
        noise_mode=str(definition["noise_mode"]),
        opportunity_prefixes=tuple(
            map(int, config["opportunity_prefixes"])
        ),
        author_tilt=float(config["author_tilt"]),
        author_amplitude=float(config["author_amplitude"]),
        condition_amplitude=float(config["condition_amplitude"]),
        society_amplitude=float(config["society_amplitude"]),
        group_amplitude=float(config["group_amplitude"]),
        panel_noise_amplitude=float(
            config["panel_noise_amplitude"]
        ),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
        minority_author_fraction=0.1,
        minority_condition_fraction=0.25,
        spec=spec,
        acquisition_reference_shift=True,
    )
    plant_audit = _empty_plant_audit()
    if str(definition["scaling_arm"]) != "w0":
        world, plant_audit = plant_minority_interaction(
            world,
            spec=spec,
            seed=plant_seed,
            active_test_authors=int(
                definition["active_test_authors"]
            ),
            active_conditions=int(config["active_conditions"]),
            support_scheme=str(definition["support_scheme"]),
            interaction_shape=str(definition["interaction_shape"]),
            scaling_arm=str(definition["scaling_arm"]),
            global_effect_share=float(config["global_effect_share"]),
            active_cell_snr=float(config["active_cell_snr"]),
            primary_opportunities=int(
                config["primary_opportunities"]
            ),
            panel_noise_amplitude=float(
                config["panel_noise_amplitude"]
            ),
            technical_noise_amplitude=float(
                config["technical_noise_amplitude"]
            ),
            heteroskedastic_strength=float(
                config["heteroskedastic_strength"]
            ),
        )

    primary_k = int(config["primary_opportunities"])
    counts = world["counts_by_k"][primary_k]
    means = world["means_by_k"][primary_k]
    _, _, test = spec.author_split
    left, left_mask = additive_residual(means[2], counts[2], test)
    right, right_mask = additive_residual(means[3], counts[3], test)
    diagnostics = wild_residual_diagnostics(
        left,
        right,
        left_mask,
        right_mask,
        rank=3,
        seed=diagnostic_seed,
        permutations=int(config["_active_permutations"]),
        alpha=float(config["holm_alpha"]),
    )
    alpha = float(config["holm_alpha"])
    return {
        "repetition": int(repetition),
        "cell_kind": str(definition["cell_kind"]),
        "scaling_arm": str(definition["scaling_arm"]),
        "support_scheme": str(definition["support_scheme"]),
        "interaction_shape": str(definition["interaction_shape"]),
        "noise_mode": str(definition["noise_mode"]),
        "active_test_authors": int(
            definition["active_test_authors"]
        ),
        "world_seed": int(world_seed),
        "plant_seed": int(plant_seed),
        "diagnostic_seed": int(diagnostic_seed),
        **{
            key: value
            for key, value in plant_audit.items()
            if key not in {
                "selected_test_authors",
                "selected_conditions",
            }
        },
        "selected_test_authors": json.dumps(
            plant_audit["selected_test_authors"]
        ),
        "selected_conditions": json.dumps(
            plant_audit["selected_conditions"]
        ),
        **diagnostics,
        "crc_detected": bool(
            diagnostics["crc_p_holm"] < alpha
        ),
        "cross_low_rank_detected": bool(
            diagnostics["cross_low_rank_p_holm"] < alpha
        ),
        "hc_detected": bool(
            diagnostics["hc_p_holm"] < alpha
        ),
        "crc_or_hc_detected": bool(
            diagnostics["crc_p_holm"] < alpha
            or diagnostics["hc_p_holm"] < alpha
        ),
    }


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        int,
        int,
    ],
) -> dict[str, Any]:
    config, definition, repetition, world_seed, plant_seed, diagnostic_seed = (
        payload
    )
    return _evaluate(
        definition=definition,
        repetition=repetition,
        world_seed=world_seed,
        plant_seed=plant_seed,
        diagnostic_seed=diagnostic_seed,
        config=config,
    )


def _logistic_information_slope(
    information: np.ndarray,
    detected: np.ndarray,
) -> dict[str, float]:
    """Fit a two-parameter logistic slope with a Wald interval."""
    x = np.log1p(np.asarray(information, dtype=float))
    y = np.asarray(detected, dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    if len(x) < 10 or np.unique(y).size < 2 or float(x.std()) <= 1e-12:
        return {
            "information_logistic_slope": float("nan"),
            "information_logistic_slope_lower_95": float("nan"),
            "information_logistic_slope_upper_95": float("nan"),
        }
    x = (x - x.mean()) / x.std()
    design = np.column_stack([np.ones(len(x)), x])
    coefficients = np.zeros(2, dtype=float)
    for _ in range(100):
        probability = np.clip(
            expit(design @ coefficients),
            1e-6,
            1.0 - 1e-6,
        )
        weights = probability * (1.0 - probability)
        information_matrix = (
            design.T @ (weights[:, None] * design)
            + 1e-8 * np.eye(2)
        )
        step = np.linalg.solve(
            information_matrix,
            design.T @ (y - probability),
        )
        coefficients += step
        if float(np.max(np.abs(step))) < 1e-9:
            break
    covariance = np.linalg.inv(information_matrix)
    standard_error = float(np.sqrt(max(covariance[1, 1], 0.0)))
    slope = float(coefficients[1])
    return {
        "information_logistic_slope": slope,
        "information_logistic_slope_lower_95": (
            slope - 1.959963984540054 * standard_error
        ),
        "information_logistic_slope_upper_95": (
            slope + 1.959963984540054 * standard_error
        ),
    }


def _summaries(
    cells: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    keys = [
        "cell_kind",
        "scaling_arm",
        "support_scheme",
        "interaction_shape",
        "noise_mode",
        "active_test_authors",
    ]
    rows: list[dict[str, Any]] = []
    rate_columns = {
        "detection": "structure_detected",
        "crc_or_hc_detection": "crc_or_hc_detected",
        "crc_detection": "crc_detected",
        "cross_low_rank_detection": "cross_low_rank_detected",
        "hc_detection": "hc_detected",
    }
    metric_columns = [
        "realized_active_test_authors",
        "information_budget_active",
        "information_budget_residual",
        "information_budget_residual_per_active_author",
        "centering_retention_ratio",
        "centering_leakage_ratio",
        "realized_global_effect_share",
        "realized_active_test_rms",
        "realized_active_cell_snr",
        "registered_active_cell_snr",
        "interaction_effective_rank",
        "projection_grand_mean_compatibility_error",
        "observed_active_cells_both_panels",
    ]
    for key, group in cells.groupby(keys, sort=True, observed=True):
        base = dict(zip(keys, key, strict=True))
        trials = len(group)
        tail_alpha = float(config["family_tail_alpha"])
        row: dict[str, Any] = {**base, "trials": int(trials)}
        for name, column in rate_columns.items():
            count = int(group[column].sum())
            lower, upper = _clopper(
                count,
                trials,
                tail_alpha=tail_alpha,
            )
            row.update({
                f"{name}_count": count,
                f"{name}_rate": count / trials,
                f"{name}_lower": lower,
                f"{name}_upper": upper,
            })
        for column in metric_columns:
            values = group[column].to_numpy(dtype=float)
            values = values[np.isfinite(values)]
            row[f"mean_{column}"] = (
                float(values.mean()) if len(values) else float("nan")
            )
        rows.append(row)
    summary = pd.DataFrame(rows)

    slope_rows: list[dict[str, Any]] = []
    for (support, shape, arm, noise), group in cells[
        cells["scaling_arm"] != "w0"
    ].groupby(
        [
            "support_scheme",
            "interaction_shape",
            "scaling_arm",
            "noise_mode",
        ],
        sort=True,
    ):
        for endpoint, column in {
            "omnibus": "structure_detected",
            "crc_or_hc": "crc_or_hc_detected",
        }.items():
            slope_rows.append({
                "support_scheme": str(support),
                "interaction_shape": str(shape),
                "scaling_arm": str(arm),
                "noise_mode": str(noise),
                "endpoint": endpoint,
                "trials": int(len(group)),
                **_logistic_information_slope(
                    group["information_budget_residual"].to_numpy(
                        dtype=float
                    ),
                    group[column].to_numpy(dtype=bool),
                ),
            })
    slopes = pd.DataFrame(slope_rows)

    target = float(config["discovery_target_power"])
    selection: dict[str, Any] = {}
    active = summary[
        (summary["support_scheme"] == "fixed")
        & (
            summary["interaction_shape"]
            == str(config["main_interaction_shape"])
        )
        & (summary["cell_kind"] != "w0")
    ]
    grid = sorted(map(int, config["active_test_author_grid"]))
    for arm in config["scaling_arms"]:
        arm_data = active[active["scaling_arm"] == str(arm)]
        minimum_rates = []
        for m in grid:
            subset = arm_data[arm_data["active_test_authors"] == m]
            minimum_rates.append(
                float(subset["crc_or_hc_detection_rate"].min())
                if len(subset) == len(config["noise_modes"])
                else float("nan")
            )
        selection[f"{arm}_minimum_rates"] = minimum_rates
        selection[f"{arm}_monotone_non_decreasing"] = bool(
            np.isfinite(minimum_rates).all()
            and np.all(np.diff(minimum_rates) >= -0.05)
        )
        for endpoint in ("detection", "crc_or_hc_detection"):
            candidate = None
            for index, m in enumerate(grid):
                tail = arm_data[
                    arm_data["active_test_authors"].isin(grid[index:])
                ]
                expected = len(grid[index:]) * len(
                    config["noise_modes"]
                )
                if (
                    len(tail) == expected
                    and tail[f"{endpoint}_rate"].min() >= target
                ):
                    candidate = int(m)
                    break
            selection[f"m90_{endpoint}_{arm}"] = candidate
    return summary, slopes, selection


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.4D R2 Minority Information Frontier

Decision: `{decision["status"]}`

## Selection

```json
{json.dumps(decision["m90_selection"], indent=2)}
```

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Boundary

This is a synthetic information-budget and detector-power experiment. The
CRC-or-HC endpoint does not prove non-low-rank geometry. Psychological,
semantic, real-text, causal, diagnostic, and clinical claims remain closed.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery", "confirmation"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    config["_active_permutations"] = (
        int(config["smoke_permutations"])
        if args.mode == "smoke"
        else int(config["permutations"])
    )
    seed = {
        "smoke": int(config["smoke_seed"]),
        "discovery": int(config["seed"]),
        "confirmation": int(config["confirmation_seed"]),
    }[args.mode]
    definitions = _cell_definitions(config, mode=args.mode)
    tasks = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(int(definition["repetitions"]))
    ]
    streams = np.random.SeedSequence(seed).spawn(3 * len(tasks))
    seeds = [
        int(stream.generate_state(1, dtype=np.uint64)[0])
        for stream in streams
    ]
    payloads = [
        (
            config,
            definition,
            repetition,
            seeds[3 * index],
            seeds[3 * index + 1],
            seeds[3 * index + 2],
        )
        for index, (definition, repetition) in enumerate(tasks)
    ]
    if int(config["jobs"]) == 1:
        rows = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            rows = list(executor.map(_worker, payloads, chunksize=1))
    cells = pd.DataFrame(rows)
    summary, slopes, selection = _summaries(cells, config=config)

    integrity = {
        "row_count": bool(len(cells) == len(tasks)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "numeric_integrity": bool(
            np.isfinite(
                cells[[
                    "crc",
                    "cross_low_rank_ratio",
                    "hc",
                    "information_budget_residual",
                    "centering_retention_ratio",
                    "centering_leakage_ratio",
                ]].to_numpy(dtype=float)
            ).all()
        ),
        "support_count_integrity": bool(
            (
                cells.loc[
                    cells["support_scheme"] == "fixed",
                    "realized_active_test_authors",
                ]
                == cells.loc[
                    cells["support_scheme"] == "fixed",
                    "active_test_authors",
                ]
            ).all()
        ),
        "projection_compatibility": bool(
            cells[
                "projection_grand_mean_compatibility_error"
            ].max()
            <= float(
                config["gates"][
                    "maximum_projection_compatibility_error"
                ]
            )
        ),
    }
    checks: dict[str, Any] = {**integrity}
    if args.mode == "confirmation":
        selected_m = config.get("confirmation_active_test_authors")
        if selected_m is None:
            checks["confirmation_m_frozen"] = False
        else:
            checks["confirmation_m_frozen"] = True
            active = summary[
                (summary["scaling_arm"] == "active_snr")
                & (summary["support_scheme"] == "fixed")
                & (
                    summary["interaction_shape"]
                    == str(config["main_interaction_shape"])
                )
                & (
                    summary["active_test_authors"]
                    == int(selected_m)
                )
            ]
            w0 = summary[summary["scaling_arm"] == "w0"]
            slope = slopes[
                (slopes["scaling_arm"] == "active_snr")
                & (slopes["support_scheme"] == "fixed")
                & (
                    slopes["interaction_shape"]
                    == str(config["main_interaction_shape"])
                )
                & (slopes["endpoint"] == "crc_or_hc")
            ]
            checks["w0_calibration"] = bool(
                len(w0) == len(config["noise_modes"])
                and w0["detection_upper"].max()
                < float(
                    config["gates"][
                        "maximum_w0_false_refusal_upper"
                    ]
                )
            )
            checks["selected_m_power"] = bool(
                len(active) == len(config["noise_modes"])
                and active["crc_or_hc_detection_lower"].min()
                > float(
                    config["gates"][
                        "minimum_confirmation_power_lower"
                    ]
                )
            )
            checks["information_slope"] = bool(
                len(slope) == len(config["noise_modes"])
                and slope[
                    "information_logistic_slope_lower_95"
                ].min()
                > float(
                    config["gates"][
                        "minimum_information_slope_lower"
                    ]
                )
            )

    if not all(integrity.values()):
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_"
            "STOP_INTEGRITY"
        )
    elif args.mode == "smoke":
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_"
            "SMOKE_COMPLETE"
        )
    elif args.mode == "discovery":
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_"
            + (
                "DISCOVERY_M90_SELECTED"
                if selection[
                    "m90_crc_or_hc_detection_active_snr"
                ] is not None
                else "DISCOVERY_NO_M90"
            )
        )
    elif all(checks.values()):
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_"
            "CONFIRMATION_PASS"
        )
    else:
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_"
            "CONFIRMATION_FAIL"
        )
    decision = {
        "status": status,
        "mode": args.mode,
        "checks": checks,
        "m90_selection": selection,
        "row_count": int(len(cells)),
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "cell_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    slopes.to_csv(args.output_dir / "information_slopes.csv", index=False)
    _write(args.output_dir / "m90_selection.json", selection)
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
            ROOT / "suica_core/v8_reference_measure_frontier.py",
            ROOT / "suica_core/v8_minority_information_frontier.py",
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
        "rows": int(len(cells)),
        "m90_selection": selection,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
