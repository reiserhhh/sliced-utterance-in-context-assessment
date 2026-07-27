#!/usr/bin/env python3
"""Run SUICA V3.7F external-zero and residual-sufficiency experiments."""
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
from suica_core.v8_author_routing_operator import (  # noqa: E402
    fit_reference_router,
)
from suica_core.v8_external_zero_uncertainty import (  # noqa: E402
    ExternalZeroWorldSpec,
    apply_external_zero_denoiser,
    confidence_region_metrics,
    cross_validated_external_rank_selection,
    empirical_parametric_sample,
    estimate_external_zero,
    fit_error_asymptote,
    fit_external_zero_denoiser,
    functional_anova_energy,
    mdc_metrics,
    normalized_mse,
    resample_counts_fast,
    residual_sufficiency_metrics,
    simulate_external_zero_world,
    subset_authors,
    true_observed_profile,
    true_stable_profile,
    with_event_budget,
)
from suica_core.v8_adaptive_rank_reference import (  # noqa: E402
    apply_population_shift,
)
from suica_core.v8_adaptive_rank_reference import (  # noqa: E402
    estimate_standardized_profile,
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


def _direction_cosine(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    return float(
        np.dot(x, y)
        / max(np.linalg.norm(x) * np.linalg.norm(y), 1e-12)
    )


def _interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int = 10_000,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return {"mean": float("nan"), "lower95": float("nan"), "upper95": float("nan")}
    index = rng.integers(0, len(vector), size=(draws, len(vector)))
    mean = vector[index].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(mean, 0.025)),
        "upper95": float(np.quantile(mean, 0.975)),
    }


def _partition(
    order: np.ndarray,
    config: dict[str, Any],
) -> dict[str, np.ndarray]:
    cursor = 0
    result: dict[str, np.ndarray] = {}
    for key in (
        "router_reference_authors",
        "zero_reference_authors",
        "calibration_authors",
        "evaluation_authors",
    ):
        size = int(config[key])
        label = key.removesuffix("_authors")
        result[label] = order[cursor : cursor + size]
        cursor += size
    return result


def _fit_pipeline(
    panel: dict[str, Any],
    partitions: dict[str, np.ndarray],
    discovery: np.ndarray,
    *,
    config: dict[str, Any],
    selection_seed: int,
) -> dict[str, Any]:
    reference_fit = fit_reference_router(
        subset_authors(panel, partitions["router_reference"]),
        discovery,
    )
    zero_panel = subset_authors(panel, partitions["zero_reference"])
    external_zero = estimate_external_zero(
        zero_panel,
        discovery,
        reference_fit=reference_fit,
    )
    calibration = subset_authors(panel, partitions["calibration"])
    left = estimate_standardized_profile(
        calibration,
        discovery,
        reference_fit=reference_fit,
        sessions=0,
    )
    right = estimate_standardized_profile(
        calibration,
        discovery,
        reference_fit=reference_fit,
        sessions=1,
    )
    selected_rank, table = cross_validated_external_rank_selection(
        left,
        right,
        external_zero=external_zero,
        candidates=config["candidate_ranks"],
        folds=int(config["selection_folds"]),
        seed=int(selection_seed),
    )
    hard = fit_external_zero_denoiser(
        left,
        right,
        external_zero=external_zero,
        rank=selected_rank,
    )
    soft = fit_external_zero_denoiser(
        left,
        right,
        external_zero=external_zero,
        rank=None,
        soft=True,
    )
    return {
        "reference_fit": reference_fit,
        "external_zero": external_zero,
        "calibration_left": left,
        "calibration_right": right,
        "selected_rank": selected_rank,
        "selection_table": table,
        "hard": hard,
        "soft": soft,
    }


def _reference_zero_variance(
    panel: dict[str, Any],
    partitions: dict[str, np.ndarray],
    discovery: np.ndarray,
    *,
    sizes: list[int],
    draws: int,
    seeds: list[np.random.SeedSequence],
) -> dict[int, float]:
    router = partitions["router_reference"]
    zero = partitions["zero_reference"]
    clouds: dict[int, list[np.ndarray]] = {size: [] for size in sizes}
    for draw in range(draws):
        rng = np.random.default_rng(seeds[draw])
        for size in sizes:
            router_draw = rng.choice(router, size=size, replace=True)
            zero_draw = rng.choice(zero, size=size, replace=True)
            fit = fit_reference_router(
                subset_authors(panel, router_draw),
                discovery,
            )
            origin = estimate_external_zero(
                subset_authors(panel, zero_draw),
                discovery,
                reference_fit=fit,
            )
            clouds[size].append(origin)
    return {
        size: float(np.mean(np.var(
            np.stack(values),
            axis=0,
            ddof=1,
        )))
        for size, values in clouds.items()
    }


