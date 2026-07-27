#!/usr/bin/env python3
"""Generate observations and encrypted truth in a generator-only process."""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_confirmation_common import (  # noqa: E402
    canonical_json,
    derive_seed,
    load_sealed_config,
    logical_task_labels,
    opaque_task_id,
    sha256_bytes,
    sha256_file,
    validate_randomness_record,
    verify_sealed_code,
)
from suica_core.m3_cross_family_contracts import observed_to_payload  # noqa: E402
from suica_core.m3_cross_family_generator import (  # noqa: E402
    M3CrossFamilySpec,
    generate_m3_cross_family_world,
)


def _truth_bytes(truth: Any, metadata: dict[str, Any]) -> bytes:
    payload: dict[str, np.ndarray] = {
        "metadata_json": np.asarray(
            canonical_json({
                **metadata,
                "world": truth.world,
                "active_targets": truth.active_targets,
                "exact_alias": truth.exact_alias,
                "validity": truth.validity,
            }),
            dtype=np.str_,
        ),
    }
    for target, values in truth.author_parameters.items():
        payload[f"parameter__{target}"] = np.asarray(values, dtype=np.float64)
    for target, values in truth.oracle_profiles.items():
        payload[f"oracle__{target}"] = np.asarray(values, dtype=np.float64)
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **payload)
    return buffer.getvalue()


def _read_key(path: Path) -> bytes:
    payload = path.read_bytes()
    try:
        decoded = bytes.fromhex(payload.decode("ascii").strip())
    except (UnicodeDecodeError, ValueError):
        decoded = payload
    if len(decoded) != 32:
        raise ValueError("truth key must contain exactly 32 bytes")
    return decoded


def _tasks(
    config: dict[str, Any],
    randomness: bytes,
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world, declaration in config["worlds"].items():
            declarations = [(f"{world}::main::{repetition}", None)]
            declarations.extend(
                (
                    f"{world}::knockout::{target}::{repetition}",
                    str(target),
                )
                for target in declaration.get("knockout_targets", [])
            )
            for label, target in declarations:
                spec = dict(config["specs"][declaration["spec"]])
                spec["events"] = int(declaration["events"])
                tasks.append({
                    "logical_label": label,
                    "task_id": opaque_task_id(randomness, label),
                    "world": world,
                    "target": target,
                    "repetition": repetition,
                    "spec": spec,
                    "generator_seed": derive_seed(
                        randomness,
                        "generator",
                        label,
                    ),
                })
    return sorted(tasks, key=lambda task: str(task["task_id"]))


def generate(
    output_dir: Path,
    randomness_path: Path,
    truth_key_path: Path,
) -> dict[str, Any]:
    """Generate every sealed task without invoking the estimator."""
    config, seal = load_sealed_config(output_dir)
    verify_sealed_code(seal, ROOT)
    if (output_dir / "generation_sealed.json").exists():
        raise RuntimeError("generation is already sealed")
    randomness_record = json.loads(
        randomness_path.read_text(encoding="utf-8")
    )
    randomness = validate_randomness_record(randomness_record)
    key = _read_key(truth_key_path)
    observations = output_dir / "observations"
    lockbox = output_dir / "truth_lockbox"
    observations.mkdir()
    lockbox.mkdir()
    tasks = _tasks(config, randomness)
    if len(tasks) != int(seal["logical_task_count"]):
        raise RuntimeError("generated task count differs from the sealed registry")
    if sorted(task["logical_label"] for task in tasks) != logical_task_labels(
        config
    ):
        raise RuntimeError("generated task labels differ from the sealed registry")

    records = []
    aes = AESGCM(key)
    for task in tasks:
        observed, truth = generate_m3_cross_family_world(
            world=str(task["world"]),
            spec=M3CrossFamilySpec(**task["spec"]),
            seed=int(task["generator_seed"]),
            disabled=(
                frozenset()
                if task["target"] is None
                else frozenset({str(task["target"])})
            ),
        )
        observation_path = observations / f"{task['task_id']}.npz"
        np.savez_compressed(observation_path, **observed_to_payload(observed))
        plaintext = _truth_bytes(
            truth,
            {
                "logical_label": task["logical_label"],
                "task_id": task["task_id"],
                "task_kind": (
                    "main" if task["target"] is None else "knockout"
                ),
                "score_target": task["target"],
                "repetition": task["repetition"],
                "generator_seed": task["generator_seed"],
                "spec": task["spec"],
            },
        )
        nonce = os.urandom(12)
        aad = str(task["task_id"]).encode("ascii")
        encrypted = nonce + aes.encrypt(nonce, plaintext, aad)
        truth_path = lockbox / f"{task['task_id']}.aesgcm"
        truth_path.write_bytes(encrypted)
        records.append({
            "task_id": task["task_id"],
            "observation_sha256": sha256_file(observation_path),
            "encrypted_truth_sha256": sha256_file(truth_path),
        })

    copied_randomness = output_dir / "randomness.record.json"
    copied_randomness.write_text(
        json.dumps(randomness_record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "version": "suica-m3-v4-generator-seal-1",
        "created_utc": datetime.now(UTC).isoformat(),
        "task_count": len(records),
        "opaque_task_ids_sha256": sha256_bytes(canonical_json(
            sorted(record["task_id"] for record in records)
        ).encode()),
        "randomness_record_sha256": sha256_file(copied_randomness),
        "truth_key_sha256": sha256_bytes(key),
        "records": records,
    }
    (output_dir / "generation_sealed.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "M3_V4_GENERATION_SEALED",
        "task_count": len(records),
        "truth_key_sha256": manifest["truth_key_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--randomness-record", type=Path, required=True)
    parser.add_argument("--truth-key-file", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        generate(
            args.output_dir,
            args.randomness_record,
            args.truth_key_file,
        ),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
