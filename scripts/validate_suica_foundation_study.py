#!/usr/bin/env python
"""Validate a SUICA foundation study contract before data or compute access."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.foundation_contracts import (  # noqa: E402
    strict_json_loads,
    validate_foundation_study,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        default=str(ROOT / "configs" / "suica_foundation_study.template.json"),
    )
    parser.add_argument("--output", default="", help="Optional JSON decision path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = strict_json_loads(Path(args.contract).read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "REFUSE_EXPERIMENT_START",
            "study_id": "",
            "maximum_licensed_layer": "",
            "required_edges": [],
            "bounded_openings": [],
            "promotion_blocked": True,
            "refusal_codes": ["INVALID_JSON"],
            "errors": [{"code": "INVALID_JSON", "detail": str(exc)}],
            "warnings": [],
        }
    else:
        result = validate_foundation_study(payload)

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] != "REFUSE_EXPERIMENT_START" else 2


if __name__ == "__main__":
    raise SystemExit(main())
