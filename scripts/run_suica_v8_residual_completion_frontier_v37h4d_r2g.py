#!/usr/bin/env python3
"""Run the V3.7H.4D-R2G residual-completion frontier."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_residual_completion_frontier import (  # noqa: E402
    CompletionFamily,
    ResidualCompletionSpec,
    evaluate_residual_arm,
    fit_completion_family,
    global_cross_view_r2,
    make_world_parameters,
    overfit_trap_metrics,
    predict_completion,
    select_completion_candidate,
    simulate_completion_panel,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_residual_completion_frontier_v37h4d_r2g.json"
)
DEFAULT_OUTPUT_ROOT = (
    ROOT / "results/v8_residual_completion_frontier"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            allow_nan=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any]) -> ResidualCompletionSpec:
    values = config["spec"]
    return ResidualCompletionSpec(
        dimensions=int(values["dimensions"]),
        latent_rank=int(values["latent_rank"]),
        units_per_group=int(values["units_per_group"]),
        opportunities_per_observation=int(
            values["opportunities_per_observation"]
        ),
        common_fraction=float(values["common_fraction"]),
        student_df=float(values["student_df"]),
    )


def _selection_key(
    world: str,
    noise_mode: str,
    effect_share: float,
) -> str:
    return f"{world}|{noise_mode}|{float(effect_share):.6f}"


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _baseline_predictions(
    model: CompletionFamily,
    panel: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    shape_a = panel["target_a"].shape
    shape_b = panel["target_b"].shape
    return (
        np.broadcast_to(model.target_center, shape_a).copy(),
        np.broadcast_to(model.target_center, shape_b).copy(),
    )


def _selected_predictions(
    models: dict[str, CompletionFamily],
    selected: dict[str, Any],
    panel: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    if int(selected["rank"]) == 0:
        return _baseline_predictions(next(iter(models.values())), panel)
    model = models[str(selected["family"])]
    return (
        predict_completion(
            model,
            panel["score_a"],
            rank=int(selected["rank"]),
        ),
        predict_completion(
            model,
            panel["score_b"],
            rank=int(selected["rank"]),
        ),
    )


def _worker(
    payload: tuple[
        dict[str, Any],
        int,
        str,
        str,
        float,
        dict[str, Any] | None,
    ],
) -> dict[str, Any]:
    config, cell_seed, world, noise_mode, effect_share, forced = payload
    streams = np.random.SeedSequence(int(cell_seed)).spawn(12)
    seeds = [_uint64(stream) for stream in streams]
    spec = _spec(config)
    parameters = make_world_parameters(
        seed=seeds[0],
        spec=spec,
        effect_share=float(effect_share),
    )
    training = simulate_completion_panel(
        seed=seeds[1],
        world=world,
        groups=int(config["training_groups"]),
        spec=spec,
        parameters=parameters,
        noise_mode=noise_mode,
    )
    calibration = simulate_completion_panel(
        seed=seeds[2],
        world=world,
        groups=int(config["calibration_groups"]),
        spec=spec,
        parameters=parameters,
        noise_mode=noise_mode,
    )
    confirmation = simulate_completion_panel(
        seed=seeds[3],
        world=world,
        groups=int(config["confirmation_groups"]),
        spec=spec,
        parameters=parameters,
        noise_mode=noise_mode,
    )
    maximum_rank = max(map(int, config["candidate_ranks"]))
    models: dict[str, CompletionFamily] = {}
    for index, family in enumerate(config["candidate_families"]):
        models[str(family)] = fit_completion_family(
            training,
            family=str(family),
            ridge_alpha=float(config["ridge_alpha"]),
            maximum_rank=maximum_rank,
            rff_components=int(config["rff_components"]),
            rff_gamma=float(config["rff_gamma"]),
            quadratic_input_rank=int(config["quadratic_input_rank"]),
            seed=seeds[4 + index],
        )
    local_selected, candidates = select_completion_candidate(
        calibration,
        models,
        ranks=config["candidate_ranks"],
        minimum_gain=float(config["minimum_calibration_gain"]),
    )
    selected = local_selected if forced is None else forced
    raw_a, raw_b = _baseline_predictions(
        next(iter(models.values())),
        confirmation,
    )
    learned_a, learned_b = _selected_predictions(
        models,
        selected,
        confirmation,
    )
    arm_predictions = {
        "raw": (raw_a, raw_b),
        "learned_completion": (learned_a, learned_b),
        "oracle_admissible": (
            confirmation["predictable_target_a"],
            confirmation["predictable_target_b"],
        ),
        "oracle_omniscient": (
            confirmation["all_systematic_target_a"],
            confirmation["all_systematic_target_b"],
        ),
    }
    arm_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    arm_metrics: dict[str, dict[str, Any]] = {}
    target_center = next(iter(models.values())).target_center
    for arm_index, (arm, prediction) in enumerate(
        arm_predictions.items()
    ):
        residual_a = confirmation["target_a"] - prediction[0]
        residual_b = confirmation["target_b"] - prediction[1]
        metrics = evaluate_residual_arm(
            residual_a,
            residual_b,
            sizes=config["group_sizes"],
            seed=seeds[7 + arm_index],
        )
        arm_metrics[arm] = metrics
        arm_rows.append({
            "world": world,
            "noise_mode": noise_mode,
            "effect_share": float(effect_share),
            "arm": arm,
            "selected_family": str(selected["family"]),
            "selected_rank": int(selected["rank"]),
            "local_selected_family": str(local_selected["family"]),
            "local_selected_rank": int(local_selected["rank"]),
            "calibration_relative_gain": float(
                selected.get("relative_gain", float("nan"))
            ),
            "cross_view_r2": global_cross_view_r2(
                confirmation,
                prediction[0],
                prediction[1],
                target_center=target_center,
            ),
            **{
                key: value
                for key, value in metrics.items()
                if key != "curve"
            },
        })
        curve_rows.extend([
            {
                "world": world,
                "noise_mode": noise_mode,
                "effect_share": float(effect_share),
                "arm": arm,
                **row,
            }
            for row in metrics["curve"]
        ])
    raw_floor = float(arm_metrics["raw"]["cross_floor_ratio"])
    learned_floor = float(
        arm_metrics["learned_completion"]["cross_floor_ratio"]
    )
    denominator = max(abs(raw_floor), 1e-12)
    floor_reduction = float((raw_floor - learned_floor) / denominator)
    for row in arm_rows:
        row["learned_cross_floor_reduction"] = floor_reduction
    candidate_rows = [
        {
            "world": world,
            "noise_mode": noise_mode,
            "effect_share": float(effect_share),
            **row,
        }
        for row in candidates
    ]
    overfit = (
        overfit_trap_metrics(
            training,
            confirmation,
            seed=seeds[11],
        )
        if world == "overfit_null"
        else {}
    )
    return {
        "arms": arm_rows,
        "curves": curve_rows,
        "candidates": candidate_rows,
        "local_selected": {
            "world": world,
            "noise_mode": noise_mode,
            "effect_share": float(effect_share),
            **local_selected,
        },
        "overfit": {
            "world": world,
            "noise_mode": noise_mode,
            "effect_share": float(effect_share),
            **overfit,
        } if overfit else {},
        "seeds": seeds,
    }


def _freeze_discovery_selection(
    candidates: pd.DataFrame,
    *,
    minimum_gain: float,
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    group_columns = ["world", "noise_mode", "effect_share"]
    for cell, frame in candidates.groupby(
        group_columns,
        sort=True,
        observed=True,
    ):
        world, noise_mode, effect_share = cell
        summary = (
            frame.groupby(
                ["family", "rank", "complexity"],
                sort=True,
                observed=True,
            )["mean_loss"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )
        summary["se"] = (
            summary["std"].fillna(0.0)
            / np.sqrt(summary["count"].clip(lower=1))
        )
        baseline = summary[
            (summary["family"] == "none")
            & (summary["rank"] == 0)
        ].iloc[0]
        best = summary.loc[summary["mean"].idxmin()]
        gain = float(1.0 - best["mean"] / baseline["mean"])
        if gain < float(minimum_gain):
            selected = baseline
        else:
            admissible = summary[
                (summary["mean"] <= best["mean"] + best["se"])
                & (
                    (summary["rank"] == 0)
                    | (
                        1.0 - summary["mean"] / baseline["mean"]
                        >= float(minimum_gain)
                    )
                )
            ]
            selected = admissible.sort_values(
                ["complexity", "mean"],
                kind="stable",
            ).iloc[0]
        key = _selection_key(
            str(world),
            str(noise_mode),
            float(effect_share),
        )
        rows[key] = {
            "family": str(selected["family"]),
            "rank": int(selected["rank"]),
            "relative_gain": float(
                1.0 - selected["mean"] / baseline["mean"]
            ),
            "discovery_mean_loss": float(selected["mean"]),
            "discovery_se_loss": float(selected["se"]),
            "selection_rule": "cross-root one-SE, minimum complexity",
        }
    return {
        "version": "v8-r2g-frozen-selection-1",
        "created_utc": datetime.now(UTC).isoformat(),
        "source": "R2G discovery only",
        "cells": rows,
    }


def _metric_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "phi_cross_view",
        "unit_energy",
        "self_floor_ratio",
        "cross_floor_ratio",
        "cross_view_r2",
        "learned_cross_floor_reduction",
    ]
    rows: list[dict[str, Any]] = []
    for cell, frame in metrics.groupby(
        ["world", "noise_mode", "effect_share", "arm"],
        sort=True,
        observed=True,
    ):
        row = dict(
            zip(
                ["world", "noise_mode", "effect_share", "arm"],
                cell,
                strict=True,
            )
        )
        row["repetitions"] = int(len(frame))
        for column in columns:
            values = frame[column].to_numpy(dtype=float)
            row[f"{column}_mean"] = float(np.nanmean(values))
            row[f"{column}_lo"] = float(np.nanquantile(values, 0.025))
            row[f"{column}_hi"] = float(np.nanquantile(values, 0.975))
        rows.append(row)
    return pd.DataFrame(rows)


def _lookup(
    summary: pd.DataFrame,
    *,
    world: str,
    noise_mode: str,
    effect_share: float,
    arm: str,
    metric: str,
    bound: str,
) -> float:
    row = summary[
        (summary["world"] == world)
        & (summary["noise_mode"] == noise_mode)
        & np.isclose(summary["effect_share"], effect_share)
        & (summary["arm"] == arm)
    ]
    if len(row) != 1:
        return float("nan")
    return float(row.iloc[0][f"{metric}_{bound}"])


def _decision(
    *,
    mode: str,
    config: dict[str, Any],
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    overfit: pd.DataFrame,
    seed_count: int,
    unique_seed_count: int,
) -> dict[str, Any]:
    if mode == "smoke":
        return {
            "status": "V8_R2G_SMOKE_COMPLETE",
            "checks": {
                "numeric_integrity": bool(len(summary)),
                "seed_uniqueness": bool(
                    seed_count == unique_seed_count
                ),
            },
        }
    if mode == "discovery":
        return {
            "status": "V8_R2G_DISCOVERY_COMPLETE_SELECTION_FROZEN",
            "checks": {
                "numeric_integrity": bool(len(summary)),
                "seed_uniqueness": bool(
                    seed_count == unique_seed_count
                ),
                "selection_cells_present": bool(len(selected)),
            },
        }

    gates = config["gates"]
    eta = float(config["primary_effect_share"])
    checks_by_noise: dict[str, dict[str, bool]] = {}
    for noise in config["noise_modes"]:
        def value(
            world: str,
            arm: str,
            metric: str,
            bound: str,
        ) -> float:
            return _lookup(
                summary,
                world=world,
                noise_mode=str(noise),
                effect_share=eta,
                arm=arm,
                metric=metric,
                bound=bound,
            )

        practical_phi = float(gates["practical_phi"])
        practical_floor = float(gates["practical_floor_ratio"])
        structured_phi = float(gates["minimum_structured_phi"])
        structured_floor = float(
            gates["minimum_structured_floor_ratio"]
        )
        minimum_reduction = float(
            gates["minimum_completion_floor_reduction"]
        )
        checks_by_noise[str(noise)] = {
            "w0_null_phi": bool(
                value(
                    "pure_iid",
                    "learned_completion",
                    "phi_cross_view",
                    "hi",
                )
                <= practical_phi
            ),
            "w0_null_floor": bool(
                value(
                    "pure_iid",
                    "learned_completion",
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
            ),
            "w1_aggregation_not_completeness": bool(
                value(
                    "author_low_rank",
                    "raw",
                    "phi_cross_view",
                    "lo",
                )
                > structured_phi
                and value(
                    "author_low_rank",
                    "raw",
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
            ),
            "w2_linear_omission_present": bool(
                value(
                    "common_low_rank",
                    "raw",
                    "phi_cross_view",
                    "lo",
                )
                > structured_phi
                and value(
                    "common_low_rank",
                    "raw",
                    "cross_floor_ratio",
                    "lo",
                )
                > structured_floor
            ),
            "w2_linear_completion_zero": bool(
                value(
                    "common_low_rank",
                    "learned_completion",
                    "phi_cross_view",
                    "hi",
                )
                <= practical_phi
                and value(
                    "common_low_rank",
                    "learned_completion",
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
                and value(
                    "common_low_rank",
                    "learned_completion",
                    "learned_cross_floor_reduction",
                    "lo",
                )
                >= minimum_reduction
            ),
            "w3_nonlinear_omission_present": bool(
                value(
                    "nonlinear_common",
                    "raw",
                    "phi_cross_view",
                    "lo",
                )
                > structured_phi
                and value(
                    "nonlinear_common",
                    "raw",
                    "cross_floor_ratio",
                    "lo",
                )
                > structured_floor
            ),
            "w3_nonlinear_completion_zero": bool(
                value(
                    "nonlinear_common",
                    "learned_completion",
                    "phi_cross_view",
                    "hi",
                )
                <= practical_phi
                and value(
                    "nonlinear_common",
                    "learned_completion",
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
                and value(
                    "nonlinear_common",
                    "learned_completion",
                    "learned_cross_floor_reduction",
                    "lo",
                )
                >= minimum_reduction
            ),
            "w4_irreducible_not_falsely_zero": bool(
                value(
                    "irreducible_common_shock",
                    "learned_completion",
                    "cross_floor_ratio",
                    "lo",
                )
                > structured_floor
            ),
        }
    overfit_check = bool(
        len(overfit)
        and overfit["training_r2"].quantile(0.025)
        >= float(gates["minimum_overfit_training_r2"])
        and overfit["confirmation_r2"].quantile(0.975)
        <= float(gates["maximum_overfit_confirmation_r2"])
    )
    null_rows = selected[
        selected["world"].isin(["pure_iid", "overfit_null"])
    ]
    null_nonzero_rate = float(
        (null_rows["rank"].astype(int) > 0).mean()
    ) if len(null_rows) else float("nan")
    null_selection_check = bool(
        null_nonzero_rate
        <= float(gates["maximum_null_nonzero_selection_rate"])
    )
    all_checks = [
        check
        for by_noise in checks_by_noise.values()
        for check in by_noise.values()
    ]
    controls = all(
        by_noise["w0_null_phi"]
        and by_noise["w0_null_floor"]
        and by_noise["w1_aggregation_not_completeness"]
        and by_noise["w4_irreducible_not_falsely_zero"]
        for by_noise in checks_by_noise.values()
    ) and overfit_check and null_selection_check
    linear_complete = all(
        by_noise["w2_linear_omission_present"]
        and by_noise["w2_linear_completion_zero"]
        for by_noise in checks_by_noise.values()
    )
    nonlinear_complete = all(
        by_noise["w3_nonlinear_omission_present"]
        and by_noise["w3_nonlinear_completion_zero"]
        for by_noise in checks_by_noise.values()
    )
    false_completeness = any(
        not by_noise["w4_irreducible_not_falsely_zero"]
        for by_noise in checks_by_noise.values()
    ) or not overfit_check
    if false_completeness:
        status = "V8_R2G_REFUTED_FALSE_COMPLETENESS"
    elif controls and linear_complete and nonlinear_complete:
        status = "V8_R2G_PASS_FINITE_COMPLETION"
    elif controls and linear_complete:
        status = "V8_R2G_PARTIAL_LINEAR_ONLY"
    elif controls:
        status = "V8_R2G_INCONCLUSIVE_BOUNDED_COMPLETION"
    else:
        status = "V8_R2G_STOP_CONTROL_FAILURE"
    return {
        "status": status,
        "checks": {
            "numeric_integrity": bool(
                len(summary)
                and np.isfinite(
                    summary.select_dtypes(include=[np.number]).to_numpy()
                ).all()
            ),
            "seed_uniqueness": bool(seed_count == unique_seed_count),
            "overfit_trap": overfit_check,
            "null_selection": null_selection_check,
            "controls": controls,
            "linear_completion": linear_complete,
            "nonlinear_completion": nonlinear_complete,
            "all_registered_endpoint_checks": bool(all(all_checks)),
        },
        "checks_by_noise": checks_by_noise,
        "null_nonzero_selection_rate": null_nonzero_rate,
    }


def _report(
    *,
    decision: dict[str, Any],
    mode: str,
    selection_manifest: dict[str, Any] | None,
) -> str:
    selection = (
        json.dumps(
            selection_manifest["cells"],
            ensure_ascii=False,
            indent=2,
        )
        if selection_manifest is not None
        else "not frozen in smoke mode"
    )
    return f"""# V8 V3.7H.4D-R2G Residual Completion Frontier

