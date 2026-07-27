#!/usr/bin/env python3
"""One-time, crash-resumable truth-open adjudication for M3-V4."""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_confirmation_common import (  # noqa: E402
    canonical_json,
    derive_seed,
    load_sealed_config,
    logical_task_labels,
    sha256_bytes,
    sha256_file,
    validate_randomness_record,
    verify_sealed_code,
)
from suica_core.m3_cross_family_audit import (  # noqa: E402
    TARGET_FAMILIES,
    audit_m3_cross_family,
    partial_geometry_correlation,
    same_author_auc,
)
from suica_core.m3_cross_family_contracts import (  # noqa: E402
    M3CrossFamilyEstimate,
    M3CrossFamilyTruth,
    observed_from_payload,
)
from suica_core.m3_cross_family_validity import (  # noqa: E402
    audit_m3_cross_family_validity,
)


@dataclass(frozen=True)
class OpenedTask:
    metadata: dict[str, Any]
    truth: M3CrossFamilyTruth
    estimate: M3CrossFamilyEstimate
    audit_rows: tuple[dict[str, Any], ...]
    validity: dict[str, Any]


def _read_key(path: Path) -> bytes:
    payload = path.read_bytes()
    try:
        decoded = bytes.fromhex(payload.decode("ascii").strip())
    except (UnicodeDecodeError, ValueError):
        decoded = payload
    if len(decoded) != 32:
        raise ValueError("truth key must contain exactly 32 bytes")
    return decoded


def _decrypt_truth(
    path: Path,
    task_id: str,
    key: bytes,
) -> tuple[M3CrossFamilyTruth, dict[str, Any]]:
    encrypted = path.read_bytes()
    plaintext = AESGCM(key).decrypt(
        encrypted[:12],
        encrypted[12:],
        task_id.encode("ascii"),
    )
    with np.load(io.BytesIO(plaintext), allow_pickle=False) as payload:
        metadata = json.loads(str(payload["metadata_json"]))
        parameters = {
            name.removeprefix("parameter__"): np.asarray(
                payload[name],
                dtype=float,
            )
            for name in payload.files
            if name.startswith("parameter__")
        }
        profiles = {
            name.removeprefix("oracle__"): np.asarray(
                payload[name],
                dtype=float,
            )
            for name in payload.files
            if name.startswith("oracle__")
        }
    return (
        M3CrossFamilyTruth(
            world=str(metadata["world"]),
            active_targets=tuple(metadata["active_targets"]),
            author_parameters=parameters,
            oracle_profiles=profiles,
            exact_alias=bool(metadata["exact_alias"]),
            validity=dict(metadata["validity"]),
        ),
        metadata,
    )


def _load_estimate(path: Path) -> M3CrossFamilyEstimate:
    with np.load(path, allow_pickle=False) as payload:
        metadata = json.loads(str(payload["metadata_json"]))
        train = {
            name.removeprefix("train__"): np.asarray(payload[name], dtype=float)
            for name in payload.files
            if name.startswith("train__")
        }
        test = {
            name.removeprefix("test__"): np.asarray(payload[name], dtype=float)
            for name in payload.files
            if name.startswith("test__")
        }
        heldout = {
            name.removeprefix("heldout__"): np.asarray(
                payload[name],
                dtype=float,
            )
            for name in payload.files
            if name.startswith("heldout__")
        }
    return M3CrossFamilyEstimate(
        train_features=train,
        test_features=test,
        heldout_metrics={
            str(name): float(value)
            for name, value in metadata["heldout_metrics"].items()
        },
        heldout_by_author=heldout,
        refusals=tuple(metadata["refusals"]),
    )


