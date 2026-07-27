#!/usr/bin/env python3
"""Run V3.7H.1 paired-schedule refusal and matched-power discovery."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_resolution_filtration import (  # noqa: E402
    fit_joint_resolution_family,
    resolution_candidates,
)
from suica_core.v8_resolution_filtration_h1 import (  # noqa: E402
    PairedScheduleSpec,
    cumulative_kappa,
    fit_fixed_linear_cumulative_predictor,
    initial_observable_history,
    paired_schedule_excess,
    paired_schedule_score_path,
    predict_joint_cumulative,
    score_space_response_ratio,
    score_paired_schedule_panel,
    simulate_paired_schedule_panel,
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


def _spec(config: dict[str, Any]) -> PairedScheduleSpec:
    return PairedScheduleSpec(
        dimension=int(config["dimension"]),
        budgets=tuple(int(value) for value in config["event_budgets"]),
        reference_authors=int(config["reference_authors"]),
        calibration_authors=int(config["calibration_authors"]),
        panel_authors=int(config["panel_authors"]),
        stable_rms=float(config["stable_rms"]),
        event_rms_at_64=float(config["event_rms_at_64"]),
        opportunity_start=int(config["opportunity_start"]),
    )


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    config, repetition, spawn_key = payload
    spec = _spec(config)
    cells = [
        (str(geometry), float(eta))
        for geometry in config["geometries"]
        for eta in config["eta_levels"]
    ]
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    streams = root.spawn(2 + 4 * len(cells))
    context_seed = _uint64(streams[0])
    selection_seed = _uint64(streams[1])
    seeds = [context_seed, selection_seed]
    context = simulate_schedule_calibration_context(
        seed=context_seed,
        spec=spec,
    )
    external_zero = context["reference"][:, :, -1].mean(axis=(0, 1))
    fitted, selected, candidate_table = fit_joint_resolution_family(
        context["calibration"],
        budgets=spec.budgets,
        external_zero=external_zero,
        candidates=resolution_candidates(),
        folds=int(config["selection_folds"]),
        seed=selection_seed,
        noise_shrinkage=float(config["noise_shrinkage"]),
    )
    candidate_rows = [
        {
            "repetition": repetition,
            **row.to_dict(),
        }
        for _, row in candidate_table.iterrows()
    ]
    rows: list[dict[str, Any]] = []
    maximum_prefix_error = float(
        context["maximum_prefix_identity_error"]
    )

    for cell_index, (geometry, eta) in enumerate(cells):
        cell_seeds = [
            _uint64(value)
            for value in streams[
                2 + 4 * cell_index:2 + 4 * (cell_index + 1)
            ]
        ]
        response_seed = cell_seeds[0]
        panel_seeds = cell_seeds[1:]
        seeds.extend(cell_seeds)
        has_drift = eta > 0.0
        refusal = simulate_paired_schedule_panel(
            context,
            seed=panel_seeds[0],
            geometry=geometry,
            eta=eta,
            drift_schedule_b=has_drift,
            response_seed=response_seed,
        )
        probe = simulate_paired_schedule_panel(
            context,
            seed=panel_seeds[1],
            geometry=geometry,
            eta=eta,
            drift_schedule_b=has_drift,
            response_seed=response_seed,
        )
        evaluation = simulate_paired_schedule_panel(
            context,
            seed=panel_seeds[2],
            geometry=geometry,
            eta=eta,
            drift_schedule_b=has_drift,
            response_seed=response_seed,
        )
        maximum_prefix_error = max(
            maximum_prefix_error,
            float(refusal["prefix_identity_error"]),
            float(probe["prefix_identity_error"]),
            float(evaluation["prefix_identity_error"]),
        )

        refusal_scores = score_paired_schedule_panel(
            refusal["values"],
            fitted,
            budgets=spec.budgets,
        )
        schedule_metrics = [
            paired_schedule_excess(
                refusal_scores,
                fitted,
                budget_index=index,
                budget=budget,
            )
            for index, budget in enumerate(spec.budgets)
        ]
        endpoint_q = float(schedule_metrics[-1]["schedule_excess_q"])
        endpoint_score_eta = {
            name: score_space_response_ratio(
                panel["response"],
                fitted[int(spec.budgets[-1])],
                fraction=float(panel["fractions"][-1]),
            )
            for name, panel in (
                ("refusal", refusal),
                ("probe", probe),
                ("evaluation", evaluation),
            )
        }
        paired_detected = bool(
            endpoint_q >= float(config["schedule_excess_margin"])
        )

        _, probe_scores, probe_residuals = paired_schedule_score_path(
            probe["values"],
            fitted,
            budgets=spec.budgets,
            schedule_index=1,
        )
        _, evaluation_scores, evaluation_residuals = (
            paired_schedule_score_path(
                evaluation["values"],
                fitted,
                budgets=spec.budgets,
                schedule_index=1,
            )
        )
        probe_features = initial_observable_history(
            probe["values"][:, 1],
            probe_scores[0],
            probe_residuals[0],
            external_zero=external_zero,
        )
        evaluation_features = initial_observable_history(
            evaluation["values"][:, 1],
            evaluation_scores[0],
            evaluation_residuals[0],
            external_zero=external_zero,
        )
        cumulative_fit = fit_fixed_linear_cumulative_predictor(
            probe_features,
            [
                probe_scores[index] - probe_scores[0]
                for index in range(1, len(spec.budgets))
            ],
            alpha=float(config["frozen_cumulative_alpha"]),
        )
        cumulative_predictions = predict_joint_cumulative(
            cumulative_fit,
            evaluation_features,
        )
        cumulative_values = [
            cumulative_kappa(
                evaluation_scores[index] - evaluation_scores[0],
                cumulative_predictions[index - 1],
            )
            for index in range(1, len(spec.budgets))
        ]
        pooled_kappa = float(np.mean(cumulative_values))
        cumulative_detected = bool(
            pooled_kappa
            >= float(config["cumulative_detection_threshold"])
        )
        diagnostic_union = bool(paired_detected or cumulative_detected)
        operational_refusal = bool(paired_detected)
        rows.append({
            "repetition": repetition,
            "geometry": geometry,
            "eta": eta,
            "world": (
                "paired_same_schedule_null"
                if not has_drift
                else f"paired_opportunity_{geometry}_eta_{eta:.2f}"
            ),
            "selected_name": str(selected["name"]),
            "achieved_eta_refusal": float(refusal["achieved_eta"]),
            "achieved_eta_probe": float(probe["achieved_eta"]),
            "achieved_eta_evaluation": float(evaluation["achieved_eta"]),
            "achieved_score_eta_refusal": float(
                endpoint_score_eta["refusal"]
            ),
            "achieved_score_eta_probe": float(
                endpoint_score_eta["probe"]
            ),
            "achieved_score_eta_evaluation": float(
                endpoint_score_eta["evaluation"]
            ),
            "schedule_excess_q_512": endpoint_q,
            "paired_detected": paired_detected,
            "cumulative_kappa_pooled": pooled_kappa,
            "cumulative_detected": cumulative_detected,
            "diagnostic_union_refusal": diagnostic_union,
            "operational_refusal": operational_refusal,
            "interval_claim_allowed": not operational_refusal,
            "false_refusal": bool(
                not has_drift and operational_refusal
            ),
            "material_detection": bool(
                has_drift and operational_refusal
            ),
            "maximum_prefix_identity_error": maximum_prefix_error,
            **{
                f"schedule_excess_q_{budget}": float(
                    schedule_metrics[index]["schedule_excess_q"]
                )
                for index, budget in enumerate(spec.budgets)
            },
            **{
                f"cumulative_kappa_{spec.budgets[index]}": float(
                    cumulative_values[index - 1]
                )
                for index in range(1, len(spec.budgets))
            },
        })
    return rows, candidate_rows, seeds


def _clopper_pearson(
    successes: int,
    trials: int,
    *,
    confidence: float,
) -> tuple[float, float]:
    alpha = 1.0 - float(confidence)
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(alpha, successes, trials - successes + 1))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(
            confidence,
            successes + 1,
            trials - successes,
        ))
    )
    return lower, upper


def _bootstrap_mean(
    values: np.ndarray,
    *,
    seed: int,
    draws: int,
    confidence: float,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    rng = np.random.default_rng(int(seed))
    sampled = vector[
        rng.integers(0, len(vector), size=(int(draws), len(vector)))
    ].mean(axis=1)
    alpha = 1.0 - float(confidence)
    return {
        "mean": float(vector.mean()),
        "one_sided_lower": float(np.quantile(sampled, alpha)),
        "one_sided_upper": float(np.quantile(sampled, confidence)),
    }


def _summarize(
    metrics: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    seed = int(config["_active_seed"]) ^ 0x371
    simultaneous_cells = (
        len(config["geometries"]) * len(config["eta_levels"])
    )
    familywise_confidence = 1.0 - (
        1.0 - float(config["power_confidence"])
    ) / max(int(simultaneous_cells), 1)
    for cell_index, ((geometry, eta), group) in enumerate(
        metrics.groupby(["geometry", "eta"], sort=True)
    ):
        trials = int(len(group))
        successes = int(group["operational_refusal"].sum())
        lower, upper = _clopper_pearson(
            successes,
            trials,
            confidence=familywise_confidence,
        )
        q = _bootstrap_mean(
            group["schedule_excess_q_512"].to_numpy(dtype=float),
            seed=seed + 2 * cell_index,
            draws=int(config["summary_bootstrap_draws"]),
            confidence=familywise_confidence,
        )
        kappa = _bootstrap_mean(
            group["cumulative_kappa_pooled"].to_numpy(dtype=float),
            seed=seed + 2 * cell_index + 1,
            draws=int(config["summary_bootstrap_draws"]),
            confidence=familywise_confidence,
        )
        row = {
            "geometry": geometry,
            "eta": float(eta),
            "trials": trials,
            "simultaneous_cells": int(simultaneous_cells),
            "familywise_confidence": float(familywise_confidence),
            "operational_refusals": successes,
            "operational_refusal_rate": float(successes / trials),
            "diagnostic_union_refusal_rate": float(
                group["diagnostic_union_refusal"].mean()
            ),
            "one_sided_cp_lower": lower,
            "one_sided_cp_upper": upper,
            "paired_detection_rate": float(
                group["paired_detected"].mean()
            ),
            "cumulative_detection_rate": float(
                group["cumulative_detected"].mean()
            ),
            "schedule_excess_q_mean": q["mean"],
            "schedule_excess_q_lower": q["one_sided_lower"],
            "schedule_excess_q_upper": q["one_sided_upper"],
            "cumulative_kappa_mean": kappa["mean"],
            "cumulative_kappa_lower": kappa["one_sided_lower"],
            "cumulative_kappa_upper": kappa["one_sided_upper"],
            "achieved_eta_mean": float(
                group["achieved_eta_evaluation"].mean()
            ),
            "achieved_score_eta_mean": float(
                group["achieved_score_eta_evaluation"].mean()
            ),
            "q_minus_score_eta_mean": float(
                (
                    group["schedule_excess_q_512"]
                    - group["achieved_score_eta_evaluation"]
                ).mean()
            ),
        }
        rows.append(row)
        evidence[f"{geometry}::{float(eta):.2f}"] = row
    summary = pd.DataFrame(rows)
    null = summary[np.isclose(summary["eta"], 0.0)]
    material = summary[
        summary["eta"].isin(
            [float(value) for value in config["material_power_levels"]]
        )
    ]
    random_material = summary[
        (summary["geometry"] == "random_rotation")
        & np.isclose(
            summary["eta"],
            float(config["primary_opportunity_eta"]),
        )
    ]
    checks = {
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
        "same_schedule_null_q": bool(
            len(null)
            and null["schedule_excess_q_upper"].max()
            <= float(config["schedule_excess_margin"])
        ),
        "primary_opportunity_q": bool(
            len(random_material)
            and random_material["schedule_excess_q_lower"].min()
            >= float(config["schedule_excess_margin"])
        ),
        "refusal_semantics": bool(
            (
                metrics["interval_claim_allowed"]
                == ~metrics["operational_refusal"].astype(bool)
            ).all()
        ),
        "prefix_identity": bool(
            metrics["maximum_prefix_identity_error"].max()
            <= float(config["maximum_prefix_identity_error"])
        ),
    }
    return summary, {
        "checks": checks,
        "cells": evidence,
        "minimum_detectable_eta": {
            str(geometry): (
                float(
                    group[
                        group["one_sided_cp_lower"]
                        >= float(config["minimum_material_power_lower"])
                    ]["eta"].min()
                )
                if (
                    group["one_sided_cp_lower"]
                    >= float(config["minimum_material_power_lower"])
                ).any()
                else None
            )
            for geometry, group in summary.groupby("geometry")
        },
        "simultaneous_inference": {
            "cells": int(simultaneous_cells),
            "nominal_familywise_confidence": float(
                config["power_confidence"]
            ),
            "bonferroni_cell_confidence": float(
                familywise_confidence
            ),
        },
    }


def _report(decision: dict[str, Any], summary: pd.DataFrame) -> str:
    return f"""# V3.7H.1 Paired-Schedule Refusal and Power

