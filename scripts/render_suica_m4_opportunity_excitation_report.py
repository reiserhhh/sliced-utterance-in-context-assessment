#!/usr/bin/env python3
"""Render the C3.3 report from frozen aggregate artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_opportunity_excitation_frontier import (  # noqa: E402
    _report,
)

REPORT_NUMERIC_COLUMNS = (
    "fisher_minimum_information",
    "baseline_geometry",
    "fisher_geometry",
    "fisher_gain",
    "recovered_headroom",
    "hazard_relative_degradation",
)


def coerce_report_numeric_columns(metrics: pd.DataFrame) -> pd.DataFrame:
    """Restore numeric columns after mixed null-world CSV serialization."""
    coerced = metrics.copy()
    for column in REPORT_NUMERIC_COLUMNS:
        coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_opportunity_excitation_frontier.json",
    )
    args = parser.parse_args()
    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    output = ROOT / config["output_directory"]
    with (output / "decision.json").open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    metrics = pd.read_csv(output / "metrics.csv", keep_default_na=False)
    metrics = coerce_report_numeric_columns(metrics)
    report_path = ROOT / config["report_path"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _report(decision, metrics, config),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
