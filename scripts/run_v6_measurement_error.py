#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.measurement_error import run_measurement_error, write_measurement_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_measurement_error")
    args = parser.parse_args()
    cfg_path = ROOT / f"configs/sim_v6/measurement_{args.profile}.json"
    raw = cfg_path.read_bytes(); cfg = json.loads(raw)
    result = run_measurement_error(cfg, hashlib.sha256(raw).hexdigest())
    path = write_measurement_report(result, args.output_dir)
    print(json.dumps({"gates": result["gates"], "output": str(path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