Mode: `{mode}`

Decision: `{decision["status"]}`

## Frozen selection

```json
{selection}
```

## Checks

```json
{json.dumps(decision.get("checks", {}), ensure_ascii=False, indent=2)}
```

## Interpretation boundary

This is a synthetic existence and identifiability experiment. A pass means a
finite, frozen score-only factor class can remove registered structured
omission on fresh groups while refusing an unavailable common shock and an
in-sample memorizer. It does not prove exact zero, complete psychological
factors, or transfer to real text.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery", "confirmation"],
        default="discovery",
    )
    parser.add_argument("--selection-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    config = _read(args.config)
    seed = int(config[f"{args.mode}_seed"])
    repetitions = int(config[f"{args.mode}_repetitions"])
    forced_manifest: dict[str, Any] | None = None
    if args.mode == "confirmation":
        if args.selection_manifest is None:
            raise SystemExit(
                "confirmation requires --selection-manifest from discovery"
            )
        forced_manifest = _read(args.selection_manifest)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir or (
        DEFAULT_OUTPUT_ROOT
        / f"v37h4d_r2g_{args.mode}_{repetitions}rep_{timestamp}"
    )
    root = np.random.SeedSequence(seed)
    cells = [
        (str(world), str(noise), float(effect))
        for world in config["worlds"]
        for noise in config["noise_modes"]
        for effect in config["effect_shares"]
    ]
    children = root.spawn(repetitions * len(cells))
    payloads = []
    for repetition in range(repetitions):
        for cell_index, (world, noise, effect) in enumerate(cells):
            child = children[repetition * len(cells) + cell_index]
            forced = None
            if forced_manifest is not None:
                forced = forced_manifest["cells"][
                    _selection_key(world, noise, effect)
                ]
            payloads.append((
                config,
                _uint64(child),
                world,
                noise,
                effect,
                forced,
            ))
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))

    arm_rows = []
    curve_rows = []
    candidate_rows = []
    selected_rows = []
    overfit_rows = []
    seeds = []
    for repetition, part in enumerate(nested):
        for row in part["arms"]:
            arm_rows.append({"repetition": repetition, **row})
        for row in part["curves"]:
            curve_rows.append({"repetition": repetition, **row})
        for row in part["candidates"]:
            candidate_rows.append({"repetition": repetition, **row})
        selected_rows.append({
            "repetition": repetition,
            **part["local_selected"],
        })
        if part["overfit"]:
            overfit_rows.append({
                "repetition": repetition,
                **part["overfit"],
            })
        seeds.extend(part["seeds"])
    metrics = pd.DataFrame(arm_rows)
    curves = pd.DataFrame(curve_rows)
    candidates = pd.DataFrame(candidate_rows)
    selected = pd.DataFrame(selected_rows)
    overfit = pd.DataFrame(overfit_rows)
    summary = _metric_summary(metrics)

    selection_manifest = forced_manifest
    if args.mode == "discovery":
        selection_manifest = _freeze_discovery_selection(
            candidates,
            minimum_gain=float(config["minimum_calibration_gain"]),
        )
    decision = _decision(
        mode=args.mode,
        config=config,
        summary=summary,
        selected=selected,
        overfit=overfit,
        seed_count=len(seeds),
        unique_seed_count=len(set(seeds)),
    )
    decision["mode"] = args.mode
    decision["repetitions"] = repetitions
    decision["root_seed"] = seed
    decision["row_counts"] = {
        "metrics": int(len(metrics)),
        "curves": int(len(curves)),
        "candidates": int(len(candidates)),
        "selected": int(len(selected)),
        "overfit": int(len(overfit)),
    }
    decision["seed_count"] = int(len(seeds))
    decision["unique_seed_count"] = int(len(set(seeds)))
    decision["claim_boundary"] = str(config["claim_boundary"])

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_dir / "metrics_by_root.csv", index=False)
    curves.to_csv(output_dir / "scaling_curves.csv", index=False)
    candidates.to_csv(
        output_dir / "calibration_candidates.csv",
        index=False,
    )
    selected.to_csv(
        output_dir / "local_selection_diagnostics.csv",
        index=False,
    )
    overfit.to_csv(output_dir / "overfit_trap.csv", index=False)
    summary.to_csv(output_dir / "metric_summary.csv", index=False)
    _write(output_dir / "decision.json", decision)
    _write(output_dir / "config_effective.json", config)
    if selection_manifest is not None:
        _write(
            output_dir / "selection_manifest.json",
            selection_manifest,
        )
    _write(output_dir / "seed_audit.json", {
        "root_seed": seed,
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (output_dir / "report.md").write_text(
        _report(
            decision=decision,
            mode=args.mode,
            selection_manifest=selection_manifest,
        ),
        encoding="utf-8",
    )
    input_paths: list[Path] = []
    if args.selection_manifest is not None:
        input_paths.append(args.selection_manifest)
    write_run_manifest(
        output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=input_paths,
        config_path=args.config,
        code_paths=[
            ROOT
            / "suica_core/v8_residual_completion_frontier.py",
            Path(__file__),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        output_dir,
        output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
