#!/usr/bin/env python3
"""Fit M3-V4 estimators from observations only in a separate process."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_confirmation_common import (  # noqa: E402
    canonical_json,
    derive_seed,
    load_sealed_config,
    sha256_bytes,
    sha256_file,
    validate_randomness_record,
    verify_sealed_code,
)
from suica_core.m3_cross_family_contracts import (  # noqa: E402
    M3CrossFamilyEstimate,
    observed_from_payload,
)
from suica_core.m3_cross_family_estimator import fit_m3_cross_family  # noqa: E402


def _estimate_payload(estimate: M3CrossFamilyEstimate) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {
        "metadata_json": np.asarray(
            canonical_json({
                "heldout_metrics": estimate.heldout_metrics,
                "refusals": estimate.refusals,
            }),
            dtype=np.str_,
        ),
    }
    for family, values in estimate.train_features.items():
        payload[f"train__{family}"] = np.asarray(values, dtype=np.float32)
    for family, values in estimate.test_features.items():
        payload[f"test__{family}"] = np.asarray(values, dtype=np.float32)
    for metric, values in estimate.heldout_by_author.items():
        payload[f"heldout__{metric}"] = np.asarray(values, dtype=np.float64)
    return payload


def _fit_one(
    observation_path: str,
    prediction_path: str,
    estimator_seed: int,
    estimator_config: dict[str, Any],
) -> dict[str, str]:
    with np.load(observation_path, allow_pickle=False) as payload:
        observed = observed_from_payload(payload)
    estimate = fit_m3_cross_family(
        observed,
        seed=estimator_seed,
        **estimator_config,
    )
    np.savez_compressed(prediction_path, **_estimate_payload(estimate))
    return {
        "task_id": Path(observation_path).stem,
        "prediction_sha256": sha256_file(prediction_path),
    }


def fit_all(output_dir: Path, max_workers: int) -> dict[str, Any]:
    """Fit exactly the generated observation registry without truth access."""
    config, seal = load_sealed_config(output_dir)
    verify_sealed_code(seal, ROOT)
    generation_path = output_dir / "generation_sealed.json"
    if not generation_path.is_file():
        raise FileNotFoundError("generation_sealed.json is missing")
    if (output_dir / "predictions_sealed.json").exists():
        raise RuntimeError("predictions are already sealed")
    generation = json.loads(generation_path.read_text(encoding="utf-8"))
    randomness_path = output_dir / "randomness.record.json"
    if sha256_file(randomness_path) != generation["randomness_record_sha256"]:
        raise RuntimeError("randomness record hash mismatch")
    randomness_record = json.loads(
        randomness_path.read_text(encoding="utf-8")
    )
    randomness = validate_randomness_record(randomness_record)
    records = list(generation["records"])
    expected_ids = {str(record["task_id"]) for record in records}
    observation_dir = output_dir / "observations"
    actual_ids = {path.stem for path in observation_dir.glob("*.npz")}
    if actual_ids != expected_ids:
        raise RuntimeError("observation task set is incomplete or contains extras")
    for record in records:
        path = observation_dir / f"{record['task_id']}.npz"
        if sha256_file(path) != record["observation_sha256"]:
            raise RuntimeError(f"observation hash mismatch: {record['task_id']}")

    prediction_dir = output_dir / "predictions"
    prediction_dir.mkdir()
    completed: list[dict[str, str]] = []
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = []
        for record in records:
            task_id = str(record["task_id"])
            futures.append(pool.submit(
                _fit_one,
                str(observation_dir / f"{task_id}.npz"),
                str(prediction_dir / f"{task_id}.npz"),
                derive_seed(randomness, "estimator", task_id),
                dict(config["estimator"]),
            ))
        for future in as_completed(futures):
            completed.append(future.result())
    completed.sort(key=lambda row: row["task_id"])
    if {row["task_id"] for row in completed} != expected_ids:
        raise RuntimeError("prediction task set is incomplete")
    manifest = {
        "version": "suica-m3-v4-prediction-seal-1",
        "created_utc": datetime.now(UTC).isoformat(),
        "task_count": len(completed),
        "opaque_task_ids_sha256": sha256_bytes(canonical_json(
            sorted(expected_ids)
        ).encode()),
        "records": completed,
        "truth_opened": False,
    }
    (output_dir / "predictions_sealed.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "M3_V4_PREDICTIONS_SEALED",
        "task_count": len(completed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(
        fit_all(args.output_dir, args.max_workers),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
