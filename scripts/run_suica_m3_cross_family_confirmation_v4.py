#!/usr/bin/env python3
"""Create the clean, pre-randomness artifact seal for M3-V4 confirmation."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_confirmation_common import (  # noqa: E402
    canonical_json,
    logical_task_labels,
    sha256_bytes,
    sha256_file,
)
from suica_core.v7_governance import git_revision  # noqa: E402


CODE_PATHS = (
    ROOT / "suica_core" / "m3_confirmation_common.py",
    ROOT / "suica_core" / "m3_cross_family_contracts.py",
    ROOT / "suica_core" / "m3_cross_family_generator.py",
    ROOT / "suica_core" / "m3_cross_family_estimator.py",
    ROOT / "suica_core" / "m3_cross_family_audit.py",
    ROOT / "suica_core" / "m3_cross_family_validity.py",
    Path(__file__).resolve(),
    ROOT / "scripts" / "run_suica_m3_cross_family_generate_v4.py",
    ROOT / "scripts" / "run_suica_m3_cross_family_fit_v4.py",
    ROOT / "scripts" / "run_suica_m3_cross_family_open_v4.py",
    ROOT / "tests" / "test_m3_cross_family.py",
    ROOT / "tests" / "test_m3_confirmation_v4.py",
)


def create_seal(config_path: Path, output_dir: Path) -> dict[str, object]:
    """Seal one exact config and code snapshot before external randomness."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if "root_seed" in config or "seed" in config:
        raise ValueError("formal confirmation config cannot contain a seed")
    revision = git_revision(ROOT)
    if revision.get("dirty") is not False:
        raise RuntimeError(
            "formal confirmation requires a clean committed worktree"
        )
    missing = [str(path) for path in CODE_PATHS if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"sealed code paths are missing: {missing}")
    if output_dir.exists() and any(
        path.name != ".DS_Store" for path in output_dir.iterdir()
    ):
        raise RuntimeError("seal output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = output_dir / "config.snapshot.json"
    snapshot.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    labels = logical_task_labels(config)
    preflight_record = None
    if "required_preflight" in config:
        requirement = dict(config["required_preflight"])
        preflight_path = ROOT / str(requirement["path"])
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        if preflight.get("decision") != requirement["decision"]:
            raise RuntimeError("required V4 power preflight did not pass")
        preflight_record = {
            "path": str(preflight_path.relative_to(ROOT)),
            "sha256": sha256_file(preflight_path),
            "required_decision": requirement["decision"],
        }
    seal: dict[str, object] = {
        "seal_version": "suica-m3-v4-clean-prerandomness-seal-1",
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "M3_V4_SEALED_CLEAN_AWAITING_EXTERNAL_RANDOMNESS",
        "estimand_id": config["estimand_id"],
        "repository": revision,
        "config_snapshot_sha256": sha256_file(snapshot),
        "logical_task_count": len(labels),
        "logical_task_labels_sha256": sha256_bytes(
            canonical_json(labels).encode()
        ),
        "code": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
            }
            for path in CODE_PATHS
        ],
        "randomness_attached": False,
        "truth_opened": False,
    }
    if preflight_record is not None:
        seal["preflight"] = preflight_record
    (output_dir / "seal.json").write_text(
        json.dumps(seal, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return seal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        create_seal(args.config, args.output_dir),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
