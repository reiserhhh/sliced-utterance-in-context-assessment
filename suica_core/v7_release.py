"""Portable release-lockbox primitives for the SUICA V7 technical core."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of one file without loading it all at once."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_lockbox_manifest(
    repository_root: str | Path,
    relative_paths: Iterable[str | Path],
    *,
    release_version: str = "0.2.0",
) -> dict[str, Any]:
    """Build a deterministic manifest using repository-relative paths only."""
    root = Path(repository_root).resolve()
    records: list[dict[str, Any]] = []
    for relative in sorted({str(Path(value)) for value in relative_paths}):
        candidate = (root / relative).resolve()
        if root not in candidate.parents:
            raise ValueError(f"Lockbox path escapes repository: {relative}")
        if not candidate.is_file():
            raise FileNotFoundError(f"Lockbox file missing: {relative}")
        records.append({
            "path": relative,
            "bytes": int(candidate.stat().st_size),
            "sha256": sha256_file(candidate),
        })
    return {
        "schema_version": "suica-v7-release-lockbox-1",
        "release_version": release_version,
        "status": "V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES",
        "highest_supported_claim": "OPERATOR_INDEXED_RELATIVE_TEXT_GEOMETRY_WITHIN_DECLARED_DOMAIN",
        "n_files": len(records),
        "files": records,
        "claim_boundary": (
            "This manifest seals code, protocols, schemas, tests, and deidentified aggregate evidence. "
            "It does not establish personality factors, reliability, clinical validity, universal "
            "language invariance, complete out-of-domain detection, or market prediction."
        ),
    }


def verify_lockbox_manifest(
    manifest_path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> dict[str, Any]:
    """Verify every repository-relative hash in a release-lockbox manifest."""
    path = Path(manifest_path).resolve()
    root = Path(repository_root).resolve() if repository_root else path.parents[2]
    payload = json.loads(path.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    for record in payload.get("files", []):
        relative = str(record.get("path", ""))
        candidate = (root / relative).resolve()
        if root not in candidate.parents:
            failures.append({"path": relative, "reason": "path_escapes_repository"})
        elif not candidate.is_file():
            failures.append({"path": relative, "reason": "missing"})
        elif sha256_file(candidate) != str(record.get("sha256")):
            failures.append({"path": relative, "reason": "sha256_mismatch"})
    expected = int(payload.get("n_files", -1))
    actual = len(payload.get("files", []))
    if expected != actual:
        failures.append({"path": str(path), "reason": "file_count_mismatch"})
    return {
        "status": "LOCKBOX_MANIFEST_PASS" if not failures else "LOCKBOX_MANIFEST_FAIL",
        "release_version": payload.get("release_version"),
        "n_expected": expected,
        "n_failures": len(failures),
        "failures": failures,
    }


def verify_release_identity(
    repository_root: str | Path,
    manifest_path: str | Path,
    *,
    tag: str = "v0.2.0",
) -> dict[str, Any]:
    """Bind a clean checkout to an annotated tag carrying the manifest hash."""
    root = Path(repository_root).resolve()
    manifest = Path(manifest_path).resolve()
    failures: list[dict[str, str]] = []
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        tag_commit = subprocess.run(
            ["git", "rev-parse", f"{tag}^{{commit}}"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        tag_type = subprocess.run(
            ["git", "cat-file", "-t", tag], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        tag_body = subprocess.run(
            ["git", "for-each-ref", "--format=%(contents)", f"refs/tags/{tag}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {
            "status": "RELEASE_IDENTITY_UNAVAILABLE",
            "tag": tag,
            "n_failures": 1,
            "failures": [{"item": tag, "reason": "git_or_tag_unavailable"}],
        }
    manifest_sha256 = sha256_file(manifest)
    if head != tag_commit:
        failures.append({"item": tag, "reason": "tag_does_not_point_to_head"})
    if tag_type != "tag":
        failures.append({"item": tag, "reason": "tag_is_not_annotated"})
    if f"LOCKBOX_MANIFEST_SHA256={manifest_sha256}" not in tag_body:
        failures.append({"item": tag, "reason": "manifest_hash_missing_from_tag_message"})
    return {
        "status": "RELEASE_IDENTITY_PASS" if not failures else "RELEASE_IDENTITY_FAIL",
        "tag": tag,
        "head": head,
        "tag_commit": tag_commit,
        "manifest_sha256": manifest_sha256,
        "n_failures": len(failures),
        "failures": failures,
    }
