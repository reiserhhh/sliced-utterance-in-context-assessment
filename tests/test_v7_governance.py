from __future__ import annotations

from tempfile import TemporaryDirectory

from suica_core.v7_governance import (
    append_ledger_event,
    pseudonymize_identifiers,
    verify_artifact_inventory,
    verify_run_manifest,
    write_artifact_inventory,
    write_run_manifest,
)


def test_artifact_inventory_detects_a_changed_runtime_file() -> None:
    with TemporaryDirectory() as directory:
        root = __import__("pathlib").Path(directory)
        (root / "runtime.bin").write_bytes(b"frozen")
        inventory = root / "artifact_inventory.json"
        write_artifact_inventory(root, inventory)
        assert verify_artifact_inventory(inventory)["status"] == "INVENTORY_PASS"
        (root / "runtime.bin").write_bytes(b"changed")
        assert verify_artifact_inventory(inventory)["status"] == "INVENTORY_FAIL"


def test_run_manifest_detects_changed_config_and_hides_identifier_secret(tmp_path) -> None:
    data = tmp_path / "data.csv"
    config = tmp_path / "config.json"
    code = tmp_path / "runner.py"
    for path, text in ((data, "x\n1\n"), (config, "{}\n"), (code, "print('ok')\n")):
        path.write_text(text, encoding="utf-8")
    manifest = tmp_path / "run_manifest.json"
    write_run_manifest(
        manifest,
        repository_root=tmp_path,
        input_paths=[data],
        config_path=config,
        code_paths=[code],
        estimand_id="test-estimand",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["config"]["path"] == "config.json"
    assert payload["config"]["path_base"] == "repository_root"
    assert verify_run_manifest(manifest)["status"] == "RUN_MANIFEST_PASS"
    config.write_text('{"changed": true}\n', encoding="utf-8")
    assert verify_run_manifest(manifest)["status"] == "RUN_MANIFEST_FAIL"
    pseudo = pseudonymize_identifiers(["alice", "alice", "bob"], secret="local-secret")
    assert pseudo[0] == pseudo[1]
    assert pseudo[0] != pseudo[2]
    assert "alice" not in pseudo[0]


def test_append_ledger_event_is_jsonl(tmp_path) -> None:
    path = tmp_path / "ledger.jsonl"
    first = append_ledger_event(path, {"estimand_id": "a", "status": "PASS"})
    second = append_ledger_event(path, {"estimand_id": "b", "status": "REFUSE"})
    assert first["estimand_id"] == "a"
    assert second["estimand_id"] == "b"
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2
