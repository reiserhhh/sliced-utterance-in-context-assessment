#!/usr/bin/env python3
"""Artifact-sealed fresh-seed confirmation for SUICA M3 cross-family objects."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_cross_family_audit import (  # noqa: E402
    audit_m3_cross_family,
)
from suica_core.m3_cross_family_contracts import (  # noqa: E402
    M3CrossFamilyEstimate,
    M3CrossFamilyTruth,
)
from suica_core.m3_cross_family_estimator import (  # noqa: E402
    fit_m3_cross_family,
)
from suica_core.m3_cross_family_generator import (  # noqa: E402
    M3CrossFamilySpec,
    generate_m3_cross_family_world,
)
from suica_core.v7_governance import (  # noqa: E402
    git_revision,
    sha256_file,
    write_artifact_inventory,
)


CODE_PATHS = (
    ROOT / "suica_core" / "m3_cross_family_contracts.py",
    ROOT / "suica_core" / "m3_cross_family_generator.py",
    ROOT / "suica_core" / "m3_cross_family_estimator.py",
    ROOT / "suica_core" / "m3_cross_family_audit.py",
    Path(__file__).resolve(),
    ROOT / "tests" / "test_m3_cross_family.py",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _derived_seed(root_seed: int, label: str) -> int:
    digest = hmac.new(
        str(root_seed).encode("utf-8"),
        label.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return int.from_bytes(digest[:8], "big") % (2**63 - 1)


def _task_id(root_seed: int, label: str) -> str:
    digest = hmac.new(
        str(root_seed).encode("utf-8"),
        f"task::{label}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t_{digest[:20]}"


def _array_digest(arrays: dict[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    for name in sorted(arrays):
        value = np.ascontiguousarray(arrays[name])
        digest.update(name.encode("utf-8"))
        digest.update(str(value.shape).encode("ascii"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _truth_payload(
    truth: M3CrossFamilyTruth,
    metadata: dict[str, Any],
) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {
        "metadata_json": np.asarray(
            _canonical_json({
                **metadata,
                "world": truth.world,
                "active_targets": truth.active_targets,
                "exact_alias": truth.exact_alias,
                "validity": truth.validity,
            }),
            dtype=np.str_,
        ),
    }
    for target, value in truth.author_parameters.items():
        payload[f"parameter__{target}"] = np.asarray(value, dtype=np.float64)
    for target, value in truth.oracle_profiles.items():
        payload[f"oracle__{target}"] = np.asarray(value, dtype=np.float64)
    return payload


def _load_truth(path: Path) -> tuple[M3CrossFamilyTruth, dict[str, Any]]:
    with np.load(path, allow_pickle=False) as payload:
        metadata = json.loads(str(payload["metadata_json"]))
        parameters = {
            key.removeprefix("parameter__"): np.asarray(payload[key], dtype=float)
            for key in payload.files
            if key.startswith("parameter__")
        }
        profiles = {
            key.removeprefix("oracle__"): np.asarray(payload[key], dtype=float)
            for key in payload.files
            if key.startswith("oracle__")
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


def _estimate_payload(estimate: M3CrossFamilyEstimate) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {
        "metadata_json": np.asarray(
            _canonical_json({
                "heldout_metrics": estimate.heldout_metrics,
                "refusals": estimate.refusals,
            }),
            dtype=np.str_,
        ),
    }
    for family, value in estimate.train_features.items():
        payload[f"train__{family}"] = np.asarray(value, dtype=np.float32)
    for family, value in estimate.test_features.items():
        payload[f"test__{family}"] = np.asarray(value, dtype=np.float32)
    return payload


def _load_estimate(path: Path) -> M3CrossFamilyEstimate:
    with np.load(path, allow_pickle=False) as payload:
        metadata = json.loads(str(payload["metadata_json"]))
        train = {
            key.removeprefix("train__"): np.asarray(payload[key], dtype=float)
            for key in payload.files
            if key.startswith("train__")
        }
        test = {
            key.removeprefix("test__"): np.asarray(payload[key], dtype=float)
            for key in payload.files
            if key.startswith("test__")
        }
    return M3CrossFamilyEstimate(
        train_features=train,
        test_features=test,
        heldout_metrics={
            str(key): float(value)
            for key, value in metadata["heldout_metrics"].items()
        },
        refusals=tuple(metadata["refusals"]),
    )


def _spec_for(
    config: dict[str, Any],
    declaration: dict[str, Any],
) -> dict[str, Any]:
    values = dict(config["specs"][declaration["spec"]])
    values["events"] = int(declaration["events"])
    return values


def _tasks(config: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world, declaration in config["worlds"].items():
            label = f"{world}::main::{repetition}"
            seed = _derived_seed(int(config["root_seed"]), label)
            tasks.append({
                "task_id": _task_id(int(config["root_seed"]), label),
                "world": world,
                "task_kind": "main",
                "score_target": None,
                "repetition": repetition,
                "seed": seed,
                "disabled": [],
                "spec": _spec_for(config, declaration),
                "estimator": config["estimator"],
            })
            if world.startswith(("cf_d_", "cf_o_", "cf_kp_")):
                targets = (
                    ["condition", "partner"]
                    if world.startswith("cf_o_")
                    else ["distribution"]
                    if world.startswith("cf_d_")
                    else ["path"]
                )
                for target in targets:
                    knockout_label = f"{world}::knockout::{target}::{repetition}"
                    tasks.append({
                        "task_id": _task_id(
                            int(config["root_seed"]),
                            knockout_label,
                        ),
                        "world": world,
                        "task_kind": "knockout",
                        "score_target": target,
                        "repetition": repetition,
                        "seed": seed,
                        "disabled": [target],
                        "spec": _spec_for(config, declaration),
                        "estimator": config["estimator"],
                    })
    return tasks


def _worker(
    task: dict[str, Any],
    truth_dir: str,
    prediction_dir: str,
) -> dict[str, Any]:
    observed, truth = generate_m3_cross_family_world(
        world=str(task["world"]),
        spec=M3CrossFamilySpec(**task["spec"]),
        seed=int(task["seed"]),
        disabled=frozenset(task["disabled"]),
    )
    truth_path = Path(truth_dir) / f"{task['task_id']}.npz"
    np.savez_compressed(
        truth_path,
        **_truth_payload(
            truth,
            {
                "task_id": task["task_id"],
                "task_kind": task["task_kind"],
                "score_target": task["score_target"],
                "repetition": task["repetition"],
                "seed": task["seed"],
            },
        ),
    )
    observation_hash = _array_digest({
        "response_train": observed.response_train,
        "response_test": observed.response_test,
        "condition_train": observed.condition_train,
        "condition_test": observed.condition_test,
        "partner_train": observed.partner_train,
        "partner_test": observed.partner_test,
        "partner_id_train": observed.partner_id_train,
        "partner_id_test": observed.partner_id_test,
    })
    del truth
    estimate = fit_m3_cross_family(
        observed,
        seed=int(task["seed"]) + 503,
        **task["estimator"],
    )
    prediction_path = Path(prediction_dir) / f"{task['task_id']}.npz"
    np.savez_compressed(prediction_path, **_estimate_payload(estimate))
    return {
        "task_id": task["task_id"],
        "observation_sha256": observation_hash,
        "truth_sha256": sha256_file(truth_path),
        "prediction_sha256": sha256_file(prediction_path),
    }


def _seal_payload(
    config_path: Path,
    output_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    preflight_path = ROOT / str(config["preflight_decision"])
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("decision") != config["required_preflight_decision"]:
        raise RuntimeError("required power preflight did not pass")
    revision = git_revision(ROOT)
    files = [config_path, preflight_path, *CODE_PATHS]
    return {
        "seal_version": "m3-cross-family-artifact-seal-v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "estimand_id": config["estimand_id"],
        "status": (
            "ARTIFACT_SEALED_DIRTY_WORKTREE"
            if revision.get("dirty")
            else "ARTIFACT_SEALED_CLEAN_WORKTREE"
        ),
        "repository": revision,
        "files": [
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
        "config_sha256": sha256_file(config_path),
        "preflight_sha256": sha256_file(preflight_path),
        "task_count": len(_tasks(config)),
        "truth_opened": False,
        "claim_boundary": (
            "Artifact seal only. A dirty worktree prevents a git-tag "
            "preregistration claim."
        ),
    }


def _verify_seal(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "seal.json"
    if not path.exists():
        raise FileNotFoundError("seal.json is missing")
    seal = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    for record in seal["files"]:
        candidate = ROOT / record["path"]
        if not candidate.exists():
            failures.append(f"missing:{record['path']}")
        elif sha256_file(candidate) != record["sha256"]:
            failures.append(f"sha256:{record['path']}")
    if failures:
        raise RuntimeError(f"artifact seal verification failed: {failures}")
    return seal


def _mode_seal(
    config_path: Path,
    output_dir: Path,
    config: dict[str, Any],
) -> None:
    if output_dir.exists():
        existing = [
            item for item in output_dir.iterdir()
            if item.name != ".DS_Store"
        ]
        if existing:
            raise RuntimeError("confirmation output directory is not empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    seal = _seal_payload(config_path, output_dir, config)
    (output_dir / "seal.json").write_text(
        json.dumps(seal, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(seal, ensure_ascii=False, indent=2))


def _mode_blind(
    output_dir: Path,
    config: dict[str, Any],
) -> None:
    _verify_seal(output_dir)
    if (output_dir / "TRUTH_OPENED").exists():
        raise RuntimeError("truth was already opened")
    prediction_seal = output_dir / "predictions_sealed.json"
    if prediction_seal.exists():
        raise RuntimeError("predictions are already sealed")
    truth_dir = output_dir / "truth_lockbox"
    prediction_dir = output_dir / "predictions"
    truth_dir.mkdir()
    prediction_dir.mkdir()
    tasks = _tasks(config)
    records: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=int(config["max_workers"])) as pool:
        futures = {
            pool.submit(
                _worker,
                task,
                str(truth_dir),
                str(prediction_dir),
            ): task["task_id"]
            for task in tasks
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            records.append(future.result())
            if completed % 32 == 0:
                print(f"completed {completed}/{len(tasks)}", flush=True)
    records.sort(key=lambda item: str(item["task_id"]))
    payload = {
        "created_utc": datetime.now(UTC).isoformat(),
        "task_count": len(records),
        "records": records,
        "truth_opened": False,
    }
    prediction_seal.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PREDICTIONS_SEALED",
        "task_count": len(records),
    }, indent=2))


def _percentile_ci(
    values: np.ndarray,
    *,
    repetitions: int,
    seed: int,
) -> tuple[float, float]:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean)]
    if not len(clean):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(clean), size=(repetitions, len(clean)))
    means = clean[indices].mean(axis=1)
    return tuple(float(value) for value in np.quantile(means, (0.025, 0.975)))


def _holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for rank, key in enumerate(ordered):
        value = min(1.0, p_values[key] * (count - rank))
        running = max(running, value)
        adjusted[key] = running
    return adjusted


def _verify_prediction_seal(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "predictions_sealed.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for record in payload["records"]:
        task_id = str(record["task_id"])
        truth_path = output_dir / "truth_lockbox" / f"{task_id}.npz"
        prediction_path = output_dir / "predictions" / f"{task_id}.npz"
        if sha256_file(truth_path) != record["truth_sha256"]:
            raise RuntimeError(f"truth hash mismatch: {task_id}")
        if sha256_file(prediction_path) != record["prediction_sha256"]:
            raise RuntimeError(f"prediction hash mismatch: {task_id}")
    return payload


def _open_rows(output_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for truth_path in sorted((output_dir / "truth_lockbox").glob("*.npz")):
        task_id = truth_path.stem
        prediction_path = output_dir / "predictions" / f"{task_id}.npz"
        truth, metadata = _load_truth(truth_path)
        estimate = _load_estimate(prediction_path)
        audited = audit_m3_cross_family(estimate, truth)
        if metadata["task_kind"] == "knockout":
            audited = [
                row for row in audited
                if row["target"] == metadata["score_target"]
            ]
        for row in audited:
            validity_pass = bool(truth.validity.get("finite", False))
            for key in (
                "density_nonnegative",
                "theoretical_moments_through_degree_four_matched",
                "poly3_projection_constructed_zero",
            ):
                if key in truth.validity:
                    validity_pass = validity_pass and bool(truth.validity[key])
            for key in (
                "second_order_max_range_train",
                "second_order_max_range_test",
            ):
                if key in truth.validity:
                    validity_pass = validity_pass and (
                        float(truth.validity[key]) <= 1e-8
                    )
            rows.append({
                "task_id": task_id,
                "task_kind": metadata["task_kind"],
                "score_target": metadata["score_target"],
                "repetition": metadata["repetition"],
                "seed": metadata["seed"],
                "validity_json": json.dumps(truth.validity, sort_keys=True),
                "validity_pass": validity_pass,
                **row,
            })
    return pd.DataFrame(rows)


def _confirmation_decision(
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    gates = config["confirmation_gates"]
    bootstrap = int(gates["bootstrap_repetitions"])
    main = metrics[
        (metrics["task_kind"] == "main")
        & (metrics["target"] != "null")
        & (~metrics["exact_alias"])
    ]
    knockouts = metrics[metrics["task_kind"] == "knockout"]
    records: list[dict[str, Any]] = []
    sign_p: dict[str, float] = {}
    for (world, target), frame in main.groupby(["world", "target"]):
        key = f"{world}::{target}"
        knockout = knockouts[
            (knockouts["world"] == world)
            & (knockouts["target"] == target)
        ]
        row: dict[str, Any] = {
            "key": key,
            "world": world,
            "target": target,
            "seeds": frame["seed"].nunique(),
            "expected_auc": float(frame["expected_auc"].mean()),
            "cheap_auc": float(frame["cheap_auc"].mean()),
            "expected_geometry": float(frame["expected_geometry"].mean()),
            "heldout_increment": float(frame["heldout_increment"].mean()),
            "positive_seeds": int(np.sum(frame["heldout_increment"] > 0.0)),
            "off_target_geometry": float(
                np.nanmean(np.abs(frame["off_target_geometry"]))
            ) if np.any(np.isfinite(frame["off_target_geometry"])) else float("nan"),
            "knockout_geometry": float(knockout["expected_geometry"].mean()),
            "validity_fraction": float(frame["validity_pass"].mean()),
            "refusal_max": int(frame["refusal_count"].max()),
        }
        for metric in (
            "expected_auc",
            "cheap_auc",
            "expected_geometry",
            "heldout_increment",
            "off_target_geometry",
        ):
            low, high = _percentile_ci(
                frame[metric].to_numpy(),
                repetitions=bootstrap,
                seed=_derived_seed(int(config["root_seed"]), f"bootstrap::{key}::{metric}"),
            )
            row[f"{metric}_ci_low"] = low
            row[f"{metric}_ci_high"] = high
        low, high = _percentile_ci(
            knockout["expected_geometry"].to_numpy(),
            repetitions=bootstrap,
            seed=_derived_seed(int(config["root_seed"]), f"bootstrap::{key}::knockout"),
        )
        row["knockout_geometry_ci_low"] = low
        row["knockout_geometry_ci_high"] = high
        sign_p[key] = float(binomtest(
            row["positive_seeds"],
            int(row["seeds"]),
            p=0.5,
            alternative="greater",
        ).pvalue)
        records.append(row)
    adjusted = _holm_adjust(sign_p)
    checks: dict[str, bool] = {}
    diagnostics: dict[str, Any] = {}
    for row in records:
        key = str(row["key"])
        cell_checks = {
            "valid": row["validity_fraction"] == 1.0,
            "no_refusal": row["refusal_max"] == 0,
            "auc": row["expected_auc_ci_low"]
            > gates["minimum_expected_auc_ci_lower"],
            "geometry": row["expected_geometry_ci_low"]
            > gates["minimum_geometry_ci_lower"],
            "increment": row["heldout_increment_ci_low"]
            > gates["minimum_increment_ci_lower"],
            "positive_seeds": row["positive_seeds"]
            >= gates["minimum_positive_seeds"],
            "holm_sign": adjusted[key] < 0.05,
            "cheap_mean": abs(row["cheap_auc"] - 0.5)
            < gates["maximum_cheap_auc_bias"],
            "cheap_ci": row["cheap_auc_ci_low"] <= 0.5
            <= row["cheap_auc_ci_high"],
            "knockout_mean": abs(row["knockout_geometry"])
            < gates["maximum_knockout_mean_abs"],
            "knockout_ci": row["knockout_geometry_ci_low"] <= 0.0
            <= row["knockout_geometry_ci_high"],
        }
        if np.isfinite(row["off_target_geometry"]):
            cell_checks["cross_talk"] = (
                row["off_target_geometry_ci_high"]
                < gates["maximum_off_target_ci_upper"]
            )
        checks[key] = all(cell_checks.values())
        diagnostics[key] = {
            "checks": cell_checks,
            "holm_sign_p": adjusted[key],
            **row,
        }

    aliases = metrics[
        (metrics["task_kind"] == "main")
        & metrics["exact_alias"]
    ]
    for (world, target), frame in aliases.groupby(["world", "target"]):
        key = f"{world}::{target}"
        auc = float(frame["expected_auc"].mean())
        geometry = float(np.mean(np.abs(frame["expected_geometry"])))
        auc_ci = _percentile_ci(
            frame["expected_auc"].to_numpy(),
            repetitions=bootstrap,
            seed=_derived_seed(int(config["root_seed"]), f"alias::{key}"),
        )
        alias_checks = {
            "valid": bool(frame["validity_pass"].all()),
            "no_refusal": int(frame["refusal_count"].max()) == 0,
            "auc_mean": abs(auc - 0.5) < gates["maximum_alias_auc_bias"],
            "auc_ci": auc_ci[0] <= 0.5 <= auc_ci[1],
            "geometry": geometry < gates["maximum_alias_geometry_abs"],
        }
        checks[key] = all(alias_checks.values())
        diagnostics[key] = {
            "checks": alias_checks,
            "expected_auc": auc,
            "expected_auc_ci": auc_ci,
            "expected_geometry_abs": geometry,
        }

    null = metrics[
        (metrics["task_kind"] == "main")
        & (metrics["target"] == "null")
    ]
    for family, frame in null.groupby("expected_family"):
        key = f"null::{family}"
        auc = float(frame["expected_auc"].mean())
        auc_ci = _percentile_ci(
            frame["expected_auc"].to_numpy(),
            repetitions=bootstrap,
            seed=_derived_seed(int(config["root_seed"]), key),
        )
        null_checks = {
            "valid": bool(frame["validity_pass"].all()),
            "no_refusal": int(frame["refusal_count"].max()) == 0,
            "auc_mean": abs(auc - 0.5) < gates["maximum_null_auc_bias"],
            "auc_ci": auc_ci[0] <= 0.5 <= auc_ci[1],
        }
        checks[key] = all(null_checks.values())
        diagnostics[key] = {
            "checks": null_checks,
            "expected_auc": auc,
            "expected_auc_ci": auc_ci,
        }
    summary = pd.DataFrame(records)
    return summary, {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_CROSS_FAMILY_ARTIFACT_SEALED_CONFIRMATION_PASS"
            if all(checks.values())
            else "M3_CROSS_FAMILY_ARTIFACT_SEALED_CONFIRMATION_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "truth_opened_once": True,
        "claim_boundary": (
            "Cross-family synthetic estimator existence only. No human-text, "
            "personality, macro-construct, or clinical claim."
        ),
    }


def _mode_open(
    output_dir: Path,
    config: dict[str, Any],
) -> None:
    seal = _verify_seal(output_dir)
    _verify_prediction_seal(output_dir)
    marker = output_dir / "TRUTH_OPENED"
    if marker.exists():
        raise RuntimeError("truth has already been opened")
    marker.write_text(
        datetime.now(UTC).isoformat() + "\n",
        encoding="utf-8",
    )
    metrics = _open_rows(output_dir)
    summary, decision = _confirmation_decision(metrics, config)
    metrics.to_csv(output_dir / "metrics.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = f"""# SUICA M3 Artifact-Sealed Cross-Family Confirmation

