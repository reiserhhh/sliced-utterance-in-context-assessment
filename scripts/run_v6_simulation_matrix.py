#!/usr/bin/env python3
"""Run the configured SUICA V6 W0-W8 simulation matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim import load_config, run_matrix, write_reports  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v6_simulation_matrix")
    args = parser.parse_args()
    config_path = args.config or ROOT / "configs" / "sim_v6" / f"{args.profile}.json"
    config, digest = load_config(config_path)
    if config["profile"] != args.profile:
        parser.error("config profile does not match --profile")
    result = run_matrix(config, digest)
    paths = write_reports(result, args.output_dir)
    print(json.dumps({"rows": len(result["rows"]), "outputs": paths}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
