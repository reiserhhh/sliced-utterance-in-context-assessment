#!/usr/bin/env python3
"""Run the SUICA V3.7H nested-resolution filtration experiment."""
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
    apply_spectrum_operator,
    model_assisted_conditional_region,
    normalized_mse,
    unresolved_channel,
)
from suica_core.v8_resolution_filtration import (  # noqa: E402
    CORE_WORLDS,
    ResolutionFiltrationWorldSpec,
    coherence_kappa,
    decompose_score_update,
    fit_coherence_predictor,
    fit_joint_resolution_family,
    history_features,
    operator_action_cosine,
    oscillating_assay_scores,
    predict_coherence_update,
    resolution_candidates,
    simulate_resolution_filtration_world,
    update_mean_energy_ratio,
)
from suica_core.v8_resolution_filtration_h1 import (  # noqa: E402
    cumulative_kappa,
    fit_joint_cumulative_predictor,
    initial_observable_history,
    predict_joint_cumulative,
    scorer_projection_metrics,
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


def _score_region_coverage(
    region: dict[str, Any],
    truth: np.ndarray,
) -> float:
    error = (
        np.asarray(truth, dtype=float)
        - np.asarray(region["center"], dtype=float)
    )
    transformed = (
        error @ np.asarray(region["inverse_root"], dtype=float).T
    )
    return float(np.mean(
        np.sum(transformed**2, axis=1) <= float(region["threshold"])
    ))


def _score_path(
    panel: np.ndarray,
    fitted: dict[int, dict[str, Any]],
    budgets: list[int],
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    profiles: list[np.ndarray] = []
    scores: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    for index, budget in enumerate(budgets):
        profile = np.asarray(panel)[:, :2, index].mean(axis=1)
        profiles.append(profile)
        scores.append(apply_spectrum_operator(profile, fitted[budget]))
        residuals.append(unresolved_channel(profile, fitted[budget]))
    return profiles, scores, residuals


def _interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int,
    alpha: float = 0.05,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return {
            "mean": float("nan"),
            "lower": float("nan"),
            "upper": float("nan"),
        }
    samples = vector[
        rng.integers(0, len(vector), size=(draws, len(vector)))
    ].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower": float(np.quantile(samples, alpha / 2.0)),
        "upper": float(np.quantile(samples, 1.0 - alpha / 2.0)),
    }


def _simultaneous_bounds(
    frame: pd.DataFrame,
    *,
    value: str,
    cells: list[str],
    seed: int,
    draws: int,
) -> dict[str, Any]:
    """Return repetition-cluster max-T simultaneous mean bounds."""
    working = frame.copy()
    working["_cell"] = working[cells].astype(str).agg("::".join, axis=1)
    pivot = working.pivot(
        index="repetition",
        columns="_cell",
        values=value,
    ).sort_index(axis=1)
    pivot = pivot.dropna(axis=0, how="any")
    if pivot.empty:
        return {
            "status": "UNRESOLVED_NO_COMPLETE_REPETITIONS",
            "cells": {},
        }
    matrix = pivot.to_numpy(dtype=float)
    mean = matrix.mean(axis=0)
    se = matrix.std(axis=0, ddof=1) / np.sqrt(len(matrix))
    safe_se = np.maximum(se, 1e-12)
    rng = np.random.default_rng(seed)
    maximum = np.empty(draws, dtype=float)
    minimum = np.empty(draws, dtype=float)
    for start in range(0, draws, 500):
        count = min(500, draws - start)
        sampled = matrix[
            rng.integers(0, len(matrix), size=(count, len(matrix)))
        ].mean(axis=1)
        statistic = (sampled - mean[None]) / safe_se[None]
        maximum[start:start + count] = statistic.max(axis=1)
        minimum[start:start + count] = statistic.min(axis=1)
    upper_q = float(np.quantile(maximum, 0.95))
    lower_q = float(np.quantile(minimum, 0.05))
    output = {
        str(name): {
            "mean": float(mean[index]),
            "lower95_simultaneous": float(
                mean[index] + lower_q * safe_se[index]
            ),
            "upper95_simultaneous": float(
                mean[index] + upper_q * safe_se[index]
            ),
        }
        for index, name in enumerate(pivot.columns)
    }
    return {
        "status": "SIMULTANEOUS_MAX_T_READY",
        "repetitions": int(len(matrix)),
        "cells": output,
        "maximum_upper": float(max(
            value["upper95_simultaneous"] for value in output.values()
        )),
        "minimum_lower": float(min(
            value["lower95_simultaneous"] for value in output.values()
        )),
    }


def _one_sided_familywise_bounds(
    frame: pd.DataFrame,
    *,
    value: str,
    cells: list[str],
    seed: int,
    draws: int,
    confidence: float,
) -> dict[str, Any]:
    """Return explicitly named one-sided familywise bootstrap bounds."""
    working = frame.copy()
    working["_cell"] = working[cells].astype(str).agg("::".join, axis=1)
    pivot = working.pivot(
        index="repetition",
        columns="_cell",
        values=value,
    ).sort_index(axis=1)
    pivot = pivot.dropna(axis=0, how="any")
    if pivot.empty:
        return {
            "status": "UNRESOLVED_NO_COMPLETE_REPETITIONS",
            "cells": {},
            "familywise_confidence": float(confidence),
        }
    matrix = pivot.to_numpy(dtype=float)
    mean = matrix.mean(axis=0)
    se = matrix.std(axis=0, ddof=1) / np.sqrt(len(matrix))
    safe_se = np.maximum(se, 1e-12)
    rng = np.random.default_rng(seed)
    maximum = np.empty(draws, dtype=float)
    minimum = np.empty(draws, dtype=float)
    for start in range(0, draws, 500):
        count = min(500, draws - start)
        sampled = matrix[
            rng.integers(0, len(matrix), size=(count, len(matrix)))
        ].mean(axis=1)
        statistic = (sampled - mean[None]) / safe_se[None]
        maximum[start:start + count] = statistic.max(axis=1)
        minimum[start:start + count] = statistic.min(axis=1)
    upper_q = float(np.quantile(maximum, confidence))
    lower_q = float(np.quantile(minimum, 1.0 - confidence))
    output = {
        str(name): {
            "mean": float(mean[index]),
            "one_sided_familywise_lower": float(
                mean[index] + lower_q * safe_se[index]
            ),
            "one_sided_familywise_upper": float(
                mean[index] + upper_q * safe_se[index]
            ),
        }
        for index, name in enumerate(pivot.columns)
    }
    return {
        "status": "ONE_SIDED_FAMILYWISE_BOUNDS_READY",
        "familywise_confidence": float(confidence),
        "repetitions": int(len(matrix)),
        "cells": output,
        "maximum_upper": float(max(
            cell["one_sided_familywise_upper"] for cell in output.values()
        )),
        "minimum_lower": float(min(
            cell["one_sided_familywise_lower"] for cell in output.values()
        )),
    }


def _world_spec(config: dict[str, Any], world: str) -> ResolutionFiltrationWorldSpec:
    return ResolutionFiltrationWorldSpec(
        world=world,
        dimension=int(config["dimension"]),
        sessions=4,
        budgets=tuple(int(value) for value in config["event_budgets"]),
        reference_authors=int(config["reference_authors"]),
        calibration_authors=int(config["calibration_authors"]),
        probe_authors=int(config["probe_authors"]),
        interval_authors=int(config["interval_authors"]),
        evaluation_authors=int(config["evaluation_authors"]),
        stable_rms=float(config["stable_rms"]),
        event_rms_at_64=float(config["event_rms_at_64"]),
        state_rms=float(config["state_rms"]),
        long_memory_rho=float(config["long_memory_rho"]),
        opportunity_shift_rms=float(config["opportunity_shift_rms"]),
        opportunity_shift_start=int(config["opportunity_shift_start"]),
        reference_shift_rms=float(config["reference_shift_rms"]),
        student_df=float(config["student_df"]),
    )


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[int],
]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    world_streams = root.spawn(len(config["worlds"]))
    budgets = [int(value) for value in config["event_budgets"]]
    candidates = resolution_candidates()
    metric_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    predictor_rows: list[dict[str, Any]] = []
    seeds: list[int] = []
    interval_worlds = set(config["interval_worlds"])
    coherence_worlds = set(config["coherence_worlds"])
    h1_enabled = bool(config.get("enable_h1_diagnostics", False))
    cumulative_worlds = set(config.get("cumulative_worlds", []))
    replication_worlds = set(config["replication_audit_worlds"])

    for world_index, world_name in enumerate(config["worlds"]):
        (
            latent_sequence,
            event_sequence,
            selection_sequence,
            interval_sequence,
            predictor_sequence,
        ) = (
            world_streams[world_index].spawn(5)
        )
        latent_seed = _uint64(latent_sequence)
        event_seed = _uint64(event_sequence)
        selection_seed = _uint64(selection_sequence)
        interval_seeds = [
            _uint64(value)
            for value in interval_sequence.spawn(len(budgets))
        ]
        predictor_seed_count = 2 * (len(budgets) - 1)
        if h1_enabled and world_name in cumulative_worlds:
            predictor_seed_count += 1
        predictor_seeds = [
            _uint64(value)
            for value in predictor_sequence.spawn(predictor_seed_count)
        ]
        seeds.extend(
            [
                latent_seed,
                event_seed,
                selection_seed,
                *interval_seeds,
                *predictor_seeds,
            ]
        )
        world = simulate_resolution_filtration_world(
            latent_seed=latent_seed,
            event_seed=event_seed,
            spec=_world_spec(config, str(world_name)),
        )
        panels = world["panels"]
        truths = world["truths"]
        external_zero = panels["reference_a"][:, :, -1].mean(axis=(0, 1))
        audit_zero = panels["reference_b"][:, :, -1].mean(axis=(0, 1))
        fitted, selected, selection_table = fit_joint_resolution_family(
            panels["calibration_a"],
            budgets=budgets,
            external_zero=external_zero,
            candidates=candidates,
            folds=int(config["selection_folds"]),
            seed=selection_seed,
            noise_shrinkage=float(config["noise_shrinkage"]),
        )
        for _, row in selection_table.iterrows():
            candidate_rows.append({
                "repetition": repetition,
                "world": world_name,
                "arm": "main",
                **row.to_dict(),
            })

        audit_fitted: dict[int, dict[str, Any]] | None = None
        audit_selected: dict[str, Any] | None = None
        if world_name in replication_worlds:
            audit_fitted, audit_selected, audit_table = (
                fit_joint_resolution_family(
                    panels["calibration_b"],
                    budgets=budgets,
                    external_zero=audit_zero,
                    candidates=candidates,
                    folds=int(config["selection_folds"]),
                    seed=selection_seed ^ 0xB37,
                    noise_shrinkage=float(config["noise_shrinkage"]),
                )
            )
            for _, row in audit_table.iterrows():
                candidate_rows.append({
                    "repetition": repetition,
                    "world": world_name,
                    "arm": "replication",
                    **row.to_dict(),
                })

        eval_profiles, eval_scores, eval_residuals = _score_path(
            panels["evaluation"],
            fitted,
            budgets,
        )
        probe_profiles, probe_scores, probe_residuals = _score_path(
            panels["probe"],
            fitted,
            budgets,
        )
        proxy = panels["evaluation"][:, 2:4, -1].mean(axis=1)
        truth = truths["evaluation"]
        truth_energy = float(np.mean(
            (truth - np.asarray(world["true_zero"])) ** 2
        ))
        interval_records: dict[int, dict[str, Any]] = {}

        for budget_index, budget in enumerate(budgets):
            score = eval_scores[budget_index]
            profile = eval_profiles[budget_index]
            residual = eval_residuals[budget_index]
            if truth_energy > 1e-12:
                nmse = normalized_mse(
                    score,
                    truth,
                    origin=np.asarray(world["true_zero"]),
                )
            else:
                nmse = np.nan
            proxy_denominator = max(
                float(np.mean((proxy - external_zero) ** 2)),
                1e-12,
            )
            proxy_nmse = float(
                np.mean((score - proxy) ** 2) / proxy_denominator
            )
            region: dict[str, Any] = {}
            reliable = (
                float(fitted[budget]["effective_df"])
                >= float(config["minimum_interval_effective_df"])
            )
            registered = world_name in interval_worlds
            if registered and reliable:
                region = model_assisted_conditional_region(
                    interval_sessions=panels["interval"][:, :, budget_index],
                    evaluation_sessions=panels["evaluation"][
                        :, :, budget_index
                    ],
                    fitted=fitted[budget],
                    level=float(config["interval_content"]),
                    tolerance_confidence=float(
                        config["per_budget_tolerance_confidence"]
                    ),
                    bootstrap_replicates=int(
                        config["_active_interval_bootstrap_replicates"]
                    ),
                    bootstrap_seed=interval_seeds[budget_index],
                    eigen_floor=float(config["interval_eigen_floor"]),
                    minimum_fit_per_dimension=float(
                        config["minimum_fit_per_dimension"]
                    ),
                    maximum_negative_mass_ratio=float(
                        config["maximum_negative_mass_ratio"]
                    ),
                    maximum_condition=float(
                        config["maximum_interval_condition"]
                    ),
                    minimum_bootstrap_replicates=int(
                        config["_active_interval_bootstrap_replicates"]
                    ),
                    minimum_bootstrap_valid_rate=float(
                        config["minimum_bootstrap_valid_rate"]
                    ),
                    maximum_bootstrap_radius_cv=float(
                        config["maximum_bootstrap_radius_cv"]
                    ),
                    maximum_bootstrap_radius_quantile_ratio=float(
                        config[
                            "maximum_bootstrap_radius_quantile_ratio"
                        ]
                    ),
                    minimum_pair_swap_radius_ratio=float(
                        config["minimum_pair_swap_radius_ratio"]
                    ),
                    maximum_pair_swap_radius_ratio=float(
                        config["maximum_pair_swap_radius_ratio"]
                    ),
                )
            if region.get("status") == "ME_TOLERANCE_BALL_95_95":
                interval_allowed = True
                interval_status = str(region["status"])
                coverage = _score_region_coverage(region, truth)
                radius = float(region["tolerance_radius"])
            else:
                interval_allowed = False
                interval_status = (
                    str(region.get("status"))
                    if region
                    else (
                        "UNRESOLVED_NO_RELIABLE_SCORE_CHANNEL"
                        if not reliable
                        else "INTERVAL_NOT_REGISTERED_FOR_WORLD"
                    )
                )
                coverage = np.nan
                radius = np.nan
            interval_records[budget] = {
                "allowed": interval_allowed,
                "status": interval_status,
                "coverage": coverage,
                "radius": radius,
            }

            score_reconstruction = float(np.max(np.abs(
                score + residual - profile
            )))
            if audit_fitted is not None:
                audit_score = apply_spectrum_operator(
                    profile,
                    audit_fitted[budget],
                )
                replication_rms = float(np.sqrt(
                    np.mean((score - audit_score) ** 2)
                ))
                operator_replication_distance = float(
                    np.linalg.norm(
                        np.asarray(fitted[budget]["operator"])
                        - np.asarray(audit_fitted[budget]["operator"])
                    )
                    / max(
                        float(np.linalg.norm(
                            np.asarray(fitted[budget]["operator"])
                        )),
                        1e-12,
                    )
                )
            else:
                replication_rms = np.nan
                operator_replication_distance = np.nan
            metric_rows.append({
                "repetition": repetition,
                "world": world_name,
                "event_budget": budget,
                "metric_scale": "NMSE",
                "latent_seed": latent_seed,
                "event_seed": event_seed,
                "selection_seed": selection_seed,
                "truth_fingerprint": _fingerprint(truth),
                "selected_name": str(selected["name"]),
                "selected_family": str(selected["family"]),
                "selected_effective_df": float(
                    fitted[budget]["effective_df"]
                ),
                "nmse": nmse,
                "proxy_nmse": proxy_nmse,
                "interval_claim_allowed": interval_allowed,
                "interval_claim_status": interval_status,
                "conditional_coverage": coverage,
                "tolerance_radius": radius,
                "interval_tolerance_order": float(
                    region.get("tolerance_order", np.nan)
                ),
                "interval_achieved_confidence": float(
                    region.get(
                        "achieved_tolerance_confidence",
                        np.nan,
                    )
                ),
                "interval_bootstrap_valid_rate": float(
                    region.get("bootstrap_valid_rate", np.nan)
                ),
                "interval_bootstrap_radius_cv": float(
                    region.get("bootstrap_radius_cv", np.nan)
                ),
                "interval_pair_swap_radius_ratio": float(
                    region.get("pair_swap_radius_ratio", np.nan)
                ),
                "score_reconstruction_error": score_reconstruction,
                "prefix_identity_error": float(
                    world["maximum_prefix_identity_error"]
                ),
                "reference_origin_rms_difference": float(np.sqrt(
                    np.mean((external_zero - audit_zero) ** 2)
                )),
                "replication_score_rms_difference": replication_rms,
                "operator_replication_distance": (
                    operator_replication_distance
                ),
                "audit_selected_name": (
                    str(audit_selected["name"])
                    if audit_selected is not None
                    else ""
                ),
                "core_world": bool(world["design"]["core_world"]),
            })

        main_transition_cache: list[dict[str, Any]] = []
        for transition_index, (left_budget, right_budget) in enumerate(
            zip(budgets[:-1], budgets[1:], strict=True)
        ):
            left_score = eval_scores[transition_index]
            right_score = eval_scores[transition_index + 1]
            update = right_score - left_score
            left_loss = float(np.mean((proxy - left_score) ** 2))
            right_loss = float(np.mean((proxy - right_score) ** 2))
            update_energy = float(np.mean(update**2))
            projection_gap = float(
                (left_loss - right_loss - update_energy)
                / max(left_loss, 1e-12)
            )
            decomposition = decompose_score_update(
                eval_profiles[transition_index],
                eval_profiles[transition_index + 1],
                fitted[left_budget],
                fitted[right_budget],
            )
            profile_change = (
                eval_profiles[transition_index + 1]
                - eval_profiles[transition_index]
            )
            channel_change = (
                update
                + eval_residuals[transition_index + 1]
                - eval_residuals[transition_index]
            )
            path_reconstruction = float(np.max(np.abs(
                profile_change - channel_change
            )))
            if (
                np.isfinite(interval_records[left_budget]["radius"])
                and np.isfinite(interval_records[right_budget]["radius"])
            ):
                radius_ratio = float(
                    interval_records[right_budget]["radius"]
                    / max(
                        interval_records[left_budget]["radius"],
                        1e-12,
                    )
                )
            else:
                radius_ratio = np.nan
            left_nmse = metric_rows[-len(budgets) + transition_index]["nmse"]
            right_nmse = metric_rows[
                -len(budgets) + transition_index + 1
            ]["nmse"]
            risk_delta = (
                float(right_nmse - left_nmse)
                if np.isfinite(left_nmse) and np.isfinite(right_nmse)
                else np.nan
            )
            covariance = np.cov(
                probe_profiles[transition_index + 1] - external_zero,
                rowvar=False,
            )
            projection_metrics = (
                scorer_projection_metrics(
                    truth,
                    left_score,
                    right_score,
                    origin=np.asarray(world["true_zero"]),
                )
                if h1_enabled and truth_energy > 1e-12
                else {
                    "true_nmse_left": np.nan,
                    "true_nmse_right": np.nan,
                    "true_nmse_delta": np.nan,
                    "update_nmse": np.nan,
                    "projection_defect": np.nan,
                    "posterior_orthogonality": np.nan,
                    "projection_algebra_error": np.nan,
                }
            )
            record = {
                "repetition": repetition,
                "world": world_name,
                "arm": "main",
                "left_budget": left_budget,
                "right_budget": right_budget,
                "transition": f"{left_budget}->{right_budget}",
                "coherence_kappa": np.nan,
                "predictor_family": "",
                "predictor_probe_cv_kappa": np.nan,
                "update_mean_energy_ratio": update_mean_energy_ratio(update),
                "projection_identity_gap": projection_gap,
                "risk_delta_nmse": risk_delta,
                "proxy_loss_delta": float(right_loss - left_loss),
                "update_energy": update_energy,
                "radius_ratio": radius_ratio,
                "event_update_energy_ratio": decomposition[
                    "event_energy_ratio"
                ],
                "operator_update_energy_ratio": decomposition[
                    "operator_energy_ratio"
                ],
                "event_operator_cross_ratio": decomposition[
                    "cross_energy_ratio"
                ],
                "update_decomposition_error": decomposition[
                    "reconstruction_error"
                ],
                "path_reconstruction_error": path_reconstruction,
                "operator_action_cosine": operator_action_cosine(
                    fitted[left_budget],
                    fitted[right_budget],
                    covariance,
                ),
                "effective_df_delta": float(
                    fitted[right_budget]["effective_df"]
                    - fitted[left_budget]["effective_df"]
                ),
                **projection_metrics,
            }
            if world_name in coherence_worlds:
                probe_features = history_features(
                    panels["probe"],
                    probe_scores,
                    probe_residuals,
                    transition_index,
                    external_zero=external_zero,
                )
                eval_features = history_features(
                    panels["evaluation"],
                    eval_scores,
                    eval_residuals,
                    transition_index,
                    external_zero=external_zero,
                )
                predictor = fit_coherence_predictor(
                    probe_features,
                    (
                        probe_scores[transition_index + 1]
                        - probe_scores[transition_index]
                    ),
                    seed=predictor_seeds[transition_index],
                    folds=int(config["coherence_folds"]),
                    alphas=tuple(
                        float(value)
                        for value in config["coherence_alphas"]
                    ),
                )
                prediction = predict_coherence_update(
                    predictor,
                    eval_features,
                )
                record["coherence_kappa"] = coherence_kappa(
                    update,
                    prediction,
                )
                record["predictor_family"] = str(predictor["family"])
                record["predictor_probe_cv_kappa"] = float(
                    predictor["cv_kappa"]
                )
                for _, predictor_row in predictor["table"].iterrows():
                    predictor_rows.append({
                        "repetition": repetition,
                        "world": world_name,
                        "arm": "main",
                        "transition": f"{left_budget}->{right_budget}",
                        **predictor_row.to_dict(),
                    })
            transition_rows.append(record)
            main_transition_cache.append(record)

        if h1_enabled and world_name in cumulative_worlds:
            probe_initial = initial_observable_history(
                panels["probe"],
                probe_scores[0],
                probe_residuals[0],
                external_zero=external_zero,
            )
            evaluation_initial = initial_observable_history(
                panels["evaluation"],
                eval_scores[0],
                eval_residuals[0],
                external_zero=external_zero,
            )
            cumulative_predictor = fit_joint_cumulative_predictor(
                probe_initial,
                [
                    probe_scores[index] - probe_scores[0]
                    for index in range(1, len(budgets))
                ],
                seed=predictor_seeds[2 * (len(budgets) - 1)],
                folds=int(config["cumulative_folds"]),
                alphas=tuple(
                    float(value)
                    for value in config["cumulative_alphas"]
                ),
                ranks=tuple(
                    int(value)
                    for value in config["cumulative_ranks"]
                ),
                rff_components=int(config["cumulative_rff_components"]),
            )
            cumulative_predictions = predict_joint_cumulative(
                cumulative_predictor,
                evaluation_initial,
            )
            for _, predictor_row in cumulative_predictor["table"].iterrows():
                predictor_rows.append({
                    "repetition": repetition,
                    "world": world_name,
                    "arm": "cumulative_path",
                    "transition": (
                        f"{budgets[0]}->"
                        + ",".join(str(value) for value in budgets[1:])
                    ),
                    **predictor_row.to_dict(),
                })
            selected_cumulative = cumulative_predictor["candidate"]
            for horizon_index, right_budget in enumerate(budgets[1:]):
                update = eval_scores[horizon_index + 1] - eval_scores[0]
                prediction = cumulative_predictions[horizon_index]
                transition_rows.append({
                    "repetition": repetition,
                    "world": world_name,
                    "arm": "cumulative_path",
                    "left_budget": budgets[0],
                    "right_budget": right_budget,
                    "transition": f"{budgets[0]}->{right_budget}",
                    "coherence_kappa": cumulative_kappa(
                        update,
                        prediction,
                    ),
                    "predictor_family": str(
                        selected_cumulative["family"]
                    ),
                    "predictor_name": str(selected_cumulative["name"]),
                    "predictor_rank": int(selected_cumulative["rank"]),
                    "predictor_probe_cv_kappa": float(
                        cumulative_predictor["cv_kappa_pooled"]
                    ),
                    "update_mean_energy_ratio": (
                        update_mean_energy_ratio(update)
                    ),
                    "projection_identity_gap": np.nan,
                    "risk_delta_nmse": np.nan,
                    "proxy_loss_delta": np.nan,
                    "update_energy": float(np.mean(update**2)),
                    "radius_ratio": np.nan,
                    "event_update_energy_ratio": np.nan,
                    "operator_update_energy_ratio": np.nan,
                    "event_operator_cross_ratio": np.nan,
                    "update_decomposition_error": np.nan,
                    "path_reconstruction_error": np.nan,
                    "operator_action_cosine": np.nan,
                    "effective_df_delta": np.nan,
                    "true_nmse_left": np.nan,
                    "true_nmse_right": np.nan,
                    "true_nmse_delta": np.nan,
                    "update_nmse": np.nan,
                    "projection_defect": np.nan,
                    "posterior_orthogonality": np.nan,
                    "projection_algebra_error": np.nan,
                })

        if world_name == str(config["oscillating_assay_source_world"]):
            assay_probe = oscillating_assay_scores(
                probe_scores,
                external_zero=external_zero,
                amplitude=float(config["oscillating_assay_amplitude"]),
            )
            assay_eval = oscillating_assay_scores(
                eval_scores,
                external_zero=external_zero,
                amplitude=float(config["oscillating_assay_amplitude"]),
            )
            for transition_index, (left_budget, right_budget) in enumerate(
                zip(budgets[:-1], budgets[1:], strict=True)
            ):
                probe_features = history_features(
                    panels["probe"],
                    assay_probe,
                    probe_residuals,
                    transition_index,
                    external_zero=external_zero,
                )
                eval_features = history_features(
                    panels["evaluation"],
                    assay_eval,
                    eval_residuals,
                    transition_index,
                    external_zero=external_zero,
                )
                predictor = fit_coherence_predictor(
                    probe_features,
                    assay_probe[transition_index + 1]
                    - assay_probe[transition_index],
                    seed=predictor_seeds[
                        len(budgets) - 1 + transition_index
                    ],
                    folds=int(config["coherence_folds"]),
                    alphas=tuple(
                        float(value)
                        for value in config["coherence_alphas"]
                    ),
                )
                update = (
                    assay_eval[transition_index + 1]
                    - assay_eval[transition_index]
                )
                prediction = predict_coherence_update(
                    predictor,
                    eval_features,
                )
                transition_rows.append({
                    "repetition": repetition,
                    "world": world_name,
                    "arm": "oscillating_assay",
                    "left_budget": left_budget,
                    "right_budget": right_budget,
                    "transition": f"{left_budget}->{right_budget}",
                    "coherence_kappa": coherence_kappa(
                        update,
                        prediction,
                    ),
                    "predictor_family": str(predictor["family"]),
                    "predictor_probe_cv_kappa": float(
                        predictor["cv_kappa"]
                    ),
                    "update_mean_energy_ratio": (
                        update_mean_energy_ratio(update)
                    ),
                    "projection_identity_gap": np.nan,
                    "risk_delta_nmse": np.nan,
                    "proxy_loss_delta": np.nan,
                    "update_energy": float(np.mean(update**2)),
                    "radius_ratio": np.nan,
                    "event_update_energy_ratio": np.nan,
                    "operator_update_energy_ratio": np.nan,
                    "event_operator_cross_ratio": np.nan,
                    "update_decomposition_error": np.nan,
                    "path_reconstruction_error": np.nan,
                    "operator_action_cosine": np.nan,
                    "effective_df_delta": np.nan,
                })
                for _, predictor_row in predictor["table"].iterrows():
                    predictor_rows.append({
                        "repetition": repetition,
                        "world": world_name,
                        "arm": "oscillating_assay",
                        "transition": f"{left_budget}->{right_budget}",
                        **predictor_row.to_dict(),
                    })

    return (
        metric_rows,
        transition_rows,
        candidate_rows,
        predictor_rows,
        seeds,
    )


