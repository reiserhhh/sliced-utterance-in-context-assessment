#!/usr/bin/env python3
"""Run the frozen SUICA behavior-v2.1 C2 planted-world battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
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
from suica_core.v8_behavior_c2 import (  # noqa: E402
    C2SimulationSpec,
    evaluate_c2_pipeline,
    fit_c2_pipeline,
    simulate_c2_world,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_c2_planted_world.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_behavior_c2_planted_world"
    / "v1_20260725"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _cases() -> list[dict[str, Any]]:
    return [
        {"case_id": "N0_null", "world": "null", "snr": 0.0, "overlap": 1.0},
        {"case_id": "N1_c1_only", "world": "c1_only", "snr": 0.0, "overlap": 1.0},
        {"case_id": "N2_intercept_only", "world": "intercept_only", "snr": 0.0, "overlap": 1.0},
        *[
            {
                "case_id": f"S1_shared_c2_snr_{snr:0.2f}",
                "world": "shared_c2",
                "snr": snr,
                "overlap": 1.0,
            }
            for snr in (0.25, 0.50, 1.00)
        ],
        {"case_id": "S2_joint_snr_0.50", "world": "joint", "snr": 0.50, "overlap": 1.0},
        {"case_id": "A1_unique_conditions", "world": "unique_conditions", "snr": 0.50, "overlap": 1.0},
        *[
            {
                "case_id": f"A2_overlap_{overlap:0.2f}",
                "world": "shared_c2",
                "snr": 0.50,
                "overlap": overlap,
            }
            for overlap in (0.25, 0.50, 0.75)
        ],
        {"case_id": "A3_unstable_operator", "world": "unstable_operator", "snr": 0.50, "overlap": 1.0},
        {
            "case_id": "A4_private_stable_coordinates",
            "world": "private_stable_coordinates",
            "snr": 0.50,
            "overlap": 1.0,
        },
        {
            "case_id": "A5_half_shuffled_coordinates",
            "world": "half_shuffled_coordinates",
            "snr": 0.50,
            "overlap": 1.0,
        },
        {
            "case_id": "A6_c1_information_imbalance",
            "world": "c1_information_imbalance",
            "snr": 0.0,
            "overlap": 1.0,
        },
        {
            "case_id": "A7_extreme_prevalence",
            "world": "extreme_prevalence",
            "snr": 0.50,
            "overlap": 1.0,
        },
    ]


def _run_one(
    *,
    config: dict[str, Any],
    spec: C2SimulationSpec,
    case: dict[str, Any],
    observation: str,
    repetition: int,
    case_index: int,
) -> list[dict[str, Any]]:
    seed = (
        int(config["seed"])
        + 1_000_003 * repetition
        + 10_007 * case_index
        + (0 if observation == "soft" else 503)
    )
    world = simulate_c2_world(
        seed=seed,
        world=str(case["world"]),
        observation=observation,
        snr=float(case["snr"]),
        overlap=float(case["overlap"]),
        spec=spec,
    )
    rows = []
    modes = ["fixed_mean"]
    if case["world"] in {
        "c1_only",
        "joint",
        "c1_information_imbalance",
    }:
        modes.append("all_mean")
    for mode in modes:
        estimate = fit_c2_pipeline(
            world,
            cell_mean_key=mode,
            ridge_candidates=tuple(
                map(float, config["ridge_candidates"])
            ),
        )
        metrics = evaluate_c2_pipeline(
            world,
            estimate,
            seed=seed + (0 if mode == "fixed_mean" else 10_000),
            bootstrap_draws=int(config["bootstrap_draws"]),
            permutations=int(config["permutations"]),
            binary_ci_bootstrap_draws=(
                int(config["binary_ci_bootstrap"]["draws"])
                if (
                    observation == "binary"
                    and mode == "fixed_mean"
                    and case["case_id"] == "S1_shared_c2_snr_0.50"
                    and repetition
                    < int(config["binary_ci_bootstrap"]["repetitions"])
                )
                else 0
            ),
            binary_ci_bootstrap_authors=int(
                config["binary_ci_bootstrap"]["confirmation_authors"]
            ),
        )
        rows.append({
            "case_id": str(case["case_id"]),
            "world": str(case["world"]),
            "observation": observation,
            "estimator": (
                "fixed_quota_primary"
                if mode == "fixed_mean"
                else "all_observations_attack"
            ),
            "repetition": repetition,
            "seed": seed,
            "snr": float(case["snr"]),
            "overlap": float(case["overlap"]),
            **metrics,
        })
    if not world["design"]["condition_identity_shared"]:
        unsafe_world = {
            **world,
            "design": {
                **world["design"],
                "condition_identity_shared": True,
            },
        }
        unsafe = fit_c2_pipeline(
            unsafe_world,
            cell_mean_key="fixed_mean",
            ridge_candidates=tuple(map(float, config["ridge_candidates"])),
        )
        unsafe_metrics = evaluate_c2_pipeline(
            unsafe_world,
            unsafe,
            seed=seed + 20_000,
            bootstrap_draws=int(config["bootstrap_draws"]),
            permutations=int(config["permutations"]),
        )
        rows.append({
            "case_id": str(case["case_id"]),
            "world": str(case["world"]),
            "observation": observation,
            "estimator": "unsafe_identity_check_bypass",
            "repetition": repetition,
            "seed": seed,
            "snr": float(case["snr"]),
            "overlap": float(case["overlap"]),
            **unsafe_metrics,
        })
    return rows


def _run_repetition(
    payload: tuple[
        int,
        dict[str, Any],
        C2SimulationSpec,
        list[dict[str, Any]],
    ],
) -> list[dict[str, Any]]:
    repetition, config, spec, cases = payload
    rows = []
    for case_index, case in enumerate(cases):
        for observation in config["observations"]:
            rows.extend(_run_one(
                config=config,
                spec=spec,
                case=case,
                observation=str(observation),
                repetition=repetition,
                case_index=case_index,
            ))
    return rows


def _summary(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = [
        "case_id",
        "world",
        "observation",
        "estimator",
        "snr",
        "overlap",
    ]
    for keys, group in seed_metrics.groupby(
        groups,
        observed=True,
        sort=False,
    ):
        ready = group["c2_numeric_output"].fillna(False).astype(bool)
        evaluated = group.loc[ready]
        row = dict(zip(groups, keys, strict=True))
        row.update({
            "repetitions": int(len(group)),
            "numeric_output_rate": float(ready.mean()),
            "refusal_rate": float(1.0 - ready.mean()),
        })
        for column in (
            "same_author_auc",
            "c1_same_author_auc",
            "intercept_same_author_auc",
            "response_surface_cosine",
            "response_distance_spearman",
            "response_nrmse",
            "response_pointwise_ci_coverage",
            "response_mean_standardized_bias",
            "response_recovery_slope",
            "response_recovery_slope_bias",
            "q_to_response_cv_r2",
            "moment_same_author_auc",
            "inference_same_author_auc",
            "moment_response_surface_cosine",
            "probability_incidence_same_author_auc",
            "binary_estimator_auc_gap",
            "binary_estimator_cosine_gap",
            "binary_parametric_ci_coverage",
            "inference_author_half_refusal_rate",
            "inference_maximum_information_condition_number",
            "studentized_score_same_author_auc",
            "raw_score_same_author_auc",
            "se_only_same_author_auc",
            "permuted_numerator_same_author_auc",
            "full_whitened_same_author_auc",
        ):
            row[f"mean_{column}"] = (
                float(evaluated[column].mean())
                if len(evaluated)
                else float("nan")
            )
            row[f"median_{column}"] = (
                float(evaluated[column].median())
                if len(evaluated)
                else float("nan")
            )
        row["pairing_rejection_rate"] = (
            float(
                evaluated["pairing_permutation_p"].le(0.01).mean()
            )
            if len(evaluated)
            else float("nan")
        )
        if len(evaluated):
            rejected = int(
                evaluated["pairing_permutation_p"].le(0.01).sum()
            )
            row["pairing_rejection_upper_95"] = float(
                beta.ppf(
                    0.95,
                    rejected + 1,
                    len(evaluated) - rejected,
                )
                if rejected < len(evaluated)
                else 1.0
            )
            auc_standard_error = float(
                evaluated["same_author_auc"].std(ddof=1)
                / np.sqrt(len(evaluated))
            )
            auc_mean = float(evaluated["same_author_auc"].mean())
            row["mean_auc_mc_ci_lower"] = (
                auc_mean - 1.96 * auc_standard_error
            )
            row["mean_auc_mc_ci_upper"] = (
                auc_mean + 1.96 * auc_standard_error
            )
        else:
            row["pairing_rejection_upper_95"] = float("nan")
            row["mean_auc_mc_ci_lower"] = float("nan")
            row["mean_auc_mc_ci_upper"] = float("nan")
        row["studentized_pairing_rejection_rate"] = (
            float(
                evaluated["studentized_score_pairing_p"].le(0.01).mean()
            )
            if (
                len(evaluated)
                and evaluated["studentized_score_pairing_p"].notna().any()
            )
            else float("nan")
        )
        row["raw_pairing_rejection_rate"] = (
            float(
                evaluated["raw_score_pairing_p"].le(0.01).mean()
            )
            if (
                len(evaluated)
                and evaluated["raw_score_pairing_p"].notna().any()
            )
            else float("nan")
        )
        for prefix, column in (
            ("se_only", "se_only_pairing_p"),
            ("full_whitened", "full_whitened_pairing_p"),
        ):
            row[f"{prefix}_pairing_rejection_rate"] = (
                float(evaluated[column].le(0.01).mean())
                if (
                    len(evaluated)
                    and evaluated[column].notna().any()
                )
                else float("nan")
            )
            if len(evaluated) and evaluated[column].notna().any():
                valid_p = evaluated[column].dropna()
                rejected = int(valid_p.le(0.01).sum())
                row[f"{prefix}_pairing_rejection_upper_95"] = float(
                    beta.ppf(
                        0.95,
                        rejected + 1,
                        len(valid_p) - rejected,
                    )
                    if rejected < len(valid_p)
                    else 1.0
                )
            else:
                row[f"{prefix}_pairing_rejection_upper_95"] = float(
                    "nan"
                )
        rows.append(row)
    return pd.DataFrame(rows)


def _row(
    summary: pd.DataFrame,
    case_id: str,
    observation: str,
    estimator: str = "fixed_quota_primary",
) -> pd.Series:
    selected = summary.loc[
        summary["case_id"].eq(case_id)
        & summary["observation"].eq(observation)
        & summary["estimator"].eq(estimator)
    ]
    if len(selected) != 1:
        raise RuntimeError(
            f"expected one row for {case_id}/{observation}/{estimator}"
        )
    return selected.iloc[0]


def _decision(
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    gates = config["gates"]
    checks: dict[str, bool] = {}
    detail: dict[str, Any] = {}
    for observation in config["observations"]:
        null = _row(summary, "N0_null", observation)
        c1 = _row(summary, "N1_c1_only", observation)
        intercept = _row(summary, "N2_intercept_only", observation)
        signal = _row(summary, "S1_shared_c2_snr_0.50", observation)
        joint = _row(summary, "S2_joint_snr_0.50", observation)
        unstable = _row(summary, "A3_unstable_operator", observation)
        checks[f"{observation}_null_type1"] = bool(
            null["pairing_rejection_upper_95"]
            <= float(gates["maximum_null_false_positive_rate"])
        )
        checks[f"{observation}_c1_attack_active"] = bool(
            c1["mean_c1_same_author_auc"]
            >= float(gates["minimum_c1_attack_auc"])
        )
        checks[f"{observation}_c1_type1"] = bool(
            c1["pairing_rejection_upper_95"]
            <= float(gates["maximum_null_false_positive_rate"])
        )
        checks[f"{observation}_c1_c2_auc_null"] = bool(
            float(gates["minimum_c1_only_c2_auc"])
            <= c1["mean_same_author_auc"]
            <= float(gates["maximum_c1_only_c2_auc"])
        )
        checks[f"{observation}_c1_no_crosstalk"] = bool(
            c1["mean_q_to_response_cv_r2"]
            <= float(gates["maximum_c1_to_c2_cv_r2"])
        )
        checks[f"{observation}_intercept_type1"] = bool(
            intercept["pairing_rejection_upper_95"]
            <= float(gates["maximum_null_false_positive_rate"])
        )
        checks[f"{observation}_snr050_power"] = bool(
            signal["pairing_rejection_rate"]
            >= float(gates["minimum_snr_050_power"])
        )
        checks[f"{observation}_snr050_cosine"] = bool(
            signal["median_response_surface_cosine"]
            >= float(gates["minimum_snr_050_surface_cosine"])
        )
        checks[f"{observation}_snr050_auc"] = bool(
            signal["mean_same_author_auc"]
            >= float(gates["minimum_snr_050_same_author_auc"])
        )
        checks[f"{observation}_snr050_distance"] = bool(
            signal["mean_response_distance_spearman"]
            >= float(gates["minimum_snr_050_distance_spearman"])
        )
        checks[f"{observation}_joint_cosine_noninferior"] = bool(
            signal["median_response_surface_cosine"]
            - joint["median_response_surface_cosine"]
            <= float(gates["maximum_joint_cosine_drop"])
        )
        checks[f"{observation}_joint_auc_noninferior"] = bool(
            signal["mean_same_author_auc"]
            - joint["mean_same_author_auc"]
            <= float(gates["maximum_joint_auc_drop"])
        )
        checks[f"{observation}_unstable_type1"] = bool(
            unstable["pairing_rejection_upper_95"]
            <= float(gates["maximum_null_false_positive_rate"])
        )
        for label, null_row in (
            ("null", null),
            ("c1", c1),
            ("intercept", intercept),
            ("unstable", unstable),
        ):
            checks[f"{observation}_{label}_auc_mc_contains_half"] = bool(
                null_row["mean_auc_mc_ci_lower"] <= 0.50
                <= null_row["mean_auc_mc_ci_upper"]
            )
            checks[f"{observation}_{label}_auc_point_null"] = bool(
                float(gates["minimum_null_auc"])
                <= null_row["mean_same_author_auc"]
                <= float(gates["maximum_null_auc"])
            )
        checks[f"{observation}_ci_coverage"] = bool(
            float(gates["minimum_ci_coverage"])
            <= (
                signal["mean_binary_parametric_ci_coverage"]
                if observation == "binary"
                else signal["mean_response_pointwise_ci_coverage"]
            )
            <= float(gates["maximum_ci_coverage"])
        )
        powers = []
        for snr in (0.25, 0.50, 1.00):
            value = _row(
                summary,
                f"S1_shared_c2_snr_{snr:0.2f}",
                observation,
            )
            powers.append((snr, value["pairing_rejection_rate"]))
        detectable = next(
            (
                snr for snr, power in powers
                if power >= float(gates["minimum_snr_050_power"])
            ),
            float("inf"),
        )
        checks[f"{observation}_detectable_snr"] = bool(
            detectable <= float(gates["maximum_detectable_snr"])
        )
        if observation == "binary":
            checks["binary_numerical_auc_agreement"] = bool(
                signal["mean_binary_estimator_auc_gap"]
                <= float(gates["maximum_binary_estimator_gap"])
            )
            checks["binary_numerical_cosine_agreement"] = bool(
                signal["mean_binary_estimator_cosine_gap"]
                <= float(gates["maximum_binary_estimator_gap"])
            )
            checks["binary_inference_bias"] = bool(
                signal["mean_response_recovery_slope_bias"]
                <= float(gates["maximum_standardized_bias"])
            )
            checks["binary_inference_refusal"] = bool(
                signal["mean_inference_author_half_refusal_rate"]
                <= float(gates["maximum_inference_refusal_rate"])
            )
            checks["binary_inference_condition"] = bool(
                signal[
                    "mean_inference_maximum_information_condition_number"
                ]
                <= float(gates["maximum_information_condition_number"])
            )
            checks["binary_score_excludes_author_specific_se"] = bool(
                not config["binary_score_track"][
                    "uses_author_specific_standard_error"
                ]
                and config["binary_score_track"]["fixed_quota_only"]
            )
            checks["binary_permuted_numerator_leakage"] = bool(
                float(gates["minimum_null_auc"])
                <= signal["mean_permuted_numerator_same_author_auc"]
                <= float(gates["maximum_null_auc"])
            )
            checks["binary_full_whitening_noninferior"] = bool(
                abs(
                    signal["mean_full_whitened_same_author_auc"]
                    - signal["mean_same_author_auc"]
                )
                <= float(gates["maximum_whitening_auc_gap"])
            )
            checks["binary_full_whitening_null"] = bool(
                null["full_whitened_pairing_rejection_upper_95"]
                <= float(gates["maximum_null_false_positive_rate"])
            )
            checks["binary_full_whitening_intercept_null"] = bool(
                intercept["full_whitened_pairing_rejection_upper_95"]
                <= float(gates["maximum_null_false_positive_rate"])
            )
        detail[observation] = {
            "c1_attack_auc": float(c1["mean_c1_same_author_auc"]),
            "c1_only_c2_auc": float(c1["mean_same_author_auc"]),
            "snr050_power": float(signal["pairing_rejection_rate"]),
            "snr050_auc": float(signal["mean_same_author_auc"]),
            "snr050_surface_cosine": float(
                signal["median_response_surface_cosine"]
            ),
            "snr050_distance_spearman": float(
                signal["mean_response_distance_spearman"]
            ),
            "minimum_detectable_snr": float(detectable),
            "ci_coverage": float(
                signal["mean_binary_parametric_ci_coverage"]
                if observation == "binary"
                else signal["mean_response_pointwise_ci_coverage"]
            ),
            "analytic_ci_coverage": float(
                signal["mean_response_pointwise_ci_coverage"]
            ),
            "mean_standardized_bias": float(
                signal["mean_response_mean_standardized_bias"]
            ),
            "recovery_slope": float(
                signal["mean_response_recovery_slope"]
            ),
            "recovery_slope_bias": float(
                signal["mean_response_recovery_slope_bias"]
            ),
            "inference_author_half_refusal_rate": float(
                signal["mean_inference_author_half_refusal_rate"]
            ),
            "inference_maximum_information_condition_number": float(
                signal[
                    "mean_inference_maximum_information_condition_number"
                ]
            ),
            "moment_auc": float(
                signal["mean_moment_same_author_auc"]
            ),
            "moment_surface_cosine": float(
                signal["median_moment_response_surface_cosine"]
            ),
            "probability_incidence_auc": float(
                signal["mean_probability_incidence_same_author_auc"]
            ),
            "binary_estimator_auc_gap": float(
                signal["mean_binary_estimator_auc_gap"]
            ),
            "binary_estimator_cosine_gap": float(
                signal["mean_binary_estimator_cosine_gap"]
            ),
        }
    for case_id in (
        "A1_unique_conditions",
        "A2_overlap_0.25",
        "A2_overlap_0.50",
        "A4_private_stable_coordinates",
        "A5_half_shuffled_coordinates",
    ):
        for observation in config["observations"]:
            row = _row(summary, case_id, observation)
            checks[f"{observation}_{case_id}_refusal"] = bool(
                row["refusal_rate"]
                >= float(gates["minimum_refusal_rate"])
            )
    c1_information = _row(
        summary,
        "A6_c1_information_imbalance",
        "binary",
    )
    checks["binary_c1_information_imbalance_auc"] = bool(
        float(gates["minimum_null_auc"])
        <= c1_information["mean_same_author_auc"]
        <= float(gates["maximum_null_auc"])
    )
    checks["binary_c1_information_imbalance_type1"] = bool(
        c1_information["pairing_rejection_upper_95"]
        <= float(gates["maximum_null_false_positive_rate"])
    )
    checks["binary_c1_information_full_whitening_type1"] = bool(
        c1_information["full_whitened_pairing_rejection_upper_95"]
        <= float(gates["maximum_null_false_positive_rate"])
    )
    extreme = _row(summary, "A7_extreme_prevalence", "binary")
    checks["binary_extreme_prevalence_refusal"] = bool(
        extreme["mean_inference_author_half_refusal_rate"]
        >= float(gates["minimum_extreme_prevalence_refusal_rate"])
    )
    status = (
        "V8_BEHAVIOR_C2_PLANTED_WORLD_PASS"
        if all(checks.values())
        else "V8_BEHAVIOR_C2_STOP_ESTIMATOR"
    )
    return {
        "status": status,
        "checks": checks,
        "headline": detail,
        "claim_boundary": str(config["claim_boundary"]),
    }


def _report(decision: dict[str, Any], summary: pd.DataFrame) -> str:
    headline = summary.loc[
        summary["estimator"].eq("fixed_quota_primary")
        & summary["case_id"].isin([
            "N0_null",
            "N1_c1_only",
            "N2_intercept_only",
            "S1_shared_c2_snr_0.25",
            "S1_shared_c2_snr_0.50",
            "S1_shared_c2_snr_1.00",
            "S2_joint_snr_0.50",
            "A1_unique_conditions",
            "A2_overlap_0.50",
            "A2_overlap_0.75",
            "A3_unstable_operator",
            "A4_private_stable_coordinates",
            "A5_half_shuffled_coordinates",
        ])
    ][[
        "case_id",
        "observation",
        "numeric_output_rate",
        "mean_same_author_auc",
        "pairing_rejection_rate",
        "median_response_surface_cosine",
        "mean_response_distance_spearman",
        "mean_response_pointwise_ci_coverage",
        "mean_response_mean_standardized_bias",
        "mean_response_recovery_slope",
        "mean_response_recovery_slope_bias",
        "mean_c1_same_author_auc",
        "mean_moment_same_author_auc",
        "mean_inference_same_author_auc",
        "median_moment_response_surface_cosine",
        "mean_probability_incidence_same_author_auc",
        "mean_binary_estimator_auc_gap",
        "mean_binary_estimator_cosine_gap",
        "mean_binary_parametric_ci_coverage",
        "mean_inference_author_half_refusal_rate",
        "mean_inference_maximum_information_condition_number",
    ]]
    return f"""# SUICA V8 Behavior C2 Planted-World Report

