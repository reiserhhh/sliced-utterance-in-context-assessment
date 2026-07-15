#!/usr/bin/env python3
"""Verify the portable SUICA v0.2.0 lockbox after clone or checkout."""
from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_release import verify_lockbox_manifest, verify_release_identity  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content-only",
        action="store_true",
        help="Verify tracked hashes without requiring the release tag at HEAD.",
    )
    args = parser.parse_args()
    result = verify_lockbox_manifest(
        ROOT / "release" / "v0.2.0" / "LOCKBOX_MANIFEST.json",
        repository_root=ROOT,
    )
    identity = None if args.content_only else verify_release_identity(
        ROOT,
        ROOT / "release" / "v0.2.0" / "LOCKBOX_MANIFEST.json",
        tag="v0.2.0",
    )
    payload = {"content": result, "identity": identity}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    passed = result["status"] == "LOCKBOX_MANIFEST_PASS"
    if identity is not None:
        passed = passed and identity["status"] == "RELEASE_IDENTITY_PASS"
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
