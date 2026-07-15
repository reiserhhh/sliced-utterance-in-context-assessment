#!/usr/bin/env python3
"""Verify the portable SUICA v0.2.0 lockbox after clone or checkout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_release import verify_lockbox_manifest  # noqa: E402


def main() -> None:
    result = verify_lockbox_manifest(
        ROOT / "release" / "v0.2.0" / "LOCKBOX_MANIFEST.json",
        repository_root=ROOT,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "LOCKBOX_MANIFEST_PASS" else 1)


if __name__ == "__main__":
    main()
