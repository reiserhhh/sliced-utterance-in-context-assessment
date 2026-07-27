#!/usr/bin/env python3
"""Run the SUICA V3.7G observable reliability-spectrum experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    sha256_file,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_reliability_spectrum import (  # noqa: E402
    ReliabilitySpectrumWorldSpec,
    apply_spectrum_operator,
    default_spectrum_candidates,
    estimate_external_origin,
    fit_reliability_spectrum,
    minimum_risk_hard_candidate,
    model_assisted_conditional_region,
    normalized_mse,
    one_se_hard_candidate,
    paired_channel_metrics,
    select_spectrum_candidate,
    simulate_reliability_spectrum_world,
    spectrum_operator,
    unresolved_channel,
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


def _fingerprint(values: np.ndarray) -> str:
    return hashlib.sha256(
        np.asarray(values, dtype=float).tobytes()
    ).hexdigest()


def _direction_cosine(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    return float(
        np.dot(x, y)
        / max(np.linalg.norm(x) * np.linalg.norm(y), 1e-12)
    )


def _score_region_coverage(
    region: dict[str, Any],
    truth: np.ndarray,
) -> float:
    """Score a fitted region without exposing truth to its construction."""
    error = (
        np.asarray(truth, dtype=float)
        - np.asarray(region["center"], dtype=float)
    )
    standardized = (
        error @ np.asarray(region["inverse_root"], dtype=float).T
    )
    statistic = np.sum(standardized**2, axis=1)
    return float(np.mean(statistic <= float(region["threshold"])))


def _interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int = 10_000,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return {
            "mean": float("nan"),
            "lower95": float("nan"),
            "upper95": float("nan"),
        }
    indices = rng.integers(
        0,
        len(vector),
        size=(draws, len(vector)),
    )
    means = vector[indices].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
    }


def _candidate_lookup(
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {
        str(candidate["name"]): candidate
        for candidate in candidates
    }


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    world_sequences = root.spawn(len(config["worlds"]))
    candidates = default_spectrum_candidates(
        int(config["dimension"])
    )
    lookup = _candidate_lookup(candidates)
    metric_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    seeds: list[int] = []
    for world_index, world_name in enumerate(config["worlds"]):
        latent_parent, event_parent, selection_parent, interval_parent = (
            world_sequences[world_index].spawn(4)
        )
        latent_seed = _uint64(latent_parent)
        seeds.append(latent_seed)
        event_sequences = event_parent.spawn(len(config["event_budgets"]))
        selection_sequences = selection_parent.spawn(
            len(config["event_budgets"])
        )
        interval_sequences = interval_parent.spawn(
            len(config["event_budgets"])
        )
        for budget_index, event_budget in enumerate(
            config["event_budgets"]
        ):
            event_seed = _uint64(event_sequences[budget_index])
            selection_seed = _uint64(
                selection_sequences[budget_index]
            )
            interval_seed = _uint64(
                interval_sequences[budget_index]
            )
            seeds.extend([event_seed, selection_seed, interval_seed])
            world = simulate_reliability_spectrum_world(
                latent_seed=latent_seed,
                event_seed=event_seed,
                spec=ReliabilitySpectrumWorldSpec(
                    world=str(world_name),
                    dimension=int(config["dimension"]),
                    sessions=int(config["sessions"]),
                    event_budget=int(event_budget),
                    reference_authors=int(
                        config["reference_authors"]
                    ),
                    calibration_authors=int(
                        config["calibration_authors"]
                    ),
                    interval_authors=int(
                        config["interval_authors"]
                    ),
                    evaluation_authors=int(
                        config["evaluation_authors"]
                    ),
                    stable_rms=float(config["stable_rms"]),
                    event_rms_at_64=float(
                        config["event_rms_at_64"]
                    ),
                    state_rms=float(config["state_rms"]),
                    state_correlation=float(
                        config["state_correlation"]
                    ),
                    slow_variance_exponent=float(
                        config["slow_variance_exponent"]
                    ),
                    population_shift_rms=float(
                        config["population_shift_rms"]
                    ),
                ),
            )
            panels = world["panels"]
            truths = world["truths"]
            external_zero = estimate_external_origin(
                panels["reference"]
            )
            selected_candidate, selection_table = (
                select_spectrum_candidate(
                    panels["calibration"],
                    external_zero=external_zero,
                    candidates=candidates,
                    folds=int(config["selection_folds"]),
                    seed=selection_seed,
                    noise_shrinkage=float(
                        config["noise_shrinkage"]
                    ),
                )
            )
            spectrum = fit_reliability_spectrum(
                panels["calibration"][:, 0],
                panels["calibration"][:, 1],
                external_zero=external_zero,
                noise_shrinkage=float(config["noise_shrinkage"]),
            )
            selected_fit = spectrum_operator(
                spectrum,
                selected_candidate,
            )
            hard_name = minimum_risk_hard_candidate(selection_table)
            hard_fit = spectrum_operator(
                spectrum,
                lookup[hard_name],
            )
            one_se_hard_name = one_se_hard_candidate(selection_table)
            one_se_hard_fit = spectrum_operator(
                spectrum,
                lookup[one_se_hard_name],
            )
            evaluation_profile = panels["evaluation"][:, :2].mean(
                axis=1
            )
            selected_score = apply_spectrum_operator(
                evaluation_profile,
                selected_fit,
            )
            hard_score = apply_spectrum_operator(
                evaluation_profile,
                hard_fit,
            )
            one_se_hard_score = apply_spectrum_operator(
                evaluation_profile,
                one_se_hard_fit,
            )
            truth = truths["evaluation"]
            true_zero = np.asarray(world["true_zero"])
            selected_nmse = normalized_mse(
                selected_score,
                truth,
                origin=true_zero,
            )
            hard_nmse = normalized_mse(
                hard_score,
                truth,
                origin=true_zero,
            )
            one_se_hard_nmse = normalized_mse(
                one_se_hard_score,
                truth,
                origin=true_zero,
            )
            raw_nmse = normalized_mse(
                evaluation_profile,
                truth,
                origin=true_zero,
            )
            scorer_nmse: dict[str, float] = {}
            fitted_by_name: dict[str, dict[str, Any]] = {}
            for candidate in candidates:
                fitted = spectrum_operator(spectrum, candidate)
                name = str(candidate["name"])
                fitted_by_name[name] = fitted
                estimate = apply_spectrum_operator(
                    evaluation_profile,
                    fitted,
                )
                scorer_nmse[name] = normalized_mse(
                    estimate,
                    truth,
                    origin=true_zero,
                )
            oracle_name = min(
                scorer_nmse,
                key=scorer_nmse.__getitem__,
            )
            oracle_nmse = float(scorer_nmse[oracle_name])
            design_interval_allowed = bool(
                world["design"]["interval_claim_allowed"]
            )
            reliable_score_available = bool(
                float(selected_fit["effective_df"])
                >= float(config["minimum_interval_effective_df"])
            )
            interval_target = bool(
                int(event_budget) == int(config["primary_budget"])
                and (
                    str(world_name) in set(config["coverage_worlds"])
                    or str(world_name)
                    in set(config["interval_secondary_worlds"])
                )
            )
            region_kwargs = {
                "tolerance_confidence": float(
                    config["tolerance_confidence"]
                ),
                "bootstrap_replicates": int(
                    config["interval_bootstrap_replicates"]
                ),
                "bootstrap_seed": interval_seed,
                "eigen_floor": float(config["interval_eigen_floor"]),
                "minimum_fit_per_dimension": float(
                    config["minimum_fit_per_dimension"]
                ),
                "maximum_negative_mass_ratio": float(
                    config["maximum_negative_mass_ratio"]
                ),
                "maximum_condition": float(
                    config["maximum_interval_condition"]
                ),
                "minimum_bootstrap_replicates": int(
                    config["minimum_interval_bootstrap_replicates"]
                ),
                "minimum_bootstrap_valid_rate": float(
                    config["minimum_bootstrap_valid_rate"]
                ),
                "maximum_bootstrap_radius_cv": float(
                    config["maximum_bootstrap_radius_cv"]
                ),
                "maximum_bootstrap_radius_quantile_ratio": float(
                    config["maximum_bootstrap_radius_quantile_ratio"]
                ),
                "minimum_pair_swap_radius_ratio": float(
                    config["minimum_pair_swap_radius_ratio"]
                ),
                "maximum_pair_swap_radius_ratio": float(
                    config["maximum_pair_swap_radius_ratio"]
                ),
            }
            if (
                design_interval_allowed
                and reliable_score_available
                and interval_target
            ):
                region = model_assisted_conditional_region(
                    interval_sessions=panels["interval"],
                    evaluation_sessions=panels["evaluation"],
                    fitted=selected_fit,
                    level=float(config["confidence_level"]),
                    **region_kwargs,
                )
                interval_claim_allowed = bool(
                    region["status"]
                    == "ME_TOLERANCE_BALL_95_95"
                )
                interval_claim_status = str(region["status"])
            else:
                interval_claim_allowed = False
                interval_claim_status = (
                    str(world["design"]["interval_claim_status"])
                    if not design_interval_allowed
                    else (
                        "UNRESOLVED_NO_RELIABLE_SCORE_CHANNEL"
                        if not reliable_score_available
                        else "INTERVAL_NOT_REGISTERED_FOR_CELL"
                    )
                )
                region = {}
            if interval_claim_allowed:
                conditional_coverage = _score_region_coverage(
                    region, truth
                )
                conditional_quadratic_threshold = float(
                    region["threshold"]
                )
                conditional_tolerance_radius = float(
                    region["tolerance_radius"]
                )
                conditional_raw_proxy_radius = float(
                    region["raw_proxy_tolerance_radius"]
                )
                bias_corrected_nmse = normalized_mse(
                    np.asarray(region["center"]),
                    truth,
                    origin=true_zero,
                )
                refused_counterfactual_coverage = np.nan
            else:
                conditional_coverage = np.nan
                conditional_quadratic_threshold = np.nan
                conditional_tolerance_radius = np.nan
                conditional_raw_proxy_radius = np.nan
                bias_corrected_nmse = np.nan
                refused_counterfactual_coverage = np.nan
            channel = paired_channel_metrics(
                panels["evaluation"],
                fitted=selected_fit,
                neighbor_count=int(config["neighbor_count"]),
            )
            unresolved = unresolved_channel(
                evaluation_profile,
                selected_fit,
            )
            reconstruction_error = float(np.max(np.abs(
                selected_score + unresolved - evaluation_profile
            )))
            target_shift = np.asarray(
                world["population_shift"],
                dtype=float,
            )
            transported_shift = (
                np.asarray(selected_fit["operator"], dtype=float)
                @ target_shift
            )
            shift_direction = (
                _direction_cosine(transported_shift, target_shift)
                if str(world_name) == "reference_shift_dense"
                else np.nan
            )
            shift_amplitude = (
                float(
                    np.linalg.norm(transported_shift)
                    / max(np.linalg.norm(target_shift), 1e-12)
                )
                if str(world_name) == "reference_shift_dense"
                else np.nan
            )
            selected_row = selection_table[
                selection_table["selected"]
            ].iloc[0]
            metric_rows.append({
                "repetition": repetition,
                "spawn_key": json.dumps(spawn_key),
                "world": str(world_name),
                "event_budget": int(event_budget),
                "latent_seed": latent_seed,
                "event_seed": event_seed,
                "selection_seed": selection_seed,
                "interval_seed": interval_seed,
                "truth_fingerprint": _fingerprint(truth),
                "selected_name": str(selected_candidate["name"]),
                "selected_family": str(
                    selected_candidate["family"]
                ),
                "hard_name": hard_name,
                "one_se_hard_name": one_se_hard_name,
                "oracle_name": oracle_name,
                "selected_cv_loss": float(selected_row["mean_loss"]),
                "selected_effective_df": float(
                    selected_fit["effective_df"]
                ),
                "hard_effective_df": float(
                    hard_fit["effective_df"]
                ),
                "one_se_hard_effective_df": float(
                    one_se_hard_fit["effective_df"]
                ),
                "selected_nmse": selected_nmse,
                "hard_nmse": hard_nmse,
                "one_se_hard_nmse": one_se_hard_nmse,
                "raw_nmse": raw_nmse,
                "oracle_nmse": oracle_nmse,
                "selected_excess_vs_hard": (
                    selected_nmse - hard_nmse
                ),
                "selected_regret": selected_nmse - oracle_nmse,
                "selected_reduction_vs_hard": (
                    (hard_nmse - selected_nmse)
                    / max(hard_nmse, 1e-12)
                ),
                "selected_reduction_vs_one_se_hard": (
                    (one_se_hard_nmse - selected_nmse)
                    / max(one_se_hard_nmse, 1e-12)
                ),
                "bias_corrected_nmse": bias_corrected_nmse,
                "conditional_coverage": conditional_coverage,
                "conditional_quadratic_threshold": (
                    conditional_quadratic_threshold
                ),
                "conditional_tolerance_radius": (
                    conditional_tolerance_radius
                ),
                "conditional_raw_proxy_radius": (
                    conditional_raw_proxy_radius
                ),
                "refused_counterfactual_coverage": (
                    refused_counterfactual_coverage
                ),
                "interval_claim_allowed": interval_claim_allowed,
                "interval_claim_status": interval_claim_status,
                "interval_negative_mass_ratio": float(
                    region.get("negative_mass_ratio", np.nan)
                ),
                "interval_psd_truncation_trace_ratio": float(
                    region.get(
                        "psd_truncation_trace_ratio",
                        np.nan,
                    )
                ),
                "interval_condition_number": float(
                    region.get("condition_number", np.nan)
                ),
                "interval_effective_rank": float(
                    region.get("effective_rank", np.nan)
                ),
                "interval_minimum_axis": float(
                    region.get("minimum_axis", np.nan)
                ),
                "interval_maximum_axis": float(
                    region.get("maximum_axis", np.nan)
                ),
                "interval_log_volume_proxy": float(
                    region.get("log_volume_proxy", np.nan)
                ),
                "interval_bootstrap_valid_rate": float(
                    region.get("bootstrap_valid_rate", np.nan)
                ),
                "interval_bootstrap_radius_cv": float(
                    region.get(
                        "bootstrap_radius_cv",
                        np.nan,
                    )
                ),
                "interval_bootstrap_radius_quantile_ratio": float(
                    region.get(
                        "bootstrap_radius_quantile_ratio",
                        np.nan,
                    )
                ),
                "interval_pair_swap_radius_ratio": float(
                    region.get("pair_swap_radius_ratio", np.nan)
                ),
                "interval_mapping_operator_norm": float(
                    region.get("mapping_operator_norm", np.nan)
                ),
                "interval_radius_scale_ratio": float(
                    region.get("radius_scale_ratio", np.nan)
                ),
                "interval_radius_to_raw_proxy_ratio": float(
                    region.get(
                        "radius_to_raw_proxy_ratio",
                        np.nan,
                    )
                ),
                "interval_tolerance_order": float(
                    region.get("tolerance_order", np.nan)
                ),
                "interval_achieved_tolerance_confidence": float(
                    region.get(
                        "achieved_tolerance_confidence",
                        np.nan,
                    )
                ),
                "reconstruction_max_abs_error": (
                    reconstruction_error
                ),
                "external_zero_error": float(
                    np.linalg.norm(external_zero - true_zero)
                ),
                "population_shift_operator_direction": shift_direction,
                "population_shift_operator_amplitude": shift_amplitude,
                **channel,
            })
            table_lookup = selection_table.set_index("name")
            for candidate in candidates:
                name = str(candidate["name"])
                candidate_rows.append({
                    "repetition": repetition,
                    "world": str(world_name),
                    "event_budget": int(event_budget),
                    "name": name,
                    "family": str(candidate["family"]),
                    "cv_loss": float(
                        table_lookup.loc[name, "mean_loss"]
                    ),
                    "cv_se": float(
                        table_lookup.loc[name, "se_loss"]
                    ),
                    "effective_df": float(
                        fitted_by_name[name]["effective_df"]
                    ),
                    "scorer_nmse": float(scorer_nmse[name]),
                    "selected": name
                    == str(selected_candidate["name"]),
                    "oracle_best": name == oracle_name,
                })
    return metric_rows, candidate_rows, seeds


def _effects(
    metrics: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    rng = np.random.default_rng(int(config["_active_seed"]) ^ 0x37A)
    primary = metrics[
        metrics["event_budget"] == int(config["primary_budget"])
    ]

    def world(name: str) -> pd.DataFrame:
        return primary[primary["world"] == name]

    exact = world("exact_rank12")
    dense = world("dense_tail48")
    broken = world("broken_spectrum48")
    permutation = world("author_permutation")
    state = metrics[
        (metrics["world"] == "dense_state_alias")
        & (
            metrics["event_budget"]
            == int(config["state_floor_budget"])
        )
    ]
    shift = metrics[
        (metrics["world"] == "reference_shift_dense")
        & (
            metrics["event_budget"]
            == int(config["shift_audit_budget"])
        )
    ]
    identifiable_names = set(config["coverage_worlds"])
    coverage = primary[
        primary["world"].isin(identifiable_names)
    ]
    core_interval_availability = float(
        coverage["interval_claim_allowed"].astype(bool).mean()
    )
    coverage_by_world = {
        str(name): _interval(
            group["conditional_coverage"].to_numpy(),
            rng=rng,
        )
        for name, group in coverage.groupby("world")
    }
    regret_by_rep = (
        primary[
            ~primary["world"].isin(
                ["author_permutation", "dense_state_alias"]
            )
        ]
        .groupby("repetition")["selected_regret"]
        .max()
    )
    return {
        "exact_excess_vs_hard": _interval(
            exact["selected_excess_vs_hard"].to_numpy(),
            rng=rng,
        ),
        "dense_reduction_vs_hard": _interval(
            dense["selected_reduction_vs_hard"].to_numpy(),
            rng=rng,
        ),
        "broken_reduction_vs_hard": _interval(
            broken["selected_reduction_vs_hard"].to_numpy(),
            rng=rng,
        ),
        "worst_world_regret": _interval(
            regret_by_rep.to_numpy(),
            rng=rng,
        ),
        "permutation_effective_df": _interval(
            permutation["selected_effective_df"].to_numpy(),
            rng=rng,
        ),
        "permutation_residual_auc": _interval(
            permutation[
                "residual_same_author_auc"
            ].to_numpy(),
            rng=rng,
        ),
        "conditional_coverage_by_world": coverage_by_world,
        "core_interval_availability": core_interval_availability,
        "conditional_coverage_min_lower95": float(min(
            item["lower95"] for item in coverage_by_world.values()
        )),
        "conditional_coverage_max_upper95": float(max(
            item["upper95"] for item in coverage_by_world.values()
        )),
        "state_alias_nmse": _interval(
            state["selected_nmse"].to_numpy(),
            rng=rng,
        ),
        "state_alias_refusal_rate": float(
            (~state["interval_claim_allowed"].astype(bool)).mean()
        ),
        "informative_precision_coverage": float(
            world("informative_precision_dense")[
                "conditional_coverage"
            ].mean()
        ),
        "reference_shift_refusal_rate": float(
            (
                ~world("reference_shift_dense")[
                    "interval_claim_allowed"
                ].astype(bool)
            ).mean()
        ),
        "population_shift_direction": _interval(
            shift["population_shift_operator_direction"].to_numpy(),
            rng=rng,
        ),
        "population_shift_amplitude": _interval(
            shift["population_shift_operator_amplitude"].to_numpy(),
            rng=rng,
        ),
        "exact_hard_selection_rate": float(
            (exact["selected_family"] == "hard").mean()
        ),
        "dense_smooth_selection_rate": float(
            (dense["selected_family"] != "hard").mean()
        ),
        "maximum_reconstruction_error": float(
            metrics["reconstruction_max_abs_error"].max()
        ),
        "conditional_interval_size": {
            "mean_maximum_axis": float(
                coverage["interval_maximum_axis"].mean()
            ),
            "mean_effective_rank": float(
                coverage["interval_effective_rank"].mean()
            ),
            "mean_log_volume_proxy": float(
                coverage["interval_log_volume_proxy"].mean()
            ),
            "mean_radius_scale_ratio": float(
                coverage["interval_radius_scale_ratio"].mean()
            ),
            "mean_radius_to_raw_proxy_ratio": float(
                coverage[
                    "interval_radius_to_raw_proxy_ratio"
                ].mean()
            ),
        },
    }


def _integrity(
    metrics: pd.DataFrame,
    candidates: pd.DataFrame,
    seeds: list[int],
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    expected = (
        int(config["_active_repetitions"])
        * len(config["worlds"])
        * len(config["event_budgets"])
    )
    candidate_count = len(default_spectrum_candidates(
        int(config["dimension"])
    ))
    required = [
        "selected_nmse",
        "hard_nmse",
        "oracle_nmse",
        "selected_regret",
        "selected_effective_df",
        "residual_hard_neighbor_auc",
        "reconstruction_max_abs_error",
    ]
    allowed = metrics["interval_claim_allowed"].astype(bool)
    allowed_intervals_finite = bool(np.isfinite(
        metrics.loc[
            allowed,
            [
                "conditional_coverage",
                "conditional_quadratic_threshold",
                "conditional_tolerance_radius",
                "conditional_raw_proxy_radius",
                "interval_negative_mass_ratio",
                "interval_psd_truncation_trace_ratio",
                "interval_condition_number",
                "interval_effective_rank",
                "interval_minimum_axis",
                "interval_maximum_axis",
                "interval_log_volume_proxy",
                "interval_bootstrap_valid_rate",
                "interval_bootstrap_radius_cv",
                "interval_bootstrap_radius_quantile_ratio",
                "interval_pair_swap_radius_ratio",
                "interval_mapping_operator_norm",
                "interval_radius_scale_ratio",
                "interval_radius_to_raw_proxy_ratio",
                "interval_tolerance_order",
                "interval_achieved_tolerance_confidence",
            ],
        ].to_numpy(dtype=float)
    ).all())
    refused_intervals_absent = bool(
        metrics.loc[
            ~allowed,
            [
                "conditional_coverage",
                "conditional_quadratic_threshold",
                "conditional_tolerance_radius",
                "conditional_raw_proxy_radius",
            ],
        ].isna().all().all()
    )
    truth_consistency = (
        metrics.groupby(["repetition", "world"])[
            "truth_fingerprint"
        ].nunique().eq(1).all()
    )
    return {
        "numeric": bool(
            np.isfinite(metrics[required].to_numpy(dtype=float)).all()
            and allowed_intervals_finite
            and np.isfinite(candidates[
                ["cv_loss", "cv_se", "effective_df", "scorer_nmse"]
            ].to_numpy(dtype=float)).all()
        ),
        "metric_rows": int(len(metrics)),
        "expected_metric_rows": int(expected),
        "candidate_rows": int(len(candidates)),
        "expected_candidate_rows": int(expected * candidate_count),
        "seed_count": int(len(seeds)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "truth_constant_across_budgets": bool(truth_consistency),
        "refused_intervals_absent": refused_intervals_absent,
        "single_selected_per_cell": bool(
            candidates.groupby(
                ["repetition", "world", "event_budget"]
            )["selected"].sum().eq(1).all()
        ),
        "single_oracle_per_cell": bool(
            candidates.groupby(
                ["repetition", "world", "event_budget"]
            )["oracle_best"].sum().eq(1).all()
        ),
    }


def _decision(
    *,
    effects: dict[str, Any],
    integrity: dict[str, Any],
    config: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    if mode != "confirmation":
        return {
            "status": (
                "V8_RELIABILITY_SPECTRUM_V37G_"
                + ("SMOKE_PASS" if mode == "smoke" else "DISCOVERY_READY")
            ),
            "effects": effects,
            "integrity": integrity,
            "claim_boundary": config["claim_boundary"],
        }
    gates = config["gates"]
    checks = {
        "numeric_integrity": integrity["numeric"],
        "row_count": (
            integrity["metric_rows"]
            == integrity["expected_metric_rows"]
            and integrity["candidate_rows"]
            == integrity["expected_candidate_rows"]
        ),
        "seed_uniqueness": integrity["seed_uniqueness"],
        "truth_constant_across_budgets": integrity[
            "truth_constant_across_budgets"
        ],
        "refused_intervals_absent": integrity[
            "refused_intervals_absent"
        ],
        "single_selection": (
            integrity["single_selected_per_cell"]
            and integrity["single_oracle_per_cell"]
        ),
        "exact_noninferiority": (
            effects["exact_excess_vs_hard"]["upper95"]
            <= gates["maximum_exact_excess_nmse"]
        ),
        "dense_improvement": (
            effects["dense_reduction_vs_hard"]["lower95"]
            >= gates["minimum_dense_reduction"]
        ),
        "regret": (
            effects["worst_world_regret"]["upper95"]
            <= gates["maximum_worst_world_regret"]
        ),
        "permutation_dimension": (
            effects["permutation_effective_df"]["upper95"]
            <= gates["maximum_permutation_effective_df"]
        ),
        "permutation_residual": (
            gates["minimum_permutation_residual_auc"]
            <= effects["permutation_residual_auc"]["lower95"]
            and effects["permutation_residual_auc"]["upper95"]
            <= gates["maximum_permutation_residual_auc"]
        ),
        "coverage_lower": (
            effects["conditional_coverage_min_lower95"]
            >= gates["minimum_core_coverage"]
        ),
        "coverage_upper": (
            effects["conditional_coverage_max_upper95"]
            <= gates["maximum_core_coverage"]
        ),
        "core_interval_availability": (
            effects["core_interval_availability"] == 1.0
        ),
        "state_alias_refusal": (
            effects["state_alias_refusal_rate"] == 1.0
        ),
        "reference_shift_refusal": (
            effects["reference_shift_refusal_rate"] == 1.0
        ),
        "shift_direction": (
            effects["population_shift_direction"]["lower95"]
            >= gates["minimum_shift_direction"]
        ),
        "shift_amplitude": (
            gates["minimum_shift_amplitude"]
            <= effects["population_shift_amplitude"]["lower95"]
            and effects["population_shift_amplitude"]["upper95"]
            <= gates["maximum_shift_amplitude"]
        ),
        "broken_improvement": (
            effects["broken_reduction_vs_hard"]["lower95"]
            >= gates["minimum_broken_reduction"]
        ),
        "information_conservation": (
            effects["maximum_reconstruction_error"]
            <= gates["maximum_reconstruction_error"]
        ),
    }
    integrity_keys = [
        "numeric_integrity",
        "row_count",
        "seed_uniqueness",
        "truth_constant_across_budgets",
        "refused_intervals_absent",
        "single_selection",
        "information_conservation",
    ]
    estimator_keys = [
        "exact_noninferiority",
        "dense_improvement",
        "broken_improvement",
        "regret",
    ]
    controls = [
        "permutation_dimension",
        "permutation_residual",
        "shift_direction",
        "shift_amplitude",
    ]
    uncertainty = [
        "coverage_lower",
        "coverage_upper",
        "core_interval_availability",
        "state_alias_refusal",
        "reference_shift_refusal",
    ]
    if not all(checks[key] for key in integrity_keys):
        status = "V8_RELIABILITY_SPECTRUM_V37G_STOP_INTEGRITY"
    elif not all(checks[key] for key in controls):
        status = "V8_RELIABILITY_SPECTRUM_V37G_STOP_CONTROLS"
    elif not all(checks[key] for key in uncertainty):
        status = "V8_RELIABILITY_SPECTRUM_V37G_STOP_UNCERTAINTY"
    elif all(checks[key] for key in estimator_keys):
        status = (
            "V8_RELIABILITY_SPECTRUM_V37G_"
            "PASS_CORE_OBSERVABLE_SPECTRUM"
        )
    else:
        status = (
            "V8_RELIABILITY_SPECTRUM_V37G_"
            "REFUTE_UNIVERSAL_ESTIMATOR"
        )
    informative_coverage = effects["informative_precision_coverage"]
    secondary_findings = {
        "informative_precision_interval": (
            "PASS_CORE_WITH_HETERO_PRECISION_LIMIT"
            if informative_coverage <= 0.98
            else "INTERVAL_INEFFICIENT_OVER_COVERAGE"
        ),
        "reference_shift_interval": (
            "PASS_CORE_REFUSE_SHIFT_INTERVAL"
            if effects["reference_shift_refusal_rate"] == 1.0
            else "STOP_UNCALIBRATED_SHIFT_INTERVAL_CLAIM"
        ),
        "state_alias_interval": (
            "STOP_FALSE_CERTAINTY_STATE_ALIAS"
            if effects["state_alias_refusal_rate"] < 1.0
            else "PASS_CORE_REFUSE_STATE_ALIAS_INTERVAL"
        ),
    }
    return {
        "status": status,
        "checks": {key: bool(value) for key, value in checks.items()},
        "secondary_findings": secondary_findings,
        "effects": effects,
        "integrity": integrity,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_parent(config: dict[str, Any]) -> dict[str, str]:
    parent = config["required_parent_seal"]
    got = sha256_file(ROOT / parent["path"])
    if got != parent["sha256"]:
        raise RuntimeError("V3.7F parent seal mismatch")
    return {"status": "V37F_PARENT_SEAL_PASS", "sha256": got}


def _verify_own_seal(path: Path, *, mode: str) -> dict[str, str]:
    if mode != "confirmation":
        return {"status": "OWN_SEAL_NOT_REQUIRED"}
    if not path.is_file():
        raise RuntimeError("confirmation requires V3.7G seal")
    seal = _read(path)
    failures = [
        relative
        for relative, expected in seal["files"].items()
        if not (ROOT / relative).is_file()
        or sha256_file(ROOT / relative) != expected
    ]
    if failures:
        raise RuntimeError(f"V3.7G seal mismatch: {failures}")
    return {
        "status": "V37G_PROSPECTIVE_SEAL_PASS",
        "sha256": sha256_file(path),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
    selection: pd.DataFrame,
) -> str:
    return f"""# V8 Reliability Spectrum V3.7G

