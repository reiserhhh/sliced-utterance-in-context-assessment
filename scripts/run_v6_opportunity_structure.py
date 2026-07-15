#!/usr/bin/env python3
"""Run V6 opportunity-conditioned author-operator simulations."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.opportunity_structure import run_opportunity_structure, write_opportunity_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--output-dir", default="results/v6_opportunity_structure")
    args = parser.parse_args()
    path = ROOT / f"configs/sim_v6/opportunity_{args.profile}.json"
    raw = path.read_bytes(); config = json.loads(raw)
    result = run_opportunity_structure(config, hashlib.sha256(raw).hexdigest())
    output = write_opportunity_report(result, ROOT / args.output_dir)
    print(json.dumps({"gates": result["gates"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
