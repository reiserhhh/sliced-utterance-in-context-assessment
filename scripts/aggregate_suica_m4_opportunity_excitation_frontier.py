#!/usr/bin/env python3
"""Aggregate deterministic M4-C.3.3 repetition shards."""
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

from scripts.run_suica_m4_opportunity_excitation_frontier import (  # noqa: E402
    _decision,
    _report,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            ROOT
            / "configs"
            / "m4_opportunity_excitation_frontier.json"
        ),
    )
    parser.add_argument(
        "--shard-directory",
        type=Path,
        default=(
            ROOT
            / "results"
            / "m4_opportunity_excitation_frontier_shards"
        ),
    )
    args = parser.parse_args()
    config = _load(args.config)
    shard_paths = sorted(
        path
        for path in args.shard_directory.iterdir()
        if path.is_dir()
    )
    if not shard_paths:
        raise ValueError("no C3.3 shard directories found")
    metrics = pd.concat(
        [
            pd.read_csv(
                path / "metrics.csv",
                keep_default_na=False,
            )
            for path in shard_paths
        ],
        ignore_index=True,
    )
    aliases = pd.concat(
        [pd.read_csv(path / "alias_audit.csv") for path in shard_paths],
        ignore_index=True,
    )
    expected = set(range(int(config["repetitions"])))
    observed = set(metrics["repetition"].astype(int).unique())
    if observed != expected:
        raise ValueError(
            f"repetition coverage mismatch: {sorted(observed)}"
        )
    duplicate_key = [
        "repetition",
        "world",
        "world_type",
        "view",
        "intervention",
        "k",
    ]
    if metrics.duplicated(duplicate_key).any():
        raise ValueError("duplicate C3.3 metric cells across shards")
    if set(aliases["repetition"].astype(int)) != expected:
        raise ValueError("alias repetition coverage mismatch")
    gauge_difference = max(
        float(_load(path / "decision.json")["diagnostics"][
            "gauge_max_difference"
        ])
        for path in shard_paths
    )
    decision = _decision(
        metrics,
        aliases,
        gauge_difference=gauge_difference,
        config=config,
    )
    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.sort_values(duplicate_key).to_csv(
        output / "metrics.csv",
        index=False,
    )
    aliases.sort_values("repetition").to_csv(
        output / "alias_audit.csv",
        index=False,
    )
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / config["report_path"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _report(decision, metrics, config),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
