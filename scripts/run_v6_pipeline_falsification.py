#!/usr/bin/env python3
"""Run the leakage-safe SIM-P0..P6 pipeline falsification battery."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from suica_sim.pipeline import load_pipeline_config, run_pipeline, write_pipeline_reports  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_pipeline_falsification")
    args = parser.parse_args()
    path = args.config or ROOT / f"configs/sim_v6/pipeline_{args.profile}.json"
    config, digest = load_pipeline_config(path)
    if config["profile"] != args.profile: parser.error("config profile does not match")
    result = run_pipeline(config, digest)
    print(json.dumps({"gates": result["gates"], "diagnostic_only": result["diagnostic_only"],
                      "outputs": write_pipeline_reports(result, args.output_dir)}, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
