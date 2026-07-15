"""Small reproducibility primitives shared by frozen SUICA V7 experiments.

The helpers intentionally know nothing about text or psychological labels.
They make an experiment artifact inspectable: a result can be replayed from
its persisted runtime, and its files can be checked against a manifest.
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: str | Path) -> str:
    """Return a streaming SHA-256 digest for one artifact."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_inventory(
    root: str | Path,
    *,
    exclude_relative_paths: Iterable[str] = (),
) -> dict[str, Any]:
    """Create a stable artifact inventory without embedding raw artifact data."""
    base = Path(root)
    excluded = {str(Path(value)) for value in exclude_relative_paths}
    records: list[dict[str, Any]] = []
    for path in sorted(candidate for candidate in base.rglob("*") if candidate.is_file()):
        relative = str(path.relative_to(base))
        if relative in excluded or path.name.startswith("._"):
            continue
        records.append({
            "path": relative,
            "bytes": int(path.stat().st_size),
            "sha256": sha256_file(path),
        })
    return {
        "created_utc": datetime.now(UTC).isoformat(),
        "root": str(base),
        "n_files": len(records),
        "files": records,
    }


def write_artifact_inventory(
    root: str | Path,
    path: str | Path,
    *,
    exclude_relative_paths: Iterable[str] = (),
) -> dict[str, Any]:
    """Write and return a deterministic manifest for all persisted artifacts."""
    destination = Path(path)
    base = Path(root)
    exclusions = set(exclude_relative_paths)
    try:
        exclusions.add(str(destination.relative_to(base)))
    except ValueError:
        pass
    payload = artifact_inventory(base, exclude_relative_paths=exclusions)
    payload["root"] = "."
    payload["root_resolution"] = "inventory_parent"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def verify_artifact_inventory(path: str | Path) -> dict[str, Any]:
    """Verify a saved inventory and return explicit missing/mismatched rows."""
    inventory_path = Path(path)
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    recorded_root = Path(str(payload["root"]))
    base = recorded_root if recorded_root.is_absolute() else (inventory_path.parent / recorded_root).resolve()
    failures: list[dict[str, str]] = []
    for record in payload.get("files", []):
        candidate = base / str(record["path"])
        if not candidate.exists():
            failures.append({"path": str(record["path"]), "reason": "missing"})
        elif sha256_file(candidate) != str(record["sha256"]):
            failures.append({"path": str(record["path"]), "reason": "sha256_mismatch"})
    return {
        "inventory": str(inventory_path),
        "n_expected": int(payload.get("n_files", len(payload.get("files", [])))),
        "n_failures": len(failures),
        "failures": failures,
        "status": "INVENTORY_PASS" if not failures else "INVENTORY_FAIL",
    }


def pseudonymize_identifiers(identifiers: Iterable[object], *, secret: str, prefix: str = "u") -> list[str]:
    """Return stable HMAC pseudonyms without persisting raw identifiers."""
    if not secret:
        raise ValueError("A non-empty pseudonymization secret is required.")
    return [
        f"{prefix}_{hmac.new(secret.encode('utf-8'), str(value).encode('utf-8'), hashlib.sha256).hexdigest()[:20]}"
        for value in identifiers
    ]


def _path_record(path: str | Path, *, repository_root: str | Path | None = None) -> dict[str, Any]:
    """Record one required file without embedding its content in a manifest."""
    candidate = Path(path).resolve()
    if not candidate.is_file():
        raise FileNotFoundError(f"Run-manifest input is missing or not a file: {candidate}")
    record_path = str(candidate)
    path_base = "absolute_legacy"
    if repository_root is not None:
        root = Path(repository_root).resolve()
        try:
            record_path = str(candidate.relative_to(root))
            path_base = "repository_root"
        except ValueError:
            pass
    return {
        "path": record_path,
        "path_base": path_base,
        "bytes": int(candidate.stat().st_size),
        "sha256": sha256_file(candidate),
    }


def _repository_root_for_manifest(manifest_path: Path) -> Path:
    """Find the checkout root for portable repository-relative records."""
    for parent in (manifest_path.parent, *manifest_path.parents):
        if (parent / ".git").exists():
            return parent.resolve()
    return manifest_path.parent.resolve()


