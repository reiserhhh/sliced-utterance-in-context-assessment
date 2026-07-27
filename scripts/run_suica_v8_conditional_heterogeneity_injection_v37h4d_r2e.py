#!/usr/bin/env python3
"""Run the H4D-R2E conditional-heterogeneity injection discovery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_geometry_information_operator_v37h4d_r2b import (  # noqa: E402
    _simulate_base_world,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _spec,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_conditional_heterogeneity_injection import (  # noqa: E402
    frame_audit,
    geometry_audit,
    injection_geometry,
    orthonormal_geometry_frame,
    paired_direction_sensitivity,
)
from suica_core.v8_conditional_heterogeneity_preflight import (  # noqa: E402
    conditional_variance,
    resample_outcome_pair,
)
from suica_core.v8_geometry_information_operator import (  # noqa: E402
    apply_interaction,
    geometry_information_coordinates,
    match_residual_information,
)
from suica_core.v8_minority_information_frontier import (  # noqa: E402
    plant_minority_interaction,
)
from suica_core.v8_permutation_orbit_frontier import (  # noqa: E402
    build_controlled_halo_interaction,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    wild_residual_diagnostics,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs"
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_conditional_heterogeneity_injection"
    / "v37h4d_r2e_discovery"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(config: dict[str, Any]) -> dict[str, Any]:
    records = []
    for relative, expected in config["frozen_source_sha256"].items():
        observed = _sha256(ROOT / str(relative))
        records.append({
            "path": str(relative),
            "expected_sha256": str(expected),
            "observed_sha256": observed,
            "match": observed == str(expected),
        })
    return {
        "pass": bool(all(record["match"] for record in records)),
        "files": records,
    }


def _geometry_plan(config: dict[str, Any]) -> list[dict[str, Any]]:
    plan = [{
        "arm": "baseline",
        "magnitude": 0.0,
        "sign": 0,
    }]
    for arm, key in [
        ("normal", "normal_tau_grid"),
        ("tangent", "tangent_phi_grid"),
    ]:
        for magnitude in map(float, config[key]):
            for sign in [-1, 1]:
                plan.append({
                    "arm": arm,
                    "magnitude": magnitude,
                    "sign": sign,
                })
    return plan


def _expected_halo_share(
    *,
    theta: float,
    arm: str,
    magnitude: float,
    sign: int,
) -> float:
    if arm == "normal":
        return float(np.sin(theta + sign * magnitude) ** 2)
    return float(np.sin(theta) ** 2)


def _paired_total_variance(
    plus: np.ndarray,
    minus: np.ndarray,
) -> dict[str, float]:
    """Estimate side-mixture variance as midpoint variance plus J."""
    positive = np.asarray(plus, dtype=float)
    negative = np.asarray(minus, dtype=float)
    sensitivity = paired_direction_sensitivity(positive, negative)
    midpoint = 0.5 * (positive + negative)
    midpoint_mean = midpoint.mean(axis=1)
    midpoint_sampling_variance = midpoint.var(axis=1, ddof=1)
    midpoint_variance = float(
        np.var(midpoint_mean, ddof=1)
        - np.mean(midpoint_sampling_variance) / midpoint.shape[1]
    )
    return {
        "direction_sensitivity_j": sensitivity,
        "midpoint_variance": midpoint_variance,
        "total_side_variance": midpoint_variance + sensitivity,
        "plus_minus_rate_gap": float(
            positive.mean() - negative.mean()
        ),
    }


def _worker(
    payload: tuple[
        dict[str, Any],
        str,
        int,
        int,
        int,
        int,
        int,
        list[int],
        list[int],
    ],
) -> dict[str, Any]:
    (
        config,
        noise_mode,
        repetition,
        world_seed,
        anchor_seed,
        geometry_seed,
        tangent_seed,
        outcome_seeds,
        diagnostic_seeds,
    ) = payload
    spec = _spec(config)
    _, _, test = spec.author_split
    base_world = _simulate_base_world(
        config,
        noise_mode=str(noise_mode),
        seed=int(world_seed),
    )
    anchor_world, anchor_audit = plant_minority_interaction(
        base_world,
        spec=spec,
        seed=int(anchor_seed),
        active_test_authors=int(config["active_test_authors"]),
        active_conditions=int(config["active_conditions"]),
        support_scheme="fixed",
        interaction_shape="iid_block",
        scaling_arm="active_snr",
        global_effect_share=float(config["anchor_global_effect_share"]),
        active_cell_snr=float(config["anchor_active_cell_snr"]),
        primary_opportunities=int(config["primary_opportunities"]),
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    active = np.asarray(
        anchor_audit["selected_test_authors"],
        dtype=int,
    )
    conditions = np.asarray(
        anchor_audit["selected_conditions"],
        dtype=int,
    )
    core_interaction, _ = build_controlled_halo_interaction(
        anchor_world["interaction"],
        spec=spec,
        test_authors=test,
        active_test_authors=active,
        active_conditions=conditions,
        halo_lambda=0.0,
        halo_author_support=int(config["active_test_authors"]),
        seed=int(geometry_seed),
    )
    baseline_interaction, _ = build_controlled_halo_interaction(
        anchor_world["interaction"],
        spec=spec,
        test_authors=test,
        active_test_authors=active,
        active_conditions=conditions,
        halo_lambda=float(config["baseline_halo_lambda"]),
        halo_author_support=int(config["halo_author_support"]),
        seed=int(geometry_seed),
    )
    theta = float(np.arcsin(np.sqrt(config["baseline_halo_lambda"])))
    raw_core = np.asarray(core_interaction[test], dtype=float)
    raw_baseline = np.asarray(baseline_interaction[test], dtype=float)
    raw_halo = (
        raw_baseline - np.cos(theta) * raw_core
    ) / np.sin(theta)
    core, halo, tangent = orthonormal_geometry_frame(
        raw_core,
        raw_halo,
        seed=int(tangent_seed),
    )
    frame_checks = frame_audit(core, halo, tangent)
    parent_id = f"{noise_mode}|r{int(repetition):04d}"
    geometry_rows = []
    outcome_rows = []
    baseline_scale = None
    for geometry_index, definition in enumerate(_geometry_plan(config)):
        expected_halo = _expected_halo_share(
            theta=theta,
            arm=str(definition["arm"]),
            magnitude=float(definition["magnitude"]),
            sign=int(definition["sign"]),
        )
        test_geometry = injection_geometry(
            core,
            halo,
            tangent,
            theta=theta,
            arm=str(definition["arm"]),
            magnitude=float(definition["magnitude"]),
            sign=int(definition["sign"]),
        )
        raw_interaction = np.asarray(
            anchor_world["interaction"],
            dtype=float,
        ).copy()
        raw_interaction[test] = test_geometry
        interaction, information_match = match_residual_information(
            base_world,
            raw_interaction,
            target_information=float(
                anchor_audit["information_budget_residual"]
            ),
            spec=spec,
            active_test_authors=active,
            active_conditions=conditions,
            primary_opportunities=int(config["primary_opportunities"]),
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
        if baseline_scale is None:
            baseline_scale = float(
                information_match["information_match_scale"]
            )
        scale_ratio = float(
            information_match["information_match_scale"]
            / baseline_scale
        )
        coordinates = geometry_information_coordinates(
            base_world,
            interaction,
            spec=spec,
            active_test_authors=active,
            active_conditions=conditions,
            primary_opportunities=int(config["primary_opportunities"]),
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
        geometry_checks = geometry_audit(
            test_geometry,
            core,
            expected_halo_share=expected_halo,
        )
        geometry_id = (
            f"{definition['arm']}|"
            f"x{float(definition['magnitude']):.3f}|"
            f"z{int(definition['sign']):+d}"
        )
        geometry_record = {
            "parent_id": parent_id,
            "noise_mode": str(noise_mode),
            "repetition": int(repetition),
            "geometry_index": int(geometry_index),
            "geometry_id": geometry_id,
            **definition,
            "expected_halo_share": expected_halo,
            "world_seed": int(world_seed),
            "anchor_seed": int(anchor_seed),
            "geometry_seed": int(geometry_seed),
            "tangent_seed": int(tangent_seed),
            **frame_checks,
            **geometry_checks,
            **information_match,
            "information_scale_ratio_to_baseline": scale_ratio,
            **coordinates,
            "interaction_sha256": hashlib.sha256(
                np.ascontiguousarray(interaction).tobytes()
            ).hexdigest(),
        }
        geometry_rows.append(geometry_record)
        world = apply_interaction(base_world, interaction)
        for outcome_index, (outcome_seed, diagnostic_seed) in enumerate(
            zip(outcome_seeds, diagnostic_seeds, strict=True)
        ):
            residuals = resample_outcome_pair(
                world,
                test_authors=test,
                seed=int(outcome_seed),
                noise_mode=str(noise_mode),
                opportunity_prefixes=tuple(
                    map(int, config["opportunity_prefixes"])
                ),
                primary_opportunities=int(
                    config["primary_opportunities"]
                ),
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
            )
            diagnostics = wild_residual_diagnostics(
                *residuals,
                rank=3,
                seed=int(diagnostic_seed),
                permutations=int(config["permutations"]),
                alpha=float(config["holm_alpha"]),
            )
            outcome_rows.append({
                "parent_id": parent_id,
                "noise_mode": str(noise_mode),
                "geometry_id": geometry_id,
                **definition,
                "outcome_replicate": int(outcome_index),
                "outcome_seed": int(outcome_seed),
                "diagnostic_seed": int(diagnostic_seed),
                **diagnostics,
                "crc_or_hc_detected": bool(
                    diagnostics["crc_p_holm"]
                    < float(config["holm_alpha"])
                    or diagnostics["hc_p_holm"]
                    < float(config["holm_alpha"])
                ),
            })
    return {
        "parent_id": parent_id,
        "geometry_rows": geometry_rows,
        "outcome_rows": outcome_rows,
        "source_seeds": [
            int(world_seed),
            int(anchor_seed),
            int(geometry_seed),
            int(tangent_seed),
            *map(int, outcome_seeds),
            *map(int, diagnostic_seeds),
        ],
    }


def _outcome_matrix(
    outcomes: pd.DataFrame,
    *,
    noise_mode: str,
    arm: str,
    magnitude: float,
    sign: int,
) -> tuple[np.ndarray, list[str]]:
    selected = outcomes[
        (outcomes["noise_mode"] == noise_mode)
        & (outcomes["arm"] == arm)
        & np.isclose(outcomes["magnitude"], magnitude)
        & (outcomes["sign"] == sign)
    ]
    pivot = selected.pivot(
        index="parent_id",
        columns="outcome_replicate",
        values="crc_or_hc_detected",
    ).sort_index()
    return pivot.to_numpy(dtype=float), pivot.index.astype(str).tolist()


def _baseline_variance(values: np.ndarray) -> float:
    return conditional_variance(
        np.asarray(values, dtype=float).sum(axis=1),
        replicates=values.shape[1],
    )


def _bootstrap_indices(
    *,
    seed: int,
    draws: int,
    parents: int,
) -> np.ndarray:
    return np.random.default_rng(int(seed)).integers(
        0,
        int(parents),
        size=(int(draws), int(parents)),
    )


def _bootstrap_baseline_variance(
    values: np.ndarray,
    indices: np.ndarray,
) -> np.ndarray:
    count = np.asarray(values, dtype=float).sum(axis=1)
    replicates = values.shape[1]
    sampled = count[indices]
    proportion = sampled / replicates
    observed = np.var(proportion, axis=1, ddof=1)
    binomial = sampled * (replicates - sampled) / (
        replicates**2 * (replicates - 1)
    )
    return observed - binomial.mean(axis=1)


def _bootstrap_paired_statistics(
    plus: np.ndarray,
    minus: np.ndarray,
    baseline_bootstrap: np.ndarray,
    indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    difference = plus - minus
    mean_difference = difference.mean(axis=1)
    sampling_variance = difference.var(axis=1, ddof=1)
    j_contribution = 0.25 * (
        mean_difference**2
        - sampling_variance / difference.shape[1]
    )
    midpoint = 0.5 * (plus + minus)
    midpoint_mean = midpoint.mean(axis=1)
    midpoint_sampling = (
        midpoint.var(axis=1, ddof=1) / midpoint.shape[1]
    )
    j_bootstrap = j_contribution[indices].mean(axis=1)
    midpoint_sample = midpoint_mean[indices]
    midpoint_variance = (
        np.var(midpoint_sample, axis=1, ddof=1)
        - midpoint_sampling[indices].mean(axis=1)
    )
    total_variance = midpoint_variance + j_bootstrap
    return j_bootstrap, total_variance - baseline_bootstrap


def _analyze_statistics(
    outcomes: pd.DataFrame,
    *,
    config: dict[str, Any],
    seed: int,
    draws: int,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, np.ndarray]]:
    records = []
    bootstrap_cache: dict[tuple[str, str, float], dict[str, np.ndarray]] = {}
    baseline_points: dict[str, float] = {}
    baseline_bootstrap: dict[str, np.ndarray] = {}
    root = np.random.SeedSequence(int(seed))
    noise_streams = root.spawn(len(config["noise_modes"]))
    indices_by_noise = {}
    for stream, noise in zip(
        noise_streams,
        map(str, config["noise_modes"]),
        strict=True,
    ):
        baseline, parents = _outcome_matrix(
            outcomes,
            noise_mode=noise,
            arm="baseline",
            magnitude=0.0,
            sign=0,
        )
        indices = _bootstrap_indices(
            seed=int(stream.generate_state(1, dtype=np.uint64)[0]),
            draws=draws,
            parents=len(parents),
        )
        indices_by_noise[noise] = indices
        baseline_points[noise] = _baseline_variance(baseline)
        baseline_bootstrap[noise] = _bootstrap_baseline_variance(
            baseline,
            indices,
        )
        records.append({
            "noise_mode": noise,
            "arm": "baseline",
            "magnitude": 0.0,
            "parents": int(len(parents)),
            "direction_sensitivity_j": float("nan"),
            "midpoint_variance": float("nan"),
            "total_side_variance": baseline_points[noise],
            "baseline_variance": baseline_points[noise],
            "delta_variance": 0.0,
            "plus_minus_rate_gap": float("nan"),
            "j_pointwise_lower_95": float("nan"),
            "j_pointwise_upper_95": float("nan"),
            "delta_v_pointwise_lower_95": float("nan"),
            "delta_v_pointwise_upper_95": float("nan"),
        })
        for arm, key in [
            ("normal", "normal_tau_grid"),
            ("tangent", "tangent_phi_grid"),
        ]:
            for magnitude in map(float, config[key]):
                plus, plus_parents = _outcome_matrix(
                    outcomes,
                    noise_mode=noise,
                    arm=arm,
                    magnitude=magnitude,
                    sign=1,
                )
                minus, minus_parents = _outcome_matrix(
                    outcomes,
                    noise_mode=noise,
                    arm=arm,
                    magnitude=magnitude,
                    sign=-1,
                )
                if parents != plus_parents or parents != minus_parents:
                    raise ValueError("paired parent order mismatch")
                point = _paired_total_variance(plus, minus)
                j_boot, delta_boot = _bootstrap_paired_statistics(
                    plus,
                    minus,
                    baseline_bootstrap[noise],
                    indices,
                )
                bootstrap_cache[(noise, arm, magnitude)] = {
                    "j": j_boot,
                    "delta_v": delta_boot,
                }
                records.append({
                    "noise_mode": noise,
                    "arm": arm,
                    "magnitude": magnitude,
                    "parents": int(len(parents)),
                    **point,
                    "baseline_variance": baseline_points[noise],
                    "delta_variance": (
                        point["total_side_variance"]
                        - baseline_points[noise]
                    ),
                    "j_pointwise_lower_95": float(
                        np.quantile(j_boot, 0.025)
                    ),
                    "j_pointwise_upper_95": float(
                        np.quantile(j_boot, 0.975)
                    ),
                    "delta_v_pointwise_lower_95": float(
                        np.quantile(delta_boot, 0.025)
                    ),
                    "delta_v_pointwise_upper_95": float(
                        np.quantile(delta_boot, 0.975)
                    ),
                })
    summary = pd.DataFrame(records)
    normal_endpoint = float(max(config["normal_tau_grid"]))
    tangent_endpoint = float(max(config["tangent_phi_grid"]))
    endpoint_order = []
    endpoint_points = []
    endpoint_bootstrap = []
    for metric in ["j", "delta_v"]:
        column = (
            "direction_sensitivity_j"
            if metric == "j"
            else "delta_variance"
        )
        for arm, magnitude in [
            ("normal", normal_endpoint),
            ("tangent", tangent_endpoint),
        ]:
            for noise in map(str, config["noise_modes"]):
                point = float(
                    summary[
                        (summary["noise_mode"] == noise)
                        & (summary["arm"] == arm)
                        & np.isclose(summary["magnitude"], magnitude)
                    ][column].iloc[0]
                )
                endpoint_order.append(f"{metric}|{arm}|{noise}")
                endpoint_points.append(point)
                endpoint_bootstrap.append(
                    bootstrap_cache[(noise, arm, magnitude)][metric]
                )
    pooled_tangent_delta = float(np.mean([
        endpoint_points[
            endpoint_order.index(f"delta_v|tangent|{noise}")
        ]
        for noise in map(str, config["noise_modes"])
    ]))
    pooled_tangent_bootstrap = np.mean([
        bootstrap_cache[(noise, "tangent", tangent_endpoint)]["delta_v"]
        for noise in map(str, config["noise_modes"])
    ], axis=0)
    endpoint_order.append("delta_v|tangent|pooled")
    endpoint_points.append(pooled_tangent_delta)
    endpoint_bootstrap.append(pooled_tangent_bootstrap)
    point_array = np.asarray(endpoint_points, dtype=float)
    bootstrap_array = np.column_stack(endpoint_bootstrap)
    lower_radius = float(np.quantile(
        np.max(point_array[None, :] - bootstrap_array, axis=1),
        0.95,
    ))
    upper_radius = float(np.quantile(
        np.max(bootstrap_array - point_array[None, :], axis=1),
        0.95,
    ))
    simultaneous = {
        name: {
            "point": float(point),
            "lower_95": float(point - lower_radius),
            "upper_95": float(point + upper_radius),
        }
        for name, point in zip(
            endpoint_order,
            point_array,
            strict=True,
        )
    }
    endpoint = {
        "normal_magnitude": normal_endpoint,
        "tangent_magnitude": tangent_endpoint,
        "simultaneous_lower_radius": lower_radius,
        "simultaneous_upper_radius": upper_radius,
        "statistics": simultaneous,
    }
    return summary, endpoint, {
        name: values
        for name, values in zip(
            endpoint_order,
            endpoint_bootstrap,
            strict=True,
        )
    }


def _decision_status(
    *,
    integrity: dict[str, bool],
    endpoint: dict[str, Any],
    geometry_rows: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    threshold = float(config["gates"]["practical_variance_threshold"])
    stats = endpoint["statistics"]
    noises = list(map(str, config["noise_modes"]))
    normal = [stats[f"j|normal|{noise}"] for noise in noises]
    tangent_j = [stats[f"j|tangent|{noise}"] for noise in noises]
    tangent_delta = [
        stats[f"delta_v|tangent|{noise}"] for noise in noises
    ]
    pooled_delta = stats["delta_v|tangent|pooled"]
    normal_pass = all(row["lower_95"] > threshold for row in normal)
    normal_refuted = all(row["upper_95"] <= threshold for row in normal)
    tangent_j_pass = all(
        row["lower_95"] > threshold for row in tangent_j
    )
    tangent_delta_pass = pooled_delta["lower_95"] > threshold
    tangent_direction = all(
        row["point"] > 0.0 for row in [*tangent_j, *tangent_delta]
    )
    tangent_positive = bool(
        all(row["lower_95"] > 0.0 for row in tangent_j)
        or pooled_delta["lower_95"] > 0.0
    )
    tangent_refuted = bool(
        all(row["upper_95"] <= threshold for row in tangent_j)
        and all(
            row["upper_95"] <= threshold for row in tangent_delta
        )
    )
    scale_min = float(
        config["gates"]["minimum_information_scale_ratio"]
    )
    scale_max = float(
        config["gates"]["maximum_information_scale_ratio"]
    )
    scale_pass = bool(
        geometry_rows["information_scale_ratio_to_baseline"].between(
            scale_min,
            scale_max,
        ).all()
    )
    checks = {
        "normal_positive_control_pass": normal_pass,
        "normal_positive_control_refuted": normal_refuted,
        "tangent_j_pass": tangent_j_pass,
        "tangent_delta_v_pass": tangent_delta_pass,
        "tangent_noise_direction_consistent": tangent_direction,
        "tangent_positive_but_subthreshold": tangent_positive,
        "tangent_refuted_at_practical_threshold": tangent_refuted,
        "information_scale_ratio_pass": scale_pass,
    }
    if not all(integrity.values()):
        status = "V8_R2E_STOP_INVALID_PROTOCOL"
    elif normal_refuted:
        status = "V8_R2E_STOP_POSITIVE_CONTROL_FAILED"
    elif (
        normal_pass
        and tangent_j_pass
        and tangent_delta_pass
        and tangent_direction
        and scale_pass
    ):
        status = "V8_R2E_DISCOVERY_GO_HIDDEN_TANGENT_GEOMETRY"
    elif (
        normal_pass
        and tangent_j_pass
        and tangent_delta_pass
        and tangent_direction
        and not scale_pass
    ):
        status = "V8_R2E_PARTIAL_TANGENT_AMPLITUDE_COUPLED"
    elif normal_pass and tangent_refuted:
        status = "V8_R2E_NORMAL_ONLY_KNOWN_MARGIN"
    elif normal_pass and tangent_positive:
        status = "V8_R2E_PARTIAL_TANGENT_SUBTHRESHOLD"
    else:
        status = "V8_R2E_INCONCLUSIVE_NO_TUNING"
    return status, checks


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
    smoke = args.mode == "smoke"
    parents_per_noise = int(
        config[
            "smoke_parents_per_noise"
            if smoke
            else "parents_per_noise"
        ]
    )
    outcome_replicates = int(
        config[
            "smoke_outcome_replicates"
            if smoke
            else "outcome_replicates"
        ]
    )
    bootstrap_draws = int(
        config["smoke_bootstrap_draws" if smoke else "bootstrap_draws"]
    )
    source_lock = _source_lock(config)
    tasks = [
        (str(noise), repetition)
        for noise in config["noise_modes"]
        for repetition in range(parents_per_noise)
    ]
    streams_per_parent = 4 + 2 * outcome_replicates
    root_seed = int(config["smoke_seed" if smoke else "seed"])
    parent_streams = np.random.SeedSequence(root_seed).spawn(len(tasks))
    nested_seeds = [
        [
            int(stream.generate_state(1, dtype=np.uint64)[0])
            for stream in parent.spawn(streams_per_parent)
        ]
        for parent in parent_streams
    ]
    source_seeds = [
        seed for parent in nested_seeds for seed in parent
    ]
    payloads = []
    for index, (noise, repetition) in enumerate(tasks):
        seeds = nested_seeds[index]
        payloads.append((
            config,
            noise,
            repetition,
            seeds[0],
            seeds[1],
            seeds[2],
            seeds[3],
            seeds[4 : 4 + outcome_replicates],
            seeds[4 + outcome_replicates : streams_per_parent],
        ))
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    geometry_rows = pd.DataFrame([
        row for item in nested for row in item["geometry_rows"]
    ])
    outcome_rows = pd.DataFrame([
        row for item in nested for row in item["outcome_rows"]
    ])
    analysis_seed = int(
        np.random.SeedSequence(root_seed ^ 0x2E2E2E2E)
        .generate_state(1, dtype=np.uint64)[0]
    )
    statistics, endpoint, _ = _analyze_statistics(
        outcome_rows,
        config=config,
        seed=analysis_seed,
        draws=bootstrap_draws,
    )
    geometry_count = len(_geometry_plan(config))
    expected_parents = 2 * parents_per_noise
    expected_geometry = expected_parents * geometry_count
    expected_outcomes = expected_geometry * outcome_replicates
    gates = config["gates"]
    common_random_number_check = (
        outcome_rows.groupby(["parent_id", "outcome_replicate"])[
            ["outcome_seed", "diagnostic_seed"]
        ].nunique()
        == 1
    ).all().all()
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "parent_count": bool(
            geometry_rows["parent_id"].nunique() == expected_parents
        ),
        "geometry_count": bool(len(geometry_rows) == expected_geometry),
        "outcome_count": bool(len(outcome_rows) == expected_outcomes),
        "geometry_completeness": bool(
            (
                geometry_rows.groupby("parent_id")["geometry_id"].nunique()
                == geometry_count
            ).all()
        ),
        "outcome_completeness": bool(
            (
                outcome_rows.groupby(
                    ["parent_id", "geometry_id"]
                )["outcome_replicate"].nunique()
                == outcome_replicates
            ).all()
        ),
        "source_seed_uniqueness": bool(
            len(source_seeds) == len(set(source_seeds))
            and [
                seed for item in nested for seed in item["source_seeds"]
            ]
            == source_seeds
        ),
        "common_random_numbers": bool(common_random_number_check),
        "information_match": bool(
            geometry_rows["information_match_relative_error"].max()
            <= float(
                gates["maximum_information_match_relative_error"]
            )
        ),
        "frame_orthonormality": bool(
            geometry_rows["maximum_axis_norm_error"].max()
            <= float(gates["maximum_frame_error"])
            and geometry_rows["maximum_axis_inner_product"].max()
            <= float(gates["maximum_frame_error"])
        ),
        "double_centering": bool(
            geometry_rows[
                "maximum_double_centering_marginal_error"
            ].max()
            <= float(gates["maximum_marginal_error"])
            and geometry_rows[
                "maximum_geometry_marginal_error"
            ].max()
            <= float(gates["maximum_marginal_error"])
        ),
        "halo_share": bool(
            geometry_rows["halo_share_error"].max()
            <= float(gates["maximum_halo_share_error"])
        ),
        "all_author_support": bool(
            (
                geometry_rows.loc[
                    geometry_rows["arm"] != "baseline",
                    "realized_author_support",
                ]
                == int(config["halo_author_support"])
            ).all()
        ),
        "numeric_integrity": bool(
            np.isfinite(
                geometry_rows[[
                    "operator_total_information",
                    "operator_neff_author",
                    "operator_neff_cell",
                    "operator_rho3",
                    "operator_whitened_leakage",
                    "operator_neff_sign",
                ]].to_numpy(dtype=float)
            ).all()
            and np.isfinite(
                statistics.loc[
                    statistics["arm"] != "baseline",
                    [
                        "direction_sensitivity_j",
                        "total_side_variance",
                        "delta_variance",
                    ],
                ].to_numpy(dtype=float)
            ).all()
        ),
    }
    if smoke:
        status = (
            "V8_R2E_SMOKE_COMPLETE"
            if all(integrity.values())
            else "V8_R2E_STOP_INVALID_PROTOCOL"
        )
        gate_checks: dict[str, Any] = {}
    else:
        status, gate_checks = _decision_status(
            integrity=integrity,
            endpoint=endpoint,
            geometry_rows=geometry_rows,
            config=config,
        )
    decision = {
        "status": status,
        "mode": args.mode,
        "integrity_checks": integrity,
        "gate_checks": gate_checks,
        "endpoint": endpoint,
        "parents": int(geometry_rows["parent_id"].nunique()),
        "geometries": int(len(geometry_rows)),
        "outcomes": int(len(outcome_rows)),
        "source_seed_count": int(len(source_seeds)),
        "unique_source_seed_count": int(len(set(source_seeds))),
        "source_lock": source_lock,
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    geometry_rows.to_csv(
        args.output_dir / "geometry_rows.csv",
        index=False,
    )
    outcome_rows.to_csv(
        args.output_dir / "outcome_rows.csv",
        index=False,
    )
    statistics.to_csv(
        args.output_dir / "injection_statistics.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "streams_per_parent": int(streams_per_parent),
        "source_seed_count": int(len(source_seeds)),
        "unique_source_seed_count": int(len(set(source_seeds))),
        "all_source_streams_unique": bool(
            len(source_seeds) == len(set(source_seeds))
        ),
        "common_random_numbers_across_13_geometries": True,
        "fresh_streams_across_parents_and_replicates": True,
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2E Conditional-Heterogeneity Injection\n\n"
        f"Decision: `{status}`\n\n"
        "Normal perturbations traverse the registered halo margin; tangent "
        "perturbations preserve halo share, support, and scalar information. "
        "This is a synthetic detector-mechanism result only.\n",
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
            ROOT / "suica_core/v8_geometry_information_operator.py",
            ROOT / "suica_core/v8_permutation_orbit_frontier.py",
            ROOT / "suica_core/v8_conditional_heterogeneity_preflight.py",
            ROOT / "suica_core/v8_conditional_heterogeneity_injection.py",
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
        "parents": int(geometry_rows["parent_id"].nunique()),
        "geometries": int(len(geometry_rows)),
        "outcomes": int(len(outcome_rows)),
        "integrity_checks": integrity,
        "gate_checks": gate_checks,
        "endpoint": endpoint,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
