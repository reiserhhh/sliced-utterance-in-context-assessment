#!/usr/bin/env python3
"""Run P7--P10 extended V6 simulations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from suica_sim.extended_features import load_extended_config, run_extended, write_extended_reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v6_extended_features")
    args = parser.parse_args()
    path = args.config or ROOT / "configs" / "sim_v6" / f"extended_{args.profile}.json"
    config, digest = load_extended_config(path)
    if config["profile"] != args.profile: parser.error("config profile does not match --profile")
    result = run_extended(config, digest)
    print(json.dumps({"rows": len(result["rows"]), "gates": result["gates"],
                      "outputs": write_extended_reports(result, args.output_dir)}, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
