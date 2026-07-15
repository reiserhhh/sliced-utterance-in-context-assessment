#!/usr/bin/env python3
"""Reload a frozen V7 E1 runtime and verify its held-out output byte-for-byte.

This is an engineering replay audit, not a new statistical test.  It refuses
to accept an E1 directory without the persisted transforms, expected values,
and artifact inventory required to reproduce its confirmation metrics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import sha256_file, verify_artifact_inventory  # noqa: E402
from suica_core.v7_multiview import evaluate_cross_view, transform_feature_block  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse one replay audit request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e1-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def _load_feature_blocks(e1_dir: Path, runtime: dict, fixture: dict) -> dict[str, np.ndarray]:
    """Load frozen feature inputs and transform only the declared confirmation rows."""
    blocks: dict[str, np.ndarray] = {}
    confirmation_ids = [str(value) for value in fixture["confirmation_user_ids"]]
    for view in runtime["view_names"]:
        spec = fixture["feature_files"][view]
        path = Path(spec["path"])
        if not path.exists() or sha256_file(path) != str(spec["sha256"]):
            raise RuntimeError(f"REPLAY_INPUT_HASH_MISMATCH: {path}")
        frame = pd.read_csv(path)
        blocks[view] = transform_feature_block(frame, scaler=runtime["scalers"][view], user_ids=confirmation_ids)
    return blocks


def main() -> int:
    """Verify artifact hashes and recompute the frozen confirmation metrics."""
    args = parse_args()
    e1_dir = args.e1_dir.resolve()
    output = args.output or e1_dir / "replay_audit.json"
    required = [
        e1_dir / "artifact_inventory.json",
        e1_dir / "replay_fixture.json",
        e1_dir / "replay_expected.npz",
        e1_dir / "artifacts" / "multiview_runtime.joblib",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        payload = {"status": "REPLAY_REFUSE_MISSING_ARTIFACT", "missing": missing}
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    inventory = verify_artifact_inventory(e1_dir / "artifact_inventory.json")
    if inventory["status"] != "INVENTORY_PASS":
        payload = {"status": "REPLAY_REFUSE_INVENTORY_MISMATCH", **inventory}
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    fixture = json.loads((e1_dir / "replay_fixture.json").read_text(encoding="utf-8"))
    runtime = joblib.load(e1_dir / "artifacts" / "multiview_runtime.joblib")
    blocks = _load_feature_blocks(e1_dir, runtime, fixture)
    actual = evaluate_cross_view(
        blocks,
        model=runtime["final_model"],
        direct_models=runtime["direct_models"],
        permuted_models=runtime["permuted_models"],
    ).sort_values(["source_view", "target_view"], kind="stable").reset_index(drop=True)
    expected = np.load(e1_dir / "replay_expected.npz")
    expected_pairs = list(zip(expected["source_view"].astype(str), expected["target_view"].astype(str), strict=True))
    actual_pairs = list(zip(actual["source_view"].astype(str), actual["target_view"].astype(str), strict=True))
    tolerances = fixture["comparison"]
    metrics = ("consensus_global_r2", "direct_global_r2", "permuted_direct_global_r2")
    allclose = expected_pairs == actual_pairs and all(
        np.allclose(actual[column].to_numpy(float), expected[column], rtol=float(tolerances["rtol"]), atol=float(tolerances["atol"]), equal_nan=True)
        for column in metrics
    )
    payload = {
        "status": "REPLAY_PASS" if allclose else "REPLAY_FAIL",
        "inventory_status": inventory["status"],
        "n_edges": len(actual),
        "rtol": float(tolerances["rtol"]),
        "atol": float(tolerances["atol"]),
        "pair_order_matches": expected_pairs == actual_pairs,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if allclose else 1


if __name__ == "__main__":
    raise SystemExit(main())
