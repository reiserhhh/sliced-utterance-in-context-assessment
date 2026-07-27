#!/usr/bin/env python3
"""Run SUICA V3.7E adaptive-rank and fixed-reference experiments."""
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
from suica_core.v8_adaptive_rank_reference import (  # noqa: E402
    AdaptiveReferenceWorldSpec,
    apply_opportunity_shift,
    apply_population_shift,
    cross_validated_rank_selection,
    estimate_standardized_profile,
    population_shift_direction,
    recovery_identity_state,
    score_rank,
    simulate_adaptive_reference_world,
    subset_authors,
    true_standardized_profile,
    with_event_budget,
)
from suica_core.v8_author_routing_operator import (  # noqa: E402
    fit_reference_router,
)
from suica_core.v8_group_free_routing_transport import (  # noqa: E402
    apply_group_free_denoiser,
    resample_routing_counts,
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
    return hashlib.sha256(np.asarray(values).tobytes()).hexdigest()


def _prefixed(
    prefix: str,
    values: dict[str, float | int | bool],
) -> dict[str, float | int | bool]:
    return {f"{prefix}_{key}": value for key, value in values.items()}


def _direction_cosine(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    return float(
        np.dot(x, y)
        / max(np.linalg.norm(x) * np.linalg.norm(y), 1e-12)
    )


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> list[dict[str, Any]]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    latent_sequence, permutation_sequence, event_parent = root.spawn(3)
    latent_seed = _uint64(latent_sequence)
    total_authors = (
        int(config["reference_authors"])
        + int(config["calibration_authors"])
        + int(config["evaluation_authors"])
    )
    order = np.random.default_rng(
        permutation_sequence,
    ).permutation(total_authors)
    n_reference = int(config["reference_authors"])
    n_calibration = int(config["calibration_authors"])
    reference_indices = order[:n_reference]
    calibration_indices = order[
        n_reference : n_reference + n_calibration
    ]
    evaluation_indices = order[n_reference + n_calibration :]
    discovery = np.arange(int(config["discovery_contexts"]))
    candidate_ranks = [int(value) for value in config["candidate_ranks"]]
    rows: list[dict[str, Any]] = []
    event_roots = iter(event_parent.spawn(
        len(config["spectra"])
        * len(config["latent_ranks"])
        * len(config["event_budgets"])
    ))
    for spectrum in config["spectra"]:
        for latent_rank in config["latent_ranks"]:
            maximum = simulate_adaptive_reference_world(
                seed=latent_seed,
                spec=AdaptiveReferenceWorldSpec(
                    authors=total_authors,
                    latent_rank=int(latent_rank),
                    maximum_latent_rank=max(config["latent_ranks"]),
                    events_per_context_session=max(
                        config["event_budgets"]
                    ),
                    author_rms=float(config["author_rms"]),
                    author_context_rms=float(
                        config["author_context_rms"]
                    ),
                    spectrum=str(spectrum),
                    spectrum_decay=float(config["spectrum_decay"]),
                    discovery_contexts=int(
                        config["discovery_contexts"]
                    ),
                    confirmation_contexts=int(
                        config["confirmation_contexts"]
                    ),
                    extrapolation_contexts=int(
                        config["extrapolation_contexts"]
                    ),
                ),
            )
            probability_fingerprint = _fingerprint(
                maximum["probability"]
            )
            for event_budget in config["event_budgets"]:
                condition_root = next(event_roots)
                (
                    reference_sequence,
                    observed_sequence,
                    selection_sequence,
                    permutation_order_sequence,
                    permutation_selection_sequence,
                    opportunity_baseline_sequence,
                    opportunity_sequence,
                    population_sequence,
                ) = condition_root.spawn(8)
                latent = with_event_budget(maximum, int(event_budget))
                reference_panel = resample_routing_counts(
                    latent,
                    np.random.default_rng(reference_sequence),
                )
                observed_panel = resample_routing_counts(
                    latent,
                    np.random.default_rng(observed_sequence),
                )
                reference_fit = fit_reference_router(
                    subset_authors(reference_panel, reference_indices),
                    discovery,
                )
                calibration = subset_authors(
                    observed_panel,
                    calibration_indices,
                )
                evaluation = subset_authors(
                    observed_panel,
                    evaluation_indices,
                )
                calibration_left = estimate_standardized_profile(
                    calibration,
                    discovery,
                    reference_fit=reference_fit,
                    sessions=0,
                )
                calibration_right = estimate_standardized_profile(
                    calibration,
                    discovery,
                    reference_fit=reference_fit,
                    sessions=1,
                )
                evaluation_left = estimate_standardized_profile(
                    evaluation,
                    discovery,
                    reference_fit=reference_fit,
                    sessions=0,
                )
                evaluation_right = estimate_standardized_profile(
                    evaluation,
                    discovery,
                    reference_fit=reference_fit,
                    sessions=1,
                )
                evaluation_combined = estimate_standardized_profile(
                    evaluation,
                    discovery,
                    reference_fit=reference_fit,
                )
                truth = true_standardized_profile(
                    subset_authors(latent, evaluation_indices),
                    discovery,
                    reference_fit=reference_fit,
                )
                selection_seed = _uint64(selection_sequence)
                adaptive_rank, selection_table = (
                    cross_validated_rank_selection(
                        calibration_left,
                        calibration_right,
                        candidates=candidate_ranks,
                        folds=int(config["selection_folds"]),
                        seed=selection_seed,
                    )
                )
                fixed_metrics, _ = score_rank(
                    calibration_left=calibration_left,
                    calibration_right=calibration_right,
                    evaluation_left=evaluation_left,
                    evaluation_right=evaluation_right,
                    evaluation_combined=evaluation_combined,
                    truth=truth,
                    rank=int(config["fixed_rank"]),
                    neighbor_count=int(config["neighbor_count"]),
                )
                adaptive_metrics, adaptive_denoiser = score_rank(
                    calibration_left=calibration_left,
                    calibration_right=calibration_right,
                    evaluation_left=evaluation_left,
                    evaluation_right=evaluation_right,
                    evaluation_combined=evaluation_combined,
                    truth=truth,
                    rank=adaptive_rank,
                    neighbor_count=int(config["neighbor_count"]),
                )
                oracle_metrics, _ = score_rank(
                    calibration_left=calibration_left,
                    calibration_right=calibration_right,
                    evaluation_left=evaluation_left,
                    evaluation_right=evaluation_right,
                    evaluation_combined=evaluation_combined,
                    truth=truth,
                    rank=int(latent_rank),
                    neighbor_count=int(config["neighbor_count"]),
                )
                thresholds = {
                    "truth_threshold": float(
                        config["recovery_truth_threshold"]
                    ),
                    "reliability_threshold": float(
                        config["recovery_reliability_threshold"]
                    ),
                    "auc_threshold": float(
                        config["identity_auc_threshold"]
                    ),
                    "top1_threshold": float(
                        config["identity_top1_threshold"]
                    ),
                }
                fixed_state = recovery_identity_state(
                    fixed_metrics,
                    **thresholds,
                )
                adaptive_state = recovery_identity_state(
                    adaptive_metrics,
                    **thresholds,
                )
                oracle_state = recovery_identity_state(
                    oracle_metrics,
                    **thresholds,
                )
                row: dict[str, Any] = {
                    "repetition": repetition,
                    "spawn_key": json.dumps(spawn_key),
                    "latent_seed": latent_seed,
                    "reference_seed": _uint64(reference_sequence),
                    "observed_seed": _uint64(observed_sequence),
                    "selection_seed": selection_seed,
                    "latent_rank": int(latent_rank),
                    "spectrum": str(spectrum),
                    "event_budget": int(event_budget),
                    "adaptive_rank": adaptive_rank,
                    "selection_min_loss": float(
                        selection_table["mean_loss"].min()
                    ),
                    "selection_at_upper_bound": bool(
                        adaptive_rank == max(candidate_ranks)
                    ),
                    "probability_fingerprint": probability_fingerprint,
                    "author_partition_fingerprint": _fingerprint(order),
                    "author_overlap": int(
                        len(
                            set(reference_indices)
                            & set(calibration_indices)
                        )
                        + len(
                            set(reference_indices)
                            & set(evaluation_indices)
                        )
                        + len(
                            set(calibration_indices)
                            & set(evaluation_indices)
                        )
                    ),
                    **_prefixed("fixed", fixed_metrics),
                    **_prefixed("adaptive", adaptive_metrics),
                    **_prefixed("oracle", oracle_metrics),
                    **_prefixed("fixed_state", fixed_state),
                    **_prefixed("adaptive_state", adaptive_state),
                    **_prefixed("oracle_state", oracle_state),
                    "permutation_rank": np.nan,
                    "permutation_auc": np.nan,
                    "opportunity_noise_floor": np.nan,
                    "opportunity_standardized_drift": np.nan,
                    "opportunity_naive_drift": np.nan,
                    "opportunity_drift_reduction": np.nan,
                    "population_shift_direction_cosine": np.nan,
                    "population_shift_amplitude": np.nan,
                    "population_shift_raw_amplitude": np.nan,
                    "cohort_refit_shift_recovery": np.nan,
                    "cohort_router_residual_recovery": np.nan,
                    "permutation_seed": np.nan,
                    "opportunity_baseline_seeds": "",
                    "opportunity_seeds": "",
                    "population_seed": np.nan,
                }
                primary_shift = (
                    int(latent_rank)
                    == int(config["primary_shift_rank"])
                    and int(event_budget)
                    == int(config["primary_shift_budget"])
                    and str(spectrum)
                    == str(config["primary_shift_spectrum"])
                )
                if primary_shift:
                    permutation_rng = np.random.default_rng(
                        permutation_order_sequence,
                    )
                    permuted_right = calibration_right[
                        permutation_rng.permutation(len(calibration_right))
                    ]
                    permutation_rank, _ = (
                        cross_validated_rank_selection(
                            calibration_left,
                            permuted_right,
                            candidates=candidate_ranks,
                            folds=int(config["selection_folds"]),
                            seed=_uint64(permutation_selection_sequence),
                        )
                    )
                    permutation_metrics, _ = score_rank(
                        calibration_left=calibration_left,
                        calibration_right=permuted_right,
                        evaluation_left=evaluation_left,
                        evaluation_right=evaluation_right,
                        evaluation_combined=evaluation_combined,
                        truth=truth,
                        rank=permutation_rank,
                        neighbor_count=int(config["neighbor_count"]),
                    )
                    row["permutation_rank"] = permutation_rank
                    row["permutation_auc"] = permutation_metrics[
                        "hard_neighbor_auc"
                    ]
                    row["permutation_seed"] = _uint64(
                        permutation_selection_sequence
                    )

                    base_score = apply_group_free_denoiser(
                        evaluation_combined,
                        adaptive_denoiser,
                    )
                    opportunity_latent = apply_opportunity_shift(
                        latent,
                        strength=float(
                            config["opportunity_shift_strength"]
                        ),
                    )
                    latent_eval = subset_authors(
                        latent,
                        evaluation_indices,
                    )
                    opportunity_eval_latent = subset_authors(
                        opportunity_latent,
                        evaluation_indices,
                    )
                    opportunity_replicates = int(
                        config["opportunity_replicates"]
                    )
                    baseline_children = (
                        opportunity_baseline_sequence.spawn(
                            opportunity_replicates
                        )
                    )
                    opportunity_children = opportunity_sequence.spawn(
                        opportunity_replicates
                    )
                    baseline_profiles = []
                    standardized_profiles = []
                    naive_profiles = []
                    for baseline_child, opportunity_child in zip(
                        baseline_children,
                        opportunity_children,
                        strict=True,
                    ):
                        baseline_panel = resample_routing_counts(
                            latent_eval,
                            np.random.default_rng(baseline_child),
                        )
                        opportunity_panel = resample_routing_counts(
                            opportunity_eval_latent,
                            np.random.default_rng(opportunity_child),
                        )
                        baseline_profiles.append(
                            estimate_standardized_profile(
                                baseline_panel,
                                discovery,
                                reference_fit=reference_fit,
                            )
                        )
                        standardized_profiles.append(
                            estimate_standardized_profile(
                                opportunity_panel,
                                discovery,
                                reference_fit=reference_fit,
                            )
                        )
                        naive_profiles.append(
                            estimate_standardized_profile(
                                opportunity_panel,
                                discovery,
                                reference_fit=reference_fit,
                                naive_exposure_weighted=True,
                            )
                        )
                    baseline_scores = np.stack([
                        apply_group_free_denoiser(
                            profile,
                            adaptive_denoiser,
                        )
                        for profile in baseline_profiles
                    ])
                    standardized_scores = np.stack([
                        apply_group_free_denoiser(
                            profile,
                            adaptive_denoiser,
                        )
                        for profile in standardized_profiles
                    ])
                    naive_scores = np.stack([
                        apply_group_free_denoiser(
                            profile,
                            adaptive_denoiser,
                        )
                        for profile in naive_profiles
                    ])
                    baseline_score = baseline_scores.mean(axis=0)
                    standardized_score = standardized_scores.mean(axis=0)
                    naive_score = naive_scores.mean(axis=0)
                    midpoint = opportunity_replicates // 2
                    baseline_left = baseline_scores[:midpoint].mean(axis=0)
                    baseline_right = baseline_scores[midpoint:].mean(axis=0)
                    noise_mse = float(np.mean(np.sum(
                        (baseline_left - baseline_right) ** 2,
                        axis=1,
                    )))
                    standardized_mse = float(np.mean(np.sum(
                        (standardized_score - baseline_score) ** 2,
                        axis=1,
                    )))
                    naive_mse = float(np.mean(np.sum(
                        (naive_score - baseline_score) ** 2,
                        axis=1,
                    )))
                    standardized_drift = float(np.sqrt(standardized_mse))
                    naive_drift = float(np.sqrt(naive_mse))
                    row["opportunity_noise_floor"] = float(
                        np.sqrt(noise_mse)
                    )
                    row["opportunity_standardized_drift"] = (
                        standardized_drift
                    )
                    row["opportunity_naive_drift"] = naive_drift
                    row["opportunity_drift_reduction"] = float(
                        (naive_mse - standardized_mse)
                        / max(naive_mse, 1e-12)
                    )
                    row["opportunity_baseline_seeds"] = json.dumps(
                        [_uint64(child) for child in baseline_children]
                    )
                    row["opportunity_seeds"] = json.dumps(
                        [_uint64(child) for child in opportunity_children]
                    )

                    shift = population_shift_direction(
                        latent,
                        rms=float(config["population_shift_rms"]),
                    )
                    shifted_latent = apply_population_shift(
                        latent,
                        indices=evaluation_indices,
                        shift_ilr=shift,
                    )
                    shifted_panel = resample_routing_counts(
                        shifted_latent,
                        np.random.default_rng(population_sequence),
                    )
                    shifted_evaluation = subset_authors(
                        shifted_panel,
                        evaluation_indices,
                    )
                    shifted_profile = estimate_standardized_profile(
                        shifted_evaluation,
                        discovery,
                        reference_fit=reference_fit,
                    )
                    shifted_truth = true_standardized_profile(
                        subset_authors(
                            shifted_latent,
                            evaluation_indices,
                        ),
                        discovery,
                        reference_fit=reference_fit,
                    )
                    shifted_score = apply_group_free_denoiser(
                        shifted_profile,
                        adaptive_denoiser,
                    )
                    estimated_delta = (
                        shifted_score.mean(axis=0)
                        - base_score.mean(axis=0)
                    )
                    raw_truth_delta = (
                        shifted_truth.mean(axis=0)
                        - truth.mean(axis=0)
                    )
                    projected_truth_delta = (
                        apply_group_free_denoiser(
                            shifted_truth,
                            adaptive_denoiser,
                        ).mean(axis=0)
                        - apply_group_free_denoiser(
                            truth,
                            adaptive_denoiser,
                        ).mean(axis=0)
                    )
                    row["population_shift_direction_cosine"] = (
                        _direction_cosine(
                            estimated_delta,
                            projected_truth_delta,
                        )
                    )
                    row["population_shift_amplitude"] = float(
                        np.linalg.norm(estimated_delta)
                        / max(
                            np.linalg.norm(projected_truth_delta),
                            1e-12,
                        )
                    )
                    row["population_shift_raw_amplitude"] = float(
                        np.linalg.norm(estimated_delta)
                        / max(np.linalg.norm(raw_truth_delta), 1e-12)
                    )
                    target_reference = fit_reference_router(
                        shifted_evaluation,
                        discovery,
                    )
                    target_relative = estimate_standardized_profile(
                        shifted_evaluation,
                        discovery,
                        reference_fit=target_reference,
                    )
                    target_centered = (
                        target_relative
                        - target_relative.mean(axis=0, keepdims=True)
                    )
                    row["cohort_refit_shift_recovery"] = float(
                        np.linalg.norm(target_centered.mean(axis=0))
                        / max(
                            np.linalg.norm(projected_truth_delta),
                            1e-12,
                        )
                    )
                    row["cohort_router_residual_recovery"] = float(
                        np.linalg.norm(target_relative.mean(axis=0))
                        / max(
                            np.linalg.norm(projected_truth_delta),
                            1e-12,
                        )
                    )
                    row["population_seed"] = _uint64(
                        population_sequence
                    )
                rows.append(row)
    return rows


def _interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int = 20_000,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    indices = rng.integers(0, len(vector), size=(draws, len(vector)))
    means = vector[indices].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
    }


def _confirmation_effects(
    frame: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    rng = np.random.default_rng(int(config["_active_seed"]) ^ 0xA37E)
    primary = frame[
        (frame["spectrum"] == config["primary_shift_spectrum"])
        & (frame["event_budget"] == config["primary_shift_budget"])
    ].copy()
    rank8 = primary[primary["latent_rank"] == 8].copy()
    rank12 = primary[primary["latent_rank"] == 12].copy()

    def fisher(column: pd.Series) -> np.ndarray:
        return np.arctanh(np.clip(
            column.to_numpy(dtype=float),
            -0.999999,
            0.999999,
        ))

    rank8_fisher = fisher(
        rank8["adaptive_truth_correlation"]
    ) - fisher(rank8["fixed_truth_correlation"])
    rank8_auc = (
        rank8["adaptive_hard_neighbor_auc"].to_numpy()
        - rank8["fixed_hard_neighbor_auc"].to_numpy()
    )
    fixed_z = fisher(rank12["fixed_truth_correlation"])
    adaptive_z = fisher(rank12["adaptive_truth_correlation"])
    oracle_z = fisher(rank12["oracle_truth_correlation"])
    fisher_denominator = oracle_z - fixed_z
    fisher_closure = np.divide(
        adaptive_z - fixed_z,
        fisher_denominator,
        out=np.zeros_like(fisher_denominator),
        where=np.abs(fisher_denominator) > 1e-10,
    )
    nrmse_denominator = (
        rank12["fixed_truth_nrmse"].to_numpy()
        - rank12["oracle_truth_nrmse"].to_numpy()
    )
    nrmse_closure = np.divide(
        rank12["fixed_truth_nrmse"].to_numpy()
        - rank12["adaptive_truth_nrmse"].to_numpy(),
        nrmse_denominator,
        out=np.zeros_like(nrmse_denominator),
        where=np.abs(nrmse_denominator) > 1e-10,
    )
    shift = frame[np.isfinite(
        frame["opportunity_drift_reduction"]
    )].copy()
    return {
        "rank8_truth_fisher_delta": _interval(
            rank8_fisher,
            rng=rng,
        ),
        "rank8_auc_delta": _interval(rank8_auc, rng=rng),
        "rank12_fisher_gap_closure": _interval(
            fisher_closure,
            rng=rng,
        ),
        "rank12_nrmse_gap_closure": _interval(
            nrmse_closure,
            rng=rng,
        ),
        "fixed_rank12_identity_only_rate": float(
            rank12["fixed_state_identity_only"].mean()
        ),
        "adaptive_rank12_identity_only_rate": float(
            rank12["adaptive_state_identity_only"].mean()
        ),
        "opportunity_drift_reduction": _interval(
            shift["opportunity_drift_reduction"].to_numpy(),
            rng=rng,
        ),
        "population_shift_direction_cosine": _interval(
            shift["population_shift_direction_cosine"].to_numpy(),
            rng=rng,
        ),
        "population_shift_amplitude": _interval(
            shift["population_shift_amplitude"].to_numpy(),
            rng=rng,
        ),
        "cohort_refit_shift_recovery": _interval(
            shift["cohort_refit_shift_recovery"].to_numpy(),
            rng=rng,
        ),
        "permutation_low_rank_rate": float(
            (shift["permutation_rank"] <= 2).mean()
        ),
        "permutation_chance_auc_rate": float(
            shift["permutation_auc"].between(0.45, 0.55).mean()
        ),
        "upper_rank_selection_rate": float(
            frame["selection_at_upper_bound"].mean()
        ),
    }


def _integrity(
    frame: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    required_columns = [
        f"{prefix}_{metric}"
        for prefix in ("fixed", "adaptive", "oracle")
        for metric in (
            "truth_correlation",
            "truth_nrmse",
            "split_reliability",
            "hard_neighbor_auc",
            "top1",
        )
    ]
    optional_columns = [
        "permutation_auc",
        "opportunity_noise_floor",
        "opportunity_standardized_drift",
        "opportunity_naive_drift",
        "opportunity_drift_reduction",
        "population_shift_direction_cosine",
        "population_shift_amplitude",
        "population_shift_raw_amplitude",
        "cohort_refit_shift_recovery",
        "cohort_router_residual_recovery",
    ]
    optional_finite = all(
        np.isfinite(frame[column].dropna().to_numpy()).all()
        for column in optional_columns
    )
    seeds = np.concatenate([
        frame["reference_seed"].to_numpy(dtype=np.uint64),
        frame["observed_seed"].to_numpy(dtype=np.uint64),
        frame["selection_seed"].to_numpy(dtype=np.uint64),
        frame["permutation_seed"].dropna().to_numpy(dtype=np.uint64),
        np.asarray([
            seed
            for payload in frame["opportunity_baseline_seeds"]
            if payload
            for seed in json.loads(payload)
        ], dtype=np.uint64),
        np.asarray([
            seed
            for payload in frame["opportunity_seeds"]
            if payload
            for seed in json.loads(payload)
        ], dtype=np.uint64),
        frame["population_seed"].dropna().to_numpy(dtype=np.uint64),
    ])
    return {
        "numeric": bool(
            np.isfinite(frame[required_columns].to_numpy()).all()
            and optional_finite
        ),
        "author_disjointness": bool((frame["author_overlap"] == 0).all()),
        "seed_uniqueness": bool(len(seeds) == len(np.unique(seeds))),
        "seed_count": int(len(seeds)),
        "rows": int(len(frame)),
        "expected_rows": int(
            config["_active_repetitions"]
            * len(config["latent_ranks"])
            * len(config["spectra"])
            * len(config["event_budgets"])
        ),
        "paired_worlds": bool(
            frame.groupby(["repetition", "spectrum"])[
                "latent_seed"
            ].nunique().max()
            == 1
        ),
    }


def _decision(
    frame: pd.DataFrame,
    effects: dict[str, Any],
    integrity: dict[str, Any],
    *,
    config: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    if mode != "confirmation":
        status = (
            "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_"
            + ("SMOKE_PASS" if mode == "smoke" else "DISCOVERY_READY")
        )
        return {
            "status": status,
            "integrity": integrity,
            "diagnostics": effects,
            "claim_boundary": config["claim_boundary"],
        }
    gates = config["gates"]
    checks = {
        "numeric_integrity": integrity["numeric"],
        "author_disjointness": integrity["author_disjointness"],
        "seed_uniqueness": integrity["seed_uniqueness"],
        "row_count": integrity["rows"] == integrity["expected_rows"],
        "paired_worlds": integrity["paired_worlds"],
        "permutation_low_rank": (
            effects["permutation_low_rank_rate"]
            >= gates["minimum_permutation_low_rank_rate"]
        ),
        "permutation_chance_auc": (
            effects["permutation_chance_auc_rate"]
            >= gates["minimum_permutation_chance_auc_rate"]
        ),
        "rank_upper_bound": (
            effects["upper_rank_selection_rate"]
            <= gates["maximum_upper_rank_selection_rate"]
        ),
        "rank8_truth_noninferiority": (
            effects["rank8_truth_fisher_delta"]["mean"]
            >= gates["minimum_rank8_truth_fisher_delta"]
        ),
        "rank8_auc_noninferiority": (
            effects["rank8_auc_delta"]["mean"]
            >= gates["minimum_rank8_auc_delta"]
        ),
        "rank12_fisher_gap_closure": (
            effects["rank12_fisher_gap_closure"]["mean"]
            >= gates["minimum_rank12_fisher_gap_closure_mean"]
            and effects["rank12_fisher_gap_closure"]["lower95"]
            >= gates["minimum_rank12_fisher_gap_closure_lower95"]
        ),
        "rank12_nrmse_gap_closure": (
            effects["rank12_nrmse_gap_closure"]["lower95"]
            > gates["minimum_rank12_nrmse_gap_closure_lower95"]
        ),
        "opportunity_transport": (
            effects["opportunity_drift_reduction"]["mean"]
            >= gates["minimum_opportunity_drift_reduction_mean"]
            and effects["opportunity_drift_reduction"]["lower95"]
            > gates["minimum_opportunity_drift_reduction_lower95"]
        ),
        "population_shift_direction": (
            effects["population_shift_direction_cosine"]["mean"]
            >= gates["minimum_population_shift_direction_cosine"]
        ),
        "population_shift_amplitude": (
            gates["minimum_population_shift_amplitude"]
            <= effects["population_shift_amplitude"]["mean"]
            <= gates["maximum_population_shift_amplitude"]
        ),
        "cohort_refit_erasure": (
            effects["cohort_refit_shift_recovery"]["mean"]
            <= gates["maximum_cohort_refit_shift_recovery"]
        ),
    }
    selector_keys = [
        "permutation_low_rank",
        "permutation_chance_auc",
        "rank_upper_bound",
        "rank8_truth_noninferiority",
        "rank8_auc_noninferiority",
        "rank12_fisher_gap_closure",
        "rank12_nrmse_gap_closure",
    ]
    reference_keys = [
        "opportunity_transport",
        "population_shift_direction",
        "population_shift_amplitude",
        "cohort_refit_erasure",
    ]
    integrity_keys = [
        "numeric_integrity",
        "author_disjointness",
        "seed_uniqueness",
        "row_count",
        "paired_worlds",
    ]
    if not all(checks[key] for key in integrity_keys + selector_keys):
        status = "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_STOP_SELECTOR_INVALID"
    elif not all(checks[key] for key in reference_keys):
        status = (
            "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_"
            "STOP_REFERENCE_NONTRANSPORTABLE"
        )
    elif (
        effects["fixed_rank12_identity_only_rate"]
        >= gates["minimum_fixed_rank12_identity_only_rate"]
        and effects["adaptive_rank12_identity_only_rate"]
        <= gates[
            "maximum_adaptive_rank12_identity_only_rate_for_explained"
        ]
    ):
        status = (
            "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_"
            "PASS_MISSPECIFICATION_EXPLAINED"
        )
    elif (
        effects["adaptive_rank12_identity_only_rate"]
        >= gates[
            "minimum_adaptive_rank12_identity_only_rate_for_persistence"
        ]
    ):
        status = (
            "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_"
            "PASS_REVERSE_SEPARATION_PERSISTS"
        )
    else:
        status = "V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_STOP_AMBIGUOUS"
    return {
        "status": status,
        "checks": {key: bool(value) for key, value in checks.items()},
        "effects": effects,
        "integrity": integrity,
        "claim_boundary": config["claim_boundary"],
    }


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "adaptive_rank",
        "fixed_truth_correlation",
        "adaptive_truth_correlation",
        "oracle_truth_correlation",
        "fixed_truth_nrmse",
        "adaptive_truth_nrmse",
        "oracle_truth_nrmse",
        "fixed_hard_neighbor_auc",
        "adaptive_hard_neighbor_auc",
        "oracle_hard_neighbor_auc",
        "fixed_top1",
        "adaptive_top1",
        "oracle_top1",
        "fixed_state_identity_only",
        "adaptive_state_identity_only",
        "adaptive_state_both",
    ]
    return (
        frame.groupby(
            ["spectrum", "latent_rank", "event_budget"],
            as_index=False,
        )[metrics]
        .mean()
    )


def _verify_parent(config: dict[str, Any]) -> dict[str, str]:
    parent = config["required_parent_seal"]
    got = sha256_file(ROOT / parent["path"])
    if got != parent["sha256"]:
        raise RuntimeError("V3.7D parent seal mismatch")
    return {"status": "PARENT_SEAL_PASS", "sha256": got}


def _verify_own_seal(
    path: Path,
    *,
    mode: str,
) -> dict[str, str]:
    if mode != "confirmation":
        return {"status": "OWN_SEAL_NOT_REQUIRED"}
    if not path.is_file():
        raise RuntimeError("confirmation requires V3.7E seal")
    seal = _read(path)
    failures = [
        relative
        for relative, expected in seal["files"].items()
        if not (ROOT / relative).is_file()
        or sha256_file(ROOT / relative) != expected
    ]
    if failures:
        raise RuntimeError(f"V3.7E seal mismatch: {failures}")
    return {
        "status": "V37E_PROSPECTIVE_SEAL_PASS",
        "sha256": sha256_file(path),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    effects = decision.get("effects", decision.get("diagnostics", {}))
    return f"""# V8 Adaptive Rank and Fixed Reference V3.7E

Decision: `{decision["status"]}`

## Integrity

```json
{json.dumps(decision["integrity"], indent=2)}
```

## Effects

```json
{json.dumps(effects, indent=2)}
```

## Cell summary

{summary.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT
        / "configs/v8_adaptive_rank_fixed_reference_v37e_discovery.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT
        / "configs/v8_adaptive_rank_fixed_reference_v37e_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "results/v8_adaptive_rank_fixed_reference/v37e_discovery",
    )
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery", "confirmation"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    if args.mode == "smoke":
        config["_active_seed"] = int(
            config.get("smoke_seed", config.get("seed"))
        )
        repetitions = 4
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
    spawn_keys = [tuple(child.spawn_key) for child in root.spawn(repetitions)]
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
    frame = pd.DataFrame([row for rows in nested for row in rows])
    summary = _summary(frame)
    integrity = _integrity(frame, config=config)
    effects = _confirmation_effects(frame, config=config)
    decision = _decision(
        frame,
        effects,
        integrity,
        config=config,
        mode=args.mode,
    )
    decision["parent_seal"] = parent
    decision["prospective_seal"] = own_seal
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "metrics.csv", index=False)
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision, summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[ROOT / config["required_parent_seal"]["path"]],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_adaptive_rank_reference.py",
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
        "rows": len(frame),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