def _effects(
    metrics: pd.DataFrame,
    transitions: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    core = set(config["core_worlds"])
    first_budget = int(config["event_budgets"][0])
    last_budget = int(config["event_budgets"][-1])
    main = transitions[transitions["arm"] == "main"]
    core_transitions = main[main["world"].isin(core)]
    draws = int(config["summary_bootstrap_draws"])
    seed = int(config["_active_seed"]) ^ 0x37B
    rng = np.random.default_rng(seed)

    endpoint_rows: list[dict[str, Any]] = []
    radius_endpoint_rows: list[dict[str, Any]] = []
    for (repetition, world), group in metrics[
        metrics["world"].isin(core)
    ].groupby(["repetition", "world"]):
        low = group[group["event_budget"] == first_budget].iloc[0]
        high = group[group["event_budget"] == last_budget].iloc[0]
        endpoint_rows.append({
            "repetition": repetition,
            "world": world,
            "relative_nmse_reduction": float(
                1.0 - high["nmse"] / max(low["nmse"], 1e-12)
            ),
        })
        radius_endpoint_rows.append({
            "repetition": repetition,
            "world": world,
            "radius_endpoint_ratio": float(
                high["tolerance_radius"]
                / max(low["tolerance_radius"], 1e-12)
            )
            if (
                np.isfinite(high["tolerance_radius"])
                and np.isfinite(low["tolerance_radius"])
            )
            else np.nan,
        })
    endpoints = pd.DataFrame(endpoint_rows)
    radius_endpoints = pd.DataFrame(radius_endpoint_rows)
    endpoint_effects = {
        str(world): _interval(
            group["relative_nmse_reduction"].to_numpy(),
            rng=rng,
            draws=draws,
        )
        for world, group in endpoints.groupby("world")
    }
    radius_endpoint_effects = {
        str(world): _interval(
            group["radius_endpoint_ratio"].to_numpy(),
            rng=rng,
            draws=draws,
        )
        for world, group in radius_endpoints.groupby("world")
    }

    core_coverage = metrics[
        metrics["world"].isin(core)
        & metrics["interval_claim_allowed"].astype(bool)
    ]
    opportunity = main[
        main["world"] == "opportunity_schedule_drift"
    ]
    assay = transitions[
        transitions["arm"] == "oscillating_assay"
    ]
    effects = {
        "core_kappa_simultaneous": _simultaneous_bounds(
            core_transitions,
            value="coherence_kappa",
            cells=["world", "transition"],
            seed=seed + 1,
            draws=draws,
        ),
        "core_mean_update_simultaneous": _simultaneous_bounds(
            core_transitions,
            value="update_mean_energy_ratio",
            cells=["world", "transition"],
            seed=seed + 2,
            draws=draws,
        ),
        "core_risk_delta_simultaneous": _simultaneous_bounds(
            core_transitions,
            value="risk_delta_nmse",
            cells=["world", "transition"],
            seed=seed + 3,
            draws=draws,
        ),
        "core_radius_ratio_simultaneous": _simultaneous_bounds(
            core_transitions.dropna(subset=["radius_ratio"]),
            value="radius_ratio",
            cells=["world", "transition"],
            seed=seed + 4,
            draws=draws,
        ),
        "core_coverage_simultaneous": _simultaneous_bounds(
            core_coverage,
            value="conditional_coverage",
            cells=["world", "event_budget"],
            seed=seed + 5,
            draws=draws,
        ),
        "endpoint_nmse_reduction": endpoint_effects,
        "endpoint_radius_ratio": radius_endpoint_effects,
        "opportunity_kappa_simultaneous": _simultaneous_bounds(
            opportunity,
            value="coherence_kappa",
            cells=["transition"],
            seed=seed + 6,
            draws=draws,
        ),
        "oscillating_kappa_simultaneous": _simultaneous_bounds(
            assay,
            value="coherence_kappa",
            cells=["transition"],
            seed=seed + 7,
            draws=draws,
        ),
        "core_projection_gap": _simultaneous_bounds(
            core_transitions,
            value="projection_identity_gap",
            cells=["world", "transition"],
            seed=seed + 8,
            draws=draws,
        ),
        "core_effective_df_nonnegative_delta_rate": float(
            (core_transitions["effective_df_delta"] >= -1e-8).mean()
        ),
        "maximum_reconstruction_error": float(max(
            metrics["score_reconstruction_error"].max(),
            transitions["update_decomposition_error"].max(),
            transitions["path_reconstruction_error"].max(),
        )),
        "maximum_prefix_identity_error": float(
            metrics["prefix_identity_error"].max()
        ),
        "reference_switch_origin_rms": float(
            metrics[
                metrics["world"] == "reference_panel_switch"
            ]["reference_origin_rms_difference"].mean()
        ),
        "informative_precision_coverage": float(
            metrics[
                (metrics["world"] == "informative_precision_dense")
                & metrics["interval_claim_allowed"].astype(bool)
            ]["conditional_coverage"].mean()
        ),
        "student_t5_coverage": float(
            metrics[
                (metrics["world"] == "student_t5_dense")
                & metrics["interval_claim_allowed"].astype(bool)
            ]["conditional_coverage"].mean()
        ),
    }
    if bool(config.get("enable_h1_diagnostics", False)):
        cumulative = transitions[
            transitions["arm"] == "cumulative_path"
        ]
        cumulative_pooled = (
            cumulative.groupby(
                ["repetition", "world"],
                as_index=False,
            )["coherence_kappa"].mean()
            .rename(columns={"coherence_kappa": "cumulative_kappa_pooled"})
        )
        core_cumulative = cumulative_pooled[
            cumulative_pooled["world"].isin(core)
        ]
        opportunity_cumulative = cumulative_pooled[
            cumulative_pooled["world"] == "opportunity_schedule_drift"
        ]
        effects.update({
            "core_true_nmse_delta_one_sided": (
                _one_sided_familywise_bounds(
                    core_transitions,
                    value="true_nmse_delta",
                    cells=["world", "transition"],
                    seed=seed + 20,
                    draws=draws,
                    confidence=0.95,
                )
            ),
            "core_projection_defect_equivalence": (
                _one_sided_familywise_bounds(
                    core_transitions,
                    value="projection_defect",
                    cells=["world", "transition"],
                    seed=seed + 21,
                    draws=draws,
                    confidence=0.975,
                )
            ),
            "core_cumulative_kappa_pooled": (
                _one_sided_familywise_bounds(
                    core_cumulative,
                    value="cumulative_kappa_pooled",
                    cells=["world"],
                    seed=seed + 22,
                    draws=draws,
                    confidence=0.95,
                )
            ),
            "opportunity_cumulative_kappa_pooled": (
                _one_sided_familywise_bounds(
                    opportunity_cumulative,
                    value="cumulative_kappa_pooled",
                    cells=["world"],
                    seed=seed + 23,
                    draws=draws,
                    confidence=0.95,
                )
            ),
            "maximum_projection_algebra_error": float(
                core_transitions["projection_algebra_error"].max()
            ),
        })
    return effects


def _integrity(
    metrics: pd.DataFrame,
    transitions: pd.DataFrame,
    candidates: pd.DataFrame,
    seeds: list[int],
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    repetitions = int(config["_active_repetitions"])
    worlds = len(config["worlds"])
    budgets = len(config["event_budgets"])
    transitions_per_world = budgets - 1
    expected_metrics = repetitions * worlds * budgets
    expected_main_transitions = repetitions * worlds * transitions_per_world
    expected_assay = repetitions * transitions_per_world
    expected_cumulative = (
        repetitions
        * len(config.get("cumulative_worlds", []))
        * transitions_per_world
        if bool(config.get("enable_h1_diagnostics", False))
        else 0
    )
    main_candidates = candidates[candidates["arm"] == "main"]
    main_transitions = transitions[transitions["arm"] == "main"]
    coherence_transitions = transitions[
        transitions["arm"].isin([
            "oscillating_assay",
            "cumulative_path",
        ])
    ]
    core_main = main_transitions[
        main_transitions["world"].isin(config["core_worlds"])
    ]
    allowed = metrics["interval_claim_allowed"].astype(bool)
    finite_required = metrics[
        [
            "selected_effective_df",
            "proxy_nmse",
            "score_reconstruction_error",
            "prefix_identity_error",
        ]
    ].to_numpy(dtype=float)
    return {
        "metric_scale_exact_nmse": bool(
            metrics["metric_scale"].eq("NMSE").all()
        ),
        "numeric": bool(
            np.isfinite(finite_required).all()
            and np.isfinite(
                transitions[
                    [
                        "update_mean_energy_ratio",
                        "update_energy",
                    ]
                ].to_numpy(dtype=float)
            ).all()
            and np.isfinite(
                main_transitions[
                    [
                        "projection_identity_gap",
                        "event_update_energy_ratio",
                        "operator_update_energy_ratio",
                        "event_operator_cross_ratio",
                        "update_decomposition_error",
                        "path_reconstruction_error",
                        "operator_action_cosine",
                        "effective_df_delta",
                    ]
                ].to_numpy(dtype=float)
            ).all()
            and np.isfinite(
                coherence_transitions["coherence_kappa"].to_numpy(
                    dtype=float
                )
            ).all()
            and (
                not bool(config.get("enable_h1_diagnostics", False))
                or (
                    np.isfinite(
                        core_main[
                            [
                                "true_nmse_left",
                                "true_nmse_right",
                                "true_nmse_delta",
                                "update_nmse",
                                "projection_defect",
                                "posterior_orthogonality",
                                "projection_algebra_error",
                            ]
                        ].to_numpy(dtype=float)
                    ).all()
                )
            )
            and np.isfinite(
                metrics.loc[
                    allowed,
                    [
                        "conditional_coverage",
                        "tolerance_radius",
                        "interval_tolerance_order",
                        "interval_achieved_confidence",
                    ],
                ].to_numpy(dtype=float)
            ).all()
        ),
        "metric_rows": int(len(metrics)),
        "expected_metric_rows": int(expected_metrics),
        "transition_rows": int(len(transitions)),
        "expected_transition_rows": int(
            expected_main_transitions
            + expected_assay
            + expected_cumulative
        ),
        "seed_count": int(len(seeds)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "single_main_candidate": bool(
            main_candidates.groupby(["repetition", "world"])[
                "selected"
            ].sum().eq(1).all()
        ),
        "shared_candidate_across_budgets": bool(
            metrics.groupby(["repetition", "world"])[
                "selected_name"
            ].nunique().eq(1).all()
        ),
        "truth_constant_across_budgets": bool(
            metrics.groupby(["repetition", "world"])[
                "truth_fingerprint"
            ].nunique().eq(1).all()
        ),
        "maximum_prefix_identity_error": float(
            metrics["prefix_identity_error"].max()
        ),
        "maximum_reconstruction_error": float(max(
            metrics["score_reconstruction_error"].max(),
            transitions["update_decomposition_error"].max(),
            transitions["path_reconstruction_error"].max(),
        )),
    }


def _preview_checks(
    effects: dict[str, Any],
    *,
    config: dict[str, Any],
) -> dict[str, bool]:
    gates = config["candidate_gates"]
    opportunity_cells = effects[
        "opportunity_kappa_simultaneous"
    ].get("cells", {})
    assay_cells = effects["oscillating_kappa_simultaneous"].get(
        "cells", {}
    )
    endpoint = effects["endpoint_nmse_reduction"]
    radius_endpoint = effects["endpoint_radius_ratio"]
    coverage = effects["core_coverage_simultaneous"]
    coverage_means = [
        value["mean"] for value in coverage.get("cells", {}).values()
    ]
    checks = {
        "core_kappa": (
            effects["core_kappa_simultaneous"].get(
                "maximum_upper", np.inf
            )
            <= gates["maximum_core_kappa_upper"]
        ),
        "core_mean_update": (
            effects["core_mean_update_simultaneous"].get(
                "maximum_upper", np.inf
            )
            <= gates["maximum_mean_update_energy_upper"]
        ),
        "core_adjacent_risk": (
            effects["core_risk_delta_simultaneous"].get(
                "maximum_upper", np.inf
            )
            <= gates["maximum_adjacent_nmse_delta_upper"]
        ),
        "core_endpoint_risk": bool(
            endpoint
            and min(value["lower"] for value in endpoint.values())
            >= gates["minimum_endpoint_nmse_reduction_lower"]
        ),
        "core_adjacent_radius": (
            effects["core_radius_ratio_simultaneous"].get(
                "maximum_upper", np.inf
            )
            <= gates["maximum_adjacent_radius_ratio_upper"]
        ),
        "core_endpoint_radius": bool(
            radius_endpoint
            and max(value["upper"] for value in radius_endpoint.values())
            <= gates["maximum_endpoint_radius_ratio_upper"]
        ),
        "coverage_lower": (
            coverage.get("minimum_lower", -np.inf)
            >= gates["minimum_core_coverage_lower"]
        ),
        "coverage_upper": (
            bool(coverage_means)
            and max(coverage_means)
            <= gates["maximum_core_mean_coverage"]
        ),
        "oscillating_code_path": (
            sum(
                value["lower95_simultaneous"]
                >= gates["minimum_control_kappa_lower"]
                for value in assay_cells.values()
            )
            >= 3
        ),
        "information_conservation": (
            effects["maximum_reconstruction_error"]
            <= gates["maximum_reconstruction_error"]
        ),
        "nested_prefix": (
            effects["maximum_prefix_identity_error"]
            <= gates["maximum_prefix_identity_error"]
        ),
    }
    if bool(config.get("enable_h1_diagnostics", False)):
        projection = effects["core_projection_defect_equivalence"]
        projection_cells = projection.get("cells", {})
        checks.update({
            "core_true_nmse_delta": (
                effects["core_true_nmse_delta_one_sided"].get(
                    "maximum_upper",
                    np.inf,
                )
                <= gates["maximum_true_nmse_delta_upper"]
            ),
            "core_projection_equivalence": bool(
                projection_cells
                and min(
                    value["one_sided_familywise_lower"]
                    for value in projection_cells.values()
                )
                >= -gates["projection_defect_margin"]
                and max(
                    value["one_sided_familywise_upper"]
                    for value in projection_cells.values()
                )
                <= gates["projection_defect_margin"]
            ),
            "projection_algebra": (
                effects["maximum_projection_algebra_error"]
                <= gates["maximum_projection_algebra_error"]
            ),
            "core_cumulative_path": (
                effects["core_cumulative_kappa_pooled"].get(
                    "maximum_upper",
                    np.inf,
                )
                <= gates["maximum_core_cumulative_kappa_upper"]
            ),
            "opportunity_cumulative_path": (
                effects["opportunity_cumulative_kappa_pooled"].get(
                    "minimum_lower",
                    -np.inf,
                )
                >= gates["minimum_opportunity_cumulative_kappa_lower"]
            ),
        })
    else:
        checks["opportunity_control"] = (
            sum(
                value["lower95_simultaneous"]
                >= gates["minimum_control_kappa_lower"]
                for value in opportunity_cells.values()
            )
            >= 3
        )
    return checks


def _decision(
    *,
    effects: dict[str, Any],
    integrity: dict[str, Any],
    config: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    integrity_pass = bool(
        integrity["metric_scale_exact_nmse"]
        and integrity["numeric"]
        and integrity["metric_rows"] == integrity["expected_metric_rows"]
        and integrity["transition_rows"] == integrity[
            "expected_transition_rows"
        ]
        and integrity["seed_uniqueness"]
        and integrity["single_main_candidate"]
        and integrity["shared_candidate_across_budgets"]
        and integrity["truth_constant_across_budgets"]
        and integrity["maximum_prefix_identity_error"]
        <= config["candidate_gates"]["maximum_prefix_identity_error"]
        and integrity["maximum_reconstruction_error"]
        <= config["candidate_gates"]["maximum_reconstruction_error"]
    )
    preview = _preview_checks(effects, config=config)
    if not integrity_pass:
        status = "V8_RESOLUTION_FILTRATION_V37H_STOP_INTEGRITY"
    elif mode == "smoke":
        status = "V8_RESOLUTION_FILTRATION_V37H_SMOKE_PASS"
    elif mode == "discovery":
        status = "V8_RESOLUTION_FILTRATION_V37H_DISCOVERY_COMPLETE"
    else:
        status = (
            "V8_RESOLUTION_FILTRATION_V37H_PASS_CORE"
            if all(preview.values())
            else "V8_RESOLUTION_FILTRATION_V37H_REFUTE_OR_STOP"
        )
    return {
        "status": status,
        "integrity_pass": integrity_pass,
        "candidate_gate_preview": preview,
        "effects": effects,
        "integrity": integrity,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_parent(config: dict[str, Any]) -> dict[str, str]:
    parent = config["required_parent_seal"]
    observed = sha256_file(ROOT / parent["path"])
    if observed != parent["sha256"]:
        raise RuntimeError("V3.7G parent seal mismatch")
    return {"status": "V37G_PARENT_SEAL_PASS", "sha256": observed}


def _report(
    decision: dict[str, Any],
    metric_summary: pd.DataFrame,
    transition_summary: pd.DataFrame,
) -> str:
    return f"""# V8 Resolution Filtration V3.7H

Decision: `{decision["status"]}`

## Candidate gate preview

```json
{json.dumps(decision["candidate_gate_preview"], indent=2)}
```

## Effects

```json
{json.dumps(decision["effects"], indent=2)}
```

## Metric summary

{metric_summary.to_markdown(index=False)}

## Transition summary

{transition_summary.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_resolution_filtration_v37h_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_resolution_filtration/v37h_discovery",
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
        config["_active_repetitions"] = int(config["smoke_repetitions"])
        config["_active_interval_bootstrap_replicates"] = int(
            config["smoke_interval_bootstrap_replicates"]
        )
    elif args.mode == "confirmation":
        if "canonical_seed" not in config:
            raise RuntimeError("confirmation config is not yet frozen")
        config["_active_seed"] = int(config["canonical_seed"])
        config["_active_repetitions"] = int(config["repetitions"])
        config["_active_interval_bootstrap_replicates"] = int(
            config["interval_bootstrap_replicates"]
        )
    else:
        config["_active_seed"] = int(config["seed"])
        config["_active_repetitions"] = int(config["repetitions"])
        config["_active_interval_bootstrap_replicates"] = int(
            config["interval_bootstrap_replicates"]
        )
    parent = _verify_parent(config)
    root = np.random.SeedSequence(int(config["_active_seed"]))
    children = root.spawn(int(config["_active_repetitions"]))
    payloads = [
        (config, repetition, tuple(child.spawn_key))
        for repetition, child in enumerate(children)
    ]
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"])
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    metrics = pd.DataFrame([
        row for part, _, _, _, _ in nested for row in part
    ])
    transitions = pd.DataFrame([
        row for _, part, _, _, _ in nested for row in part
    ])
    candidates = pd.DataFrame([
        row for _, _, part, _, _ in nested for row in part
    ])
    predictors = pd.DataFrame([
        row for _, _, _, part, _ in nested for row in part
    ])
    seeds = [
        seed for _, _, _, _, part in nested for seed in part
    ]
    effects = _effects(metrics, transitions, config=config)
    integrity = _integrity(
        metrics,
        transitions,
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
    metric_summary = metrics.groupby(
        ["world", "event_budget"],
        as_index=False,
    ).mean(numeric_only=True)
    transition_summary = transitions.groupby(
        ["world", "arm", "transition"],
        as_index=False,
    ).mean(numeric_only=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    transitions.to_csv(args.output_dir / "transition_metrics.csv", index=False)
    candidates.to_csv(args.output_dir / "candidate_metrics.csv", index=False)
    predictors.to_csv(args.output_dir / "predictor_metrics.csv", index=False)
    metric_summary.to_csv(
        args.output_dir / "metric_summary.csv",
        index=False,
    )
    transition_summary.to_csv(
        args.output_dir / "transition_summary.csv",
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
        _report(decision, metric_summary, transition_summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[ROOT / config["required_parent_seal"]["path"]],
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
        "status": decision["status"],
        "metric_rows": len(metrics),
        "transition_rows": len(transitions),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
