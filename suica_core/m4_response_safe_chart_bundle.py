"""Serialization boundary for pre-response M4-C.3.5 chart arms."""
from __future__ import annotations

from dataclasses import replace
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
from typing import Any

import numpy as np

from .m4_condition_manifold_contracts import M4ConditionObserved


CONDITION_FIELDS = (
    "reference_calibration",
    "reference_selection",
    "mechanism_calibration",
    "mechanism_selection",
    "mechanism_evaluation",
)
BASIS_ROLES = ("calibration", "selection", "evaluation")


def sanitize_pre_response(
    observed: M4ConditionObserved,
) -> M4ConditionObserved:
    """Remove response bytes while preserving the validated tensor schema."""
    return M4ConditionObserved(
        **{
            name: replace(
                getattr(observed, name),
                response=np.zeros_like(getattr(observed, name).response),
            )
            for name in CONDITION_FIELDS
        },
        design=dict(observed.design),
    )


def pre_response_digest(observed: M4ConditionObserved) -> str:
    """Hash only declared pre-response chart inputs."""
    digest = hashlib.sha256()
    for name in CONDITION_FIELDS:
        panel = getattr(observed, name)
        digest.update(name.encode("utf-8"))
        digest.update(
            np.ascontiguousarray(panel.pre_context).view(np.uint8)
        )
        digest.update(
            json.dumps(
                panel.provenance_fields,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    digest.update(
        json.dumps(
            observed.design,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    """Hash one serialized artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_hash_manifest(
    root: Path,
    paths: list[Path],
) -> dict[str, str]:
    """Hash a fixed source set using repository-relative path keys."""
    return {
        path.resolve().relative_to(root.resolve()).as_posix(): file_sha256(path)
        for path in sorted(paths)
    }


def verify_source_hash_manifest(
    root: Path,
    expected: dict[str, str],
) -> None:
    """Refuse when any source sealed by Phase A has changed."""
    for relative, digest in expected.items():
        path = root / relative
        if not path.is_file():
            raise ValueError(f"sealed source is missing: {relative}")
        actual = file_sha256(path)
        if actual != digest:
            raise ValueError(
                f"sealed source changed: {relative}; "
                f"expected {digest}, found {actual}"
            )


def runtime_fingerprint() -> dict[str, str]:
    """Return the numerical runtime versions relevant to sealed replay."""
    packages = ("numpy", "pandas", "scipy", "scikit-learn")
    return {
        "python": platform.python_version(),
        **{
            package: metadata.version(package)
            for package in packages
        },
    }


def write_basis_bundle(
    path: Path,
    bases: dict[str, dict[str, np.ndarray]],
    *,
    extra_bases: dict[str, dict[str, np.ndarray]] | None = None,
) -> str:
    """Serialize chart bases and return the file hash."""
    arrays = {
        f"{arm}__{role}": np.asarray(values, dtype=float)
        for arm, roles in bases.items()
        for role, values in roles.items()
    }
    for arm, roles in (extra_bases or {}).items():
        for role, values in roles.items():
            arrays[f"{arm}__{role}"] = np.asarray(values, dtype=float)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)
    return file_sha256(path)


def read_basis_bundle(
    path: Path,
    *,
    expected_sha256: str,
) -> dict[str, dict[str, np.ndarray]]:
    """Verify and load a pre-response chart bundle."""
    actual = file_sha256(path)
    if actual != expected_sha256:
        raise ValueError(
            f"chart bundle hash mismatch: expected {expected_sha256}, "
            f"found {actual}"
        )
    output: dict[str, dict[str, np.ndarray]] = {}
    with np.load(path, allow_pickle=False) as archive:
        for name in archive.files:
            arm, role = name.split("__", maxsplit=1)
            output.setdefault(arm, {})[role] = archive[name].copy()
    for arm, roles in output.items():
        if set(roles) != set(BASIS_ROLES):
            raise ValueError(f"incomplete basis roles for {arm}")
    return output
