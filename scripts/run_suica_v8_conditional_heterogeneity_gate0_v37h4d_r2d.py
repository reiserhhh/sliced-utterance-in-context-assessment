#!/usr/bin/env python3
"""Run the fresh repeated-outcome Gate-0 before the full H4D-R2D model."""
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
from suica_core.v8_conditional_heterogeneity_preflight import (  # noqa: E402
    conditional_variance,
    half_split_probabilities,
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
    ROOT / "configs/v8_conditional_heterogeneity_gate0_v37h4d_r2d.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_posterior_predictive_orbit"
    / "v37h4d_r2d_conditional_heterogeneity_gate0"
)
CELL_COLUMNS = [
    "noise_mode",
    "halo_lambda",
    "halo_author_support",
    "support_label",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(config: dict[str, Any]) -> dict[str, Any]:
    records = []
    for relative, expected in config["frozen_source_sha256"].items():
        observed = _sha256(ROOT / relative)
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


def _cell_definitions(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "noise_mode": str(noise),
            "halo_lambda": float(cell["halo_lambda"]),
            "halo_author_support": int(cell["halo_author_support"]),
            "support_label": str(cell["support_label"]),
        }
        for noise in config["noise_modes"]
        for cell in config["cells"]
    ]


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
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
        definition,
        repetition,
        world_seed,
        anchor_seed,
        geometry_seed,
        outcome_seeds,
        diagnostic_seeds,
    ) = payload
    spec = _spec(config)
    _, _, test = spec.author_split
    base_world = _simulate_base_world(
        config,
        noise_mode=str(definition["noise_mode"]),
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
    interaction, support_audit = build_controlled_halo_interaction(
        anchor_world["interaction"],
        spec=spec,
        test_authors=test,
        active_test_authors=active,
        active_conditions=conditions,
        halo_lambda=float(definition["halo_lambda"]),
        halo_author_support=int(definition["halo_author_support"]),
        seed=int(geometry_seed),
    )
    interaction, information_match = match_residual_information(
        base_world,
        interaction,
        target_information=float(
            anchor_audit["information_budget_residual"]
        ),
        spec=spec,
        active_test_authors=active,
        active_conditions=conditions,
        primary_opportunities=int(config["primary_opportunities"]),
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
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
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    world = apply_interaction(base_world, interaction)
    interaction_hash = hashlib.sha256(
        np.ascontiguousarray(interaction).tobytes()
    ).hexdigest()
    base_id = (
        f"{definition['noise_mode']}|"
        f"l{float(definition['halo_lambda']):.3f}|"
        f"s{int(definition['halo_author_support']):02d}|"
        f"{definition['support_label']}|r{int(repetition):04d}"
    )
    rows = []
    alpha = float(config["holm_alpha"])
    for outcome_index, (outcome_seed, diagnostic_seed) in enumerate(
        zip(outcome_seeds, diagnostic_seeds, strict=True)
    ):
        residuals = resample_outcome_pair(
            world,
            test_authors=test,
            seed=int(outcome_seed),
            noise_mode=str(definition["noise_mode"]),
            opportunity_prefixes=tuple(
                map(int, config["opportunity_prefixes"])
            ),
            primary_opportunities=int(config["primary_opportunities"]),
            panel_noise_amplitude=float(config["panel_noise_amplitude"]),
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
            alpha=alpha,
        )
        rows.append({
            "base_id": base_id,
            "repetition": int(repetition),
            **definition,
            "outcome_replicate": int(outcome_index),
            "outcome_half": (
                "A"
                if outcome_index < len(outcome_seeds) // 2
                else "B"
            ),
            "world_seed": int(world_seed),
            "anchor_seed": int(anchor_seed),
            "geometry_seed": int(geometry_seed),
            "outcome_seed": int(outcome_seed),
            "diagnostic_seed": int(diagnostic_seed),
            "interaction_sha256": interaction_hash,
            **information_match,
            **coordinates,
            **support_audit,
            **diagnostics,
            "crc_or_hc_detected": bool(
                diagnostics["crc_p_holm"] < alpha
                or diagnostics["hc_p_holm"] < alpha
            ),
        })
    return {
        "base_id": base_id,
        "rows": rows,
        "interaction_sha256": interaction_hash,
        "source_seeds": [
            int(world_seed),
            int(anchor_seed),
            int(geometry_seed),
            *map(int, outcome_seeds),
            *map(int, diagnostic_seeds),
        ],
    }


def _base_summary(
    rows: pd.DataFrame,
    *,
    outcome_replicates: int,
) -> pd.DataFrame:
    half = int(outcome_replicates) // 2
    records = []
    for base_id, group in rows.groupby("base_id", sort=True):
        ordered = group.sort_values("outcome_replicate")
        outcome = ordered["crc_or_hc_detected"].to_numpy(dtype=int)
        record = {
            "base_id": str(base_id),
            **{
                column: ordered.iloc[0][column]
                for column in CELL_COLUMNS
            },
            "outcome_replicates": int(len(outcome)),
            "success_total": int(outcome.sum()),
            "success_a": int(outcome[:half].sum()),
            "success_b": int(outcome[half:].sum()),
        }
        records.append(record)
    bases = pd.DataFrame(records)
    bases["candidate_probability"] = half_split_probabilities(
        bases["success_a"].to_numpy(dtype=float),
        half_replicates=half,
    )
    cell_success = bases.groupby(CELL_COLUMNS)["success_a"].transform(
        "sum"
    )
    cell_bases = bases.groupby(CELL_COLUMNS)["base_id"].transform(
        "count"
    )
    bases["cell_probability"] = (
        cell_success - bases["success_a"] + 0.5
    ) / ((cell_bases - 1) * half + 1.0)
    bases["candidate_log_loss"] = (
        bases["success_b"]
        * -np.log(bases["candidate_probability"])
        + (half - bases["success_b"])
        * -np.log(1.0 - bases["candidate_probability"])
    ) / half
    bases["cell_log_loss"] = (
        bases["success_b"]
        * -np.log(bases["cell_probability"])
        + (half - bases["success_b"])
        * -np.log(1.0 - bases["cell_probability"])
    ) / half
    empirical_b = bases["success_b"] / half
    bases["candidate_brier"] = (
        empirical_b * (1.0 - bases["candidate_probability"]) ** 2
        + (1.0 - empirical_b) * bases["candidate_probability"] ** 2
    )
    bases["cell_brier"] = (
        empirical_b * (1.0 - bases["cell_probability"]) ** 2
        + (1.0 - empirical_b) * bases["cell_probability"] ** 2
    )
    bases["log_loss_gain"] = (
        bases["cell_log_loss"] - bases["candidate_log_loss"]
    )
    bases["brier_gain"] = (
        bases["cell_brier"] - bases["candidate_brier"]
    )
    return bases


def _conditional_variance_table(
    bases: pd.DataFrame,
    *,
    outcome_replicates: int,
    seed: int,
    draws: int,
) -> tuple[pd.DataFrame, dict[str, float]]:
    groups = list(bases.groupby(CELL_COLUMNS, sort=True))
    points = np.asarray([
        conditional_variance(
            group["success_total"].to_numpy(dtype=float),
            replicates=int(outcome_replicates),
        )
        for _, group in groups
    ])
    streams = np.random.SeedSequence(int(seed)).spawn(len(groups))
    bootstrap = np.empty((int(draws), len(groups)), dtype=float)
    for column, (stream, (_, group)) in enumerate(
        zip(streams, groups, strict=True)
    ):
        count = group["success_total"].to_numpy(dtype=float)
        rng = np.random.default_rng(stream)
        for draw in range(int(draws)):
            sampled = count[rng.integers(0, len(count), len(count))]
            bootstrap[draw, column] = conditional_variance(
                sampled,
                replicates=int(outcome_replicates),
            )
    lower_max_deviation = np.max(
        points[None, :] - bootstrap,
        axis=1,
    )
    upper_max_deviation = np.max(
        bootstrap - points[None, :],
        axis=1,
    )
    simultaneous_lower_radius = float(
        np.quantile(lower_max_deviation, 0.95)
    )
    simultaneous_upper_radius = float(
        np.quantile(upper_max_deviation, 0.95)
    )
    records = []
    for column, ((key, group), point) in enumerate(
        zip(groups, points, strict=True)
    ):
        records.append({
            **dict(zip(CELL_COLUMNS, key, strict=True)),
            "bases": int(len(group)),
            "conditional_variance": float(point),
            "pointwise_lower_95": float(
                np.quantile(bootstrap[:, column], 0.025)
            ),
            "pointwise_upper_95": float(
                np.quantile(bootstrap[:, column], 0.975)
            ),
            "simultaneous_lower_95": float(
                point - simultaneous_lower_radius
            ),
            "simultaneous_upper_95": float(
                point + simultaneous_upper_radius
            ),
        })
    pooled_bootstrap = bootstrap.mean(axis=1)
    pooled = {
        "mean": float(points.mean()),
        "lower_95": float(np.quantile(pooled_bootstrap, 0.025)),
        "upper_95": float(np.quantile(pooled_bootstrap, 0.975)),
        "simultaneous_lower_radius": simultaneous_lower_radius,
        "simultaneous_upper_radius": simultaneous_upper_radius,
    }
    return pd.DataFrame(records), pooled


def _stratified_bootstrap_gains(
    bases: pd.DataFrame,
    *,
    seed: int,
    draws: int,
) -> dict[str, dict[str, float]]:
    groups = [
        group[["log_loss_gain", "brier_gain"]].to_numpy(dtype=float)
        for _, group in bases.groupby(CELL_COLUMNS, sort=True)
    ]
    rng = np.random.default_rng(int(seed))
    bootstrap = np.empty((int(draws), 2), dtype=float)
    for draw in range(int(draws)):
        sampled = [
            values[rng.integers(0, len(values), len(values))]
            for values in groups
        ]
        bootstrap[draw] = np.concatenate(sampled).mean(axis=0)
    point = bases[["log_loss_gain", "brier_gain"]].mean().to_numpy()
    return {
        name: {
            "mean": float(point[index]),
            "lower_95": float(np.quantile(bootstrap[:, index], 0.025)),
            "upper_95": float(np.quantile(bootstrap[:, index], 0.975)),
        }
        for index, name in enumerate(["log_loss_gain", "brier_gain"])
    }


def _noise_direction(bases: pd.DataFrame) -> dict[str, dict[str, float]]:
    return {
        str(noise): {
            "log_loss_gain": float(group["log_loss_gain"].mean()),
            "brier_gain": float(group["brier_gain"].mean()),
        }
        for noise, group in bases.groupby("noise_mode", sort=True)
    }


def _formal_status(
    *,
    integrity: dict[str, bool],
    variance: pd.DataFrame,
    pooled_variance: dict[str, float],
    gains: dict[str, dict[str, float]],
    noise_direction: dict[str, dict[str, float]],
    gates: dict[str, Any],
) -> tuple[str, dict[str, bool]]:
    direction_consistent = bool(
        all(
            record["log_loss_gain"] > 0.0
            and record["brier_gain"] > 0.0
            for record in noise_direction.values()
        )
    )
    variance_cells = int(
        (
            variance["simultaneous_lower_95"]
            > float(gates["minimum_go_cell_variance_lower"])
        ).sum()
    )
    go_checks = {
        "pooled_brier_gain": bool(
            gains["brier_gain"]["lower_95"]
            > float(gates["minimum_go_brier_gain_lower"])
        ),
        "pooled_log_loss_gain": bool(
            gains["log_loss_gain"]["lower_95"]
            > float(gates["minimum_go_log_loss_gain_lower"])
        ),
        "cell_variance": bool(
            variance_cells >= int(gates["minimum_go_cells"])
        ),
        "noise_direction_consistency": direction_consistent,
    }
    stop_checks = {
        "pooled_variance_absent": bool(
            pooled_variance["upper_95"]
            <= float(gates["maximum_stop_pooled_variance_upper"])
        ),
    }
    checks = {
        **{f"integrity_{key}": value for key, value in integrity.items()},
        **{f"go_{key}": value for key, value in go_checks.items()},
        **{f"stop_{key}": value for key, value in stop_checks.items()},
        "go_variance_cells": variance_cells,
    }
    if not all(integrity.values()):
        return (
            "V8_R2D_GATE0_STOP_INVALID_PROTOCOL",
            checks,
        )
    if all(go_checks.values()):
        return (
            "V8_R2D_GATE0_GO_CONDITIONAL_TARGET_DEMONSTRATED",
            checks,
        )
    if any(stop_checks.values()):
        return (
            "V8_R2D_GATE0_STOP_NO_EXPLOITABLE_CONDITIONAL_TARGET",
            checks,
        )
    return (
        "V8_R2D_GATE0_INCONCLUSIVE_INCREASE_REPLICATES_ONLY",
        checks,
    )


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
    bases_per_cell = int(
        config["smoke_bases_per_cell" if smoke else "bases_per_cell"]
    )
    outcome_replicates = int(
        config[
            "smoke_outcome_replicates"
            if smoke
            else "outcome_replicates"
        ]
    )
    if outcome_replicates % 2:
        raise ValueError("outcome_replicates must be even")
    bootstrap_draws = int(
        config["smoke_bootstrap_draws" if smoke else "bootstrap_draws"]
    )
    source_lock = _source_lock(config)
    definitions = _cell_definitions(config)
    tasks = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(bases_per_cell)
    ]
    streams_per_base = 3 + 2 * outcome_replicates
    root_seed = int(config["smoke_seed" if smoke else "seed"])
    base_streams = np.random.SeedSequence(root_seed).spawn(len(tasks))
    nested_streams = [
        stream.spawn(streams_per_base)
        for stream in base_streams
    ]
    nested_seeds = [
        [
            int(stream.generate_state(1, dtype=np.uint64)[0])
            for stream in base
        ]
        for base in nested_streams
    ]
    seeds = [seed for base in nested_seeds for seed in base]
    payloads = []
    for index, (definition, repetition) in enumerate(tasks):
        base_seeds = nested_seeds[index]
        payloads.append((
            config,
            definition,
            repetition,
            base_seeds[0],
            base_seeds[1],
            base_seeds[2],
            base_seeds[3 : 3 + outcome_replicates],
            base_seeds[
                3 + outcome_replicates : streams_per_base
            ],
        ))
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    rows = pd.DataFrame([
        row for item in nested for row in item["rows"]
    ])
    bases = _base_summary(
        rows,
        outcome_replicates=outcome_replicates,
    )
    summary_streams = np.random.SeedSequence(
        root_seed ^ 0xD20D20D2
    ).spawn(2)
    variance, pooled_variance = _conditional_variance_table(
        bases,
        outcome_replicates=outcome_replicates,
        seed=int(
            summary_streams[0].generate_state(1, dtype=np.uint64)[0]
        ),
        draws=bootstrap_draws,
    )
    gains = _stratified_bootstrap_gains(
        bases,
        seed=int(
            summary_streams[1].generate_state(1, dtype=np.uint64)[0]
        ),
        draws=bootstrap_draws,
    )
    noise_direction = _noise_direction(bases)
    expected_bases = len(definitions) * bases_per_cell
    expected_rows = expected_bases * outcome_replicates
    base_row_count = rows.groupby("base_id").size()
    replicate_count = rows.groupby("base_id")[
        "outcome_replicate"
    ].nunique()
    source_seeds = [
        seed for item in nested for seed in item["source_seeds"]
    ]
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "row_count": bool(len(rows) == expected_rows),
        "base_count": bool(bases["base_id"].nunique() == expected_bases),
        "replicate_completeness": bool(
            (base_row_count == outcome_replicates).all()
            and (replicate_count == outcome_replicates).all()
        ),
        "source_seed_uniqueness": bool(
            len(source_seeds) == len(set(source_seeds))
            and source_seeds == seeds
        ),
        "information_match": bool(
            rows["information_match_relative_error"].max()
            <= float(
                config["gates"][
                    "maximum_information_match_relative_error"
                ]
            )
        ),
        "fixed_latent_world_per_base": bool(
            (
                rows.groupby("base_id")[
                    [
                        "world_seed",
                        "anchor_seed",
                        "geometry_seed",
                        "interaction_sha256",
                    ]
                ].nunique()
                == 1
            ).all().all()
        ),
        "numeric_integrity": bool(
            np.isfinite(
                rows[[
                    "crc",
                    "hc",
                    "cross_low_rank_ratio",
                    "operator_total_information",
                ]].to_numpy(dtype=float)
            ).all()
            and np.isfinite(
                bases[[
                    "candidate_probability",
                    "cell_probability",
                    "log_loss_gain",
                    "brier_gain",
                ]].to_numpy(dtype=float)
            ).all()
        ),
    }
    if smoke:
        status = (
            "V8_R2D_CONDITIONAL_HETEROGENEITY_GATE0_SMOKE_COMPLETE"
            if all(integrity.values())
            else "V8_R2D_GATE0_STOP_INVALID_PROTOCOL"
        )
        gate_checks: dict[str, Any] = {}
    else:
        status, gate_checks = _formal_status(
            integrity=integrity,
            variance=variance,
            pooled_variance=pooled_variance,
            gains=gains,
            noise_direction=noise_direction,
            gates=config["gates"],
        )
    decision = {
        "status": status,
        "mode": args.mode,
        "integrity_checks": integrity,
        "gate_checks": gate_checks,
        "conditional_variance": {
            "pooled": pooled_variance,
            "cells_with_simultaneous_lower_above_go_threshold": int(
                (
                    variance["simultaneous_lower_95"]
                    > float(
                        config["gates"][
                            "minimum_go_cell_variance_lower"
                        ]
                    )
                ).sum()
            ),
        },
        "predictive_gains": gains,
        "noise_direction": noise_direction,
        "rows": int(len(rows)),
        "bases": int(bases["base_id"].nunique()),
        "outcome_replicates_per_base": int(outcome_replicates),
        "source_seed_count": int(len(source_seeds)),
        "unique_source_seed_count": int(len(set(source_seeds))),
        "source_lock": source_lock,
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows.to_csv(args.output_dir / "outcome_rows.csv", index=False)
    bases.to_csv(args.output_dir / "base_predictions.csv", index=False)
    variance.to_csv(
        args.output_dir / "conditional_variance_by_cell.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "streams_per_base": int(streams_per_base),
        "source_seed_count": int(len(source_seeds)),
        "unique_source_seed_count": int(len(set(source_seeds))),
        "all_source_streams_unique": bool(
            len(source_seeds) == len(set(source_seeds))
        ),
        "hierarchical_base_streams": True,
        "replicate_32_to_64_preserves_base_and_first_32_streams": True,
        "latent_world_streams": [
            "world_seed",
            "anchor_seed",
            "geometry_seed",
        ],
        "fresh_streams_per_outcome": [
            "outcome_seed",
            "diagnostic_seed",
        ],
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2D Conditional-Heterogeneity Gate-0\n\n"
        f"Decision: `{status}`\n\n"
        "Each base holds latent Q and geometry fixed while independently "
        "resampling opportunity counts, panel shocks, technical noise, and "
        "the registered detector. This resource gate does not fit R2D.\n",
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
        "rows": int(len(rows)),
        "bases": int(bases["base_id"].nunique()),
        "integrity_checks": integrity,
        "conditional_variance": pooled_variance,
        "predictive_gains": gains,
        "noise_direction": noise_direction,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
