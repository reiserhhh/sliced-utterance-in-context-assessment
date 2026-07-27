#!/usr/bin/env python3
"""Run the fresh H4D-R2C permutation-orbit mechanism frontier."""
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

from scripts.analyze_suica_v8_geometry_information_operator_v37h4d_r2b import (  # noqa: E402
    _binary_log_loss,
    build_feature_frame,
    cluster_bootstrap_mean,
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
from suica_core.v8_geometry_information_operator import (  # noqa: E402
    apply_interaction,
    geometry_information_coordinates,
    match_residual_information,
)
from suica_core.v8_minority_information_frontier import (  # noqa: E402
    plant_minority_interaction,
)
from suica_core.v8_permutation_orbit_frontier import (  # noqa: E402
    author_contribution_spectrum,
    build_controlled_halo_interaction,
    frozen_logistic_probability,
    orbit_rejection_probability,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    additive_residual,
    wild_residual_diagnostics,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_permutation_orbit_frontier_v37h4d_r2c.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_permutation_orbit_frontier"
    / "v37h4d_r2c_discovery"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(config: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for relative, expected in config["frozen_source_sha256"].items():
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


def _geometry_plan(
    config: dict[str, Any],
    *,
    active_test_authors: int,
) -> list[dict[str, Any]]:
    """Return the nine frozen core/halo cells for one paired base."""
    plan = [{
        "halo_lambda": 0.0,
        "halo_author_support": int(active_test_authors),
        "support_label": "core_only",
    }]
    for halo_lambda in map(float, config["halo_lambda_grid"]):
        if halo_lambda == 0.0:
            continue
        for support in map(
            int,
            config["nonzero_halo_author_support"],
        ):
            if support < int(active_test_authors):
                continue
            plan.append({
                "halo_lambda": halo_lambda,
                "halo_author_support": support,
                "support_label": (
                    "bounded_8" if support == 8 else "all_test"
                ),
            })
    return plan


def _panel_residuals(
    world: dict[str, Any],
    *,
    primary_opportunities: int,
    test_authors: np.ndarray,
    panels: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    counts = world["counts_by_k"][int(primary_opportunities)]
    means = world["means_by_k"][int(primary_opportunities)]
    left, left_mask = additive_residual(
        means[panels[0]],
        counts[panels[0]],
        test_authors,
    )
    right, right_mask = additive_residual(
        means[panels[1]],
        counts[panels[1]],
        test_authors,
    )
    return left, right, left_mask, right_mask


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
    orbit_seed: int,
    outcome_seed: int,
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
    interaction, support_audit = build_controlled_halo_interaction(
        anchor_interaction,
        spec=spec,
        test_authors=test,
        active_test_authors=active,
        active_conditions=conditions,
        halo_lambda=float(geometry["halo_lambda"]),
        halo_author_support=int(geometry["halo_author_support"]),
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
    mechanism = _panel_residuals(
        world,
        primary_opportunities=int(config["primary_opportunities"]),
        test_authors=test,
        panels=(0, 1),
    )
    outcome = _panel_residuals(
        world,
        primary_opportunities=int(config["primary_opportunities"]),
        test_authors=test,
        panels=(2, 3),
    )
    mechanism_spectrum = author_contribution_spectrum(*mechanism)
    outcome_spectrum = author_contribution_spectrum(*outcome)
    orbit = orbit_rejection_probability(
        *mechanism,
        seed=orbit_seed,
        orbit_draws=int(config["_active_orbit_draws"]),
        detector_permutations=int(
            config["_active_outcome_permutations"]
        ),
        resamples=int(config["_active_orbit_resamples"]),
        alpha=float(config["holm_alpha"]),
        rank=3,
    )
    diagnostics = wild_residual_diagnostics(
        *outcome,
        rank=3,
        seed=outcome_seed,
        permutations=int(config["_active_outcome_permutations"]),
        alpha=float(config["holm_alpha"]),
    )
    alpha = float(config["holm_alpha"])
    return {
        "base_id": base_id,
        "repetition": int(repetition),
        "noise_mode": str(definition["noise_mode"]),
        "active_test_authors": int(
            definition["active_test_authors"]
        ),
        "halo_lambda": float(geometry["halo_lambda"]),
        "halo_author_support": int(geometry["halo_author_support"]),
        "support_label": str(geometry["support_label"]),
        "world_seed": int(world_seed),
        "anchor_seed": int(anchor_seed),
        "geometry_seed": int(geometry_seed),
        "orbit_seed": int(orbit_seed),
        "outcome_seed": int(outcome_seed),
        **match,
        **coordinates,
        **support_audit,
        **{
            f"mechanism_{key}": value
            for key, value in mechanism_spectrum.items()
        },
        **{
            f"outcome_{key}": value
            for key, value in outcome_spectrum.items()
        },
        **orbit,
        **diagnostics,
        "crc_detected": bool(diagnostics["crc_p_holm"] < alpha),
        "hc_detected": bool(diagnostics["hc_p_holm"] < alpha),
        "crc_or_hc_detected": bool(
            diagnostics["crc_p_holm"] < alpha
            or diagnostics["hc_p_holm"] < alpha
        ),
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
        orbit_seed,
        outcome_seed,
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
    plan = _geometry_plan(
        config,
        active_test_authors=int(
            definition["active_test_authors"]
        ),
    )
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
            orbit_seed=orbit_seed,
            outcome_seed=outcome_seed,
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
            orbit_seed,
            outcome_seed,
            *geometry_seeds,
        ],
    }


def _paired_gap(
    cells: pd.DataFrame,
    *,
    seed: int,
    draws: int,
) -> pd.DataFrame:
    records = []
    streams = np.random.SeedSequence(int(seed)).spawn(2)
    for index, noise in enumerate(sorted(cells["noise_mode"].unique())):
        selected = cells[
            (cells["noise_mode"] == noise)
            & (cells["active_test_authors"] == 4)
            & (
                (
                    (cells["halo_lambda"] == 0.0)
                    & (cells["support_label"] == "core_only")
                )
                | (
                    np.isclose(cells["halo_lambda"], 0.03)
                    & (cells["support_label"] == "all_test")
                )
            )
        ]
        pivot = selected.pivot(
            index="base_id",
            columns=["halo_lambda", "support_label"],
            values="crc_or_hc_detected",
        )
        difference = (
            pivot[(0.03, "all_test")].to_numpy(dtype=float)
            - pivot[(0.0, "core_only")].to_numpy(dtype=float)
        )
        rng = np.random.default_rng(streams[index])
        bootstrap = np.empty(int(draws))
        for draw in range(int(draws)):
            sample = rng.integers(0, len(difference), len(difference))
            bootstrap[draw] = float(difference[sample].mean())
        records.append({
            "noise_mode": noise,
            "pairs": int(len(difference)),
            "lambda03_minus_zero_power_gap": float(difference.mean()),
            "lower_95": float(np.quantile(bootstrap, 0.025)),
            "upper_95": float(np.quantile(bootstrap, 0.975)),
        })
    return pd.DataFrame(records)


def _cell_calibration(
    cells: pd.DataFrame,
    *,
    seed: int,
    draws: int,
) -> pd.DataFrame:
    keys = [
        "noise_mode",
        "active_test_authors",
        "halo_lambda",
        "halo_author_support",
        "support_label",
    ]
    grouped = list(cells.groupby(keys, sort=True))
    streams = np.random.SeedSequence(int(seed)).spawn(len(grouped))
    records = []
    for stream, (key, group) in zip(streams, grouped, strict=True):
        outcome = group["crc_or_hc_detected"].to_numpy(dtype=float)
        prediction = group[
            "orbit_rejection_probability"
        ].to_numpy(dtype=float)
        difference = outcome - prediction
        rng = np.random.default_rng(stream)
        bootstrap = np.empty(int(draws))
        for draw in range(int(draws)):
            sample = rng.integers(0, len(difference), len(difference))
            bootstrap[draw] = abs(float(difference[sample].mean()))
        records.append({
            **dict(zip(keys, key, strict=True)),
            "trials": int(len(group)),
            "observed_power": float(outcome.mean()),
            "mean_orbit_probability": float(prediction.mean()),
            "absolute_calibration_error": abs(float(difference.mean())),
            "calibration_error_upper_95": float(
                np.quantile(bootstrap, 0.975)
            ),
        })
    return pd.DataFrame(records)


def _spectrum_retest(
    cells: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    """Report total and registered-cell-centered panel correlations."""
    keys = [
        "noise_mode",
        "active_test_authors",
        "halo_lambda",
        "halo_author_support",
        "support_label",
    ]
    result: dict[str, dict[str, float]] = {
        "overall": {},
        "within_cell": {},
    }
    for name in ["n1", "n2", "n_inf"]:
        left = cells[f"mechanism_{name}"].to_numpy(dtype=float)
        right = cells[f"outcome_{name}"].to_numpy(dtype=float)
        result["overall"][name] = float(
            np.corrcoef(left, right)[0, 1]
        )
        mechanism_centered = (
            cells[f"mechanism_{name}"]
            - cells.groupby(keys)[f"mechanism_{name}"].transform("mean")
        ).to_numpy(dtype=float)
        outcome_centered = (
            cells[f"outcome_{name}"]
            - cells.groupby(keys)[f"outcome_{name}"].transform("mean")
        ).to_numpy(dtype=float)
        result["within_cell"][name] = float(
            np.corrcoef(mechanism_centered, outcome_centered)[0, 1]
        )
    return result


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
    config["_active_outcome_permutations"] = int(
        config[
            "smoke_outcome_permutations"
            if smoke
            else "outcome_permutations"
        ]
    )
    config["_active_orbit_draws"] = int(
        config["smoke_orbit_draws" if smoke else "orbit_draws"]
    )
    config["_active_orbit_resamples"] = int(
        config[
            "smoke_orbit_resamples" if smoke else "orbit_resamples"
        ]
    )
    repetitions = int(
        config["smoke_repetitions" if smoke else "discovery_repetitions"]
    )
    bootstrap_draws = int(
        config["smoke_bootstrap_draws" if smoke else "bootstrap_draws"]
    )
    source_lock = _source_lock(config)
    definitions = [
        {
            "noise_mode": str(noise),
            "active_test_authors": int(m),
        }
        for noise in config["noise_modes"]
        for m in config["active_test_author_grid"]
    ]
    tasks = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(repetitions)
    ]
    geometry_count = len(
        _geometry_plan(
            config,
            active_test_authors=max(
                map(int, config["active_test_author_grid"])
            ),
        )
    )
    streams_per_base = 4 + geometry_count
    root_seed = int(config["smoke_seed"] if smoke else config["seed"])
    streams = np.random.SeedSequence(root_seed).spawn(
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
            seeds[start + 3],
            seeds[start + 4 : start + streams_per_base],
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

    artifact_path = ROOT / str(config["frozen_operator_path"])
    artifact = _read(artifact_path)
    feature_frame = build_feature_frame(cells)
    feature_columns = list(map(str, artifact["feature_columns"]))
    cells["frozen_r2b_probability"] = frozen_logistic_probability(
        feature_frame[feature_columns].to_numpy(dtype=float),
        artifact,
    )
    response = cells["crc_or_hc_detected"].to_numpy(dtype=float)
    frozen_loss = _binary_log_loss(
        response,
        cells["frozen_r2b_probability"].to_numpy(dtype=float),
    )
    orbit_loss = _binary_log_loss(
        response,
        cells["orbit_rejection_probability"].to_numpy(dtype=float),
    )
    frozen_brier = (
        response - cells["frozen_r2b_probability"].to_numpy(dtype=float)
    ) ** 2
    orbit_brier = (
        response - cells["orbit_rejection_probability"].to_numpy(dtype=float)
    ) ** 2
    cells["orbit_log_loss_improvement"] = frozen_loss - orbit_loss
    cells["orbit_brier_improvement"] = frozen_brier - orbit_brier

    summary_seed = np.random.SeedSequence(root_seed ^ 0xA5A5A5A5)
    gain_stream, brier_stream, gap_stream, cell_stream = (
        summary_seed.spawn(4)
    )
    log_loss_gain = cluster_bootstrap_mean(
        cells["orbit_log_loss_improvement"],
        cells["base_id"],
        seed=int(gain_stream.generate_state(1, dtype=np.uint64)[0]),
        draws=bootstrap_draws,
    )
    brier_gain = cluster_bootstrap_mean(
        cells["orbit_brier_improvement"],
        cells["base_id"],
        seed=int(brier_stream.generate_state(1, dtype=np.uint64)[0]),
        draws=bootstrap_draws,
    )
    gap = _paired_gap(
        cells,
        seed=int(gap_stream.generate_state(1, dtype=np.uint64)[0]),
        draws=bootstrap_draws,
    )
    calibration = _cell_calibration(
        cells,
        seed=int(cell_stream.generate_state(1, dtype=np.uint64)[0]),
        draws=bootstrap_draws,
    )
    spectrum = _spectrum_retest(cells)
    base_counts = cells.groupby("base_id").size()
    gates = config["gates"]
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "row_count": bool(len(cells) == len(tasks) * geometry_count),
        "base_pairing": bool((base_counts == geometry_count).all()),
        "seed_stream_uniqueness": bool(len(seeds) == len(set(seeds))),
        "information_match": bool(
            cells["information_match_relative_error"].max()
            <= float(
                gates["maximum_information_match_relative_error"]
            )
        ),
        "numeric_integrity": bool(
            np.isfinite(
                cells[[
                    "orbit_rejection_probability",
                    "frozen_r2b_probability",
                    "mechanism_n1",
                    "mechanism_n2",
                    "mechanism_n_inf",
                    "outcome_n1",
                    "outcome_n2",
                    "outcome_n_inf",
                    "crc",
                    "hc",
                ]].to_numpy(dtype=float)
            ).all()
        ),
        "orbit_probability_bounds": bool(
            cells["orbit_rejection_probability"].between(0.0, 1.0).all()
        ),
    }
    frontier_reproduced = bool(
        len(gap) == 2
        and gap["lower_95"].min()
        > float(gates["minimum_m4_lambda03_power_gap_lower"])
    )
    gain_pass = bool(
        log_loss_gain["lower_95"]
        > float(gates["minimum_log_loss_improvement_lower"])
        and brier_gain["lower_95"]
        > float(gates["minimum_brier_improvement_lower"])
    )
    calibration_pass = bool(
        calibration["absolute_calibration_error"].max()
        <= float(gates["maximum_cell_calibration_point"])
        and calibration["calibration_error_upper_95"].max()
        <= float(gates["maximum_cell_calibration_upper"])
    )
    lambda03 = calibration[
        (calibration["active_test_authors"] == 4)
        & np.isclose(calibration["halo_lambda"], 0.03)
        & (calibration["support_label"] == "all_test")
    ]
    lambda03_calibration = bool(
        len(lambda03) == 2
        and lambda03["absolute_calibration_error"].max()
        <= float(gates["maximum_m4_lambda03_calibration"])
    )
    spectrum_pass = bool(
        min(spectrum["within_cell"].values())
        >= float(gates["minimum_spectrum_retest_correlation"])
    )

    if not all(integrity.values()) or not frontier_reproduced:
        status = (
            "V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_"
            "STOP_INVALID_FRONTIER"
        )
    elif not gain_pass:
        status = (
            "V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_"
            "REFUTED_PERMUTATION_ORBIT_EXPLANATION"
        )
    elif calibration_pass and lambda03_calibration and spectrum_pass:
        status = (
            "V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_"
            "PASS_RESOLUTION_INDEXED_ORBIT"
        )
    elif calibration_pass and lambda03_calibration:
        status = (
            "V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_"
            "PARTIAL_ORBIT_CALIBRATED_SPECTRUM_UNSTABLE"
        )
    else:
        status = (
            "V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_"
            "PARTIAL_ORBIT_ORDER_ONLY"
        )
    decision = {
        "status": status,
        "mode": args.mode,
        "integrity_checks": integrity,
        "frontier_reproduced": frontier_reproduced,
        "gain_pass": gain_pass,
        "calibration_pass": calibration_pass,
        "lambda03_calibration_pass": lambda03_calibration,
        "spectrum_retest_pass": spectrum_pass,
        "log_loss_improvement": log_loss_gain,
        "brier_improvement": brier_gain,
        "spectrum_retest_correlations": spectrum,
        "maximum_cell_calibration_error": float(
            calibration["absolute_calibration_error"].max()
        ),
        "maximum_cell_calibration_upper_95": float(
            calibration["calibration_error_upper_95"].max()
        ),
        "rows": int(len(cells)),
        "bases": int(cells["base_id"].nunique()),
        "source_lock": source_lock,
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "orbit_rows.csv", index=False)
    gap.to_csv(args.output_dir / "halo_power_gap.csv", index=False)
    calibration.to_csv(
        args.output_dir / "cell_calibration.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "source_seed_count": int(len(seeds)),
        "unique_source_seed_count": int(len(set(seeds))),
        "paired_within_base": [
            "world_seed",
            "anchor_seed",
            "orbit_seed",
            "outcome_seed",
        ],
        "geometry_seed_is_independent_per_geometry": True,
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2C Permutation-Orbit Frontier\n\n"
        f"Decision: `{status}`\n\n"
        "Panels 0/1 estimate the finite randomization orbit. Panels 2/3 "
        "supply the independent frozen-detector outcome.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[artifact_path],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_reference_measure_frontier.py",
            ROOT / "suica_core/v8_minority_information_frontier.py",
            ROOT / "suica_core/v8_geometry_information_operator.py",
            ROOT / "suica_core/v8_permutation_orbit_frontier.py",
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
        "integrity_checks": integrity,
        "frontier_reproduced": frontier_reproduced,
        "log_loss_improvement": log_loss_gain,
        "brier_improvement": brier_gain,
        "spectrum_retest_correlations": spectrum,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