def _record_path(record: dict[str, Any], manifest_path: Path) -> Path:
    candidate = Path(str(record.get("path", "")))
    if candidate.is_absolute() or record.get("path_base") == "absolute_legacy":
        return candidate
    return (_repository_root_for_manifest(manifest_path) / candidate).resolve()


def git_revision(root: str | Path) -> dict[str, Any]:
    """Return a non-fatal Git revision snapshot for a reproducibility record."""
    base = Path(root).resolve()
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=base, check=True, capture_output=True, text=True
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=base, check=True, capture_output=True, text=True
        ).stdout.strip())
        return {"status": "GIT_AVAILABLE", "revision": revision, "dirty": dirty}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"status": "GIT_UNAVAILABLE", "revision": None, "dirty": None}


def runtime_environment(packages: Iterable[str] = ("numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "pyarrow", "joblib")) -> dict[str, Any]:
    """Capture Python and selected package versions used for one V7 run."""
    versions: dict[str, str | None] = {}
    for package in packages:
        try:
            versions[str(package)] = importlib.metadata.version(str(package))
        except importlib.metadata.PackageNotFoundError:
            versions[str(package)] = None
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": versions,
    }


def build_run_manifest(
    *,
    repository_root: str | Path,
    input_paths: Iterable[str | Path],
    config_path: str | Path,
    code_paths: Iterable[str | Path],
    estimand_id: str,
    external_labels_read: bool,
    raw_identifiers_persisted: bool,
    pseudonym_salt_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Build a V7.3 provenance manifest before a numerical analysis begins."""
    if not estimand_id:
        raise ValueError("A declared estimand_id is required for every V7.3 run.")
    if raw_identifiers_persisted and not pseudonym_salt_fingerprint:
        raise ValueError("Raw identifier persistence requires an explicit privacy exception fingerprint.")
    return {
        "manifest_version": "v7.3-provenance-1",
        "created_utc": datetime.now(UTC).isoformat(),
        "estimand_id": str(estimand_id),
        "repository": git_revision(repository_root),
        "path_policy": "repository_relative_when_inside_checkout",
        "inputs": [_path_record(path, repository_root=repository_root) for path in input_paths],
        "config": _path_record(config_path, repository_root=repository_root),
        "code": [_path_record(path, repository_root=repository_root) for path in code_paths],
        "environment": runtime_environment(),
        "external_labels_read": bool(external_labels_read),
        "privacy": {
            "raw_identifiers_persisted": bool(raw_identifiers_persisted),
            "pseudonym_salt_fingerprint": pseudonym_salt_fingerprint,
        },
        "claim_boundary": "Provenance record only. It does not validate an estimator or a psychological interpretation.",
    }


def write_run_manifest(path: str | Path, **kwargs: Any) -> dict[str, Any]:
    """Build and save one provenance manifest."""
    payload = build_run_manifest(**kwargs)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def verify_run_manifest(path: str | Path) -> dict[str, Any]:
    """Re-hash all declared input/config/code files in a saved run manifest."""
    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    for group in ("inputs", "code"):
        for record in payload.get(group, []):
            candidate = _record_path(record, manifest_path)
            if not candidate.is_file():
                failures.append({"group": group, "path": str(candidate), "reason": "missing"})
            elif sha256_file(candidate) != str(record["sha256"]):
                failures.append({"group": group, "path": str(candidate), "reason": "sha256_mismatch"})
    config = payload.get("config", {})
    if config:
        candidate = _record_path(config, manifest_path)
        if not candidate.is_file():
            failures.append({"group": "config", "path": str(candidate), "reason": "missing"})
        elif sha256_file(candidate) != str(config.get("sha256")):
            failures.append({"group": "config", "path": str(candidate), "reason": "sha256_mismatch"})
    return {
        "manifest": str(manifest_path),
        "estimand_id": payload.get("estimand_id"),
        "n_failures": len(failures),
        "failures": failures,
        "status": "RUN_MANIFEST_PASS" if not failures else "RUN_MANIFEST_FAIL",
    }


def append_ledger_event(path: str | Path, event: dict[str, Any]) -> dict[str, Any]:
    """Append one compact, schema-agnostic event to a V7 JSONL evidence ledger."""
    if not isinstance(event, dict) or not event:
        raise ValueError("A non-empty ledger event mapping is required.")
    payload = {"recorded_utc": datetime.now(UTC).isoformat(), **event}
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return payload
