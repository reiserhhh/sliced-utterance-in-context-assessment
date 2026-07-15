#!/usr/bin/env python3
"""Validate a declared V7 estimand registry before an analysis is run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_estimand import load_estimand_registry  # noqa: E402


def main() -> int:
    """Write a machine-readable preflight result and return a refusal exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = load_estimand_registry(args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ESTIMAND_REGISTRY_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
