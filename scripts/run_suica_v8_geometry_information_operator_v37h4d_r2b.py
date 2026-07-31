#!/usr/bin/env python3
"""Generate the paired H4D-R2B geometry-information discovery panel."""
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

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _clopper,
    _read,
    _spec,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_geometry_information_operator import (  # noqa: E402
    GEOMETRY_FAMILIES,
    apply_interaction,
    build_geometry_interaction,
    geometry_information_coordinates,
    match_residual_information,
)
from suica_core.v8_minority_information_frontier import (  # noqa: E402
    complete_double_center,
    plant_minority_interaction,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    additive_residual,
    simulate_reference_world,
    wild_residual_diagnostics,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_geometry_information_operator_v37h4d_r2b.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_geometry_information_operator"
    / "v37h4d_r2b_discovery"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(config: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for relative, expected in config["frozen_detector_sha256"].items():
        observed = _sha256(ROOT / relative)
        rows.append({
            "path": relative,
            "expected_sha256": str(expected),
            "observed_sha256": observed,
            "match": observed == str(expected),
        })
    return {
        "pass": bool(all(row["match"] for row in rows)),
        "files": rows,
    }


def _base_definitions(
    config: dict[str, Any],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    repetitions = (
        int(config["smoke_repetitions"])
        if mode == "smoke"
        else int(config["discovery_repetitions"])
    )
    return [
        {
            "noise_mode": str(noise),
            "active_test_authors": int(m),
            "repetitions": repetitions,
        }
        for noise in config["noise_modes"]
        for m in config["active_test_author_grid"]
    ]


def _geometry_plan(
    config: dict[str, Any],
    *,
    repetition: int,
) -> list[dict[str, Any]]:
    lambdas = list(map(float, config["halo_lambda_grid"]))
    plan = []
    for family in config["geometry_families"]:
        plan.append({
            "geometry_family": str(family),
            "halo_lambda": (
                lambdas[int(repetition) % len(lambdas)]
                if str(family) == "halo_sweep"
                else float("nan")
            ),
        })
    return plan


def _simulate_base_world(
    config: dict[str, Any],
    *,
    noise_mode: str,
    seed: int,
) -> dict[str, Any]:
    spec = _spec(config)
    return simulate_reference_world(
        seed=seed,
        world="additive",
        effect_share=0.0,
        reference_jsd=float(config["main_reference_jsd"]),
        support_coverage=1.0,
        near_kernel_fraction=0.02,
        noise_mode=noise_mode,
        opportunity_prefixes=tuple(
            map(int, config["opportunity_prefixes"])
        ),
        author_tilt=float(config["author_tilt"]),
        author_amplitude=float(config["author_amplitude"]),
        condition_amplitude=float(config["condition_amplitude"]),
        society_amplitude=float(config["society_amplitude"]),
        group_amplitude=float(config["group_amplitude"]),
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
        minority_author_fraction=0.1,
        minority_condition_fraction=0.25,
        spec=spec,
        acquisition_reference_shift=True,
    )


def _evaluate_geometry(
    *,
    base_world: dict[str, Any],
    anchor_interaction: np.ndarray,
    anchor_audit: dict[str, Any],
    definition: dict[str, Any],
    geometry: dict[str, Any],
    repetition: int,
    base_id: str,
    world_seed: int,
    anchor_seed: int,
    geometry_seed: int,
    diagnostic_seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    spec = _spec(config)
    _, _, test = spec.author_split
    active = np.asarray(
        anchor_audit["selected_test_authors"],
        dtype=int,
    )
    conditions = np.asarray(
        anchor_audit["selected_conditions"],
        dtype=int,
    )
    interaction = build_geometry_interaction(
        anchor_interaction,
        spec=spec,
        test_authors=test,
        active_test_authors=active,
        active_conditions=conditions,
        geometry_family=str(geometry["geometry_family"]),
        halo_lambda=float(geometry["halo_lambda"]),
        seed=geometry_seed,
    )
    interaction, match = match_residual_information(
        base_world,
        interaction,
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
    world = apply_interaction(base_world, interaction)
    primary_k = int(config["primary_opportunities"])
    counts = world["counts_by_k"][primary_k]
    means = world["means_by_k"][primary_k]
    left, left_mask = additive_residual(means[2], counts[2], test)
    right, right_mask = additive_residual(means[3], counts[3], test)
    diagnostics = wild_residual_diagnostics(
        left,
        right,
        left_mask,
        right_mask,
        rank=3,
        seed=diagnostic_seed,
        permutations=int(config["_active_permutations"]),
        alpha=float(config["holm_alpha"]),
    )
    alpha = float(config["holm_alpha"])
    q_test = interaction[
        np.ix_(
            test,
            np.arange(spec.conditions),
            np.arange(spec.dimensions),
        )
    ]
    grand_mean = interaction.mean(axis=(0, 1), keepdims=True)
    projection_error = float(
        np.max(
            np.abs(
                complete_double_center(q_test)
                - complete_double_center(q_test - grand_mean)
            )
        )
    )
    return {
        "base_id": base_id,
        "repetition": int(repetition),
        "noise_mode": str(definition["noise_mode"]),
        "active_test_authors": int(
            definition["active_test_authors"]
        ),
        "geometry_family": str(geometry["geometry_family"]),
        "halo_lambda": float(geometry["halo_lambda"]),
        "world_seed": int(world_seed),
        "anchor_seed": int(anchor_seed),
        "geometry_seed": int(geometry_seed),
        "diagnostic_seed": int(diagnostic_seed),
        **match,
        **coordinates,
        **diagnostics,
        "crc_detected": bool(diagnostics["crc_p_holm"] < alpha),
        "cross_low_rank_detected": bool(
            diagnostics["cross_low_rank_p_holm"] < alpha
        ),
        "hc_detected": bool(diagnostics["hc_p_holm"] < alpha),
        "crc_or_hc_detected": bool(
            diagnostics["crc_p_holm"] < alpha
            or diagnostics["hc_p_holm"] < alpha
        ),
        "projection_grand_mean_compatibility_error": projection_error,
        "selected_test_authors": json.dumps(
            anchor_audit["selected_test_authors"]
        ),
        "selected_conditions": json.dumps(
            anchor_audit["selected_conditions"]
        ),
    }


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        int,
        int,
        list[int],
    ],
) -> dict[str, Any]:
    (
        config,
        definition,
        repetition,
        world_seed,
        anchor_seed,
        diagnostic_seed,
        geometry_seeds,
    ) = payload
    spec = _spec(config)
    base_world = _simulate_base_world(
        config,
        noise_mode=str(definition["noise_mode"]),
        seed=world_seed,
    )
    anchor_world, anchor_audit = plant_minority_interaction(
        base_world,
        spec=spec,
        seed=anchor_seed,
        active_test_authors=int(
            definition["active_test_authors"]
        ),
        active_conditions=int(config["active_conditions"]),
        support_scheme="fixed",
        interaction_shape="iid_block",
        scaling_arm="active_snr",
        global_effect_share=float(
            config["anchor_global_effect_share"]
        ),
        active_cell_snr=float(config["anchor_active_cell_snr"]),
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
    plan = _geometry_plan(config, repetition=repetition)
    base_id = (
        f"{definition['noise_mode']}|"
        f"m{int(definition['active_test_authors'])}|"
        f"r{int(repetition):04d}"
    )
    rows = [
        _evaluate_geometry(
            base_world=base_world,
            anchor_interaction=anchor_world["interaction"],
            anchor_audit=anchor_audit,
            definition=definition,
            geometry=geometry,
            repetition=repetition,
            base_id=base_id,
            world_seed=world_seed,
            anchor_seed=anchor_seed,
            geometry_seed=geometry_seed,
            diagnostic_seed=diagnostic_seed,
            config=config,
        )
        for geometry, geometry_seed in zip(
            plan,
            geometry_seeds,
            strict=True,
        )
    ]
    return {
        "rows": rows,
        "base_id": base_id,
        "source_seeds": [
            world_seed,
            anchor_seed,
            diagnostic_seed,
            *geometry_seeds,
        ],
    }


def _summarize(
    cells: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    keys = [
        "geometry_family",
        "halo_lambda",
        "noise_mode",
        "active_test_authors",
    ]
    for key, group in cells.groupby(keys, sort=True, dropna=False):
        count = int(group["crc_or_hc_detected"].sum())
        lower, upper = _clopper(
            count,
            len(group),
            tail_alpha=0.025,
        )
        rows.append({
            **dict(zip(keys, key, strict=True)),
            "trials": int(len(group)),
            "crc_or_hc_detection_count": count,
            "crc_or_hc_detection_rate": count / len(group),
            "crc_or_hc_detection_lower": lower,
            "crc_or_hc_detection_upper": upper,
            "mean_information": float(
                group["operator_total_information"].mean()
            ),
            "mean_neff_author": float(
                group["operator_neff_author"].mean()
            ),
            "mean_neff_sign": float(
                group["operator_neff_sign"].mean()
            ),
            "mean_neff_cell": float(
                group["operator_neff_cell"].mean()
            ),
            "mean_rho3": float(group["operator_rho3"].mean()),
            "mean_whitened_leakage": float(
                group["operator_whitened_leakage"].mean()
            ),
        })
    return pd.DataFrame(rows)


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
    config["_active_permutations"] = (
        int(config["smoke_permutations"])
        if args.mode == "smoke"
        else int(config["permutations"])
    )
    source_lock = _source_lock(config)
    definitions = _base_definitions(config, mode=args.mode)
    tasks = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(int(definition["repetitions"]))
    ]
    geometry_count = len(config["geometry_families"])
    streams_per_base = 3 + geometry_count
    seed = (
        int(config["smoke_seed"])
        if args.mode == "smoke"
        else int(config["seed"])
    )
    streams = np.random.SeedSequence(seed).spawn(
        streams_per_base * len(tasks)
    )
    seeds = [
        int(stream.generate_state(1, dtype=np.uint64)[0])
        for stream in streams
    ]
    payloads = []
    for index, (definition, repetition) in enumerate(tasks):
        start = streams_per_base * index
        payloads.append((
            config,
            definition,
            repetition,
            seeds[start],
            seeds[start + 1],
            seeds[start + 2],
            seeds[start + 3 : start + streams_per_base],
        ))
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    cells = pd.DataFrame([
        row for item in nested for row in item["rows"]
    ])
    summary = _summarize(cells, config=config)
    expected_rows = len(tasks) * geometry_count
    base_counts = cells.groupby("base_id").size()
    family_counts = cells.groupby("base_id")[
        "geometry_family"
    ].nunique()
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "row_count": bool(len(cells) == expected_rows),
        "base_pairing": bool(
            (base_counts == geometry_count).all()
            and (family_counts == geometry_count).all()
        ),
        "seed_stream_uniqueness": bool(len(seeds) == len(set(seeds))),
        "information_match": bool(
            cells["information_match_relative_error"].max()
            <= float(
                config["gates"][
                    "maximum_information_match_relative_error"
                ]
            )
        ),
        "operator_information_identity": bool(
            np.max(
                np.abs(
                    cells["operator_total_information"]
                    - cells["matched_residual_information"]
                )
                / np.maximum(
                    cells["matched_residual_information"],
                    1e-12,
                )
            )
            <= 1e-6
        ),
        "projection_compatibility": bool(
            cells[
                "projection_grand_mean_compatibility_error"
            ].max()
            <= float(
                config["gates"][
                    "maximum_projection_compatibility_error"
                ]
            )
        ),
        "numeric_integrity": bool(
            np.isfinite(
                cells[[
                    "crc",
                    "cross_low_rank_ratio",
                    "hc",
                    "operator_total_information",
                    "operator_neff_author",
                    "operator_neff_cell",
                    "operator_rho3",
                    "operator_whitened_leakage",
                    "operator_neff_sign",
                ]].to_numpy(dtype=float)
            ).all()
        ),
    }
    status = (
        "V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_"
        + (
            "SMOKE_COMPLETE"
            if args.mode == "smoke" and all(integrity.values())
            else (
                "DISCOVERY_COMPLETE"
                if all(integrity.values())
                else "STOP_INVALID_DESIGN"
            )
        )
    )
    decision = {
        "status": status,
        "mode": args.mode,
        "checks": integrity,
        "source_lock": source_lock,
        "row_count": int(len(cells)),
        "base_count": int(cells["base_id"].nunique()),
        "seed_stream_count": int(len(seeds)),
        "unique_seed_stream_count": int(len(set(seeds))),
        "maximum_information_match_relative_error": float(
            cells["information_match_relative_error"].max()
        ),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "geometry_rows.csv", index=False)
    summary.to_csv(args.output_dir / "geometry_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "pairing_audit.json", {
        "expected_geometry_rows_per_base": geometry_count,
        "minimum_rows_per_base": int(base_counts.min()),
        "maximum_rows_per_base": int(base_counts.max()),
        "minimum_families_per_base": int(family_counts.min()),
        "maximum_families_per_base": int(family_counts.max()),
    })
    _write(args.output_dir / "seed_audit.json", {
        "source_seed_count": len(seeds),
        "unique_source_seed_count": len(set(seeds)),
        "all_source_streams_unique": len(seeds) == len(set(seeds)),
        "diagnostic_seed_reuse": (
            "intentional within each paired base world"
        ),
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2B Geometry Information Operator\n\n"
        f"Decision: `{status}`\n\n"
        "This artifact is the paired geometry discovery panel. Predictive "
        "operator gates are evaluated in the separate LOGO audit.\n",
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
        "rows": int(len(cells)),
        "bases": int(cells["base_id"].nunique()),
        "checks": integrity,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