Decision: `{decision["status"]}`

## Object

The battery tests recovery of an author-specific response surface under a
shared randomized factorial condition design. It separately attacks C1
selection, stable intercepts, incomplete overlap, unstable operators, and
private condition coordinates. No human construct or external label is used.

## Headline

{headline.to_markdown(index=False)}

## Decision Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    args = parser.parse_args()
    config = _read_json(args.config)
    repetitions = (
        int(args.repetitions)
        if args.repetitions is not None
        else int(config["repetitions"])
    )
    spec = C2SimulationSpec(**config["spec"])
    rows = []
    cases = _cases()
    jobs = (
        int(args.jobs)
        if args.jobs is not None
        else int(config.get("jobs", 1))
    )
    payloads = [
        (repetition, config, spec, cases)
        for repetition in range(repetitions)
    ]
    if jobs <= 1:
        for payload in payloads:
            rows.extend(_run_repetition(payload))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            for repetition_rows in executor.map(
                _run_repetition,
                payloads,
                chunksize=1,
            ):
                rows.extend(repetition_rows)
    seed_metrics = pd.DataFrame(rows)
    summary = _summary(seed_metrics)
    decision = _decision(summary, config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    seed_metrics.to_csv(args.output_dir / "seed_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "world_summary.csv", index=False)
    _write_json(args.output_dir / "decision.json", decision)
    resolved = {
        **config,
        "executed_repetitions": repetitions,
        "executed_jobs": jobs,
    }
    _write_json(args.output_dir / "config.resolved.json", resolved)
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
            Path(__file__),
            ROOT / "suica_core" / "v8_behavior_c2.py",
        ],
        estimand_id="V8-I14-behavior-c2-planted-world",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
