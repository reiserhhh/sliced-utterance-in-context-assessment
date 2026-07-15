import json
import subprocess

import pytest

from suica_core.v7_release import build_lockbox_manifest, verify_lockbox_manifest, verify_release_identity


def test_release_manifest_round_trip_and_tamper_detection(tmp_path):
    (tmp_path / "artifact.txt").write_text("sealed\n", encoding="utf-8")
    manifest = build_lockbox_manifest(tmp_path, ["artifact.txt"])
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify_lockbox_manifest(manifest_path, repository_root=tmp_path)["status"] == "LOCKBOX_MANIFEST_PASS"

    (tmp_path / "artifact.txt").write_text("tampered\n", encoding="utf-8")
    result = verify_lockbox_manifest(manifest_path, repository_root=tmp_path)
    assert result["status"] == "LOCKBOX_MANIFEST_FAIL"
    assert result["failures"] == [{"path": "artifact.txt", "reason": "sha256_mismatch"}]


def test_release_manifest_refuses_repository_escape(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes repository"):
        build_lockbox_manifest(tmp_path, ["../outside.txt"])


def test_release_identity_requires_annotated_tag_at_head_with_manifest_hash(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("sealed\n", encoding="utf-8")
    manifest = build_lockbox_manifest(tmp_path, ["artifact.txt"])
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "seal"], cwd=tmp_path, check=True)
    digest = __import__("hashlib").sha256(manifest_path.read_bytes()).hexdigest()
    subprocess.run(
        ["git", "tag", "-a", "v0.2.0", "-m", f"LOCKBOX_MANIFEST_SHA256={digest}"],
        cwd=tmp_path,
        check=True,
    )
    assert verify_release_identity(tmp_path, manifest_path)["status"] == "RELEASE_IDENTITY_PASS"

    (tmp_path / "later.txt").write_text("later\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "later"], cwd=tmp_path, check=True)
    result = verify_release_identity(tmp_path, manifest_path)
    assert result["status"] == "RELEASE_IDENTITY_FAIL"
    assert {row["reason"] for row in result["failures"]} == {"tag_does_not_point_to_head"}