def _append_ledger(path: Path, event: str, details: dict[str, Any]) -> None:
    previous = ""
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
        if lines:
            previous = str(json.loads(lines[-1])["record_sha256"])
    payload = {
        "event": event,
        "recorded_utc": datetime.now(UTC).isoformat(),
        "previous_record_sha256": previous,
        **details,
    }
    payload["record_sha256"] = sha256_bytes(canonical_json(payload).encode())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _verify_and_open(
    output_dir: Path,
    key: bytes,
) -> tuple[list[OpenedTask], dict[str, Any], dict[str, Any]]:
    config, seal = load_sealed_config(output_dir)
    verify_sealed_code(seal, ROOT)
    generation = json.loads(
        (output_dir / "generation_sealed.json").read_text(encoding="utf-8")
    )
    predictions = json.loads(
        (output_dir / "predictions_sealed.json").read_text(encoding="utf-8")
    )
    generated = {str(row["task_id"]): row for row in generation["records"]}
    predicted = {str(row["task_id"]): row for row in predictions["records"]}
    if set(generated) != set(predicted):
        raise RuntimeError("generation and prediction task sets differ")
    if len(generated) != int(generation["task_count"]):
        raise RuntimeError("generation task count mismatch")
    if len(predicted) != int(predictions["task_count"]):
        raise RuntimeError("prediction task count mismatch")
    tasks: list[OpenedTask] = []
    logical_labels = []
    for task_id in sorted(generated):
        observation_path = output_dir / "observations" / f"{task_id}.npz"
        truth_path = output_dir / "truth_lockbox" / f"{task_id}.aesgcm"
        prediction_path = output_dir / "predictions" / f"{task_id}.npz"
        if sha256_file(observation_path) != generated[task_id][
            "observation_sha256"
        ]:
            raise RuntimeError(f"observation hash mismatch: {task_id}")
        if sha256_file(truth_path) != generated[task_id][
            "encrypted_truth_sha256"
        ]:
            raise RuntimeError(f"encrypted truth hash mismatch: {task_id}")
        if sha256_file(prediction_path) != predicted[task_id][
            "prediction_sha256"
        ]:
            raise RuntimeError(f"prediction hash mismatch: {task_id}")
        truth, metadata = _decrypt_truth(truth_path, task_id, key)
        if metadata["task_id"] != task_id:
            raise RuntimeError(f"truth task id mismatch: {task_id}")
        logical_labels.append(str(metadata["logical_label"]))
        with np.load(observation_path, allow_pickle=False) as payload:
            observed = observed_from_payload(payload)
        estimate = _load_estimate(prediction_path)
        rows = audit_m3_cross_family(estimate, truth)
        if metadata["task_kind"] == "knockout":
            rows = [
                row for row in rows
                if row["target"] == metadata["score_target"]
            ]
        tasks.append(OpenedTask(
            metadata=metadata,
            truth=truth,
            estimate=estimate,
            audit_rows=tuple(rows),
            validity=audit_m3_cross_family_validity(observed, truth),
        ))
    if sorted(logical_labels) != logical_task_labels(config):
        raise RuntimeError("opened logical task registry is incomplete")
    return tasks, config, predictions


def _validity_pass(values: dict[str, Any], gates: dict[str, Any]) -> bool:
    if not bool(values.get("finite", False)):
        return False
    maximums = {
        "density_normalization_max_error": 1e-10,
        "moment_tensor_degree4_max_author_range": 1e-9,
        "poly3_projection_ratio_max": 1e-10,
        "nuisance_sum_to_zero_max_error": 1e-10,
        "actor_dyad_overlap_max": 0.0,
        "theoretical_lag02_max_author_range": 1e-12,
        "renewal_mean_dwell_max_error": 1e-12,
        "renewal_singleton_probability_max_error": 1e-12,
        "cycle_row_sum_max_error": 1e-12,
        "cycle_uniform_stationarity_max_error": 1e-12,
        "cycle_transpose_pair_max_error": 1e-12,
        "alias_on_support_basis_max_abs": 0.0,
    }
    maximums.update(gates.get("validity_maximums", {}))
    for name, maximum in maximums.items():
        if name in values and float(values[name]) > float(maximum):
            return False
    if float(values.get("density_relative_minimum", 1.0)) < float(
        gates.get("minimum_density", 0.05)
    ):
        return False
    for name in (
        "same_partner_population",
        "all_partners_covered",
        "actor_partner_graph_connected",
    ):
        if name in values and not bool(values[name]):
            return False
    if (
        "actor_partner_incidence_rank" in values
        and values["actor_partner_incidence_rank"]
        != values["actor_partner_incidence_expected_rank"]
    ):
        return False
    return True


def _holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    output: dict[str, float] = {}
    running = 0.0
    for index, key in enumerate(ordered):
        adjusted = min(1.0, p_values[key] * (len(ordered) - index))
        running = max(running, adjusted)
        output[key] = running
    return output