Decision: `{decision["status"]}`

## Integrity

```json
{json.dumps(decision["integrity"], indent=2)}
```

## Effects

```json
{json.dumps(decision["effects"], indent=2)}
```

## World summary

{summary.to_markdown(index=False)}

## Selection frequencies

{selection.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT
        / "configs/v8_reliability_spectrum_v37g_discovery.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT / "configs/v8_reliability_spectrum_v37g_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "results/v8_reliability_spectrum/v37g_discovery",
    )
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery", "confirmation"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    if args.mode == "smoke":
        config["_active_seed"] = int(config["smoke_seed"])
        repetitions = 1
    elif args.mode == "confirmation":
        config["_active_seed"] = int(config["canonical_seed"])
        repetitions = int(config["repetitions"])
    else:
        config["_active_seed"] = int(config["seed"])
        repetitions = int(config["repetitions"])
    config["_active_repetitions"] = repetitions
    parent = _verify_parent(config)
    own_seal = _verify_own_seal(args.seal, mode=args.mode)
    root = np.random.SeedSequence(int(config["_active_seed"]))
    spawn_keys = [
        tuple(child.spawn_key) for child in root.spawn(repetitions)
    ]
    payloads = [
        (config, repetition, spawn_keys[repetition])
        for repetition in range(repetitions)
    ]
    if args.mode == "smoke":
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"])
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    metric_rows = [row for rows, _, _ in nested for row in rows]
    candidate_rows = [row for _, rows, _ in nested for row in rows]
    seeds = [seed for _, _, values in nested for seed in values]
    metrics = pd.DataFrame(metric_rows)
    candidates = pd.DataFrame(candidate_rows)
    summary = (
        metrics.groupby(["world", "event_budget"], as_index=False)
        .mean(numeric_only=True)
    )
    selection = (
        metrics.groupby(
            ["world", "event_budget", "selected_family"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "count"})
    )
    effects = _effects(metrics, config=config)
    integrity = _integrity(
        metrics,
        candidates,
        seeds,
        config=config,
    )
    decision = _decision(
        effects=effects,
        integrity=integrity,
        config=config,
        mode=args.mode,
    )
    decision["parent_seal"] = parent
    decision["prospective_seal"] = own_seal
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    candidates.to_csv(
        args.output_dir / "candidate_metrics.csv",
        index=False,
    )
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    selection.to_csv(
        args.output_dir / "selection_summary.csv",
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
        _report(decision, summary, selection),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[ROOT / config["required_parent_seal"]["path"]],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_reliability_spectrum.py",
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
        "status": decision["status"],
        "rows": len(metrics),
        "candidate_rows": len(candidates),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
