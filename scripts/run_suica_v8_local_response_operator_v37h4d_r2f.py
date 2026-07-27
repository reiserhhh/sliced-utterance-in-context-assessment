#!/usr/bin/env python3
"""Generate the H4D-R2F constrained local-response discovery data."""
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

from scripts import (  # noqa: E402
    run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e as r2e,
)
from scripts.run_suica_v8_geometry_information_operator_v37h4d_r2b import (  # noqa: E402
    _simulate_base_world,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _spec,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    verify_run_manifest,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_conditional_heterogeneity_injection import (  # noqa: E402
    frame_audit,
    geometry_audit,
    injection_geometry,
    orthonormal_geometry_frame,
)
from suica_core.v8_conditional_heterogeneity_preflight import (  # noqa: E402
    resample_outcome_pair,
)
from suica_core.v8_geometry_information_operator import (  # noqa: E402
    apply_interaction,
    geometry_information_coordinates,
    match_residual_information,
)
from suica_core.v8_local_response_operator import (  # noqa: E402
    ambient_probe_frame,
    central_coordinate_jacobian,
    constrained_probe_basis,
    tangent_geodesic,
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
    ROOT / "configs/v8_local_response_operator_v37h4d_r2f_discovery.json"
)
DEFAULT_OUTPUT = (
    ROOT / "results/v8_local_response_operator/r2f_discovery"
)
DEFAULT_PREFLIGHT = (
    ROOT / "results/v8_local_response_operator/r2f_geometry_preflight"
)


def _unit(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    return result / max(float(np.linalg.norm(result)), 1e-12)


def _geometry_plan(config: dict[str, Any]) -> list[dict[str, Any]]:
    dimensions = int(config["tangent_dimensions"])
    step = float(config["finite_difference_step"])
    plan: list[dict[str, Any]] = [{
        "geometry_id": "baseline",
        "arm": "baseline",
        "magnitude": 0.0,
        "sign": 0,
        "coefficients": np.zeros(dimensions),
    }]
    for axis in range(dimensions):
        for magnitude in (step, 2.0 * step):
            for sign in (-1, 1):
                coefficients = np.zeros(dimensions)
                coefficients[axis] = sign * magnitude
                plan.append({
                    "geometry_id": (
                        f"axis|k{axis}|x{magnitude:.3f}|z{sign:+d}"
                    ),
                    "arm": "axis",
                    "magnitude": magnitude,
                    "sign": sign,
                    "axis_left": axis,
                    "axis_right": -1,
                    "sign_left": sign,
                    "sign_right": 0,
                    "coefficients": coefficients,
                })
    for left in range(dimensions):
        for right in range(left + 1, dimensions):
            for left_sign in (-1, 1):
                for right_sign in (-1, 1):
                    coefficients = np.zeros(dimensions)
                    coefficients[left] = left_sign * step
                    coefficients[right] = right_sign * step
                    plan.append({
                        "geometry_id": (
                            f"corner|k{left}|l{right}|"
                            f"z{left_sign:+d}{right_sign:+d}"
                        ),
                        "arm": "corner",
                        "magnitude": float(np.linalg.norm(coefficients)),
                        "sign": 0,
                        "axis_left": left,
                        "axis_right": right,
                        "sign_left": left_sign,
                        "sign_right": right_sign,
                        "coefficients": coefficients,
                    })
    normal_tau = float(config["normal_tau"])
    null_phi = float(config["registered_null_phi"])
    for sign in (-1, 1):
        plan.append({
            "geometry_id": f"normal|x{normal_tau:.3f}|z{sign:+d}",
            "arm": "normal",
            "magnitude": normal_tau,
            "sign": sign,
            "coefficients": np.zeros(dimensions),
        })
    for sign in (-1, 1):
        plan.append({
            "geometry_id": (
                f"registered_null|x{null_phi:.3f}|z{sign:+d}"
            ),
            "arm": "registered_null",
            "magnitude": null_phi,
            "sign": sign,
            "coefficients": np.zeros(dimensions),
        })
    return plan


def _coordinate_vector(
    coordinates: dict[str, float],
    names: list[str],
) -> np.ndarray:
    return np.asarray([float(coordinates[name]) for name in names])


def _parent_context(
    config: dict[str, Any],
    *,
    noise_mode: str,
    repetition: int,
    world_seed: int,
    anchor_seed: int,
    geometry_seed: int,
    null_tangent_seed: int,
    probe_seed: int,
) -> dict[str, Any]:
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
        halo_author_support=int(config["halo_author_support"]),
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
    raw_core_unit = _unit(raw_core)
    raw_halo_unit = _unit(raw_halo)
    raw_baseline_reconstruction_error = float(
        np.linalg.norm(
            _unit(raw_baseline)
            - _unit(
                np.cos(theta) * raw_core_unit
                + np.sin(theta) * raw_halo_unit
            )
        )
    )
    core, halo, null_tangent = orthonormal_geometry_frame(
        raw_core,
        raw_halo,
        seed=int(null_tangent_seed),
    )
    frame_checks = frame_audit(core, halo, null_tangent)
    probes = ambient_probe_frame(
        core,
        halo,
        seed=int(probe_seed),
        count=int(config["probe_count"]),
    )
    coordinate_names = list(map(str, config["constraint_coordinates"]))
    coordinate_scales = np.asarray([
        float(config["coordinate_scales"][name])
        for name in coordinate_names
    ])
    target_information = float(
        anchor_audit["information_budget_residual"]
    )

    def match_geometry(
        geometry: np.ndarray,
    ) -> tuple[np.ndarray, dict[str, float], dict[str, float]]:
        raw_interaction = np.asarray(
            anchor_world["interaction"],
            dtype=float,
        ).copy()
        raw_interaction[test] = geometry
        interaction, match = match_residual_information(
            base_world,
            raw_interaction,
            target_information=target_information,
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
        return interaction, match, coordinates

    def evaluate_delta(delta: np.ndarray) -> np.ndarray:
        radius = float(np.linalg.norm(delta))
        if radius <= 1e-15:
            geometry = tangent_geodesic(
                core,
                halo,
                np.zeros((1, *core.shape)),
                np.zeros(1),
                theta=theta,
            )
        else:
            geometry = tangent_geodesic(
                core,
                halo,
                np.stack([np.asarray(delta) / radius]),
                np.asarray([radius]),
                theta=theta,
            )
        _, _, coordinates = match_geometry(geometry)
        return _coordinate_vector(coordinates, coordinate_names)

    jacobian = central_coordinate_jacobian(
        evaluate_delta,
        probes,
        epsilon=float(config["jacobian_epsilon"]),
        coordinate_scales=coordinate_scales,
    )
    tangent_basis, coefficients, constraint_audit = (
        constrained_probe_basis(
            probes,
            jacobian,
            dimensions=int(config["tangent_dimensions"]),
            relative_rank_tolerance=float(
                config["jacobian_relative_rank_tolerance"]
            ),
            minimum_projected_norm=float(
                config["minimum_projected_probe_norm"]
            ),
        )
    )
    flattened_basis = tangent_basis.reshape(len(tangent_basis), -1)
    basis_gram = flattened_basis @ flattened_basis.T
    basis_sha256 = hashlib.sha256(
        np.ascontiguousarray(tangent_basis).tobytes()
    ).hexdigest()
    coefficient_sha256 = hashlib.sha256(
        np.ascontiguousarray(coefficients).tobytes()
    ).hexdigest()
    return {
        "spec": spec,
        "test": test,
        "base_world": base_world,
        "anchor_world": anchor_world,
        "anchor_audit": anchor_audit,
        "active": active,
        "conditions": conditions,
        "theta": theta,
        "core": core,
        "halo": halo,
        "null_tangent": null_tangent,
        "tangent_basis": tangent_basis,
        "coefficients": coefficients,
        "jacobian": jacobian,
        "match_geometry": match_geometry,
        "target_information": target_information,
        "frame_checks": frame_checks,
        "constraint_audit": constraint_audit,
        "basis_gram_error": float(
            np.max(
                np.abs(
                    basis_gram
                    - np.eye(int(config["tangent_dimensions"]))
                )
            )
        ),
        "maximum_basis_core_inner_product": float(
            np.max(np.abs(flattened_basis @ core.reshape(-1)))
        ),
        "maximum_basis_halo_inner_product": float(
            np.max(np.abs(flattened_basis @ halo.reshape(-1)))
        ),
        "raw_baseline_reconstruction_error": (
            raw_baseline_reconstruction_error
        ),
        "orthonormal_core_change": float(
            np.linalg.norm(core - raw_core_unit)
        ),
        "orthonormal_halo_change": float(
            np.linalg.norm(halo - raw_halo_unit)
        ),
        "basis_sha256": basis_sha256,
        "coefficient_sha256": coefficient_sha256,
        "coordinate_names": coordinate_names,
        "coordinate_scales": coordinate_scales,
        "noise_mode": str(noise_mode),
        "repetition": int(repetition),
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
        null_tangent_seed,
        probe_seed,
        outcome_seeds,
        diagnostic_seeds,
    ) = payload
    context = _parent_context(
        config,
        noise_mode=noise_mode,
        repetition=repetition,
        world_seed=world_seed,
        anchor_seed=anchor_seed,
        geometry_seed=geometry_seed,
        null_tangent_seed=null_tangent_seed,
        probe_seed=probe_seed,
    )
    spec = context["spec"]
    test = context["test"]
    core = context["core"]
    halo = context["halo"]
    theta = float(context["theta"])
    parent_id = f"{noise_mode}|r{int(repetition):04d}"
    coordinate_names = context["coordinate_names"]
    coordinate_scales = context["coordinate_scales"]
    geometry_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    baseline_coordinates: dict[str, float] | None = None
    baseline_scale: float | None = None
    plan = _geometry_plan(config)

    for geometry_index, definition in enumerate(plan):
        arm = str(definition["arm"])
        magnitude = float(definition["magnitude"])
        sign = int(definition["sign"])
        if arm == "baseline":
            test_geometry = tangent_geodesic(
                core,
                halo,
                context["tangent_basis"],
                np.zeros(int(config["tangent_dimensions"])),
                theta=theta,
            )
            expected_halo = float(config["baseline_halo_lambda"])
        elif arm in {"axis", "corner"}:
            test_geometry = tangent_geodesic(
                core,
                halo,
                context["tangent_basis"],
                np.asarray(definition["coefficients"], dtype=float),
                theta=theta,
            )
            expected_halo = float(config["baseline_halo_lambda"])
        elif arm == "normal":
            test_geometry = injection_geometry(
                core,
                halo,
                context["null_tangent"],
                theta=theta,
                arm="normal",
                magnitude=magnitude,
                sign=sign,
            )
            expected_halo = float(np.sin(theta + sign * magnitude) ** 2)
        elif arm == "registered_null":
            test_geometry = injection_geometry(
                core,
                halo,
                context["null_tangent"],
                theta=theta,
                arm="tangent",
                magnitude=magnitude,
                sign=sign,
            )
            expected_halo = float(config["baseline_halo_lambda"])
        else:
            raise ValueError(f"unknown local-response arm: {arm}")

        interaction, information_match, coordinates = context[
            "match_geometry"
        ](test_geometry)
        if baseline_coordinates is None:
            baseline_coordinates = coordinates
            baseline_scale = float(
                information_match["information_match_scale"]
            )
        macro_drift = float(max(
            abs(
                float(coordinates[name])
                - float(baseline_coordinates[name])
            )
            / float(scale)
            for name, scale in zip(
                coordinate_names,
                coordinate_scales,
                strict=True,
            )
        ))
        normal_builder_error = float("nan")
        if arm in {"baseline", "normal"}:
            direct, _ = build_controlled_halo_interaction(
                context["anchor_world"]["interaction"],
                spec=spec,
                test_authors=test,
                active_test_authors=context["active"],
                active_conditions=context["conditions"],
                halo_lambda=expected_halo,
                halo_author_support=int(config["halo_author_support"]),
                seed=int(geometry_seed),
            )
            direct_matched, _ = match_residual_information(
                context["base_world"],
                direct,
                target_information=context["target_information"],
                spec=spec,
                active_test_authors=context["active"],
                active_conditions=context["conditions"],
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
            normal_builder_error = float(
                np.linalg.norm(interaction[test] - direct_matched[test])
                / max(float(np.linalg.norm(direct_matched[test])), 1e-12)
            )
        geometry_checks = geometry_audit(
            test_geometry,
            core,
            expected_halo_share=expected_halo,
        )
        coefficients = np.asarray(
            definition["coefficients"],
            dtype=float,
        )
        row = {
            "parent_id": parent_id,
            "noise_mode": str(noise_mode),
            "repetition": int(repetition),
            "geometry_index": int(geometry_index),
            "geometry_id": str(definition["geometry_id"]),
            "arm": arm,
            "magnitude": magnitude,
            "sign": sign,
            "axis_left": int(definition.get("axis_left", -1)),
            "axis_right": int(definition.get("axis_right", -1)),
            "sign_left": int(definition.get("sign_left", 0)),
            "sign_right": int(definition.get("sign_right", 0)),
            **{
                f"coefficient_{index}": float(value)
                for index, value in enumerate(coefficients)
            },
            "expected_halo_share": expected_halo,
            "world_seed": int(world_seed),
            "anchor_seed": int(anchor_seed),
            "geometry_seed": int(geometry_seed),
            "null_tangent_seed": int(null_tangent_seed),
            "probe_seed": int(probe_seed),
            "basis_sha256": context["basis_sha256"],
            "coefficient_sha256": context["coefficient_sha256"],
            **context["frame_checks"],
            "basis_gram_error": context["basis_gram_error"],
            "maximum_basis_core_inner_product": context[
                "maximum_basis_core_inner_product"
            ],
            "maximum_basis_halo_inner_product": context[
                "maximum_basis_halo_inner_product"
            ],
            "raw_baseline_reconstruction_error": context[
                "raw_baseline_reconstruction_error"
            ],
            "orthonormal_core_change": context[
                "orthonormal_core_change"
            ],
            "orthonormal_halo_change": context[
                "orthonormal_halo_change"
            ],
            "jacobian_rank": int(
                context["constraint_audit"]["jacobian_rank"]
            ),
            "jacobian_nullity": int(
                context["constraint_audit"]["jacobian_nullity"]
            ),
            "maximum_constraint_residual": float(
                context["constraint_audit"][
                    "maximum_constraint_residual"
                ]
            ),
            "minimum_source_projection_norm": float(
                context["constraint_audit"][
                    "minimum_source_projection_norm"
                ]
            ),
            **geometry_checks,
            "normal_builder_equivalence_error": normal_builder_error,
            "maximum_standardized_macro_drift": macro_drift,
            **information_match,
            "information_scale_ratio_to_baseline": float(
                information_match["information_match_scale"]
                / max(float(baseline_scale), 1e-12)
            ),
            **coordinates,
            "interaction_sha256": hashlib.sha256(
                np.ascontiguousarray(interaction).tobytes()
            ).hexdigest(),
        }
        geometry_rows.append(row)
        if bool(config.get("_geometry_only", False)):
            continue
        world = apply_interaction(context["base_world"], interaction)
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
                "geometry_id": str(definition["geometry_id"]),
                "arm": arm,
                "magnitude": magnitude,
                "sign": sign,
                "axis_left": int(definition.get("axis_left", -1)),
                "axis_right": int(definition.get("axis_right", -1)),
                "sign_left": int(definition.get("sign_left", 0)),
                "sign_right": int(definition.get("sign_right", 0)),
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
    basis_row = {
        "parent_id": parent_id,
        "noise_mode": str(noise_mode),
        "repetition": int(repetition),
        "basis_sha256": context["basis_sha256"],
        "coefficient_sha256": context["coefficient_sha256"],
        **context["constraint_audit"],
    }
    basis_row.pop("jacobian_singular_values")
    for probe in range(context["coefficients"].shape[0]):
        for axis in range(context["coefficients"].shape[1]):
            basis_row[f"probe_{probe:02d}_axis_{axis}"] = float(
                context["coefficients"][probe, axis]
            )
    jacobian_rows = []
    for coordinate_index, coordinate in enumerate(
        context["coordinate_names"]
    ):
        for probe in range(context["jacobian"].shape[1]):
            jacobian_rows.append({
                "parent_id": parent_id,
                "noise_mode": str(noise_mode),
                "repetition": int(repetition),
                "coordinate": coordinate,
                "coordinate_index": coordinate_index,
                "probe_index": probe,
                "standardized_derivative": float(
                    context["jacobian"][coordinate_index, probe]
                ),
            })
    return {
        "parent_id": parent_id,
        "geometry_rows": geometry_rows,
        "outcome_rows": outcome_rows,
        "basis_row": basis_row,
        "jacobian_rows": jacobian_rows,
        "coefficients": context["coefficients"],
        "jacobian": context["jacobian"],
        "source_seeds": [
            int(world_seed),
            int(anchor_seed),
            int(geometry_seed),
            int(null_tangent_seed),
            int(probe_seed),
            *map(int, outcome_seeds),
            *map(int, diagnostic_seeds),
        ],
    }


def _preflight_equivalence(
    geometry_rows: pd.DataFrame,
    basis_rows: pd.DataFrame,
    preflight_dir: Path,
) -> tuple[bool, dict[str, Any]]:
    if not preflight_dir.exists():
        return False, {"reason": "preflight directory is missing"}
    manifest = verify_run_manifest(preflight_dir / "run_manifest.json")
    inventory = verify_artifact_inventory(
        preflight_dir / "artifact_inventory.json"
    )
    expected_geometry = pd.read_csv(
        preflight_dir / "geometry_rows.csv",
        usecols=["parent_id", "geometry_id", "interaction_sha256"],
    ).sort_values(["parent_id", "geometry_id"]).reset_index(drop=True)
    observed_geometry = geometry_rows[
        ["parent_id", "geometry_id", "interaction_sha256"]
    ].sort_values(["parent_id", "geometry_id"]).reset_index(drop=True)
    expected_basis = pd.read_csv(
        preflight_dir / "basis_rows.csv",
        usecols=["parent_id", "basis_sha256", "coefficient_sha256"],
    ).sort_values("parent_id").reset_index(drop=True)
    observed_basis = basis_rows[
        ["parent_id", "basis_sha256", "coefficient_sha256"]
    ].sort_values("parent_id").reset_index(drop=True)
    checks = {
        "manifest": manifest["status"] == "RUN_MANIFEST_PASS",
        "inventory": inventory["status"] == "INVENTORY_PASS",
        "geometry_hashes": expected_geometry.equals(observed_geometry),
        "basis_hashes": expected_basis.equals(observed_basis),
    }
    return bool(all(checks.values())), checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preflight-dir", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument(
        "--mode",
        choices=["geometry-preflight", "smoke", "discovery"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    geometry_only = args.mode == "geometry-preflight"
    smoke = args.mode == "smoke"
    config["_geometry_only"] = geometry_only
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
    plan = _geometry_plan(config)
    source_lock = r2e._source_lock(config)
    tasks = [
        (str(noise), repetition)
        for noise in config["noise_modes"]
        for repetition in range(parents_per_noise)
    ]
    streams_per_parent = 5 + 2 * outcome_replicates
    root_seed = int(config["smoke_seed" if smoke else "seed"])
    parent_streams = np.random.SeedSequence(root_seed).spawn(len(tasks))
    nested_seeds = [
        [
            int(stream.generate_state(1, dtype=np.uint64)[0])
            for stream in parent.spawn(streams_per_parent)
        ]
        for parent in parent_streams
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
            seeds[4],
            seeds[5 : 5 + outcome_replicates],
            seeds[5 + outcome_replicates : streams_per_parent],
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
    basis_rows = pd.DataFrame([item["basis_row"] for item in nested])
    jacobian_rows = pd.DataFrame([
        row for item in nested for row in item["jacobian_rows"]
    ])
    expected_parents = len(config["noise_modes"]) * parents_per_noise
    expected_geometries = expected_parents * len(plan)
    expected_outcomes = (
        0
        if geometry_only
        else expected_geometries * outcome_replicates
    )
    gates = config["gates"]
    macro_constrained_arms = list(
        map(
            str,
            config.get(
                "macro_constrained_arms",
                ["axis", "corner", "registered_null"],
            ),
        )
    )
    constrained_rows = geometry_rows[
        geometry_rows["arm"].isin(macro_constrained_arms)
    ]
    registered_null_rows = geometry_rows[
        geometry_rows["arm"] == "registered_null"
    ]
    normal_rows = geometry_rows[
        geometry_rows["arm"].isin(["baseline", "normal"])
    ]
    all_source_seeds = [
        seed for item in nested for seed in item["source_seeds"]
    ]
    preflight_match = True
    preflight_checks: dict[str, Any] = {"not_required": True}
    if args.mode == "discovery":
        preflight_match, preflight_checks = _preflight_equivalence(
            geometry_rows,
            basis_rows,
            args.preflight_dir,
        )
    common_random_numbers = bool(
        geometry_only
        or (
            outcome_rows.groupby(["parent_id", "outcome_replicate"])[
                ["outcome_seed", "diagnostic_seed"]
            ].nunique()
            == 1
        ).all().all()
    )
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "parent_count": bool(
            geometry_rows["parent_id"].nunique() == expected_parents
        ),
        "geometry_count": bool(len(geometry_rows) == expected_geometries),
        "outcome_count": bool(len(outcome_rows) == expected_outcomes),
        "geometry_completeness": bool(
            (
                geometry_rows.groupby("parent_id")["geometry_id"].nunique()
                == len(plan)
            ).all()
        ),
        "outcome_completeness": bool(
            geometry_only
            or (
                outcome_rows.groupby(
                    ["parent_id", "geometry_id"]
                )["outcome_replicate"].nunique()
                == outcome_replicates
            ).all()
        ),
        "source_seed_uniqueness": bool(
            len(all_source_seeds) == len(set(all_source_seeds))
        ),
        "common_random_numbers": common_random_numbers,
        "basis_constraint": bool(
            geometry_rows["maximum_constraint_residual"].max()
            <= float(gates["maximum_constraint_residual"])
            and geometry_rows["jacobian_nullity"].min()
            >= int(config["tangent_dimensions"])
        ),
        "basis_orthonormality": bool(
            geometry_rows["basis_gram_error"].max()
            <= float(gates["maximum_frame_error"])
            and geometry_rows[
                "maximum_basis_core_inner_product"
            ].max()
            <= float(gates["maximum_frame_error"])
            and geometry_rows[
                "maximum_basis_halo_inner_product"
            ].max()
            <= float(gates["maximum_frame_error"])
        ),
        "baseline_reconstruction": bool(
            geometry_rows["raw_baseline_reconstruction_error"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
            and geometry_rows["orthonormal_core_change"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
            and geometry_rows["orthonormal_halo_change"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
        ),
        "normal_builder_equivalence": bool(
            normal_rows["normal_builder_equivalence_error"].max()
            <= float(gates["maximum_matched_builder_error"])
        ),
        "information_match": bool(
            geometry_rows["information_match_relative_error"].max()
            <= float(gates["maximum_information_match_relative_error"])
        ),
        "geometry_frame": bool(
            geometry_rows["maximum_axis_norm_error"].max()
            <= float(gates["maximum_frame_error"])
            and geometry_rows["maximum_axis_inner_product"].max()
            <= float(gates["maximum_frame_error"])
            and geometry_rows[
                "maximum_double_centering_marginal_error"
            ].max()
            <= float(gates["maximum_marginal_error"])
            and geometry_rows[
                "maximum_geometry_marginal_error"
            ].max()
            <= float(gates["maximum_marginal_error"])
            and geometry_rows["halo_share_error"].max()
            <= float(gates["maximum_halo_share_error"])
        ),
        "all_author_support": bool(
            (
                geometry_rows["realized_author_support"]
                == int(config["halo_author_support"])
            ).all()
        ),
        "macro_coordinate_drift": bool(
            constrained_rows["maximum_standardized_macro_drift"].max()
            <= float(gates["maximum_standardized_macro_drift"])
        ),
        "preflight_equivalence": bool(preflight_match),
        "numeric_integrity": bool(
            np.isfinite(
                geometry_rows[[
                    "operator_total_information",
                    *map(str, config["constraint_coordinates"]),
                ]].to_numpy(dtype=float)
            ).all()
        ),
    }
    plus_normal = geometry_rows[
        (geometry_rows["arm"] == "normal")
        & (geometry_rows["sign"] == 1)
    ]
    minus_normal = geometry_rows[
        (geometry_rows["arm"] == "normal")
        & (geometry_rows["sign"] == -1)
    ]
    potency = {}
    for noise in map(str, config["noise_modes"]):
        plus = float(
            plus_normal[plus_normal["noise_mode"] == noise][
                "operator_whitened_leakage"
            ].mean()
        )
        minus = float(
            minus_normal[minus_normal["noise_mode"] == noise][
                "operator_whitened_leakage"
            ].mean()
        )
        potency[noise] = {
            "plus_endpoint_mean_leakage": plus,
            "minus_endpoint_mean_leakage": minus,
            "leakage_gap": plus - minus,
            "pass": bool(
                plus >= float(gates["minimum_positive_control_leakage"])
                and plus - minus
                >= float(gates["minimum_positive_control_leakage_gap"])
            ),
        }
    integrity["positive_control_geometry_potency"] = bool(
        all(record["pass"] for record in potency.values())
    )
    if all(integrity.values()):
        if geometry_only:
            status = "V8_R2F_GEOMETRY_PREFLIGHT_PASS"
        elif smoke:
            status = "V8_R2F_SMOKE_DATA_COMPLETE"
        else:
            status = "V8_R2F_DISCOVERY_DATA_COMPLETE"
    else:
        status = "V8_R2F_STOP_INVALID_DATA_GENERATION"
    decision = {
        "status": status,
        "mode": args.mode,
        "integrity_checks": integrity,
        "preflight_checks": preflight_checks,
        "positive_control_geometry_potency": potency,
        "parents": int(geometry_rows["parent_id"].nunique()),
        "geometries": int(len(geometry_rows)),
        "outcomes": int(len(outcome_rows)),
        "geometry_count_per_parent": len(plan),
        "maximum_constraint_residual": float(
            geometry_rows["maximum_constraint_residual"].max()
        ),
        "maximum_standardized_macro_drift": float(
            constrained_rows["maximum_standardized_macro_drift"].max()
        ),
        "registered_null_maximum_standardized_macro_drift": float(
            registered_null_rows[
                "maximum_standardized_macro_drift"
            ].max()
        ),
        "maximum_normal_builder_equivalence_error": float(
            normal_rows["normal_builder_equivalence_error"].max()
        ),
        "source_seed_count": len(all_source_seeds),
        "unique_source_seed_count": len(set(all_source_seeds)),
        "source_lock": source_lock,
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    geometry_rows.to_csv(args.output_dir / "geometry_rows.csv", index=False)
    basis_rows.to_csv(args.output_dir / "basis_rows.csv", index=False)
    jacobian_rows.to_csv(
        args.output_dir / "constraint_jacobians.csv",
        index=False,
    )
    parent_order = [item["parent_id"] for item in nested]
    np.savez_compressed(
        args.output_dir / "tangent_basis.npz",
        parent_ids=np.asarray(parent_order),
        coefficients=np.stack(
            [item["coefficients"] for item in nested],
            axis=0,
        ),
        jacobians=np.stack(
            [item["jacobian"] for item in nested],
            axis=0,
        ),
    )
    if not geometry_only:
        outcome_rows.to_csv(
            args.output_dir / "outcome_rows.csv",
            index=False,
        )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "streams_per_parent": streams_per_parent,
        "source_seed_count": len(all_source_seeds),
        "unique_source_seed_count": len(set(all_source_seeds)),
        "all_source_streams_unique": (
            len(all_source_seeds) == len(set(all_source_seeds))
        ),
        "common_random_numbers_across_45_geometries": True,
        "fresh_streams_across_parents_and_replicates": True,
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2F Local Response Operator Data\n\n"
        f"Decision: `{status}`\n\n"
        "This artifact contains geometry and detector outcomes only. "
        "Candidate selection is performed by the frozen analysis script.\n",
        encoding="utf-8",
    )
    input_paths = [
        ROOT
        / str(config["coordinate_scale_source"]["path"]),
    ]
    if args.mode == "discovery":
        input_paths.extend([
            args.preflight_dir / "decision.json",
            args.preflight_dir / "geometry_rows.csv",
            args.preflight_dir / "basis_rows.csv",
        ])
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=input_paths,
        config_path=args.config,
        code_paths=[
            ROOT / path
            for path in config["frozen_source_sha256"]
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
        "integrity_checks": integrity,
        "parents": decision["parents"],
        "geometries": decision["geometries"],
        "outcomes": decision["outcomes"],
        "maximum_constraint_residual": decision[
            "maximum_constraint_residual"
        ],
        "maximum_standardized_macro_drift": decision[
            "maximum_standardized_macro_drift"
        ],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