Decision: `{decision["decision"]}`

Seal status: `{seal["status"]}`

## Registered target summary

{summary.to_markdown(index=False)}

## Failed conjunction cells

{os.linesep.join(f"- `{key}`" for key, value in decision["checks"].items() if not value) or "- None"}

## Claim boundary

This one-time truth-open result concerns cross-family synthetic recovery only.
It does not license human-text persistence, personality interpretation,
construct validity, or clinical use. The dirty-worktree artifact seal is not
a git-tag preregistration.
"""
    (ROOT / "reports" / "SUICA_M3_CROSS_FAMILY_CONFIRMATION.md").write_text(
        report,
        encoding="utf-8",
    )
    write_artifact_inventory(
        output_dir,
        output_dir / "artifact_inventory.json",
        exclude_relative_paths=("artifact_inventory.json",),
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


def main() -> None:
    raise RuntimeError(
        "Retired unsafe V1 confirmation runner. Use the separate M3-V4 "
        "seal/generate/fit/open scripts; V1 does not provide physical truth "
        "isolation or sealed-config enforcement."
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("seal", "blind", "open"), required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_cross_family_confirmation.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_cross_family_confirmation",
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.mode == "seal":
        _mode_seal(args.config, args.output_dir, config)
    elif args.mode == "blind":
        _mode_blind(args.output_dir, config)
    else:
        _mode_open(args.output_dir, config)


if __name__ == "__main__":
    main()