def _nested_uncertainty(
    *,
    latent: dict[str, Any],
    panel: dict[str, Any],
    partitions: dict[str, np.ndarray],
    pipeline: dict[str, Any],
    discovery: np.ndarray,
    config: dict[str, Any],
    seed_sequence: np.random.SeedSequence,
) -> tuple[dict[str, Any], list[int]]:
    tracked = int(config["tracked_authors"])
    r_draws = int(config["bootstrap_reference_draws"])
    k_draws = int(config["bootstrap_selection_draws"])
    e_draws = int(config["bootstrap_event_draws"])
    root_children = seed_sequence.spawn(
        r_draws + k_draws + e_draws + r_draws
    )
    r_sequences = root_children[:r_draws]
    k_sequences = root_children[r_draws : r_draws + k_draws]
    e_sequences = root_children[
        r_draws + k_draws : r_draws + k_draws + e_draws
    ]
    ref_sensitivity_sequences = root_children[-r_draws:]
    seeds = [_uint64(child) for child in root_children]

    evaluation_latent = subset_authors(
        latent,
        partitions["evaluation"],
    )
    evaluation_observed = subset_authors(
        panel,
        partitions["evaluation"],
    )
    empirical = empirical_parametric_sample(evaluation_observed)
    event_source = (
        evaluation_latent
        if bool(config.get("oracle_event_calibration", True))
        else empirical
    )
    event_panels = [
        resample_counts_fast(
            event_source,
            np.random.default_rng(sequence),
        )
        for sequence in e_sequences
    ]
    router_indices = partitions["router_reference"]
    zero_indices = partitions["zero_reference"]
    calibration_indices = partitions["calibration"]
    reference_draws = []
    for sequence in r_sequences:
        rng = np.random.default_rng(sequence)
        reference_draws.append({
            "router": rng.choice(
                router_indices,
                size=len(router_indices),
                replace=True,
            ),
            "zero": rng.choice(
                zero_indices,
                size=len(zero_indices),
                replace=True,
            ),
        })
    selection_draws = []
    for sequence in k_sequences:
        rng = np.random.default_rng(sequence)
        selection_draws.append({
            "index": rng.integers(
                0,
                len(calibration_indices),
                size=len(calibration_indices),
            ),
            "seed": int(rng.integers(0, np.iinfo(np.int32).max)),
        })

    cloud = np.empty((
        r_draws,
        k_draws,
        e_draws,
        tracked,
        int(config["profile_dimension"]),
    ))
    selected_ranks = np.empty((r_draws, k_draws), dtype=int)
    for r_index, reference_draw in enumerate(reference_draws):
        reference_fit = fit_reference_router(
            subset_authors(panel, reference_draw["router"]),
            discovery,
        )
        external_zero = estimate_external_zero(
            subset_authors(panel, reference_draw["zero"]),
            discovery,
            reference_fit=reference_fit,
        )
        calibration = subset_authors(panel, calibration_indices)
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
        event_profiles = [
            estimate_standardized_profile(
                event_panel,
                discovery,
                reference_fit=reference_fit,
            )[:tracked]
            for event_panel in event_panels
        ]
        for k_index, selection_draw in enumerate(selection_draws):
            selected = selection_draw["index"]
            rank, _ = cross_validated_external_rank_selection(
                calibration_left[selected],
                calibration_right[selected],
                external_zero=external_zero,
                candidates=config["candidate_ranks"],
                folds=int(config["selection_folds"]),
                seed=int(selection_draw["seed"]),
            )
            selected_ranks[r_index, k_index] = rank
            denoiser = fit_external_zero_denoiser(
                calibration_left[selected],
                calibration_right[selected],
                external_zero=external_zero,
                rank=rank,
            )
            for e_index, profile in enumerate(event_profiles):
                cloud[r_index, k_index, e_index] = (
                    apply_external_zero_denoiser(profile, denoiser)
                )

    base_truth = true_stable_profile(
        evaluation_latent,
        discovery,
        reference_fit=pipeline["reference_fit"],
    )[:tracked]
    target = apply_external_zero_denoiser(
        base_truth,
        pipeline["hard"],
    )
    flattened = cloud.reshape(-1, tracked, cloud.shape[-1])
    full_region = confidence_region_metrics(flattened, target)

    fixed_event = np.stack([
        apply_external_zero_denoiser(
            estimate_standardized_profile(
                event_panel,
                discovery,
                reference_fit=pipeline["reference_fit"],
            )[:tracked],
            pipeline["hard"],
        )
        for event_panel in event_panels
    ])
    event_region = confidence_region_metrics(fixed_event, target)
    mdc = mdc_metrics(
        fixed_event,
        rng=np.random.default_rng(
            int(config["_active_seed"]) ^ 0x37F0
        ),
    )
    anova = functional_anova_energy(cloud)
    sizes = [int(value) for value in config["reference_sizes"]]
    reference_variance = _reference_zero_variance(
        panel,
        partitions,
        discovery,
        sizes=sizes,
        draws=r_draws,
        seeds=ref_sensitivity_sequences,
    )
    small = min(sizes)
    large = max(sizes)
    reduction = (
        reference_variance[small] - reference_variance[large]
    ) / max(reference_variance[small], 1e-12)
    return {
        "event_coverage": event_region["coverage"],
        "event_median_radius": event_region["median_radius"],
        "full_coverage": full_region["coverage"],
        "full_median_radius": full_region["median_radius"],
        "anova_reconstruction_error": anova["reconstruction_error"],
        "variance_reference": anova["reference"],
        "variance_selection": anova["selection"],
        "variance_event": anova["event"],
        "variance_interactions": float(
            anova["reference_selection"]
            + anova["reference_event"]
            + anova["selection_event"]
            + anova["three_way"]
        ),
        "reference_variance_small": reference_variance[small],
        "reference_variance_large": reference_variance[large],
        "reference_variance_reduction": float(reduction),
        "rank_selection_sd": float(np.std(selected_ranks, ddof=1)),
        **mdc,
    }, seeds


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    (
        latent_sequence,
        partition_sequence,
        panel_parent,
        selection_parent,
        uncertainty_parent,
        shift_parent,
    ) = root.spawn(6)
    total_authors = sum(
        int(config[key])
        for key in (
            "router_reference_authors",
            "zero_reference_authors",
            "calibration_authors",
            "evaluation_authors",
        )
    )
    order = np.random.default_rng(
        partition_sequence
    ).permutation(total_authors)
    partitions = _partition(order, config)
    overlap = sum(
        len(set(partitions[left]) & set(partitions[right]))
        for index, left in enumerate(partitions)
        for right in list(partitions)[index + 1 :]
    )
    discovery = np.arange(int(config["discovery_contexts"]))
    rows: list[dict[str, Any]] = []
    uncertainty_rows: list[dict[str, Any]] = []
    latent_world_sequences = latent_sequence.spawn(len(config["worlds"]))
    all_seeds = [_uint64(partition_sequence)]
    world_sequences = panel_parent.spawn(len(config["worlds"]))
    selection_sequences = selection_parent.spawn(
        len(config["worlds"]) * len(config["event_budgets"])
    )
    uncertainty_sequences = uncertainty_parent.spawn(
        len(config["worlds"]) * len(config["event_budgets"])
    )
    shift_sequences = shift_parent.spawn(
        len(config["worlds"]) * len(config["event_budgets"])
    )
    selection_iterator = iter(selection_sequences)
    uncertainty_iterator = iter(uncertainty_sequences)
    shift_iterator = iter(shift_sequences)
    for world_index, world_name in enumerate(config["worlds"]):
        latent_seed = _uint64(latent_world_sequences[world_index])
        all_seeds.append(latent_seed)
        latent = simulate_external_zero_world(
            seed=latent_seed,
            spec=ExternalZeroWorldSpec(
                authors=total_authors,
                world=str(world_name),
                events_per_context_session=max(config["event_budgets"]),
                sessions=int(config["sessions"]),
                discovery_contexts=int(config["discovery_contexts"]),
                confirmation_contexts=int(config["confirmation_contexts"]),
                extrapolation_contexts=int(config["extrapolation_contexts"]),
                author_rms=float(config["author_rms"]),
                author_context_rms=float(
                    config["author_context_rms"]
                ),
                state_rms=float(config["state_rms"]),
                dense_exponent=float(config["dense_exponent"]),
            ),
        )
        budget_sequences = world_sequences[world_index].spawn(
            len(config["event_budgets"])
        )
        for budget_index, event_budget in enumerate(
            config["event_budgets"]
        ):
            selection_sequence = next(selection_iterator)
            uncertainty_sequence = next(uncertainty_iterator)
            shift_sequence = next(shift_iterator)
            panel_sequence = budget_sequences[budget_index]
            all_seeds.extend([
                _uint64(panel_sequence),
                _uint64(selection_sequence),
                _uint64(shift_sequence),
            ])
            budget_latent = with_event_budget(latent, int(event_budget))
            panel = resample_counts_fast(
                budget_latent,
                np.random.default_rng(panel_sequence),
            )
            pipeline = _fit_pipeline(
                panel,
                partitions,
                discovery,
                config=config,
                selection_seed=_uint64(selection_sequence),
            )
            evaluation = subset_authors(
                panel,
                partitions["evaluation"],
            )
            evaluation_latent = subset_authors(
                budget_latent,
                partitions["evaluation"],
            )
            left = estimate_standardized_profile(
                evaluation,
                discovery,
                reference_fit=pipeline["reference_fit"],
                sessions=0,
            )
            right = estimate_standardized_profile(
                evaluation,
                discovery,
                reference_fit=pipeline["reference_fit"],
                sessions=1,
            )
            combined = estimate_standardized_profile(
                evaluation,
                discovery,
                reference_fit=pipeline["reference_fit"],
            )
            stable_truth = true_stable_profile(
                evaluation_latent,
                discovery,
                reference_fit=pipeline["reference_fit"],
            )
            observed_infinite = true_observed_profile(
                evaluation_latent,
                discovery,
                reference_fit=pipeline["reference_fit"],
            )
            hard_score = apply_external_zero_denoiser(
                combined,
                pipeline["hard"],
            )
            soft_score = apply_external_zero_denoiser(
                combined,
                pipeline["soft"],
            )
            hard_infinite = apply_external_zero_denoiser(
                observed_infinite,
                pipeline["hard"],
            )
            soft_infinite = apply_external_zero_denoiser(
                observed_infinite,
                pipeline["soft"],
            )
            hard_truth_projection = apply_external_zero_denoiser(
                stable_truth,
                pipeline["hard"],
            )
            soft_truth_projection = apply_external_zero_denoiser(
                stable_truth,
                pipeline["soft"],
            )
            use_hard_full_space = bool(
                int(pipeline["selected_rank"])
                == int(config["profile_dimension"])
            )
            conserving_score = (
                hard_score if use_hard_full_space else soft_score
            )
            conserving_infinite = (
                hard_infinite if use_hard_full_space else soft_infinite
            )
            conserving_truth_projection = (
                hard_truth_projection
                if use_hard_full_space
                else soft_truth_projection
            )
            residual = residual_sufficiency_metrics(
                left,
                right,
                denoiser=pipeline["hard"],
                neighbor_count=int(config["neighbor_count"]),
            )
            oracle_basis = np.asarray(
                budget_latent["components"]["stable_loading"][:, :12],
                dtype=float,
            )
            oracle_projector = oracle_basis @ oracle_basis.T
            oracle_residual = residual_sufficiency_metrics(
                left,
                right,
                denoiser={
                    "external_zero": pipeline["external_zero"],
                    "projector": oracle_projector,
                    "orthogonal_projector": oracle_projector,
                },
                neighbor_count=int(config["neighbor_count"]),
            )
            permutation = np.random.default_rng(
                int(_uint64(selection_sequence)) ^ 0xA11CE
            ).permutation(len(right))
            residual_permuted = residual_sufficiency_metrics(
                left,
                right,
                denoiser=pipeline["hard"],
                neighbor_count=int(config["neighbor_count"]),
                permutation=permutation,
            )
            score_alone = apply_external_zero_denoiser(
                combined[: int(config["tracked_authors"])],
                pipeline["hard"],
            )
            score_together = hard_score[
                : int(config["tracked_authors"])
            ]
            row: dict[str, Any] = {
                "repetition": repetition,
                "spawn_key": json.dumps(spawn_key),
                "world": str(world_name),
                "event_budget": int(event_budget),
                "latent_seed": latent_seed,
                "panel_seed": _uint64(panel_sequence),
                "selection_seed": _uint64(selection_sequence),
                "author_partition_fingerprint": _fingerprint(order),
                "author_overlap": int(overlap),
                "selected_rank": int(pipeline["selected_rank"]),
                "soft_effective_rank": int(pipeline["soft"]["rank"]),
                "external_zero_norm": float(np.linalg.norm(
                    pipeline["external_zero"]
                )),
                "evaluation_cohort_invariance_error": float(
                    np.max(np.abs(score_alone - score_together))
                ),
                "hard_total_nmse": normalized_mse(
                    hard_score,
                    stable_truth,
                ),
                "soft_total_nmse": normalized_mse(
                    soft_score,
                    stable_truth,
                ),
                "conserving_total_nmse": normalized_mse(
                    conserving_score,
                    stable_truth,
                ),
                "raw_total_nmse": normalized_mse(
                    combined,
                    stable_truth,
                ),
                "hard_event_nmse": normalized_mse(
                    hard_score,
                    hard_infinite,
                ),
                "soft_event_nmse": normalized_mse(
                    soft_score,
                    soft_infinite,
                ),
                "hard_capacity_floor": normalized_mse(
                    hard_truth_projection,
                    stable_truth,
                ),
                "soft_capacity_floor": normalized_mse(
                    soft_truth_projection,
                    stable_truth,
                ),
                "conserving_capacity_floor": normalized_mse(
                    conserving_truth_projection,
                    stable_truth,
                ),
                "hard_infinite_total_floor": normalized_mse(
                    hard_infinite,
                    stable_truth,
                ),
                "soft_infinite_total_floor": normalized_mse(
                    soft_infinite,
                    stable_truth,
                ),
                "conserving_infinite_total_floor": normalized_mse(
                    conserving_infinite,
                    stable_truth,
                ),
                "conserving_used_hard_full_space": (
                    use_hard_full_space
                ),
                **residual,
                "oracle_residual_hard_neighbor_auc": (
                    oracle_residual["residual_hard_neighbor_auc"]
                ),
                "permuted_residual_hard_neighbor_auc": (
                    residual_permuted["residual_hard_neighbor_auc"]
                ),
                "population_shift_direction_cosine": np.nan,
                "population_shift_amplitude": np.nan,
            }
            if (
                str(world_name) == "hard_rank12"
                and int(event_budget)
                == int(config["primary_budget"])
            ):
                shift = np.asarray(
                    budget_latent["components"]["stable_loading"][:, 0],
                    dtype=float,
                )
                shift *= float(config["population_shift_rms"]) / max(
                    float(np.sqrt(np.mean(shift**2))),
                    1e-12,
                )
                shifted = apply_population_shift(
                    budget_latent,
                    indices=partitions["evaluation"],
                    shift_ilr=shift,
                )
                shifted_panel = resample_counts_fast(
                    shifted,
                    np.random.default_rng(shift_sequence),
                )
                shifted_evaluation = subset_authors(
                    shifted_panel,
                    partitions["evaluation"],
                )
                shifted_profile = estimate_standardized_profile(
                    shifted_evaluation,
                    discovery,
                    reference_fit=pipeline["reference_fit"],
                )
                shifted_score = apply_external_zero_denoiser(
                    shifted_profile,
                    pipeline["hard"],
                )
                shifted_truth = true_observed_profile(
                    subset_authors(
                        shifted,
                        partitions["evaluation"],
                    ),
                    discovery,
                    reference_fit=pipeline["reference_fit"],
                )
                target_delta = (
                    apply_external_zero_denoiser(
                        shifted_truth,
                        pipeline["hard"],
                    ).mean(axis=0)
                    - hard_infinite.mean(axis=0)
                )
                estimated_delta = (
                    shifted_score.mean(axis=0)
                    - hard_score.mean(axis=0)
                )
                row["population_shift_direction_cosine"] = (
                    _direction_cosine(estimated_delta, target_delta)
                )
                row["population_shift_amplitude"] = float(
                    np.linalg.norm(estimated_delta)
                    / max(np.linalg.norm(target_delta), 1e-12)
                )

            if (
                str(world_name) in config["uncertainty_worlds"]
                and int(event_budget) in config["uncertainty_budgets"]
            ):
                uncertainty, nested_seeds = _nested_uncertainty(
                    latent=budget_latent,
                    panel=panel,
                    partitions=partitions,
                    pipeline=pipeline,
                    discovery=discovery,
                    config=config,
                    seed_sequence=uncertainty_sequence,
                )
                all_seeds.extend(nested_seeds)
                uncertainty_rows.append({
                    "repetition": repetition,
                    "world": str(world_name),
                    "event_budget": int(event_budget),
                    **uncertainty,
                })
            rows.append(row)
    return rows, uncertainty_rows, all_seeds


