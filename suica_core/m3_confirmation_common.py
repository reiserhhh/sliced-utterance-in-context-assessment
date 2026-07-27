"""Shared, truth-free primitives for the M3-V4 sealed confirmation workflow."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


def canonical_json(payload: Any) -> str:
    """Return one byte-stable JSON representation."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def logical_task_labels(config: dict[str, Any]) -> list[str]:
    """Enumerate the complete preregistered task set without assigning seeds."""
    labels: list[str] = []
    for repetition in range(int(config["repetitions"])):
        for world, declaration in config["worlds"].items():
            labels.append(f"{world}::main::{repetition}")
            for target in declaration.get("knockout_targets", []):
                labels.append(
                    f"{world}::knockout::{target}::{repetition}"
                )
    return sorted(labels)


def validate_randomness_record(record: dict[str, Any]) -> bytes:
    """Validate externally recorded post-seal randomness."""
    required = {"source", "value_hex", "retrieved_utc"}
    missing = required - set(record)
    if missing:
        raise ValueError(f"randomness record is missing: {sorted(missing)}")
    try:
        value = bytes.fromhex(str(record["value_hex"]))
    except ValueError as exc:
        raise ValueError("randomness value_hex is invalid") from exc
    if len(value) < 32:
        raise ValueError("at least 256 bits of post-seal randomness are required")
    return value


def derive_seed(randomness: bytes, domain: str, label: str) -> int:
    """Derive independent domain-separated 63-bit seeds."""
    digest = hmac.new(
        randomness,
        f"{domain}::{label}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return int.from_bytes(digest[:8], "big") % (2**63 - 1)


def opaque_task_id(randomness: bytes, logical_label: str) -> str:
    digest = hmac.new(
        randomness,
        f"task::{logical_label}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t_{digest[:24]}"


def load_sealed_config(output_dir: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load only the snapshot named by the seal and verify its digest."""
    root = Path(output_dir)
    seal_path = root / "seal.json"
    if not seal_path.is_file():
        raise FileNotFoundError("seal.json is missing")
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    snapshot = root / "config.snapshot.json"
    if not snapshot.is_file():
        raise FileNotFoundError("config.snapshot.json is missing")
    if sha256_file(snapshot) != str(seal["config_snapshot_sha256"]):
        raise RuntimeError("sealed config snapshot hash mismatch")
    config = json.loads(snapshot.read_text(encoding="utf-8"))
    labels = logical_task_labels(config)
    if sha256_bytes(canonical_json(labels).encode()) != str(
        seal["logical_task_labels_sha256"]
    ):
        raise RuntimeError("sealed logical task registry mismatch")
    if len(labels) != int(seal["logical_task_count"]):
        raise RuntimeError("sealed logical task count mismatch")
    return config, seal


def verify_sealed_code(
    seal: dict[str, Any],
    repository_root: str | Path,
) -> None:
    """Verify every preregistered code artifact before each workflow phase."""
    root = Path(repository_root)
    failures = []
    for record in seal.get("code", []):
        path = root / str(record["path"])
        if not path.is_file():
            failures.append(f"missing:{record['path']}")
        elif sha256_file(path) != str(record["sha256"]):
            failures.append(f"sha256:{record['path']}")
    preflight = seal.get("preflight")
    if preflight:
        path = root / str(preflight["path"])
        if not path.is_file():
            failures.append(f"missing:{preflight['path']}")
        elif sha256_file(path) != str(preflight["sha256"]):
            failures.append(f"sha256:{preflight['path']}")
    if failures:
        raise RuntimeError(f"sealed code verification failed: {failures}")
