#!/usr/bin/env python
"""Validate a SUICA V8 assessment contract before model or data access."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v8_contracts import strict_json_loads, validate_assessment_contract  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        default=str(ROOT / "configs" / "v8_assessment_contract.template.json"),
    )
    parser.add_argument(
        "--expected-active-sha256",
        default="",
        help="Trusted active-bundle hash supplied outside the candidate contract.",
    )
    parser.add_argument(
        "--trusted-authorities",
        default="",
        help="External JSON registry of authority IDs, Ed25519 public keys, and purposes.",
    )
    parser.add_argument("--output", default="", help="Optional JSON decision path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = strict_json_loads(Path(args.contract).read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "REFUSE_V8_ASSESSMENT_CONTRACT",
            "contract_id": "",
            "measurement_components": [],
            "refusal_codes": ["INVALID_JSON"],
            "errors": [{"code": "INVALID_JSON", "detail": str(exc)}],
            "claim_boundary": "",
        }
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        print(rendered, end="")
        return 2
    authorities = {}
    if args.trusted_authorities:
        try:
            authorities = strict_json_loads(
                Path(args.trusted_authorities).read_text(encoding="utf-8")
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            result = {
                "status": "REFUSE_V8_ASSESSMENT_CONTRACT",
                "contract_id": "",
                "measurement_components": [],
                "refusal_codes": ["INVALID_AUTHORITY_REGISTRY"],
                "errors": [{"code": "INVALID_AUTHORITY_REGISTRY", "detail": str(exc)}],
                "claim_boundary": "",
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 2
    result = validate_assessment_contract(
        payload,
        base_dir=ROOT,
        expected_active_sha256=args.expected_active_sha256,
        trusted_authorities=authorities,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "V8_ASSESSMENT_CONTRACT_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