def _asymptotes(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (repetition, world), group in frame.groupby(
        ["repetition", "world"]
    ):
        group = group.sort_values("event_budget")
        for metric in (
            "hard_event_nmse",
            "soft_event_nmse",
            "hard_total_nmse",
            "soft_total_nmse",
        ):
            fit = fit_error_asymptote(
                group["event_budget"].to_numpy(),
                group[metric].to_numpy(),
            )
            rows.append({
                "repetition": repetition,
                "world": world,
                "metric": metric,
                **fit,
            })
    return pd.DataFrame(rows)


def _effects(
    frame: pd.DataFrame,
    uncertainty: pd.DataFrame,
    asymptotes: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    rng = np.random.default_rng(int(config["_active_seed"]) ^ 0x37F)
    primary = frame[
        frame["event_budget"] == int(config["primary_budget"])
    ]
    hard = primary[primary["world"] == "hard_rank12"]
    dense = primary[primary["world"] == "dense_tail48"]
    control = primary[primary["world"] == "author_permutation"]
    state = primary[primary["world"] == "dense_state_alias"]
    uncertainty64 = uncertainty[
        uncertainty["event_budget"] == min(
            config["uncertainty_budgets"]
        )
    ]
    uncertainty256 = uncertainty[
        uncertainty["event_budget"] == max(
            config["uncertainty_budgets"]
        )
    ]
    radius_ratio = (
        uncertainty256["full_median_radius"].mean()
        / max(uncertainty64["full_median_radius"].mean(), 1e-12)
    )
    hard_asymptote = asymptotes[
        (asymptotes["world"] == "hard_rank12")
        & (asymptotes["metric"] == "hard_event_nmse")
    ]
    conserving_reduction = (
        dense["hard_capacity_floor"].to_numpy()
        - dense["conserving_capacity_floor"].to_numpy()
    ) / np.maximum(
        dense["hard_capacity_floor"].to_numpy(),
        1e-12,
    )
    shift = hard.dropna(subset=["population_shift_direction_cosine"])
    return {
        "external_zero_invariance_max": float(
            frame["evaluation_cohort_invariance_error"].max()
        ),
        "population_shift_direction": _interval(
            shift["population_shift_direction_cosine"].to_numpy(),
            rng=rng,
        ),
        "population_shift_amplitude": _interval(
            shift["population_shift_amplitude"].to_numpy(),
            rng=rng,
        ),
        "permutation_low_rank_rate": float(
            (control["selected_rank"] <= 2).mean()
        ),
        "permutation_residual_auc": _interval(
            control["residual_hard_neighbor_auc"].to_numpy(),
            rng=rng,
        ),
        "permuted_pair_residual_auc": _interval(
            primary["permuted_residual_hard_neighbor_auc"].to_numpy(),
            rng=rng,
        ),
        "hard_residual_auc": _interval(
            hard["residual_hard_neighbor_auc"].to_numpy(),
            rng=rng,
        ),
        "hard_oracle_residual_auc": _interval(
            hard["oracle_residual_hard_neighbor_auc"].to_numpy(),
            rng=rng,
        ),
        "dense_residual_auc": _interval(
            dense["residual_hard_neighbor_auc"].to_numpy(),
            rng=rng,
        ),
        "dense_residual_increment": _interval(
            dense["residual_incremental_auc"].to_numpy(),
            rng=rng,
        ),
        "hard_capacity_floor": _interval(
            hard["hard_capacity_floor"].to_numpy(),
            rng=rng,
        ),
        "dense_hard_capacity_floor": _interval(
            dense["hard_capacity_floor"].to_numpy(),
            rng=rng,
        ),
        "dense_soft_capacity_floor": _interval(
            dense["soft_capacity_floor"].to_numpy(),
            rng=rng,
        ),
        "dense_conserving_capacity_floor": _interval(
            dense["conserving_capacity_floor"].to_numpy(),
            rng=rng,
        ),
        "dense_conserving_floor_reduction": _interval(
            conserving_reduction,
            rng=rng,
        ),
        "state_alias_infinite_floor": _interval(
            state["soft_infinite_total_floor"].to_numpy(),
            rng=rng,
        ),
        "event_asymptotic_floor": _interval(
            hard_asymptote["floor"].to_numpy(),
            rng=rng,
        ),
        "event_coverage": float(uncertainty["event_coverage"].mean()),
        "full_coverage": float(uncertainty["full_coverage"].mean()),
        "region_radius_ratio": float(radius_ratio),
        "anova_reconstruction_error_max": float(
            uncertainty["anova_reconstruction_error"].max()
        ),
        "reference_variance_reduction": float(
            uncertainty[
                "reference_variance_reduction"
            ].mean()
        ),
        "null_change_false_positive": float(
            uncertainty["null_false_positive"].mean()
        ),
        "two_mdc_power": float(uncertainty["two_mdc_power"].mean()),
    }


def _integrity(
    frame: pd.DataFrame,
    uncertainty: pd.DataFrame,
    seeds: list[int],
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    required = [
        "hard_total_nmse",
        "soft_total_nmse",
        "hard_event_nmse",
        "soft_event_nmse",
        "hard_capacity_floor",
        "soft_capacity_floor",
        "residual_hard_neighbor_auc",
        "residual_incremental_auc",
    ]
    expected = (
        int(config["_active_repetitions"])
        * len(config["worlds"])
        * len(config["event_budgets"])
    )
    expected_uncertainty = (
        int(config["_active_repetitions"])
        * len(config["uncertainty_worlds"])
        * len(config["uncertainty_budgets"])
    )
    return {
        "numeric": bool(
            np.isfinite(frame[required].to_numpy()).all()
            and np.isfinite(
                uncertainty.drop(
                    columns=["world"],
                    errors="ignore",
                ).to_numpy(dtype=float)
            ).all()
        ),
        "author_disjointness": bool((frame["author_overlap"] == 0).all()),
        "row_count": int(len(frame)),
        "expected_rows": int(expected),
        "uncertainty_row_count": int(len(uncertainty)),
        "expected_uncertainty_rows": int(expected_uncertainty),
        "seed_count": int(len(seeds)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
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
                "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
                + ("SMOKE_PASS" if mode == "smoke" else "DISCOVERY_READY")
            ),
            "effects": effects,
            "integrity": integrity,
            "claim_boundary": config["claim_boundary"],
        }
    gates = config["gates"]
    checks = {
        "numeric_integrity": integrity["numeric"],
        "author_disjointness": integrity["author_disjointness"],
        "row_count": (
            integrity["row_count"] == integrity["expected_rows"]
            and integrity["uncertainty_row_count"]
            == integrity["expected_uncertainty_rows"]
        ),
        "seed_uniqueness": integrity["seed_uniqueness"],
        "external_zero_invariance": (
            effects["external_zero_invariance_max"]
            <= gates["maximum_external_zero_invariance_error"]
        ),
        "population_shift_direction": (
            effects["population_shift_direction"]["mean"]
            >= gates["minimum_population_shift_direction"]
        ),
        "population_shift_amplitude": (
            gates["minimum_population_shift_amplitude"]
            <= effects["population_shift_amplitude"]["mean"]
            <= gates["maximum_population_shift_amplitude"]
        ),
        "permutation_low_rank": (
            effects["permutation_low_rank_rate"]
            >= gates["minimum_permutation_low_rank_rate"]
        ),
        "permutation_residual_auc": (
            gates["minimum_permutation_residual_auc"]
            <= effects["permutation_residual_auc"]["mean"]
            <= gates["maximum_permutation_residual_auc"]
        ),
        "event_coverage": (
            gates["minimum_event_coverage"]
            <= effects["event_coverage"]
            <= gates["maximum_event_coverage"]
        ),
        "full_coverage": (
            gates["minimum_full_coverage"]
            <= effects["full_coverage"]
            <= gates["maximum_full_coverage"]
        ),
        "region_contraction": (
            effects["region_radius_ratio"]
            <= gates["maximum_region_radius_ratio"]
        ),
        "anova_reconstruction": (
            effects["anova_reconstruction_error_max"]
            <= gates["maximum_anova_reconstruction_error"]
        ),
        "reference_scaling": (
            effects["reference_variance_reduction"]
            >= gates["minimum_reference_variance_reduction"]
        ),
        "hard_residual_null": (
            effects["hard_oracle_residual_auc"]["upper95"]
            <= gates["maximum_hard_residual_auc_upper95"]
        ),
        "dense_residual_detected": (
            effects["dense_residual_auc"]["lower95"]
            > gates["minimum_dense_residual_auc_lower95"]
        ),
        "dense_residual_increment": (
            effects["dense_residual_increment"]["lower95"]
            > gates["minimum_dense_residual_increment_lower95"]
        ),
        "hard_capacity_floor": (
            effects["hard_capacity_floor"]["upper95"]
            <= gates["maximum_hard_capacity_floor_upper95"]
        ),
        "dense_capacity_floor": (
            effects["dense_hard_capacity_floor"]["lower95"]
            > gates["minimum_dense_capacity_floor_lower95"]
        ),
        "conserving_floor_reduction": (
            effects["dense_conserving_floor_reduction"]["mean"]
            >= gates["minimum_conserving_floor_reduction"]
        ),
        "event_floor": (
            effects["event_asymptotic_floor"]["upper95"]
            <= gates["maximum_event_asymptotic_floor_upper95"]
        ),
        "state_floor": (
            effects["state_alias_infinite_floor"]["lower95"]
            > gates["minimum_state_alias_floor_lower95"]
        ),
        "null_change": (
            effects["null_change_false_positive"]
            <= gates["maximum_null_change_false_positive"]
        ),
        "change_power": (
            effects["two_mdc_power"]
            >= gates["minimum_two_mdc_power"]
        ),
    }
    integrity_keys = [
        "numeric_integrity",
        "author_disjointness",
        "row_count",
        "seed_uniqueness",
    ]
    zero_keys = [
        "external_zero_invariance",
        "population_shift_direction",
        "population_shift_amplitude",
        "reference_scaling",
    ]
    uncertainty_keys = [
        "event_coverage",
        "full_coverage",
        "region_contraction",
        "anova_reconstruction",
        "null_change",
        "change_power",
    ]
    residual_control_keys = [
        "permutation_low_rank",
        "permutation_residual_auc",
        "hard_residual_null",
    ]
    asymptote_keys = [
        "hard_capacity_floor",
        "dense_capacity_floor",
        "conserving_floor_reduction",
        "event_floor",
        "state_floor",
    ]
    if not all(checks[key] for key in integrity_keys):
        status = "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_STOP_CONTROLS_INVALID"
    elif not all(checks[key] for key in zero_keys):
        status = "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_STOP_EXTERNAL_ZERO_INVALID"
    elif not all(checks[key] for key in uncertainty_keys):
        status = (
            "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
            "STOP_UNCERTAINTY_MISCALIBRATED"
        )
    elif not all(checks[key] for key in residual_control_keys):
        status = (
            "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
            "STOP_RESIDUAL_TEST_INVALID"
        )
    elif not all(checks[key] for key in asymptote_keys):
        status = (
            "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
            "STOP_ASYMPTOTE_UNIDENTIFIED"
        )
    elif (
        checks["dense_residual_detected"]
        and checks["dense_residual_increment"]
    ):
        status = (
            "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
            "PASS_EVENT_NOISE_ZERO_TOTAL_FLOOR_POSITIVE"
        )
    else:
        status = (
            "V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_"
            "PASS_EXTERNAL_ZERO_ERROR_THEORY_RESIDUAL_SAFE"
        )
    return {
        "status": status,
        "checks": {key: bool(value) for key, value in checks.items()},
        "effects": effects,
        "integrity": integrity,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_parent(config: dict[str, Any]) -> dict[str, str]:
    parent = config["required_parent_seal"]
    got = sha256_file(ROOT / parent["path"])
    if got != parent["sha256"]:
        raise RuntimeError("V3.7E parent seal mismatch")
    return {"status": "PARENT_SEAL_PASS", "sha256": got}


def _verify_own_seal(path: Path, *, mode: str) -> dict[str, str]:
    if mode != "confirmation":
        return {"status": "OWN_SEAL_NOT_REQUIRED"}
    if not path.is_file():
        raise RuntimeError("confirmation requires V3.7F seal")
    seal = _read(path)
    failures = [
        relative
        for relative, expected in seal["files"].items()
        if not (ROOT / relative).is_file()
        or sha256_file(ROOT / relative) != expected
    ]
    if failures:
        raise RuntimeError(f"V3.7F seal mismatch: {failures}")
    return {
        "status": "V37F_PROSPECTIVE_SEAL_PASS",
        "sha256": sha256_file(path),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
    uncertainty_summary: pd.DataFrame,
) -> str:
    return f"""# V8 External Zero and Residual Sufficiency V3.7F

Decision: `{decision["status"]}`

## Integrity

```json
{json.dumps(decision["integrity"], indent=2)}
```

## Effects

```json
{json.dumps(decision["effects"], indent=2)}
```

## Main summary

{summary.to_markdown(index=False)}

## Nested uncertainty

{uncertainty_summary.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT
        / "configs/v8_external_zero_uncertainty_v37f_discovery.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT
        / "configs/v8_external_zero_uncertainty_v37f_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "results/v8_external_zero_uncertainty/v37f_discovery",
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
        repetitions = 2
        config["bootstrap_reference_draws"] = 3
        config["bootstrap_selection_draws"] = 3
        config["bootstrap_event_draws"] = 64
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
    rows = [row for part, _, _ in nested for row in part]
    uncertainty_rows = [
        row for _, part, _ in nested for row in part
    ]
    seeds = [seed for _, _, part in nested for seed in part]
    frame = pd.DataFrame(rows)
    uncertainty = pd.DataFrame(uncertainty_rows)
    asymptotes = _asymptotes(frame)
    summary = (
        frame.groupby(["world", "event_budget"], as_index=False)
        .mean(numeric_only=True)
    )
    uncertainty_summary = (
        uncertainty.groupby(["world", "event_budget"], as_index=False)
        .mean(numeric_only=True)
    )
    effects = _effects(
        frame,
        uncertainty,
        asymptotes,
        config=config,
    )
    integrity = _integrity(
        frame,
        uncertainty,
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
    frame.to_csv(args.output_dir / "metrics.csv", index=False)
    uncertainty.to_csv(
        args.output_dir / "uncertainty_metrics.csv",
        index=False,
    )
    asymptotes.to_csv(
        args.output_dir / "asymptote_summary.csv",
        index=False,
    )
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    uncertainty_summary.to_csv(
        args.output_dir / "uncertainty_summary.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision, summary, uncertainty_summary),
        encoding="utf-8",
    )
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[ROOT / config["required_parent_seal"]["path"]],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_external_zero_uncertainty.py",
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
        "uncertainty_rows": len(uncertainty),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