Decision: `{decision["status"]}`

## Candidate checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Power cells

{summary.to_markdown(index=False)}

## Boundary

This is a synthetic design and power experiment. It tests whether a frozen
score path can refuse stable-author interpretation when the same authors
change under registered opportunity schedules. It does not establish
real-text opportunity detection, personality validity, or clinical safety.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_schedule_refusal_v37h1.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_schedule_refusal/v37h1_discovery",
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
    candidates = pd.DataFrame([
        row for _, part, _ in nested for row in part
    ])
    seeds = [seed for _, _, part in nested for seed in part]
    summary, evidence = _summarize(metrics, config=config)
    integrity = {
        "metric_rows": int(len(metrics)),
        "expected_metric_rows": int(
            config["_active_repetitions"]
            * len(config["geometries"])
            * len(config["eta_levels"])
        ),
        "numeric": bool(np.isfinite(
            metrics[
                [
                    "schedule_excess_q_512",
                    "cumulative_kappa_pooled",
                    "achieved_eta_evaluation",
                    "achieved_score_eta_evaluation",
                    "maximum_prefix_identity_error",
                ]
            ].to_numpy(dtype=float)
        ).all()),
        "seed_count": int(len(seeds)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
    }
    integrity_pass = bool(
        integrity["metric_rows"] == integrity["expected_metric_rows"]
        and integrity["numeric"]
        and integrity["seed_uniqueness"]
    )
    if not integrity_pass:
        status = "V8_SCHEDULE_REFUSAL_V37H1_STOP_INTEGRITY"
    elif args.mode == "smoke":
        status = "V8_SCHEDULE_REFUSAL_V37H1_SMOKE_COMPLETE"
    elif args.mode == "power":
        status = (
            "V8_SCHEDULE_REFUSAL_V37H1_POWER_CANDIDATE_PASS"
            if all(evidence["checks"].values())
            else "V8_SCHEDULE_REFUSAL_V37H1_POWER_CANDIDATE_REFUTED"
        )
    else:
        status = "V8_SCHEDULE_REFUSAL_V37H1_DISCOVERY_COMPLETE"
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "integrity": integrity,
        **evidence,
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    candidates.to_csv(args.output_dir / "candidate_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "power_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (args.output_dir / "report.md").write_text(
        _report(decision, summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_resolution_filtration.py",
            ROOT / "suica_core/v8_resolution_filtration_h1.py",
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
