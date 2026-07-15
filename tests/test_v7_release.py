import json

import pytest

from suica_core.v7_release import build_lockbox_manifest, verify_lockbox_manifest


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
