#!/usr/bin/env python3
"""Run the R2G.1 score-opportunity limit experiment."""
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
    ResidualCompletionSpec,
    evaluate_residual_arm,
    fit_completion_family,
    global_cross_view_r2,
    make_world_parameters,
    predict_completion,
    simulate_completion_panel,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs/v8_residual_completion_k_frontier_v37h4d_r2g1.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/v8_residual_completion_frontier"
    / "v37h4d_r2g1_k_frontier"
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


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


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


def _key(world: str, noise_mode: str, effect_share: float) -> str:
    return f"{world}|{noise_mode}|{float(effect_share):.6f}"


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        str,
        str,
    ],
) -> dict[str, Any]:
    config, selection, cell_seed, train_groups, world, noise_mode = payload
    streams = np.random.SeedSequence(int(cell_seed)).spawn(7)
    seeds = [_uint64(stream) for stream in streams]
    spec = _spec(config)
    effect_share = float(config["effect_share"])
    frozen = selection["cells"][_key(world, noise_mode, effect_share)]
    parameters = make_world_parameters(
        seed=seeds[0],
        spec=spec,
        effect_share=effect_share,
    )
    rows: list[dict[str, Any]] = []
    for opportunities in map(int, config["score_opportunities"]):
        training = simulate_completion_panel(
            seed=seeds[1],
            world=world,
            groups=int(train_groups),
            spec=spec,
            parameters=parameters,
            noise_mode=noise_mode,
            score_opportunities=opportunities,
            target_opportunities=int(config["target_opportunities"]),
        )
        confirmation = simulate_completion_panel(
            seed=seeds[2],
            world=world,
            groups=int(config["confirmation_groups"]),
            spec=spec,
            parameters=parameters,
            noise_mode=noise_mode,
            score_opportunities=opportunities,
            target_opportunities=int(config["target_opportunities"]),
        )
        target_center = np.concatenate(
            [
                training["target_a"].reshape(
                    -1,
                    spec.dimensions,
                ),
                training["target_b"].reshape(
                    -1,
                    spec.dimensions,
                ),
            ],
            axis=0,
        ).mean(axis=0)
        if int(frozen["rank"]) > 0:
            model = fit_completion_family(
                training,
                family=str(frozen["family"]),
                ridge_alpha=float(config["ridge_alpha"]),
                maximum_rank=int(frozen["rank"]),
                rff_components=int(config["rff_components"]),
                rff_gamma=float(config["rff_gamma"]),
                quadratic_input_rank=int(
                    config["quadratic_input_rank"]
                ),
                seed=seeds[3],
            )
            learned_a = predict_completion(
                model,
                confirmation["score_a"],
                rank=int(frozen["rank"]),
            )
            learned_b = predict_completion(
                model,
                confirmation["score_b"],
                rank=int(frozen["rank"]),
            )
            target_center = model.target_center
        else:
            learned_a = np.broadcast_to(
                target_center,
                confirmation["target_a"].shape,
            ).copy()
            learned_b = np.broadcast_to(
                target_center,
                confirmation["target_b"].shape,
            ).copy()
        raw_a = np.broadcast_to(
            target_center,
            confirmation["target_a"].shape,
        ).copy()
        raw_b = np.broadcast_to(
            target_center,
            confirmation["target_b"].shape,
        ).copy()
        predictions = {
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
        for arm_index, (arm, prediction) in enumerate(
            predictions.items()
        ):
            residual_a = confirmation["target_a"] - prediction[0]
            residual_b = confirmation["target_b"] - prediction[1]
            metrics = evaluate_residual_arm(
                residual_a,
                residual_b,
                sizes=config["group_sizes"],
                seed=seeds[4 + (arm_index % 3)],
            )
            rows.append({
                "training_groups": int(train_groups),
                "world": world,
                "noise_mode": noise_mode,
                "score_opportunities": opportunities,
                "score_limit": (
                    "infinity" if opportunities == 0 else str(opportunities)
                ),
                "arm": arm,
                "frozen_family": str(frozen["family"]),
                "frozen_rank": int(frozen["rank"]),
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
    return {"rows": rows, "seeds": seeds}


def _summary(metrics: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "phi_cross_view",
        "cross_floor_ratio",
        "self_floor_ratio",
        "cross_view_r2",
    ]
    rows: list[dict[str, Any]] = []
    group_columns = [
        "training_groups",
        "world",
        "noise_mode",
        "score_opportunities",
        "score_limit",
        "arm",
    ]
    for cell, frame in metrics.groupby(
        group_columns,
        sort=True,
        observed=True,
    ):
        row = dict(zip(group_columns, cell, strict=True))
        row["repetitions"] = int(len(frame))
        for column in columns:
            values = frame[column].to_numpy(dtype=float)
            row[f"{column}_mean"] = float(np.mean(values))
            row[f"{column}_lo"] = float(np.quantile(values, 0.025))
            row[f"{column}_hi"] = float(np.quantile(values, 0.975))
        rows.append(row)
    return pd.DataFrame(rows)


def _get(
    summary: pd.DataFrame,
    *,
    training_groups: int,
    world: str,
    noise_mode: str,
    opportunities: int,
    arm: str,
    metric: str,
    bound: str,
) -> float:
    row = summary[
        (summary["training_groups"] == training_groups)
        & (summary["world"] == world)
        & (summary["noise_mode"] == noise_mode)
        & (summary["score_opportunities"] == opportunities)
        & (summary["arm"] == arm)
    ]
    if len(row) != 1:
        return float("nan")
    return float(row.iloc[0][f"{metric}_{bound}"])


def _decision(
    config: dict[str, Any],
    summary: pd.DataFrame,
    *,
    seed_count: int,
    unique_seed_count: int,
) -> dict[str, Any]:
    gates = config["gates"]
    training_groups = max(map(int, config["training_groups"]))
    checks_by_noise: dict[str, dict[str, bool]] = {}
    for noise in config["noise_modes"]:
        def value(
            world: str,
            opportunities: int,
            metric: str,
            bound: str,
        ) -> float:
            return _get(
                summary,
                training_groups=training_groups,
                world=world,
                noise_mode=str(noise),
                opportunities=opportunities,
                arm="learned_completion",
                metric=metric,
                bound=bound,
            )

        practical_phi = float(gates["practical_phi"])
        practical_floor = float(gates["practical_floor_ratio"])
        checks_by_noise[str(noise)] = {
            "null_limit_control": bool(
                value("pure_iid", 0, "phi_cross_view", "hi")
                <= practical_phi
                and value(
                    "pure_iid",
                    0,
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
            ),
            "linear_limit_zero": bool(
                value(
                    "common_low_rank",
                    0,
                    "phi_cross_view",
                    "hi",
                )
                <= practical_phi
                and value(
                    "common_low_rank",
                    0,
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
            ),
            "nonlinear_limit_zero": bool(
                value(
                    "nonlinear_common",
                    0,
                    "phi_cross_view",
                    "hi",
                )
                <= practical_phi
                and value(
                    "nonlinear_common",
                    0,
                    "cross_floor_ratio",
                    "hi",
                )
                <= practical_floor
            ),
            "irreducible_limit_persists": bool(
                value(
                    "irreducible_common_shock",
                    0,
                    "cross_floor_ratio",
                    "lo",
                )
                > float(gates["minimum_irreducible_floor_ratio"])
            ),
            "linear_resolution_gain": bool(
                value(
                    "common_low_rank",
                    0,
                    "cross_floor_ratio",
                    "hi",
                )
                < value(
                    "common_low_rank",
                    4,
                    "cross_floor_ratio",
                    "lo",
                )
            ),
            "nonlinear_resolution_gain": bool(
                value(
                    "nonlinear_common",
                    0,
                    "cross_floor_ratio",
                    "hi",
                )
                < value(
                    "nonlinear_common",
                    4,
                    "cross_floor_ratio",
                    "lo",
                )
            ),
        }
    controls = all(
        row["null_limit_control"]
        and row["irreducible_limit_persists"]
        for row in checks_by_noise.values()
    )
    linear = all(
        row["linear_limit_zero"] and row["linear_resolution_gain"]
        for row in checks_by_noise.values()
    )
    nonlinear = all(
        row["nonlinear_limit_zero"]
        and row["nonlinear_resolution_gain"]
        for row in checks_by_noise.values()
    )
    if controls and linear and nonlinear:
        status = "V8_R2G1_PASS_FACTOR_COMPLETENESS_LIMIT"
    elif controls and linear:
        status = "V8_R2G1_PARTIAL_LINEAR_LIMIT"
    elif controls:
        status = "V8_R2G1_INCONCLUSIVE_LIMIT"
    else:
        status = "V8_R2G1_STOP_CONTROL_FAILURE"
    return {
        "status": status,
        "scientific_decision": (
            "PARTIAL_CONSTRUCTIVE_EXISTENCE"
            if status == "V8_R2G1_PASS_FACTOR_COMPLETENESS_LIMIT"
            else "UNRESOLVED_SYNTHETIC_LIMIT"
        ),
        "checks": {
            "numeric_integrity": bool(
                len(summary)
                and np.isfinite(
                    summary.select_dtypes(include=[np.number]).to_numpy()
                ).all()
            ),
            "seed_uniqueness": seed_count == unique_seed_count,
            "controls": controls,
            "linear_limit": linear,
            "nonlinear_limit": nonlinear,
        },
        "checks_by_noise": checks_by_noise,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--selection-manifest",
        type=Path,
        required=True,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    selection = _read(args.selection_manifest)
    root = np.random.SeedSequence(int(config["seed"]))
    cells = [
        (int(groups), str(world), str(noise))
        for groups in config["training_groups"]
        for world in config["worlds"]
        for noise in config["noise_modes"]
    ]
    children = root.spawn(int(config["repetitions"]) * len(cells))
    payloads = []
    for repetition in range(int(config["repetitions"])):
        for index, cell in enumerate(cells):
            payloads.append((
                config,
                selection,
                _uint64(children[repetition * len(cells) + index]),
                *cell,
            ))
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    rows = []
    seeds = []
    for root_index, part in enumerate(nested):
        for row in part["rows"]:
            rows.append({"root_index": root_index, **row})
        seeds.extend(part["seeds"])
    metrics = pd.DataFrame(rows)
    summary = _summary(metrics)
    decision = _decision(
        config,
        summary,
        seed_count=len(seeds),
        unique_seed_count=len(set(seeds)),
    )
    decision.update({
        "repetitions": int(config["repetitions"]),
        "root_seed": int(config["seed"]),
        "metric_rows": int(len(metrics)),
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "common_random_number_policy": (
            "Latents and target observations are paired across score K "
            "within each root."
        ),
        "claim_boundary": str(config["claim_boundary"]),
    })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "k_frontier_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "k_frontier_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "root_seed": int(config["seed"]),
        "source_seed_count": len(seeds),
        "unique_source_seed_count": len(set(seeds)),
        "all_source_streams_unique": len(seeds) == len(set(seeds)),
        "paired_across_k": True,
    })
    (args.output_dir / "report.md").write_text(
        f"""# V8 R2G.1 Score-Resolution Limit

Decision: `{decision["status"]}`

Scientific decision: `{decision["scientific_decision"]}`

```json
{json.dumps(decision["checks"], ensure_ascii=False, indent=2)}
```

`score_opportunities=0` is the noiseless mathematical limit, not an
attainable real-text observation. The experiment tests whether the frozen
R2G factor classes approach their oracle residual when score measurement
error is removed.
""",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[args.selection_manifest],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_residual_completion_frontier.py",
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
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
