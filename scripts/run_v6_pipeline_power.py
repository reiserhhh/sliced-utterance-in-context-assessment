#!/usr/bin/env python3
"""Run repeated-alternative power estimation for P0-P6."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.pipeline_power import run_power_assay, write_power_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--reference", default="results/v6_pipeline_falsification/full/v6_pipeline_falsification_full.json")
    parser.add_argument("--output-dir", default="results/v6_pipeline_power")
    args = parser.parse_args()
    cfg_path = ROOT / f"configs/sim_v6/power_{args.profile}.json"
    raw = cfg_path.read_bytes(); config = json.loads(raw)
    reference = json.loads((ROOT / args.reference).read_text())
    result = run_power_assay(config, hashlib.sha256(raw).hexdigest(), reference)
    output = write_power_report(result, ROOT / args.output_dir)
    print(json.dumps({"gates": result["gates"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
