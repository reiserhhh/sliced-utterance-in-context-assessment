#!/usr/bin/env python3
"""Aggregate deterministic M4-C.3.5-R2 repetition shards."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    ARM_NAMES,
    _decision,
    _report,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate(
    metrics: pd.DataFrame,
    controls: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> None:
    repetitions = set(range(int(config["repetitions"])))
    observed = set(pd.to_numeric(metrics["repetition"]).astype(int))
    if observed != repetitions:
        raise ValueError(f"repetition coverage mismatch: {sorted(observed)}")
    metric_keys = [
        "repetition",
        "world",
        "world_type",
        "view",
        "arm",
    ]
    control_keys = ["repetition", "world", "control"]
    if metrics.duplicated(metric_keys).any():
        raise ValueError("duplicate R2 metric cells across shards")
    if controls.duplicated(control_keys).any():
        raise ValueError("duplicate R2 control cells across shards")
    worlds = {
        **{world: "main" for world in config["main_worlds"]},
    }
    for world in config["null_worlds"]:
        repeats = int(config.get("null_repeats", {}).get(world, 1))
        worlds.update(
            {
                f"{world}__draw_{draw:02d}": "null"
                for draw in range(repeats)
            }
        )
    expected_metric = {
        (repetition, world, world_type, view, arm)
        for repetition in repetitions
        for world, world_type in worlds.items()
        for view in ("train", "test")
        for arm in ARM_NAMES
    }
    actual_metric = {
        (
            int(row.repetition),
            str(row.world),
            str(row.world_type),
            str(row.view),
            str(row.arm),
        )
        for row in metrics.itertuples()
    }
    if actual_metric != expected_metric:
        missing = sorted(expected_metric - actual_metric)[:5]
        extra = sorted(actual_metric - expected_metric)[:5]
        raise ValueError(
            f"R2 metric cell mismatch: missing={missing}, extra={extra}"
        )
    expected_control = set()
    first_world = str(config["main_worlds"][0])
    for repetition in repetitions:
        for world in worlds:
            expected_control.add(
                (repetition, str(world), "basis_contract")
            )
        for world in config["main_worlds"]:
            expected_control.add(
                (repetition, str(world), "author_permutation")
            )
            expected_control.add(
                (repetition, str(world), "source_shuffle")
            )
            expected_control.add(
                (repetition, str(world), "cka_permutation")
            )
        expected_control.update(
            {
                (repetition, first_world, "block_gauge"),
                (repetition, first_world, "common_shift"),
                (
                    repetition,
                    "evaluation_support_shift",
                    "support_shift",
                ),
                (
                    repetition,
                    "condition_alias_ecology",
                    "latent_alias",
                ),
            }
        )
    actual_control = {
        (int(row.repetition), str(row.world), str(row.control))
        for row in controls.itertuples()
    }
    if actual_control != expected_control:
        missing = sorted(expected_control - actual_control)[:5]
        extra = sorted(actual_control - expected_control)[:5]
        raise ValueError(
            f"R2 control cell mismatch: missing={missing}, extra={extra}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_response_safe_chart_replacement.json",
    )
    parser.add_argument(
        "--shard-directory",
        type=Path,
        default=(
            ROOT
            / "results"
            / "m4_response_safe_chart_replacement_shards"
        ),
    )
    args = parser.parse_args()
    config = _load(args.config)
    shards = sorted(
        path for path in args.shard_directory.iterdir() if path.is_dir()
    )
    if not shards:
        raise ValueError("no R2 shard directories found")
    metrics = pd.concat(
        [
            pd.read_csv(path / "metrics.csv", keep_default_na=False)
            for path in shards
        ],
        ignore_index=True,
    )
    controls = pd.concat(
        [
            pd.read_csv(path / "controls.csv", keep_default_na=False)
            for path in shards
        ],
        ignore_index=True,
    )
    for column in metrics.columns:
        if column not in {
            "world",
            "world_type",
            "view",
            "arm",
            "rcca_refused",
            "rcca_refusal_reasons",
        }:
            metrics[column] = pd.to_numeric(metrics[column], errors="raise")
    metrics["rcca_refused"] = (
        metrics["rcca_refused"].astype(str).str.lower().eq("true")
    )
    controls["repetition"] = pd.to_numeric(controls["repetition"])
    controls["value"] = pd.to_numeric(controls["value"])
    controls["passed"] = controls["passed"].astype(str).str.lower().eq("true")
    _validate(metrics, controls, config=config)
    decision = _decision(metrics, controls, config=config)

    metric_keys = [
        "repetition",
        "world_type",
        "world",
        "view",
        "arm",
    ]
    control_keys = ["repetition", "control", "world"]
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.sort_values(metric_keys).to_csv(
        output / "metrics.csv",
        index=False,
    )
    controls.sort_values(control_keys).to_csv(
        output / "controls.csv",
        index=False,
    )
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, metrics), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
