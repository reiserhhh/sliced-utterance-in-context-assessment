#!/usr/bin/env python3
"""Aggregate deterministic M4-C.3.4 repetition shards."""
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

from scripts.run_suica_m4_creation_residual_attribution import (  # noqa: E402
    _decision,
    _report,
)

METRIC_NUMERIC_COLUMNS = (
    "repetition",
    "c",
    "s",
    "p",
    "geometry",
    "baseline_geometry",
    "oracle_swap_geometry",
    "oracle_headroom",
    "geometry_gain",
    "recovered_headroom",
    "evaluation_loss",
    "comparable_hazard_loss",
    "joint_information_minimum",
    "joint_information_full_rank_coverage",
    "source_at_risk_coverage",
    "common_shift_distance_error",
)
DECOMPOSITION_NUMERIC_COLUMNS = (
    "repetition",
    "baseline_geometry",
    "full_geometry",
    "oracle_swap_geometry",
    "oracle_headroom",
    "full_gain",
    "full_recovered_headroom",
    "observation_main_effect",
    "mobius_C",
    "mobius_S",
    "mobius_CS",
    "mobius_P",
    "mobius_CP",
    "mobius_SP",
    "mobius_CSP",
    "shapley_C",
    "shapley_S",
    "shapley_P",
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _coerce(
    frame: pd.DataFrame,
    columns: tuple[str, ...],
) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        output[column] = pd.to_numeric(output[column], errors="coerce")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_creation_residual_attribution.json",
    )
    parser.add_argument(
        "--shard-directory",
        type=Path,
        default=(
            ROOT
            / "results"
            / "m4_creation_residual_attribution_shards"
        ),
    )
    args = parser.parse_args()
    config = _load(args.config)
    shards = sorted(
        path for path in args.shard_directory.iterdir() if path.is_dir()
    )
    if not shards:
        raise ValueError("no C3.4 shard directories found")

    metrics = pd.concat(
        [
            pd.read_csv(path / "metrics.csv", keep_default_na=False)
            for path in shards
        ],
        ignore_index=True,
    )
    decomposition = pd.concat(
        [
            pd.read_csv(path / "decomposition.csv", keep_default_na=False)
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
    aliases = pd.concat(
        [
            pd.read_csv(path / "alias_audit.csv", keep_default_na=False)
            for path in shards
        ],
        ignore_index=True,
    )
    metrics = _coerce(metrics, METRIC_NUMERIC_COLUMNS)
    decomposition = _coerce(
        decomposition,
        DECOMPOSITION_NUMERIC_COLUMNS,
    )
    controls = _coerce(
        controls,
        ("repetition", "permutation_gain"),
    )
    aliases = _coerce(
        aliases,
        (
            "repetition",
            "truth_open_alias_information_loss",
            "alias_oracle_skill",
            "alias_skill_gap",
            "alias_retained_ratio",
            "alias_gap_lcb",
        ),
    )

    expected = set(range(int(config["repetitions"])))
    observed = set(metrics["repetition"].astype(int).unique())
    if observed != expected:
        raise ValueError(
            f"repetition coverage mismatch: {sorted(observed)}"
        )
    keys = {
        "metrics": [
            "repetition",
            "world",
            "world_type",
            "view",
            "c",
            "s",
            "p",
        ],
        "decomposition": [
            "repetition",
            "world",
            "world_type",
            "view",
        ],
        "controls": [
            "repetition",
            "world",
            "world_type",
            "view",
        ],
    }
    for name, frame in (
        ("metrics", metrics),
        ("decomposition", decomposition),
        ("controls", controls),
    ):
        if frame.duplicated(keys[name]).any():
            raise ValueError(f"duplicate C3.4 {name} cells across shards")
    if set(aliases["repetition"].astype(int)) != expected:
        raise ValueError("alias repetition coverage mismatch")
    gauge_difference = max(
        float(
            _load(path / "decision.json")["diagnostics"][
                "gauge_max_difference"
            ]
        )
        for path in shards
    )
    decision = _decision(
        metrics,
        decomposition,
        controls[
            (controls["view"] == "test")
            & (controls["world_type"] == "main")
        ],
        aliases,
        gauge_difference=gauge_difference,
        config=config,
    )

    output = ROOT / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    metrics.sort_values(keys["metrics"]).to_csv(
        output / "metrics.csv",
        index=False,
    )
    decomposition.sort_values(keys["decomposition"]).to_csv(
        output / "decomposition.csv",
        index=False,
    )
    controls.sort_values(keys["controls"]).to_csv(
        output / "controls.csv",
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
        _report(decision, metrics, decomposition),
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
