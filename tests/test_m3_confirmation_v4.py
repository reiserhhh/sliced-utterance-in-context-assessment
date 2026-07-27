"""Governance and isolation tests for the M3-V4 confirmation workflow."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from suica_core.m3_confirmation_common import (
    canonical_json,
    derive_seed,
    load_sealed_config,
    logical_task_labels,
    opaque_task_id,
    sha256_bytes,
    sha256_file,
)
from suica_core.m3_cross_family_generator import (
    M3CrossFamilySpec,
    WORLD_TARGETS,
    generate_m3_cross_family_world,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _config() -> dict[str, object]:
    return {
        "estimand_id": "TEST",
        "repetitions": 2,
        "worlds": {
            "cf_kp_cycle": {
                "spec": "path",
                "events": 64,
                "knockout_targets": ["direction"],
            },
            "null_author": {
                "spec": "path",
                "events": 64,
                "knockout_targets": [],
            },
        },
        "specs": {
            "path": {
                "authors": 12,
                "occasions": 4,
                "events": 64,
                "dimensions": 3,
                "partners": 8,
                "noise": 0.1,
            },
        },
        "estimator": {
            "frequency_directions": 8,
            "nystroem_components": 8,
            "ridge": 0.35,
        },
        "confirmation_gates": {},
    }


def test_task_registry_and_seed_domains_are_independent() -> None:
    config = _config()
    labels = logical_task_labels(config)
    assert len(labels) == 6
    randomness = bytes(range(32))
    task_ids = {opaque_task_id(randomness, label) for label in labels}
    assert len(task_ids) == len(labels)
    label = labels[0]
    assert derive_seed(randomness, "generator", label) != derive_seed(
        randomness,
        "estimator",
        opaque_task_id(randomness, label),
    )


def test_sealed_config_rejects_substitution(tmp_path: Path) -> None:
    config = _config()
    snapshot = tmp_path / "config.snapshot.json"
    snapshot.write_text(json.dumps(config), encoding="utf-8")
    labels = logical_task_labels(config)
    (tmp_path / "seal.json").write_text(json.dumps({
        "config_snapshot_sha256": sha256_file(snapshot),
        "logical_task_count": len(labels),
        "logical_task_labels_sha256": sha256_bytes(
            canonical_json(labels).encode()
        ),
        "code": [],
    }), encoding="utf-8")
    loaded, _ = load_sealed_config(tmp_path)
    assert loaded["estimand_id"] == "TEST"
    snapshot.write_text(json.dumps({**config, "repetitions": 3}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="snapshot hash mismatch"):
        load_sealed_config(tmp_path)


def test_fit_process_source_has_no_generator_or_truth_access() -> None:
    source = (
        ROOT / "scripts" / "run_suica_m3_cross_family_fit_v4.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "m3_cross_family_generator",
        "M3CrossFamilyTruth",
        "truth_lockbox",
        "truth-key",
        "AESGCM",
    )
    assert not any(token in source for token in forbidden)


def test_truth_payload_is_encrypted_and_not_plaintext() -> None:
    generator_script = _load_script(
        "m3_generate_v4_test",
        "scripts/run_suica_m3_cross_family_generate_v4.py",
    )
    _, truth = generate_m3_cross_family_world(
        world="cf_kp_cycle",
        spec=M3CrossFamilySpec(
            authors=12,
            occasions=4,
            events=64,
            dimensions=3,
            partners=8,
        ),
        seed=101,
    )
    plaintext = generator_script._truth_bytes(
        truth,
        {"task_id": "t_test", "logical_label": "hidden"},
    )
    key = bytes(range(32))
    nonce = bytes(range(12))
    aad = b"t_test"
    encrypted = generator_script.AESGCM(key).encrypt(
        nonce,
        plaintext,
        aad,
    )
    assert b"cf_kp_cycle" not in encrypted
    assert b"parameter__direction" not in encrypted
    assert generator_script.AESGCM(key).decrypt(
        nonce,
        encrypted,
        aad,
    ) == plaintext


def test_truth_open_ledger_is_hash_chained(tmp_path: Path) -> None:
    open_script = _load_script(
        "m3_open_v4_test",
        "scripts/run_suica_m3_cross_family_open_v4.py",
    )
    ledger = tmp_path / "ledger.jsonl"
    open_script._append_ledger(ledger, "START", {"value": 1})
    open_script._append_ledger(ledger, "COMPLETE", {"value": 2})
    rows = [
        json.loads(line)
        for line in ledger.read_text(encoding="utf-8").splitlines()
    ]
    assert rows[1]["previous_record_sha256"] == rows[0]["record_sha256"]


def test_truth_open_recovers_after_atomic_publish_crash(tmp_path: Path) -> None:
    open_script = _load_script(
        "m3_open_v4_recovery_test",
        "scripts/run_suica_m3_cross_family_open_v4.py",
    )
    opened = tmp_path / "opened"
    opened.mkdir()
    decision = {"decision": "TEST_PASS"}
    (opened / "decision.json").write_text(
        json.dumps(decision),
        encoding="utf-8",
    )
    open_script._append_ledger(
        tmp_path / "truth_open_ledger.jsonl",
        "TRUTH_OPEN_STARTED",
        {"truth_key_sha256": "fingerprint"},
    )
    recovered = open_script.open_once(
        tmp_path,
        tmp_path / "missing-key-is-not-read",
    )
    assert recovered == decision
    assert (tmp_path / "TRUTH_OPEN_COMPLETE").is_file()


def test_formal_seal_rejects_predeclared_seed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seal_script = _load_script(
        "m3_seal_v4_test",
        "scripts/run_suica_m3_cross_family_confirmation_v4.py",
    )
    monkeypatch.setattr(
        seal_script,
        "git_revision",
        lambda _: {"status": "GIT_AVAILABLE", "revision": "abc", "dirty": False},
    )
    config = {**_config(), "seed": 123}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot contain a seed"):
        seal_script.create_seal(config_path, tmp_path / "sealed")


def test_preflight_null_gate_is_two_sided_and_requires_validity() -> None:
    preflight = _load_script(
        "m3_preflight_v4_test",
        "scripts/run_suica_m3_cross_family_preflight.py",
    )
    metrics = pd.DataFrame([
        {
            "world": "null_author",
            "seed": 1,
            "target": "null",
            "exact_alias": False,
            "expected_family": "distribution_ecf",
            "expected_auc": 0.20,
            "cheap_auc": np.nan,
            "expected_geometry": np.nan,
            "cheap_geometry": np.nan,
            "heldout_increment": np.nan,
            "off_target_geometry": np.nan,
            "knockout_geometry": np.nan,
            "validity_pass": True,
            "refusal_count": 0,
        },
    ])
    _, decision = preflight._decision(metrics, {
        "estimand_id": "TEST",
        "preflight_gates": {"maximum_null_auc_deviation": 0.04},
    })
    assert decision["checks"]["null_calibration"] is False
    assert (
        decision["diagnostics"]["null_calibration"]
        ["maximum_auc_deviation"]
        == pytest.approx(0.30)
    )


def test_formal_v4_config_is_seed_free_and_task_complete() -> None:
    config = json.loads(
        (
            ROOT / "configs" / "m3_cross_family_confirmation_v4.json"
        ).read_text(encoding="utf-8")
    )
    assert "seed" not in config
    assert "root_seed" not in config
    assert set(config["worlds"]) == set(WORLD_TARGETS)
    for world, declaration in config["worlds"].items():
        expected = (
            []
            if world.startswith("alias_") or world == "null_author"
            else list(WORLD_TARGETS[world])
        )
        assert declaration["knockout_targets"] == expected
    assert len(logical_task_labels(config)) == 832
    assert config["required_preflight"] == {
        "path": "results/m3_cross_family_preflight_v4/decision.json",
        "decision": "M3_CROSS_FAMILY_V4_READY_FOR_CLEAN_SEAL",
    }


def test_current_v4_workflow_runs_end_to_end_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seal_script = _load_script(
        "m3_seal_v4_e2e_test",
        "scripts/run_suica_m3_cross_family_confirmation_v4.py",
    )
    monkeypatch.setattr(
        seal_script,
        "git_revision",
        lambda _: {"status": "GIT_AVAILABLE", "revision": "test", "dirty": False},
    )
    config = {
        "version": "test-e2e",
        "estimand_id": "TEST_E2E",
        "repetitions": 1,
        "worlds": {
            "cf_d_tail": {
                "spec": "distribution",
                "events": 64,
                "knockout_targets": ["distribution"],
            },
            "cf_o_spline": {
                "spec": "operator",
                "events": 32,
                "knockout_targets": ["condition", "partner"],
            },
            "cf_kp_cycle": {
                "spec": "path",
                "events": 64,
                "knockout_targets": ["direction"],
            },
            "alias_operator_support": {
                "spec": "operator",
                "events": 32,
                "knockout_targets": [],
            },
            "null_author": {
                "spec": "path",
                "events": 64,
                "knockout_targets": [],
            },
        },
        "specs": {
            family: {
                "authors": 12,
                "occasions": 4,
                "events": events,
                "dimensions": 3,
                "partners": 8,
                "noise": 0.1,
            }
            for family, events in (
                ("distribution", 64),
                ("operator", 32),
                ("path", 64),
            )
        },
        "estimator": {
            "frequency_directions": 8,
            "nystroem_components": 8,
            "ridge": 0.35,
        },
        "confirmation_gates": {
            "minimum_expected_auc_ci_lower": -1.0,
            "minimum_geometry_ci_lower": -1.0,
            "minimum_increment_ci_lower": -1.0,
            "maximum_cheap_auc_bias": 1.0,
            "maximum_knockout_mean_abs": 1.0,
            "maximum_alias_auc_bias": 1.0,
            "maximum_alias_geometry_abs": 1.0,
            "maximum_null_auc_bias": 1.0,
            "minimum_density": 0.0,
            "bootstrap_repetitions": 25,
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output_dir = tmp_path / "sealed"
    seal_script.create_seal(config_path, output_dir)
    randomness = tmp_path / "randomness.json"
    randomness.write_text(json.dumps({
        "source": "test-only",
        "value_hex": bytes(range(32)).hex(),
        "retrieved_utc": "2000-01-01T00:00:00+00:00",
    }), encoding="utf-8")
    key = tmp_path / "truth.key"
    key.write_bytes(bytes(reversed(range(32))))

    subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "run_suica_m3_cross_family_generate_v4.py"),
        "--output-dir",
        str(output_dir),
        "--randomness-record",
        str(randomness),
        "--truth-key-file",
        str(key),
    ], check=True, capture_output=True, text=True)
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "run_suica_m3_cross_family_fit_v4.py"),
        "--output-dir",
        str(output_dir),
        "--max-workers",
        "1",
    ], check=True, capture_output=True, text=True)
    open_script = _load_script(
        "m3_open_v4_e2e_test",
        "scripts/run_suica_m3_cross_family_open_v4.py",
    )
    decision = open_script.open_once(output_dir, key)
    assert decision["truth_opened_once"] is True
    assert (output_dir / "opened" / "metrics.csv").is_file()
    assert (output_dir / "TRUTH_OPEN_COMPLETE").is_file()
    with pytest.raises(RuntimeError, match="already exists"):
        open_script.open_once(output_dir, key)
