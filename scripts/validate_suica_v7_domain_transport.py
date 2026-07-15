#!/usr/bin/env python3
"""Validate a future SUICA V7 domain/language transport manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_domain_transport import validate_domain_transport_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate_domain_transport_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {
        "DOMAIN_TRANSPORT_LOCAL_REFERENCE_READY",
        "PAIRED_ALIGNMENT_PROTOCOL_READY_NOT_YET_EVALUATED",
        "PAIRED_ALIGNMENT_HELDOUT_SUPPORTED",
        "PRETRAINED_ALIGNMENT_INDEPENDENTLY_VALIDATED",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
