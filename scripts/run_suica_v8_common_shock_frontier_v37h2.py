#!/usr/bin/env python3
"""Run the V3.7H.2 repeated-opportunity common-shock frontier."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta, t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_common_shock_frontier import (  # noqa: E402
    CommonShockSpec,
    legacy_stream_excess,
    prepare_response_geometry,
    repeated_opportunity_excess,
    score_common_shock_panel,
    simulate_common_shock_panel,
)
from suica_core.v8_resolution_filtration import (  # noqa: E402
    fit_joint_resolution_family,
    resolution_candidates,
)
from suica_core.v8_resolution_filtration_h1 import (  # noqa: E402
    PairedScheduleSpec,
    simulate_schedule_calibration_context,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _schedule_spec(config: dict[str, Any]) -> PairedScheduleSpec:
    return PairedScheduleSpec(
        dimension=int(config["dimension"]),
        budgets=tuple(int(value) for value in config["event_budgets"]),
        reference_authors=int(config["reference_authors"]),
        calibration_authors=int(config["calibration_authors"]),
        panel_authors=int(config["panel_authors"]),
        stable_rms=float(config["stable_rms"]),
        event_rms_at_64=float(config["event_rms_at_64"]),
        opportunity_start=int(config["event_budgets"][0]),
    )


def _common_spec(config: dict[str, Any]) -> CommonShockSpec:
    return CommonShockSpec(
        dimension=int(config["dimension"]),
        endpoint_budget=int(config["endpoint_budget"]),
        panel_authors=int(config["panel_authors"]),
        event_rms_at_64=float(config["event_rms_at_64"]),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )


def _cells(config: dict[str, Any]) -> list[tuple[int, float, float, str, float]]:
    return [
        (
            int(repeats),
            float(correlation),
            float(common_energy),
            str(noise_mode),
            float(response_eta),
        )
        for repeats in config["opportunity_repeats"]
        for correlation in config["stream_correlations"]
        for common_energy in config["common_shock_score_energy"]
        for noise_mode in config["noise_modes"]
        for response_eta in config["response_score_eta"]
    ]


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    config, repetition, spawn_key = payload
    cells = _cells(config)
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    streams = root.spawn(3 + len(cells) + 2)
    context_seed = _uint64(streams[0])
    selection_seed = _uint64(streams[1])
    response_seed = _uint64(streams[2])
    cell_seeds = [_uint64(value) for value in streams[3:3 + len(cells)]]
    alias_seed = _uint64(streams[-2])
    global_seed = _uint64(streams[-1])
    all_seeds = [
        context_seed,
        selection_seed,
        response_seed,
        *cell_seeds,
        alias_seed,
        global_seed,
    ]

    schedule_spec = _schedule_spec(config)
    common_spec = _common_spec(config)
    context = simulate_schedule_calibration_context(
        seed=context_seed,
        spec=schedule_spec,
    )
    external_zero = context["reference"][:, :, -1].mean(axis=(0, 1))
    fitted, selected, _ = fit_joint_resolution_family(
        context["calibration"],
        budgets=schedule_spec.budgets,
        external_zero=external_zero,
        candidates=resolution_candidates(),
        folds=int(config["selection_folds"]),
        seed=selection_seed,
        noise_shrinkage=float(config["noise_shrinkage"]),
    )
    endpoint = fitted[int(config["endpoint_budget"])]
    response_geometry = prepare_response_geometry(
        context,
        endpoint,
        geometry=str(config["response_geometry"]),
        seed=response_seed,
    )

    rows: list[dict[str, Any]] = []
    margin = float(config["schedule_excess_margin"])
    for cell, panel_seed in zip(cells, cell_seeds, strict=True):
        repeats, correlation, common_energy, noise_mode, response_eta = cell
        panel = simulate_common_shock_panel(
            context,
            endpoint,
            response_geometry,
            seed=panel_seed,
            spec=common_spec,
            opportunity_repeats=repeats,
            stream_correlation=correlation,
            common_shock_score_energy=common_energy,
            noise_mode=noise_mode,
            response_score_eta=response_eta,
        )
        scores = score_common_shock_panel(panel["values"], endpoint)
        legacy = legacy_stream_excess(scores, endpoint)
        repeated = repeated_opportunity_excess(scores, endpoint)
        identified = bool(repeated["identified"])
        rows.append({
            "repetition": int(repetition),
            "opportunity_repeats": repeats,
            "stream_correlation": correlation,
            "common_shock_score_energy": common_energy,
            "noise_mode": noise_mode,
            "response_score_eta": response_eta,
            "selected_name": str(selected["name"]),
            "achieved_response_score_eta": float(
                panel["achieved_response_score_eta"]
            ),
            "achieved_common_shock_score_energy": float(
                panel["achieved_common_shock_score_energy"]
            ),
            "legacy_q_total": float(legacy["q_total"]),
            "legacy_q_author": float(legacy["q_author"]),
            "legacy_detected": bool(legacy["q_total"] >= margin),
            "repeated_identified": identified,
            "repeated_q_total": float(repeated["q_total"]),
            "repeated_q_author": float(repeated["q_author"]),
            "repeated_detected": bool(
                identified and repeated["q_total"] >= margin
            ),
            "repeated_bias": (
                float(
                    repeated["q_total"]
                    - panel["achieved_response_score_eta"]
                )
                if identified
                else float("nan")
            ),
            "legacy_noise_correction": float(
                legacy["noise_correction"]
            ),
            "repeated_noise_correction": float(
                repeated["noise_correction"]
            ),
        })

    assay_common = {
        "context": context,
        "fitted": endpoint,
        "response_geometry": response_geometry,
        "spec": common_spec,
        "opportunity_repeats": 4,
        "stream_correlation": 0.3,
        "common_shock_score_energy": 0.01,
        "noise_mode": "gaussian",
    }
    response_world = simulate_common_shock_panel(
        **assay_common,
        seed=alias_seed,
        response_score_eta=float(config["alias_response_score_eta"]),
        effect_source="author_response",
    )
    confound_world = simulate_common_shock_panel(
        **assay_common,
        seed=alias_seed,
        response_score_eta=float(config["alias_response_score_eta"]),
        effect_source="persistent_schedule_confound",
    )
    alias_error = float(np.max(np.abs(
        response_world["values"] - confound_world["values"]
    )))

    global_world = simulate_common_shock_panel(
        **assay_common,
        seed=global_seed,
        response_score_eta=0.0,
        global_shift_score_eta=float(config["global_shift_score_eta"]),
    )
    global_scores = score_common_shock_panel(
        global_world["values"],
        endpoint,
    )
    global_estimate = repeated_opportunity_excess(
        global_scores,
        endpoint,
    )
    assay_rows = [{
        "repetition": int(repetition),
        "alias_identity_error": alias_error,
        "alias_classification": (
            "SCHEDULE_SENSITIVITY_IDENTIFIED_CAUSE_UNIDENTIFIED"
        ),
        "global_shift_score_eta": float(
            global_world["achieved_global_shift_score_eta"]
        ),
        "global_q_total": float(global_estimate["q_total"]),
        "global_q_author": float(global_estimate["q_author"]),
        "global_total_detected": bool(
            global_estimate["q_total"] >= margin
        ),
        "global_author_detected": bool(
            global_estimate["q_author"] >= margin
        ),
    }]
    return rows, assay_rows, all_seeds


def _clopper_pearson(
    successes: int,
    trials: int,
    *,
    alpha: float,
) -> tuple[float, float]:
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(
            float(alpha),
            successes,
            trials - successes + 1,
        ))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(
            1.0 - float(alpha),
            successes + 1,
            trials - successes,
        ))
    )
    return lower, upper


def _summarize(
    metrics: pd.DataFrame,
    assays: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    identified_repeat_count = sum(
        int(value) >= 2 for value in config["opportunity_repeats"]
    )
    identified_cells = (
        identified_repeat_count
        * len(config["stream_correlations"])
        * len(config["common_shock_score_energy"])
        * len(config["noise_modes"])
    )
    bias_cells = identified_cells * len(config["response_score_eta"])
    family_alpha = (
        1.0 - float(config["power_confidence"])
    ) / max(int(identified_cells), 1)
    bias_alpha = (
        1.0 - float(config["power_confidence"])
    ) / max(2 * int(bias_cells), 1)

    rows: list[dict[str, Any]] = []
    keys = [
        "opportunity_repeats",
        "stream_correlation",
        "common_shock_score_energy",
        "noise_mode",
        "response_score_eta",
    ]
    for key, group in metrics.groupby(keys, sort=True, dropna=False):
        repeats, correlation, common_energy, noise_mode, response_eta = key
        identified = bool(group["repeated_identified"].all())
        trials = int(len(group))
        successes = int(group["repeated_detected"].sum())
        lower, upper = (
            _clopper_pearson(successes, trials, alpha=family_alpha)
            if identified
            else (float("nan"), float("nan"))
        )
        bias = group["repeated_bias"].dropna().to_numpy(dtype=float)
        if len(bias) > 1:
            standard_error = float(bias.std(ddof=1) / np.sqrt(len(bias)))
            critical = float(t.ppf(
                1.0 - bias_alpha,
                len(bias) - 1,
            ))
            bias_mean = float(bias.mean())
            bias_lower = bias_mean - critical * standard_error
            bias_upper = bias_mean + critical * standard_error
        else:
            bias_mean = bias_lower = bias_upper = float("nan")
        rows.append({
            "opportunity_repeats": int(repeats),
            "stream_correlation": float(correlation),
            "common_shock_score_energy": float(common_energy),
            "noise_mode": str(noise_mode),
            "response_score_eta": float(response_eta),
            "trials": trials,
            "repeated_identified": identified,
            "repeated_refusals": successes,
            "repeated_refusal_rate": (
                float(successes / trials) if identified else float("nan")
            ),
            "one_sided_cp_lower": lower,
            "one_sided_cp_upper": upper,
            "legacy_refusal_rate": float(
                group["legacy_detected"].mean()
            ),
            "legacy_q_mean": float(group["legacy_q_total"].mean()),
            "repeated_q_mean": (
                float(group["repeated_q_total"].mean())
                if identified
                else float("nan")
            ),
            "repeated_author_q_mean": (
                float(group["repeated_q_author"].mean())
                if identified
                else float("nan")
            ),
            "achieved_response_eta_mean": float(
                group["achieved_response_score_eta"].mean()
            ),
            "achieved_common_energy_mean": float(
                group["achieved_common_shock_score_energy"].mean()
            ),
            "bias_mean": bias_mean,
            "bias_simultaneous_lower": bias_lower,
            "bias_simultaneous_upper": bias_upper,
            "decision_family_cells": int(identified_cells),
            "bias_family_cells": int(bias_cells),
        })
    summary = pd.DataFrame(rows)

    identified = summary[summary["repeated_identified"]]
    null = identified[np.isclose(
        identified["response_score_eta"],
        0.0,
    )]
    material = identified[np.isclose(
        identified["response_score_eta"],
        float(config["material_eta"]),
    )]
    gaussian = identified[identified["noise_mode"] == "gaussian"]
    heavy = identified[
        identified["noise_mode"] == "heteroskedastic_t5"
    ]
    k1 = metrics[metrics["opportunity_repeats"] == 1]

    global_trials = int(len(assays))
    global_total = int(assays["global_total_detected"].sum())
    global_author = int(assays["global_author_detected"].sum())
    global_alpha = (
        1.0 - float(config["power_confidence"])
    ) / 2.0
    total_lower, _ = _clopper_pearson(
        global_total,
        global_trials,
        alpha=global_alpha,
    )
    _, author_upper = _clopper_pearson(
        global_author,
        global_trials,
        alpha=global_alpha,
    )

    gaussian_tolerance = float(config["gaussian_bias_tolerance"])
    heavy_tolerance = float(config["heavy_tail_bias_tolerance"])
    checks = {
        "k1_explicitly_unidentifiable": bool(
            len(k1)
            and (~k1["repeated_identified"]).all()
            and k1["repeated_q_total"].isna().all()
            and k1["repeated_q_author"].isna().all()
        ),
        "false_refusal": bool(
            len(null)
            and null["one_sided_cp_upper"].max()
            <= float(config["maximum_false_refusal_upper"])
        ),
        "material_power": bool(
            len(material)
            and material["one_sided_cp_lower"].min()
            >= float(config["minimum_material_power_lower"])
        ),
        "gaussian_bias": bool(
            len(gaussian)
            and gaussian["bias_simultaneous_lower"].min()
            >= -gaussian_tolerance
            and gaussian["bias_simultaneous_upper"].max()
            <= gaussian_tolerance
        ),
        "heavy_tail_bias": bool(
            len(heavy)
            and heavy["bias_simultaneous_lower"].min()
            >= -heavy_tolerance
            and heavy["bias_simultaneous_upper"].max()
            <= heavy_tolerance
        ),
        "global_shift_decomposition": bool(
            total_lower >= float(config["minimum_material_power_lower"])
            and author_upper
            <= float(config["maximum_false_refusal_upper"])
        ),
        "persistent_cause_alias": bool(
            assays["alias_identity_error"].max()
            <= float(config["maximum_identity_error"])
            and (
                assays["alias_classification"]
                == "SCHEDULE_SENSITIVITY_IDENTIFIED_CAUSE_UNIDENTIFIED"
            ).all()
        ),
        "legacy_failure_exposed": bool(
            metrics[
                (metrics["response_score_eta"] == 0.0)
                & (
                    (metrics["stream_correlation"] > 0.0)
                    | (metrics["common_shock_score_energy"] > 0.0)
                )
            ]["legacy_detected"].mean()
            > 0.10
        ),
    }
    evidence = {
        "checks": checks,
        "familywise_inference": {
            "decision_family_cells": int(identified_cells),
            "decision_cell_alpha": float(family_alpha),
            "bias_family_cells": int(bias_cells),
            "bias_tail_alpha": float(bias_alpha),
            "directions_combined": False,
        },
        "extrema": {
            "maximum_null_false_refusal_upper": float(
                null["one_sided_cp_upper"].max()
            ),
            "minimum_material_power_lower": float(
                material["one_sided_cp_lower"].min()
            ),
            "maximum_gaussian_absolute_bias_bound": float(max(
                abs(gaussian["bias_simultaneous_lower"].min()),
                abs(gaussian["bias_simultaneous_upper"].max()),
            )),
            "maximum_heavy_absolute_bias_bound": float(max(
                abs(heavy["bias_simultaneous_lower"].min()),
                abs(heavy["bias_simultaneous_upper"].max()),
            )),
            "legacy_contaminated_null_refusal_rate": float(
                metrics[
                    (metrics["response_score_eta"] == 0.0)
                    & (
                        (metrics["stream_correlation"] > 0.0)
                        | (
                            metrics["common_shock_score_energy"]
                            > 0.0
                        )
                    )
                ]["legacy_detected"].mean()
            ),
        },
        "global_shift_assay": {
            "trials": global_trials,
            "total_detection_rate": float(global_total / global_trials),
            "total_detection_lower": float(total_lower),
            "author_detection_rate": float(global_author / global_trials),
            "author_detection_upper": float(author_upper),
            "mean_total_q": float(assays["global_q_total"].mean()),
            "mean_author_q": float(assays["global_q_author"].mean()),
        },
        "cause_alias_assay": {
            "maximum_identity_error": float(
                assays["alias_identity_error"].max()
            ),
            "classification": (
                "SCHEDULE_SENSITIVITY_IDENTIFIED_CAUSE_UNIDENTIFIED"
            ),
        },
    }
    return summary, evidence


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.2 Common-Shock Frontier

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Extrema

```json
{json.dumps(decision["extrema"], indent=2)}
```

## Global shift

```json
{json.dumps(decision["global_shift_assay"], indent=2)}
```

## Boundary

This is synthetic discovery and power work. A repeated-opportunity pass can
identify schedule-sensitivity energy under the registered occasion model. It
cannot identify the psychological cause of a persistent schedule difference,
validate real text, establish personality meaning, or license clinical use.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_common_shock_frontier_v37h2.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_common_shock_frontier/v37h2_discovery",
    )
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery", "power"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    if args.mode == "smoke":
        config["_active_seed"] = int(config["smoke_seed"])
        config["_active_repetitions"] = int(config["smoke_repetitions"])
    elif args.mode == "power":
        config["_active_seed"] = int(config["power_seed"])
        config["_active_repetitions"] = int(config["power_repetitions"])
    else:
        config["_active_seed"] = int(config["seed"])
        config["_active_repetitions"] = int(config["repetitions"])

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
            max_workers=int(config["jobs"])
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    metrics = pd.DataFrame([
        row for part, _, _ in nested for row in part
    ])
    assays = pd.DataFrame([
        row for _, part, _ in nested for row in part
    ])
    seeds = [seed for _, _, part in nested for seed in part]
    summary, evidence = _summarize(metrics, assays, config=config)

    expected_rows = (
        int(config["_active_repetitions"]) * len(_cells(config))
    )
    identified = metrics["repeated_identified"].astype(bool)
    finite_columns = [
        "legacy_q_total",
        "legacy_q_author",
        "achieved_response_score_eta",
        "achieved_common_shock_score_energy",
    ]
    repeated_columns = [
        "repeated_q_total",
        "repeated_q_author",
        "repeated_bias",
    ]
    integrity = {
        "metric_rows": int(len(metrics)),
        "expected_metric_rows": int(expected_rows),
        "assay_rows": int(len(assays)),
        "expected_assay_rows": int(config["_active_repetitions"]),
        "finite_base_metrics": bool(np.isfinite(
            metrics[finite_columns].to_numpy(dtype=float)
        ).all()),
        "finite_identified_metrics": bool(np.isfinite(
            metrics.loc[identified, repeated_columns].to_numpy(dtype=float)
        ).all()),
        "k1_nan_contract": bool(
            metrics.loc[~identified, repeated_columns].isna().all().all()
        ),
        "seed_count": int(len(seeds)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
    }
    integrity_pass = bool(
        integrity["metric_rows"] == integrity["expected_metric_rows"]
        and integrity["assay_rows"] == integrity["expected_assay_rows"]
        and integrity["finite_base_metrics"]
        and integrity["finite_identified_metrics"]
        and integrity["k1_nan_contract"]
        and integrity["seed_uniqueness"]
    )
    if not integrity_pass:
        status = "V8_COMMON_SHOCK_FRONTIER_V37H2_STOP_INTEGRITY"
    elif args.mode == "smoke":
        status = "V8_COMMON_SHOCK_FRONTIER_V37H2_SMOKE_COMPLETE"
    elif args.mode == "power":
        status = (
            "V8_COMMON_SHOCK_FRONTIER_V37H2_POWER_CANDIDATE_PASS"
            if all(evidence["checks"].values())
            else "V8_COMMON_SHOCK_FRONTIER_V37H2_POWER_CANDIDATE_REFUTED"
        )
    else:
        status = "V8_COMMON_SHOCK_FRONTIER_V37H2_DISCOVERY_COMPLETE"
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "integrity": integrity,
        **evidence,
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    assays.to_csv(args.output_dir / "assay_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "frontier_summary.csv", index=False)
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
            ROOT / "suica_core/v8_reliability_spectrum.py",
            ROOT / "suica_core/v8_resolution_filtration.py",
            ROOT / "suica_core/v8_resolution_filtration_h1.py",
            ROOT / "suica_core/v8_common_shock_frontier.py",
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
        "metric_rows": len(metrics),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
