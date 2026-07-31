#!/usr/bin/env python3
"""Run the V3.7H.4 misspecification and transport discovery battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta, t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_misspecification_transport import (  # noqa: E402
    MisspecificationSpec,
    cell_means,
    crc_permutation_p,
    crossfit_additive_prediction,
    crossfit_residual,
    crossfit_structured_prediction,
    gain_signflip_p,
    holm_adjust,
    low_rank_permutation_p,
    main_component_recovery,
    operation_gap,
    select_structured_rank,
    simulate_misspecification_world,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_misspecification_transport_v37h4.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_misspecification_transport"
    / "v37h4_discovery"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            allow_nan=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _spec(config: dict[str, Any]) -> MisspecificationSpec:
    values = config["spec"]
    return MisspecificationSpec(
        societies=int(values["societies"]),
        groups_per_society=int(values["groups_per_society"]),
        authors_per_group=int(values["authors_per_group"]),
        conditions=int(values["conditions"]),
        train_conditions=int(values["train_conditions"]),
        calibration_conditions=int(values["calibration_conditions"]),
        test_conditions=int(values["test_conditions"]),
        panels=int(values["panels"]),
        opportunities=int(values["opportunities"]),
        technical_streams=int(values["technical_streams"]),
        dimensions=int(values["dimensions"]),
        latent_dimensions=int(values["latent_dimensions"]),
        latent_subgroups=int(values["latent_subgroups"]),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )


def _cells(config: dict[str, Any]) -> list[tuple[str, float, str]]:
    cells: list[tuple[str, float, str]] = []
    for noise_mode in config["noise_modes"]:
        cells.append(("additive", 0.0, str(noise_mode)))
        for world in config["worlds"]:
            if world == "additive":
                continue
            for share in config["effect_shares"]:
                cells.append((
                    str(world),
                    float(share),
                    str(noise_mode),
                ))
    return cells


def _evaluate_cell(
    *,
    repetition: int,
    world_name: str,
    effect_share: float,
    noise_mode: str,
    world_seed: int,
    diagnostic_seed: int,
    config: dict[str, Any],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    spec = _spec(config)
    world = simulate_misspecification_world(
        seed=world_seed,
        world=world_name,
        effect_share=effect_share,
        noise_mode=noise_mode,
        spec=spec,
        main_effect_amplitude=float(config["main_effect_amplitude"]),
        opportunity_amplitude=float(config["opportunity_amplitude"]),
        technical_amplitude=float(config["technical_amplitude"]),
        nonlinear_saturation=float(config["nonlinear_saturation"]),
        nonergodic_author_correlation=float(
            config["nonergodic_author_correlation"]
        ),
        nonergodic_stable_fraction=float(
            config["nonergodic_stable_fraction"]
        ),
        nonergodic_regime_persistence=float(
            config["nonergodic_regime_persistence"]
        ),
    )
    train, calibration, test = spec.condition_split
    fit = np.concatenate([train, calibration])
    labels = np.asarray(world["registered_group_labels"])
    maximum_k = max(map(int, config["recovery_k"]))
    cells = cell_means(
        world["observations"],
        opportunities=maximum_k,
    )
    selected_rank, rank_losses = select_structured_rank(
        cells[0],
        cells[1],
        registered_group_labels=labels,
        train_conditions=train,
        calibration_conditions=calibration,
        rank_candidates=tuple(map(int, config["rank_candidates"])),
    )

    additive_prediction = crossfit_additive_prediction(
        cells[2],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    structured_prediction = crossfit_structured_prediction(
        cells[2],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
        rank=selected_rank,
    )
    heldout = cells[3][:, test]
    additive_error = np.mean(
        (heldout - additive_prediction) ** 2,
        axis=(1, 2),
    )
    structured_error = np.mean(
        (heldout - structured_prediction) ** 2,
        axis=(1, 2),
    )
    gain_by_author = additive_error - structured_error
    outcome_variance = max(
        float(np.mean((heldout - heldout.mean()) ** 2)),
        1e-12,
    )
    t_gen = float(gain_by_author.mean() / outcome_variance)

    oracle = np.asarray(world["oracle_panel_truth"])[3][:, test]
    oracle_mse = float(np.mean((heldout - oracle) ** 2))
    additive_mse = float(additive_error.mean())
    structured_mse = float(structured_error.mean())
    gap_closure = float(
        (additive_mse - structured_mse)
        / max(additive_mse - oracle_mse, 1e-12)
    )

    residual_3 = crossfit_residual(
        cells[0],
        cells[2],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    residual_4 = crossfit_residual(
        cells[1],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    diagnostic_streams = np.random.SeedSequence(
        int(diagnostic_seed)
    ).spawn(3)
    crc, crc_p = crc_permutation_p(
        residual_3,
        residual_4,
        labels,
        seed=_uint64(diagnostic_streams[0]),
        permutations=int(config["_active_permutations"]),
    )
    low_rank, low_rank_p = low_rank_permutation_p(
        0.5 * (residual_3 + residual_4),
        rank=selected_rank,
        seed=_uint64(diagnostic_streams[1]),
        permutations=int(config["_active_permutations"]),
    )
    mean_gain, gain_p = gain_signflip_p(
        gain_by_author,
        seed=_uint64(diagnostic_streams[2]),
        permutations=int(config["_active_permutations"]),
    )
    adjusted = holm_adjust({
        "crc": crc_p,
        "low_rank": low_rank_p,
        "gain": gain_p,
    })
    inadequate = bool(
        min(adjusted.values()) < float(config["holm_alpha"])
    )
    classification = (
        "MODEL_INADEQUATE_CAUSE_UNIDENTIFIED"
        if inadequate
        else "ADEQUATE"
    )

    recovery_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    residual_energy: dict[int, float] = {}
    for opportunities in map(int, config["recovery_k"]):
        for row in main_component_recovery(
            world["observations"],
            world["main_components"],
            opportunities=opportunities,
        ):
            recovery_rows.append({
                "repetition": int(repetition),
                "world": world_name,
                "effect_share": float(effect_share),
                "noise_mode": noise_mode,
                "opportunities": opportunities,
                **row,
            })
        prefix = cell_means(
            world["observations"],
            opportunities=opportunities,
        )
        left = crossfit_residual(
            prefix[0],
            prefix[2],
            registered_group_labels=labels,
            fit_conditions=fit,
            eval_conditions=test,
        )
        right = crossfit_residual(
            prefix[1],
            prefix[3],
            registered_group_labels=labels,
            fit_conditions=fit,
            eval_conditions=test,
        )
        energy = float(np.mean(left * right))
        residual_energy[opportunities] = energy
        residual_rows.append({
            "repetition": int(repetition),
            "world": world_name,
            "effect_share": float(effect_share),
            "noise_mode": noise_mode,
            "opportunities": opportunities,
            "cross_panel_residual_energy": energy,
        })

    rank_rows = [{
        "repetition": int(repetition),
        "world": world_name,
        "effect_share": float(effect_share),
        "noise_mode": noise_mode,
        "rank": int(rank),
        "calibration_mse": float(loss),
        "selected": bool(int(rank) == selected_rank),
    } for rank, loss in rank_losses.items()]
    k_low = min(residual_energy)
    k_high = max(residual_energy)
    k_ratio = float(
        residual_energy[k_high]
        / max(residual_energy[k_low], 1e-12)
    )
    cell_row = {
        "repetition": int(repetition),
        "world": world_name,
        "effect_share": float(effect_share),
        "noise_mode": noise_mode,
        "world_seed": int(world_seed),
        "diagnostic_seed": int(diagnostic_seed),
        "selected_rank": int(selected_rank),
        "crc": float(crc),
        "crc_p": float(crc_p),
        "crc_p_holm": float(adjusted["crc"]),
        "low_rank_ratio": float(low_rank),
        "low_rank_p": float(low_rank_p),
        "low_rank_p_holm": float(adjusted["low_rank"]),
        "mean_author_mse_gain": float(mean_gain),
        "gain_p": float(gain_p),
        "gain_p_holm": float(adjusted["gain"]),
        "t_gen": t_gen,
        "additive_mse": additive_mse,
        "structured_mse": structured_mse,
        "oracle_mse": oracle_mse,
        "gap_closure": gap_closure,
        "model_inadequate": inadequate,
        "classification": classification,
        "specific_causal_attribution": False,
        "operation_gap": float(operation_gap(
            world["observations"],
            opportunities=maximum_k,
        )),
        "k_high_to_low_residual_ratio": k_ratio,
        "alias_identity_error": float(
            world["alias_identity_error"]
        ),
        "achieved_effect_energy": float(
            world["achieved_interaction_energy"]
        ),
        "effect_scale": float(world["effect_scale"]),
    }
    return cell_row, recovery_rows, residual_rows, rank_rows


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> dict[str, Any]:
    config, repetition, spawn_key = payload
    cells = _cells(config)
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    streams = root.spawn(2 * len(cells))
    seeds = [_uint64(stream) for stream in streams]
    cell_rows: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    rank_rows: list[dict[str, Any]] = []
    for index, (world, share, noise_mode) in enumerate(cells):
        cell, recovery, residual, ranks = _evaluate_cell(
            repetition=repetition,
            world_name=world,
            effect_share=share,
            noise_mode=noise_mode,
            world_seed=seeds[2 * index],
            diagnostic_seed=seeds[2 * index + 1],
            config=config,
        )
        cell_rows.append(cell)
        recovery_rows.extend(recovery)
        residual_rows.extend(residual)
        rank_rows.extend(ranks)
    return {
        "cells": cell_rows,
        "recovery": recovery_rows,
        "residual": residual_rows,
        "ranks": rank_rows,
        "seeds": seeds,
    }


def _clopper_pearson(
    successes: int,
    trials: int,
    *,
    confidence: float,
) -> tuple[float, float]:
    alpha = 1.0 - float(confidence)
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(
            alpha,
            successes,
            trials - successes + 1,
        ))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(
            1.0 - alpha,
            successes + 1,
            trials - successes,
        ))
    )
    return lower, upper


def _mean_interval(
    values: pd.Series,
    *,
    confidence: float,
    family_cells: int = 1,
) -> tuple[float, float, float]:
    data = values.dropna().to_numpy(dtype=float)
    mean = float(data.mean())
    if len(data) < 2:
        return mean, float("nan"), float("nan")
    alpha = (1.0 - float(confidence)) / max(int(family_cells), 1)
    critical = float(t.ppf(1.0 - alpha / 2.0, len(data) - 1))
    radius = critical * float(data.std(ddof=1) / np.sqrt(len(data)))
    return mean, mean - radius, mean + radius


def _summaries(
    cells: pd.DataFrame,
    recovery: pd.DataFrame,
    residual: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    cell_rows = []
    keys = ["world", "effect_share", "noise_mode"]
    for key, group in cells.groupby(keys, sort=True, observed=True):
        world, share, noise_mode = key
        detected = int(group["model_inadequate"].sum())
        lower, upper = _clopper_pearson(
            detected,
            len(group),
            confidence=0.95,
        )
        closure_mean, closure_lower, closure_upper = _mean_interval(
            group["gap_closure"],
            confidence=0.95,
            family_cells=4,
        )
        crc_mean, crc_lower, crc_upper = _mean_interval(
            group["crc"],
            confidence=0.90,
        )
        gain_mean, gain_lower, gain_upper = _mean_interval(
            group["t_gen"],
            confidence=0.90,
        )
        cell_rows.append({
            "world": str(world),
            "effect_share": float(share),
            "noise_mode": str(noise_mode),
            "trials": int(len(group)),
            "model_inadequate_count": detected,
            "model_inadequate_rate": float(detected / len(group)),
            "detection_cp_lower_95": lower,
            "detection_cp_upper_95": upper,
            "mean_crc": crc_mean,
            "crc_ci_lower_90": crc_lower,
            "crc_ci_upper_90": crc_upper,
            "mean_t_gen": gain_mean,
            "t_gen_ci_lower_90": gain_lower,
            "t_gen_ci_upper_90": gain_upper,
            "mean_gap_closure": closure_mean,
            "gap_closure_simultaneous_lower_95": closure_lower,
            "gap_closure_simultaneous_upper_95": closure_upper,
            "mean_k_high_to_low_residual_ratio": float(
                group["k_high_to_low_residual_ratio"].mean()
            ),
            "maximum_operation_gap": float(
                group["operation_gap"].max()
            ),
            "maximum_alias_identity_error": float(
                group["alias_identity_error"].max()
            ),
            "specific_causal_attribution_rate": float(
                group["specific_causal_attribution"].mean()
            ),
        })
    cell_summary = pd.DataFrame(cell_rows)

    recovery_rows = []
    recovery_keys = [
        "world",
        "effect_share",
        "noise_mode",
        "opportunities",
        "component",
    ]
    for key, group in recovery.groupby(
        recovery_keys,
        sort=True,
        observed=True,
    ):
        mean_r2, lower_r2, upper_r2 = _mean_interval(
            group["recovery_r2"],
            confidence=0.95,
            family_cells=8,
        )
        mean_split, lower_split, upper_split = _mean_interval(
            group["split_panel_correlation"],
            confidence=0.95,
            family_cells=8,
        )
        recovery_rows.append({
            **dict(zip(recovery_keys, key, strict=True)),
            "trials": int(len(group)),
            "mean_recovery_r2": mean_r2,
            "recovery_simultaneous_lower_95": lower_r2,
            "recovery_simultaneous_upper_95": upper_r2,
            "mean_split_panel_correlation": mean_split,
            "split_simultaneous_lower_95": lower_split,
            "split_simultaneous_upper_95": upper_split,
        })
    recovery_summary = pd.DataFrame(recovery_rows)
    residual_summary = (
        residual.groupby(
            [
                "world",
                "effect_share",
                "noise_mode",
                "opportunities",
            ],
            sort=True,
            observed=True,
        )["cross_panel_residual_energy"]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
    )

    gates = config["gates"]
    w0_cells = cell_summary[cell_summary["world"] == "additive"]
    w0_recovery = recovery_summary[
        (recovery_summary["world"] == "additive")
        & (recovery_summary["opportunities"] == 4)
    ]
    strong = cell_summary[
        cell_summary["world"].isin(["nonlinear", "latent_hierarchy"])
        & np.isclose(cell_summary["effect_share"], 0.20)
    ]
    nonergodic = cell_summary[
        cell_summary["world"] == "nonergodic"
    ]
    specific_count = int(cells["specific_causal_attribution"].sum())
    _, specific_upper = _clopper_pearson(
        specific_count,
        len(cells),
        confidence=0.95,
    )
    checks = {
        "numeric_integrity": bool(
            np.isfinite(cells[[
                "crc",
                "low_rank_ratio",
                "t_gen",
                "additive_mse",
                "structured_mse",
                "oracle_mse",
                "gap_closure",
                "operation_gap",
            ]].to_numpy(dtype=float)).all()
        ),
        "w0_recovery": bool(
            len(w0_recovery)
            and w0_recovery[
                "recovery_simultaneous_lower_95"
            ].min() >= float(gates["minimum_w0_recovery_lower"])
        ),
        "w0_split_stability": bool(
            len(w0_recovery)
            and w0_recovery[
                "split_simultaneous_lower_95"
            ].min() >= float(gates["minimum_w0_split_lower"])
        ),
        "w0_false_refusal": bool(
            len(w0_cells)
            and w0_cells["detection_cp_upper_95"].max()
            < float(gates["maximum_w0_false_refusal_upper"])
        ),
        "w0_crc_calibration": bool(
            len(w0_cells)
            and w0_cells["crc_ci_lower_90"].min()
            >= -float(gates["maximum_w0_crc_abs_ci"])
            and w0_cells["crc_ci_upper_90"].max()
            <= float(gates["maximum_w0_crc_abs_ci"])
        ),
        "w0_gain_calibration": bool(
            len(w0_cells)
            and w0_cells["t_gen_ci_lower_90"].min()
            >= -float(gates["maximum_w0_gain_abs_ci"])
            and w0_cells["t_gen_ci_upper_90"].max()
            <= float(gates["maximum_w0_gain_abs_ci"])
        ),
        "operation_commutation": bool(
            cells["operation_gap"].max()
            <= float(gates["maximum_operation_gap"])
        ),
        "strong_detection": bool(
            len(strong)
            and strong["detection_cp_lower_95"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "strong_gap_closure": bool(
            len(strong)
            and strong[
                "gap_closure_simultaneous_lower_95"
            ].min()
            > float(gates["minimum_strong_gap_closure_lower"])
        ),
        "strong_crc": bool(
            len(strong)
            and strong["mean_crc"].min()
            > float(gates["minimum_strong_crc_mean"])
        ),
        "nonergodic_refusal": bool(
            len(nonergodic)
            and nonergodic["detection_cp_lower_95"].min()
            > float(gates["minimum_nonergodic_refusal_lower"])
        ),
        "nonergodic_persistence": bool(
            len(nonergodic)
            and nonergodic[
                "mean_k_high_to_low_residual_ratio"
            ].min()
            >= float(gates["minimum_nonergodic_k8_k2_ratio"])
        ),
        "cause_alias_refusal": bool(
            cells["alias_identity_error"].max()
            <= float(gates["maximum_alias_identity_error"])
            and specific_upper
            < float(gates["maximum_specific_cause_upper"])
        ),
    }
    evidence = {
        "checks": checks,
        "extrema": {
            "minimum_w0_recovery_lower": float(
                w0_recovery[
                    "recovery_simultaneous_lower_95"
                ].min()
            ),
            "minimum_w0_split_lower": float(
                w0_recovery[
                    "split_simultaneous_lower_95"
                ].min()
            ),
            "maximum_w0_false_refusal_upper": float(
                w0_cells["detection_cp_upper_95"].max()
            ),
            "minimum_strong_detection_lower": float(
                strong["detection_cp_lower_95"].min()
            ),
            "minimum_strong_gap_closure_lower": float(
                strong[
                    "gap_closure_simultaneous_lower_95"
                ].min()
            ),
            "minimum_strong_crc_mean": float(
                strong["mean_crc"].min()
            ),
            "minimum_nonergodic_refusal_lower": float(
                nonergodic["detection_cp_lower_95"].min()
            ),
            "minimum_nonergodic_k_ratio": float(
                nonergodic[
                    "mean_k_high_to_low_residual_ratio"
                ].min()
            ),
            "maximum_operation_gap": float(
                cells["operation_gap"].max()
            ),
            "maximum_alias_identity_error": float(
                cells["alias_identity_error"].max()
            ),
            "specific_cause_upper_95": float(specific_upper),
        },
    }
    return cell_summary, recovery_summary, residual_summary, evidence


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.4 Misspecification and Transport

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Extrema

```json
{json.dumps(decision["extrema"], indent=2)}
```

## Boundary

This is a synthetic misspecification discovery. A stable residual can refuse
the registered additive coordinate system, but it cannot identify a
personality construct or distinguish a persistent opportunity process from an
observationally equivalent author response.
"""


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
    if args.mode == "smoke":
        config["_active_seed"] = int(config["smoke_seed"])
        config["_active_repetitions"] = int(
            config["smoke_repetitions"]
        )
        config["_active_permutations"] = int(
            config["smoke_permutations"]
        )
    else:
        config["_active_seed"] = int(config["seed"])
        config["_active_repetitions"] = int(
            config["discovery_repetitions"]
        )
        config["_active_permutations"] = int(config["permutations"])

    root = np.random.SeedSequence(int(config["_active_seed"]))
    payloads = [
        (config, repetition, tuple(child.spawn_key))
        for repetition, child in enumerate(
            root.spawn(int(config["_active_repetitions"]))
        )
    ]
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))

    cells = pd.DataFrame([
        row for part in nested for row in part["cells"]
    ])
    recovery = pd.DataFrame([
        row for part in nested for row in part["recovery"]
    ])
    residual = pd.DataFrame([
        row for part in nested for row in part["residual"]
    ])
    ranks = pd.DataFrame([
        row for part in nested for row in part["ranks"]
    ])
    seeds = [seed for part in nested for seed in part["seeds"]]
    (
        cell_summary,
        recovery_summary,
        residual_summary,
        evidence,
    ) = _summaries(cells, recovery, residual, config=config)
    checks = {
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        **evidence["checks"],
    }
    integrity_pass = bool(
        checks["seed_uniqueness"]
        and checks["numeric_integrity"]
    )
    if not integrity_pass:
        status = "V8_MISSPECIFICATION_TRANSPORT_V37H4_STOP_INTEGRITY"
    elif args.mode == "smoke":
        status = "V8_MISSPECIFICATION_TRANSPORT_V37H4_SMOKE_COMPLETE"
    elif all(checks.values()):
        status = (
            "V8_MISSPECIFICATION_TRANSPORT_V37H4_"
            "PASS_MISSPECIFICATION_AWARE"
        )
    elif all(checks[name] for name in (
        "w0_recovery",
        "w0_split_stability",
        "w0_false_refusal",
        "w0_crc_calibration",
        "w0_gain_calibration",
    )) and (
        checks["strong_detection"] or checks["nonergodic_refusal"]
    ):
        status = (
            "V8_MISSPECIFICATION_TRANSPORT_V37H4_"
            "PARTIAL_DETECTS_NOT_LOCALIZES"
        )
    else:
        status = (
            "V8_MISSPECIFICATION_TRANSPORT_V37H4_"
            "REFUTED_OVERCONFIDENT_ADDITIVE"
        )
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "checks": checks,
        **evidence,
        "row_counts": {
            "cells": int(len(cells)),
            "recovery": int(len(recovery)),
            "residual": int(len(residual)),
            "rank_losses": int(len(ranks)),
        },
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "cell_metrics.csv", index=False)
    cell_summary.to_csv(
        args.output_dir / "cell_summary.csv",
        index=False,
    )
    recovery.to_csv(
        args.output_dir / "recovery_metrics.csv",
        index=False,
    )
    recovery_summary.to_csv(
        args.output_dir / "recovery_summary.csv",
        index=False,
    )
    residual.to_csv(
        args.output_dir / "residual_k_metrics.csv",
        index=False,
    )
    residual_summary.to_csv(
        args.output_dir / "residual_k_summary.csv",
        index=False,
    )
    ranks.to_csv(
        args.output_dir / "rank_selection_metrics.csv",
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
        _report(decision),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT
            / "suica_core/v8_multiscale_zero_identification.py",
            ROOT
            / "suica_core/v8_misspecification_transport.py",
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
        "repetitions": int(config["_active_repetitions"]),
        "cells": int(len(cells)),
        "output_dir": str(args.output_dir),
        "checks": checks,
    }, indent=2))
    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