def _hierarchical_bootstrap(
    tasks: list[OpenedTask],
    target: str,
    *,
    repetitions: int,
    seed: int,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    expected, _ = TARGET_FAMILIES[target]
    geometry = np.empty(repetitions, dtype=float)
    increment = np.empty(repetitions, dtype=float)
    for repetition in range(repetitions):
        selected = rng.integers(0, len(tasks), size=len(tasks))
        seed_geometry = []
        seed_increment = []
        for task_index in selected:
            task = tasks[int(task_index)]
            oracle = task.truth.oracle_profiles.get(
                target,
                task.truth.author_parameters[target],
            )
            authors = len(oracle)
            index = rng.integers(0, authors, size=authors)
            nuisance = [
                task.truth.oracle_profiles.get(
                    other,
                    task.truth.author_parameters[other],
                )[index]
                for other in task.truth.active_targets
                if other != target
            ]
            value = partial_geometry_correlation(
                task.estimate.test_features[expected][index],
                oracle[index],
                nuisance,
            )
            if np.isfinite(value):
                seed_geometry.append(value)
            author_increment = task.estimate.heldout_by_author[
                f"{expected}_score_gain"
            ]
            seed_increment.append(float(np.mean(author_increment[index])))
        geometry[repetition] = (
            float(np.mean(seed_geometry)) if seed_geometry else np.nan
        )
        increment[repetition] = float(np.mean(seed_increment))
    return {"geometry": geometry, "increment": increment}


def _interval(values: np.ndarray) -> tuple[float, float]:
    clean = values[np.isfinite(values)]
    return tuple(float(value) for value in np.quantile(
        clean,
        (0.025, 0.975),
    ))


def _adjudicate(
    tasks: list[OpenedTask],
    config: dict[str, Any],
    randomness: bytes,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    gates = config["confirmation_gates"]
    main_groups: dict[tuple[str, str], list[OpenedTask]] = {}
    knockout_groups: dict[tuple[str, str], list[OpenedTask]] = {}
    flat_rows = []
    validity_rows = []
    for task in tasks:
        valid = _validity_pass(task.validity, gates)
        validity_rows.append({
            "task_id": task.metadata["task_id"],
            "logical_label": task.metadata["logical_label"],
            "validity_pass": valid,
            **task.validity,
        })
        for row in task.audit_rows:
            flat_rows.append({
                "task_id": task.metadata["task_id"],
                "logical_label": task.metadata["logical_label"],
                "task_kind": task.metadata["task_kind"],
                "repetition": task.metadata["repetition"],
                "validity_pass": valid,
                **row,
            })
            if row["target"] != "null" and not task.truth.exact_alias:
                key = (task.truth.world, str(row["target"]))
                destination = (
                    main_groups
                    if task.metadata["task_kind"] == "main"
                    else knockout_groups
                )
                destination.setdefault(key, []).append(task)

    bootstrap_repetitions = int(gates.get("bootstrap_repetitions", 2000))
    summaries = []
    raw_p: dict[str, float] = {}
    bootstrap_cache: dict[str, dict[str, np.ndarray]] = {}
    for (world, target), group in main_groups.items():
        key = f"{world}::{target}"
        bootstrap = _hierarchical_bootstrap(
            group,
            target,
            repetitions=bootstrap_repetitions,
            seed=derive_seed(randomness, "bootstrap", key),
        )
        bootstrap_cache[key] = bootstrap
        rows = [
            row
            for task in group
            for row in task.audit_rows
            if row["target"] == target
        ]
        auc_values = np.asarray([float(row["expected_auc"]) for row in rows])
        cheap_values = np.asarray([float(row["cheap_auc"]) for row in rows])
        geometry_ci = _interval(bootstrap["geometry"])
        increment_ci = _interval(bootstrap["increment"])
        auc_ci = _interval(auc_values)
        cheap_ci = _interval(cheap_values)
        raw_p[f"{key}::geometry"] = float(
            (1.0 + np.sum(bootstrap["geometry"] <= 0.0))
            / (len(bootstrap["geometry"]) + 1.0)
        )
        raw_p[f"{key}::increment"] = float(
            (1.0 + np.sum(bootstrap["increment"] <= 0.0))
            / (len(bootstrap["increment"]) + 1.0)
        )
        summaries.append({
            "key": key,
            "world": world,
            "target": target,
            "seeds": len(group),
            "expected_auc": float(auc_values.mean()),
            "expected_auc_ci_low": auc_ci[0],
            "expected_auc_ci_high": auc_ci[1],
            "cheap_auc": float(cheap_values.mean()),
            "cheap_auc_ci_low": cheap_ci[0],
            "cheap_auc_ci_high": cheap_ci[1],
            "expected_geometry": float(np.nanmean(bootstrap["geometry"])),
            "geometry_ci_low": geometry_ci[0],
            "geometry_ci_high": geometry_ci[1],
            "heldout_increment": float(np.mean(bootstrap["increment"])),
            "increment_ci_low": increment_ci[0],
            "increment_ci_high": increment_ci[1],
            "validity_fraction": float(np.mean([
                _validity_pass(task.validity, gates) for task in group
            ])),
            "refusal_max": max(len(task.estimate.refusals) for task in group),
        })

    adjusted = _holm(raw_p)
    checks: dict[str, bool] = {}
    diagnostics: dict[str, Any] = {}
    for summary in summaries:
        key = str(summary["key"])
        target_gates = {
            **gates,
            **gates.get("target_overrides", {}).get(
                str(summary["target"]),
                {},
            ),
        }
        knockout = knockout_groups.get(
            (str(summary["world"]), str(summary["target"])),
            [],
        )
        knockout_geometry = [
            float(row["expected_geometry"])
            for task in knockout
            for row in task.audit_rows
            if row["target"] == summary["target"]
        ]
        cell = {
            "valid": summary["validity_fraction"] == 1.0,
            "no_refusal": summary["refusal_max"] == 0,
            "auc": summary["expected_auc_ci_low"]
            > float(target_gates["minimum_expected_auc_ci_lower"]),
            "geometry": summary["geometry_ci_low"]
            > float(target_gates["minimum_geometry_ci_lower"]),
            "increment": summary["increment_ci_low"]
            > float(target_gates["minimum_increment_ci_lower"]),
            "cheap_mean": abs(summary["cheap_auc"] - 0.5)
            < float(target_gates["maximum_cheap_auc_bias"]),
            "cheap_ci": summary["cheap_auc_ci_low"] <= 0.5
            <= summary["cheap_auc_ci_high"],
            "holm_geometry": adjusted[f"{key}::geometry"] < 0.05,
            "holm_increment": adjusted[f"{key}::increment"] < 0.05,
            "knockout": bool(knockout_geometry)
            and abs(float(np.mean(knockout_geometry)))
            < float(target_gates["maximum_knockout_mean_abs"]),
        }
        checks[key] = all(cell.values())
        diagnostics[key] = {
            "checks": cell,
            "holm_geometry_p": adjusted[f"{key}::geometry"],
            "holm_increment_p": adjusted[f"{key}::increment"],
            "knockout_geometry": (
                float(np.mean(knockout_geometry))
                if knockout_geometry
                else None
            ),
            **summary,
        }

    alias_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    null_groups: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        if task.metadata["task_kind"] != "main":
            continue
        for row in task.audit_rows:
            if task.truth.exact_alias:
                alias_groups.setdefault(
                    (task.truth.world, str(row["target"])),
                    [],
                ).append({
                    "row": row,
                    "valid": _validity_pass(task.validity, gates),
                    "refusals": len(task.estimate.refusals),
                })
            elif row["target"] == "null":
                null_groups.setdefault(
                    str(row["expected_family"]),
                    [],
                ).append({
                    "row": row,
                    "valid": _validity_pass(task.validity, gates),
                    "refusals": len(task.estimate.refusals),
                })

    for (world, target), group in alias_groups.items():
        key = f"{world}::{target}"
        auc = np.asarray([
            float(item["row"]["expected_auc"]) for item in group
        ])
        geometry = np.asarray([
            abs(float(item["row"]["expected_geometry"])) for item in group
        ])
        auc_ci = _interval(auc)
        geometry_ci = _interval(geometry)
        cell = {
            "valid": all(bool(item["valid"]) for item in group),
            "no_refusal": max(int(item["refusals"]) for item in group) == 0,
            "auc_mean": abs(float(auc.mean()) - 0.5)
            < float(gates["maximum_alias_auc_bias"]),
            "auc_ci": auc_ci[0] <= 0.5 <= auc_ci[1],
            "geometry": geometry_ci[1]
            < float(gates["maximum_alias_geometry_abs"]),
        }
        checks[key] = all(cell.values())
        diagnostics[key] = {
            "checks": cell,
            "expected_auc": float(auc.mean()),
            "expected_auc_ci": auc_ci,
            "expected_geometry_abs": float(geometry.mean()),
            "expected_geometry_abs_ci": geometry_ci,
        }

    for family, group in null_groups.items():
        key = f"null::{family}"
        auc = np.asarray([
            float(item["row"]["expected_auc"]) for item in group
        ])
        auc_ci = _interval(auc)
        cell = {
            "valid": all(bool(item["valid"]) for item in group),
            "no_refusal": max(int(item["refusals"]) for item in group) == 0,
            "auc_mean": abs(float(auc.mean()) - 0.5)
            < float(gates["maximum_null_auc_bias"]),
            "auc_ci": auc_ci[0] <= 0.5 <= auc_ci[1],
        }
        checks[key] = all(cell.values())
        diagnostics[key] = {
            "checks": cell,
            "expected_auc": float(auc.mean()),
            "expected_auc_ci": auc_ci,
        }

    decision = {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_CROSS_FAMILY_V4_CONFIRMATION_PASS"
            if checks and all(checks.values())
            else "M3_CROSS_FAMILY_V4_CONFIRMATION_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "holm_adjusted_primary_tests": adjusted,
        "truth_opened_once": True,
        "claim_boundary": (
            "Cross-family synthetic mathematical existence only. No human "
            "personality, construct-validity, or clinical claim."
        ),
    }
    return pd.DataFrame(flat_rows), pd.DataFrame(validity_rows), decision


def open_once(output_dir: Path, truth_key_path: Path) -> dict[str, Any]:
    """Open truth once, resume safely after a crash, and atomically publish."""
    opened_dir = output_dir / "opened"
    completion_marker = output_dir / "TRUTH_OPEN_COMPLETE"
    ledger = output_dir / "truth_open_ledger.jsonl"
    if opened_dir.exists() and completion_marker.exists():
        raise RuntimeError("truth-open output already exists")
    if opened_dir.exists():
        decision = json.loads(
            (opened_dir / "decision.json").read_text(encoding="utf-8")
        )
        _append_ledger(ledger, "TRUTH_OPEN_COMPLETE_RECOVERED", {
            "decision": decision["decision"],
            "opened_decision_sha256": sha256_file(
                opened_dir / "decision.json"
            ),
        })
        completion_marker.write_text(
            datetime.now(UTC).isoformat() + "\n",
            encoding="utf-8",
        )
        return decision
    key = _read_key(truth_key_path)
    key_fingerprint = sha256_bytes(key)
    generation = json.loads(
        (output_dir / "generation_sealed.json").read_text(encoding="utf-8")
    )
    if generation["truth_key_sha256"] != key_fingerprint:
        raise RuntimeError("truth key fingerprint mismatch")
    prediction_path = output_dir / "predictions_sealed.json"
    if not ledger.exists():
        _append_ledger(ledger, "TRUTH_OPEN_STARTED", {
            "truth_key_sha256": key_fingerprint,
            "predictions_sealed_sha256": sha256_file(prediction_path),
        })
    else:
        first = json.loads(
            ledger.read_text(encoding="utf-8").splitlines()[0]
        )
        if first.get("truth_key_sha256") != key_fingerprint:
            raise RuntimeError("truth-open ledger key fingerprint mismatch")
    tasks, config, _ = _verify_and_open(output_dir, key)
    randomness_record = json.loads(
        (output_dir / "randomness.record.json").read_text(encoding="utf-8")
    )
    randomness = validate_randomness_record(randomness_record)
    metrics, validity, decision = _adjudicate(tasks, config, randomness)

    staging = output_dir / ".truth_open_staging"
    staging.mkdir(exist_ok=True)
    metrics.to_csv(staging / "metrics.csv", index=False)
    validity.to_csv(staging / "validity.csv", index=False)
    (staging / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(staging, opened_dir)
    _append_ledger(ledger, "TRUTH_OPEN_COMPLETE", {
        "decision": decision["decision"],
        "opened_decision_sha256": sha256_file(opened_dir / "decision.json"),
    })
    completion_marker.write_text(
        datetime.now(UTC).isoformat() + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--truth-key-file", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        open_once(args.output_dir, args.truth_key_file),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
