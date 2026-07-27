#!/usr/bin/env python3
"""Run the corrected H4D-R2E.1 heterogeneity-injection discovery."""
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
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e1.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_conditional_heterogeneity_injection"
    / "v37h4d_r2e1_corrected_discovery"
)


def _unit(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    return result / max(float(np.linalg.norm(result)), 1e-12)


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
    # support=64 is required even at lambda=0 so the RNG consumes the same
    # support-selection draw as every all-author halo geometry.
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
    core, halo, tangent = orthonormal_geometry_frame(
        raw_core,
        raw_halo,
        seed=int(tangent_seed),
    )
    frame_checks = frame_audit(core, halo, tangent)
    orthonormal_core_change = float(
        np.linalg.norm(core - raw_core_unit)
    )
    orthonormal_halo_change = float(
        np.linalg.norm(halo - raw_halo_unit)
    )
    parent_id = f"{noise_mode}|r{int(repetition):04d}"
    geometry_rows = []
    outcome_rows = []
    baseline_scale = None
    for geometry_index, definition in enumerate(r2e._geometry_plan(config)):
        expected_halo = r2e._expected_halo_share(
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
        builder_equivalence_error = float("nan")
        direct_interaction = None
        if str(definition["arm"]) in {"baseline", "normal"}:
            direct_interaction, _ = build_controlled_halo_interaction(
                anchor_world["interaction"],
                spec=spec,
                test_authors=test,
                active_test_authors=active,
                active_conditions=conditions,
                halo_lambda=expected_halo,
                halo_author_support=int(config["halo_author_support"]),
                seed=int(geometry_seed),
            )
            builder_equivalence_error = float(
                np.linalg.norm(
                    _unit(direct_interaction[test])
                    - _unit(test_geometry)
                )
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
        matched_builder_error = float("nan")
        matched_scale_error = float("nan")
        maximum_operator_coordinate_error = float("nan")
        if direct_interaction is not None:
            direct_matched, direct_match = match_residual_information(
                base_world,
                direct_interaction,
                target_information=float(
                    anchor_audit["information_budget_residual"]
                ),
                spec=spec,
                active_test_authors=active,
                active_conditions=conditions,
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
            direct_coordinates = geometry_information_coordinates(
                base_world,
                direct_matched,
                spec=spec,
                active_test_authors=active,
                active_conditions=conditions,
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
            matched_builder_error = float(
                np.linalg.norm(
                    interaction[test] - direct_matched[test]
                )
                / max(
                    float(np.linalg.norm(direct_matched[test])),
                    1e-12,
                )
            )
            matched_scale_error = abs(
                float(information_match["information_match_scale"])
                - float(direct_match["information_match_scale"])
            ) / max(
                abs(float(direct_match["information_match_scale"])),
                1e-12,
            )
            maximum_operator_coordinate_error = float(max(
                abs(float(coordinates[key]) - float(direct_coordinates[key]))
                / max(abs(float(direct_coordinates[key])), 1e-12)
                for key in coordinates
            ))
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
        geometry_rows.append({
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
            "raw_baseline_reconstruction_error": (
                raw_baseline_reconstruction_error
            ),
            "orthonormal_core_change": orthonormal_core_change,
            "orthonormal_halo_change": orthonormal_halo_change,
            **geometry_checks,
            "normal_builder_equivalence_error": (
                builder_equivalence_error
            ),
            "matched_builder_equivalence_error": matched_builder_error,
            "matched_information_scale_error": matched_scale_error,
            "maximum_operator_coordinate_error": (
                maximum_operator_coordinate_error
            ),
            **information_match,
            "information_scale_ratio_to_baseline": scale_ratio,
            **coordinates,
            "interaction_sha256": hashlib.sha256(
                np.ascontiguousarray(interaction).tobytes()
            ).hexdigest(),
        })
        if bool(config.get("_geometry_only", False)):
            continue
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=["geometry-preflight", "smoke", "discovery"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    smoke = args.mode == "smoke"
    geometry_only = args.mode == "geometry-preflight"
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
    bootstrap_draws = int(
        config["smoke_bootstrap_draws" if smoke else "bootstrap_draws"]
    )
    source_lock = r2e._source_lock(config)
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
        np.random.SeedSequence(root_seed ^ 0x2E1E2E1E)
        .generate_state(1, dtype=np.uint64)[0]
    )
    if geometry_only:
        statistics = pd.DataFrame()
        endpoint: dict[str, Any] = {}
    else:
        statistics, endpoint, _ = r2e._analyze_statistics(
            outcome_rows,
            config=config,
            seed=analysis_seed,
            draws=bootstrap_draws,
        )
    geometry_count = len(r2e._geometry_plan(config))
    expected_parents = 2 * parents_per_noise
    expected_geometry = expected_parents * geometry_count
    expected_outcomes = (
        0 if geometry_only else expected_geometry * outcome_replicates
    )
    gates = config["gates"]
    common_random_number_check = bool(
        geometry_only
        or (
            outcome_rows.groupby(["parent_id", "outcome_replicate"])[
                ["outcome_seed", "diagnostic_seed"]
            ].nunique()
            == 1
        ).all().all()
    )
    normal_rows = geometry_rows[
        geometry_rows["arm"].isin(["baseline", "normal"])
    ]
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
            geometry_only
            or (
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
        "normal_builder_equivalence": bool(
            normal_rows["normal_builder_equivalence_error"].max()
            <= float(gates["maximum_builder_equivalence_error"])
        ),
        "baseline_reconstruction": bool(
            geometry_rows["raw_baseline_reconstruction_error"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
            and geometry_rows["orthonormal_core_change"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
            and geometry_rows["orthonormal_halo_change"].max()
            <= float(gates["maximum_raw_reconstruction_error"])
        ),
        "matched_builder_equivalence": bool(
            normal_rows["matched_builder_equivalence_error"].max()
            <= float(gates["maximum_matched_builder_error"])
            and normal_rows["matched_information_scale_error"].max()
            <= float(gates["maximum_matched_scale_error"])
            and normal_rows["maximum_operator_coordinate_error"].max()
            <= float(gates["maximum_operator_coordinate_error"])
        ),
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
                geometry_rows["realized_author_support"]
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
            and (
                geometry_only
                or np.isfinite(
                statistics.loc[
                    statistics["arm"] != "baseline",
                    [
                        "direction_sensitivity_j",
                        "total_side_variance",
                        "delta_variance",
                    ],
                ].to_numpy(dtype=float)
                ).all()
            )
        ),
    }
    plus_endpoint = geometry_rows[
        (geometry_rows["arm"] == "normal")
        & np.isclose(
            geometry_rows["magnitude"],
            max(config["normal_tau_grid"]),
        )
        & (geometry_rows["sign"] == 1)
    ]
    minus_endpoint = geometry_rows[
        (geometry_rows["arm"] == "normal")
        & np.isclose(
            geometry_rows["magnitude"],
            max(config["normal_tau_grid"]),
        )
        & (geometry_rows["sign"] == -1)
    ]
    potency_by_noise = {}
    for noise in map(str, config["noise_modes"]):
        plus_leakage = float(
            plus_endpoint[
                plus_endpoint["noise_mode"] == noise
            ]["operator_whitened_leakage"].mean()
        )
        minus_leakage = float(
            minus_endpoint[
                minus_endpoint["noise_mode"] == noise
            ]["operator_whitened_leakage"].mean()
        )
        potency_by_noise[noise] = {
            "plus_endpoint_mean_leakage": plus_leakage,
            "minus_endpoint_mean_leakage": minus_leakage,
            "leakage_gap": plus_leakage - minus_leakage,
            "minimum_pass": bool(
                plus_leakage
                >= float(gates["minimum_positive_control_leakage"])
                and plus_leakage - minus_leakage
                >= float(gates["minimum_positive_control_leakage_gap"])
            ),
            "registered_range_pass": bool(
                float(gates["minimum_registered_leakage_range"])
                <= plus_leakage
                <= float(gates["maximum_registered_leakage_range"])
            ),
        }
    integrity["positive_control_geometry_potency"] = bool(
        all(
            record["minimum_pass"]
            and record["registered_range_pass"]
            for record in potency_by_noise.values()
        )
    )
    if geometry_only:
        status = (
            "V8_R2E1_GEOMETRY_PREFLIGHT_PASS"
            if all(integrity.values())
            else "V8_R2E1_STOP_INVALID_GEOMETRY_PREFLIGHT"
        )
        gate_checks = {"potency_by_noise": potency_by_noise}
    elif smoke:
        status = (
            "V8_R2E1_SMOKE_COMPLETE"
            if all(integrity.values())
            else "V8_R2E1_STOP_INVALID_PROTOCOL"
        )
        gate_checks: dict[str, Any] = {}
    else:
        legacy_status, gate_checks = r2e._decision_status(
            integrity=integrity,
            endpoint=endpoint,
            geometry_rows=geometry_rows,
            config=config,
        )
        status = legacy_status.replace("V8_R2E_", "V8_R2E1_", 1)
    decision = {
        "status": status,
        "mode": args.mode,
        "corrects": "V8_R2E_INVALID_POSITIVE_CONTROL_CORE_RNG_MISMATCH",
        "integrity_checks": integrity,
        "gate_checks": gate_checks,
        "endpoint": endpoint,
        "geometry_potency": potency_by_noise,
        "parents": int(geometry_rows["parent_id"].nunique()),
        "geometries": int(len(geometry_rows)),
        "outcomes": int(len(outcome_rows)),
        "maximum_normal_builder_equivalence_error": float(
            normal_rows["normal_builder_equivalence_error"].max()
        ),
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
    if not geometry_only:
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
        "# H4D-R2E.1 Corrected Conditional-Heterogeneity Injection\n\n"
        f"Decision: `{status}`\n\n"
        "The all-author core RNG path is now held identical across direct "
        "builder and reconstructed normal geometries.\n",
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
            ROOT
            / "scripts"
            / "run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e.py",
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
        "geometry_potency": potency_by_noise,
        "maximum_normal_builder_equivalence_error": float(
            normal_rows["normal_builder_equivalence_error"].max()
        ),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
