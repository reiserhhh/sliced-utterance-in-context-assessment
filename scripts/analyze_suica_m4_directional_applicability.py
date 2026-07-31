#!/usr/bin/env python3
"""Aggregate sealed directional cells and evaluate scalar/vector policies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import _load  # noqa: E402
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    runtime_fingerprint,
    verify_source_hash_manifest,
)


def _oof_predictions(
    frame: pd.DataFrame,
    feature_names: list[str],
    groups: pd.Series,
    config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    x = frame[feature_names].to_numpy(dtype=float)
    y = frame["forced_r_gain"].to_numpy(dtype=float)
    harmful = frame["harmful"].astype(int).to_numpy()
    predicted = np.full(len(frame), np.nan)
    probability = np.full(len(frame), np.nan)
    model = config["applicability_model"]
    splitter = LeaveOneGroupOut()
    for train, test in splitter.split(x, y, groups.to_numpy()):
        regression = make_pipeline(
            StandardScaler(),
            Ridge(alpha=float(model["ridge_alpha"])),
        )
        regression.fit(x[train], y[train])
        predicted[test] = regression.predict(x[test])
        classes = np.unique(harmful[train])
        if len(classes) < 2:
            probability[test] = float(classes[0])
        else:
            classifier = make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    C=float(model["logistic_c"]),
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=0,
                ),
            )
            classifier.fit(x[train], harmful[train])
            probability[test] = classifier.predict_proba(x[test])[:, 1]
    if not np.isfinite(predicted).all() or not np.isfinite(probability).all():
        raise ValueError("OOF applicability predictions are incomplete")
    return predicted, probability


def _cluster_mean_interval(
    frame: pd.DataFrame,
    column: str,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float, float]:
    values = frame.groupby("repetition", sort=True)[column].mean().to_numpy()
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    draws = np.mean(values[indices], axis=1)
    return (
        float(np.mean(values)),
        float(np.quantile(draws, 0.025)),
        float(np.quantile(draws, 0.975)),
    )


def _cluster_auc_interval(
    frame: pd.DataFrame,
    probability_column: str,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float, float, float]:
    truth = frame["harmful"].astype(int).to_numpy()
    score = frame[probability_column].to_numpy(dtype=float)
    if len(np.unique(truth)) < 2:
        return float("nan"), float("nan"), float("nan"), 0.0
    point = float(roc_auc_score(truth, score))
    groups = [
        indices.to_numpy()
        for _, indices in frame.groupby("repetition", sort=True).groups.items()
    ]
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repetitions):
        chosen = rng.integers(0, len(groups), size=len(groups))
        indices = np.concatenate([groups[index] for index in chosen])
        current = truth[indices]
        if len(np.unique(current)) < 2:
            continue
        values.append(roc_auc_score(current, score[indices]))
    if not values:
        return point, float("nan"), float("nan"), 0.0
    return (
        point,
        float(np.quantile(values, 0.025)),
        float(np.quantile(values, 0.975)),
        len(values) / repetitions,
    )


def _model_metrics(
    frame: pd.DataFrame,
    *,
    model_name: str,
    cutoff: float,
    seed: int,
    bootstrap_repetitions: int,
) -> dict[str, float]:
    rows = frame.copy()
    predicted = rows[f"{model_name}_predicted_gain"].to_numpy(dtype=float)
    truth = rows["forced_r_gain"].to_numpy(dtype=float)
    use_r = predicted >= cutoff
    rows["policy_value"] = np.where(use_r, truth, 0.0)
    rows["routing_value"] = np.where(use_r, 0.0, -truth)
    policy, policy_lcb, policy_ucb = _cluster_mean_interval(
        rows,
        "policy_value",
        seed=seed,
        repetitions=bootstrap_repetitions,
    )
    routing, routing_lcb, routing_ucb = _cluster_mean_interval(
        rows,
        "routing_value",
        seed=seed + 1,
        repetitions=bootstrap_repetitions,
    )
    auc, auc_lcb, auc_ucb, auc_valid = _cluster_auc_interval(
        rows,
        f"{model_name}_harm_probability",
        seed=seed + 2,
        repetitions=bootstrap_repetitions,
    )
    return {
        "r2": float(r2_score(truth, predicted)),
        "spearman_rho": float(spearmanr(truth, predicted).statistic),
        "mae": float(mean_absolute_error(truth, predicted)),
        "harm_auc": auc,
        "harm_auc_lcb": auc_lcb,
        "harm_auc_ucb": auc_ucb,
        "harm_auc_bootstrap_valid_rate": auc_valid,
        "policy_value_over_b0": policy,
        "policy_value_lcb": policy_lcb,
        "policy_value_ucb": policy_ucb,
        "routing_value_over_forced_r": routing,
        "routing_value_lcb": routing_lcb,
        "routing_value_ucb": routing_ucb,
        "use_r_rate": float(np.mean(use_r)),
    }


def _paired_delta(
    frame: pd.DataFrame,
    *,
    left: str,
    right: str,
    cutoff: float,
    seed: int,
    repetitions: int,
) -> dict[str, float]:
    truth = frame["forced_r_gain"].to_numpy(dtype=float)
    left_use = frame[f"{left}_predicted_gain"].to_numpy() >= cutoff
    right_use = frame[f"{right}_predicted_gain"].to_numpy() >= cutoff
    rows = frame[["repetition"]].copy()
    rows["policy_delta"] = (
        np.where(left_use, truth, 0.0)
        - np.where(right_use, truth, 0.0)
    )
    rows["routing_delta"] = (
        np.where(left_use, 0.0, -truth)
        - np.where(right_use, 0.0, -truth)
    )
    policy, policy_lcb, policy_ucb = _cluster_mean_interval(
        rows,
        "policy_delta",
        seed=seed,
        repetitions=repetitions,
    )
    routing, routing_lcb, routing_ucb = _cluster_mean_interval(
        rows,
        "routing_delta",
        seed=seed + 1,
        repetitions=repetitions,
    )
    left_auc = roc_auc_score(
        frame["harmful"].astype(int),
        frame[f"{left}_harm_probability"],
    )
    right_auc = roc_auc_score(
        frame["harmful"].astype(int),
        frame[f"{right}_harm_probability"],
    )
    return {
        "policy_value_delta": policy,
        "policy_value_delta_lcb": policy_lcb,
        "policy_value_delta_ucb": policy_ucb,
        "routing_value_delta": routing,
        "routing_value_delta_lcb": routing_lcb,
        "routing_value_delta_ucb": routing_ucb,
        "harm_auc_delta": float(left_auc - right_auc),
    }


def _evaluate_split(
    frame: pd.DataFrame,
    feature_names: list[str],
    *,
    group_column: str,
    config: dict[str, Any],
    seed: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    rows = frame.reset_index(drop=True).copy()
    for name, features in (
        ("S1", ["support_minimum_coverage"]),
        ("Q", feature_names),
    ):
        predicted, probability = _oof_predictions(
            rows,
            features,
            rows[group_column],
            config,
        )
        rows[f"{name}_predicted_gain"] = predicted
        rows[f"{name}_harm_probability"] = probability
    cutoff = float(config["applicability_model"]["route_gain_cutoff"])
    repetitions = int(config["bootstrap_repetitions"])
    diagnostics = {
        name: _model_metrics(
            rows,
            model_name=name,
            cutoff=cutoff,
            seed=seed + index * 10,
            bootstrap_repetitions=repetitions,
        )
        for index, name in enumerate(("S1", "Q"))
    }
    diagnostics["Q_minus_S1"] = _paired_delta(
        rows,
        left="Q",
        right="S1",
        cutoff=cutoff,
        seed=seed + 100,
        repetitions=repetitions,
    )
    historical_use = rows["historical_accept"].astype(bool).to_numpy()
    truth = rows["forced_r_gain"].to_numpy(dtype=float)
    historical = rows[["repetition"]].copy()
    historical["policy"] = np.where(historical_use, truth, 0.0)
    historical["routing"] = np.where(historical_use, 0.0, -truth)
    u, u_lcb, u_ucb = _cluster_mean_interval(
        historical,
        "policy",
        seed=seed + 200,
        repetitions=repetitions,
    )
    v, v_lcb, v_ucb = _cluster_mean_interval(
        historical,
        "routing",
        seed=seed + 201,
        repetitions=repetitions,
    )
    diagnostics["S0_historical"] = {
        "policy_value_over_b0": u,
        "policy_value_lcb": u_lcb,
        "policy_value_ucb": u_ucb,
        "routing_value_over_forced_r": v,
        "routing_value_lcb": v_lcb,
        "routing_value_ucb": v_ucb,
        "use_r_rate": float(np.mean(historical_use)),
    }
    return diagnostics, rows


def _passes(diagnostics: dict[str, Any], targets: dict[str, float]) -> bool:
    q = diagnostics["Q"]
    delta = diagnostics["Q_minus_S1"]
    return bool(
        q["policy_value_lcb"] > targets["minimum_policy_value_lcb"]
        and q["routing_value_lcb"] > targets["minimum_routing_value_lcb"]
        and delta["policy_value_delta_lcb"]
        > targets["minimum_policy_delta_lcb"]
        and q["harm_auc_lcb"] >= targets["minimum_harm_auc_lcb"]
        and delta["harm_auc_delta"] >= targets["minimum_harm_auc_gain"]
        and q["r2"] > targets["minimum_gain_r2"]
    )


def _report(decision: dict[str, Any], metrics: pd.DataFrame) -> str:
    main = metrics[metrics["world_type"].eq("main")]
    by_direction = (
        main.groupby(
            ["target_count", "direction_mode"],
            dropna=False,
            sort=True,
        )[["forced_r_gain", "oracle_error", "harmful"]]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    by_world = (
        main.groupby("world", sort=True)[["forced_r_gain", "harmful"]]
        .mean()
        .reset_index()
        .to_markdown(index=False, floatfmt=".4f")
    )
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4 Fixed-Coverage Directional Applicability

## Decision

`{decision["decision"]}`

This fresh development experiment holds exact support amount fixed while
changing only the pre-response direction of departure. It compares the
historical scalar threshold (`S0`), a fold-local scalar learner (`S1`), and
the preregistered vector signature (`Q`).

## Diagnostics

{diagnostics}

## Direction summary

{by_direction}

## World summary

{by_world}

## Interpretation

{decision["interpretation"]}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--shard-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()
    config = _load(args.config)
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    manifest_path = bundle_root / "stage_a_manifest.json"
    if file_sha256(manifest_path) != args.expected_manifest_sha256:
        raise ValueError("Stage-A directional manifest hash mismatch")
    manifest = _load(manifest_path)
    if manifest["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after directional sealing")
    if manifest["runtime"] != runtime_fingerprint():
        raise ValueError("runtime changed after directional sealing")
    verify_source_hash_manifest(ROOT, manifest["source_sha256"])

    shard_root = args.shard_directory
    if not shard_root.is_absolute():
        shard_root = ROOT / shard_root
    frames = []
    covered: list[int] = []
    for metadata_path in sorted(shard_root.glob("metrics_rep_*.json")):
        metadata = _load(metadata_path)
        if metadata["manifest_sha256"] != args.expected_manifest_sha256:
            raise ValueError("shard belongs to a different Stage-A manifest")
        csv_path = metadata_path.with_suffix(".csv")
        if file_sha256(csv_path) != metadata["metrics_sha256"]:
            raise ValueError("shard metrics hash mismatch")
        frames.append(pd.read_csv(csv_path))
        covered.extend(range(
            int(metadata["repetition_start"]),
            int(metadata["repetition_end"]),
        ))
    expected = list(range(int(config["repetitions"])))
    if sorted(covered) != expected:
        raise ValueError(f"repetition coverage mismatch: {sorted(covered)}")
    metrics = pd.concat(frames, ignore_index=True)
    if len(metrics) != len(manifest["cells"]):
        raise ValueError("scored rows do not match sealed cells")
    main = metrics[metrics["world_type"].eq("main")].reset_index(drop=True)
    null = metrics[metrics["world_type"].eq("null")]
    feature_names = sorted(manifest["cells"][0]["signature"])
    seed = int(config["bootstrap_seed"])
    lowo, lowo_predictions = _evaluate_split(
        main,
        feature_names,
        group_column="world",
        config=config,
        seed=seed,
    )
    loro, loro_predictions = _evaluate_split(
        main,
        feature_names,
        group_column="repetition",
        config=config,
        seed=seed + 10_000,
    )
    integrity = {
        "sealed_cells": len(metrics),
        "main_cells": len(main),
        "null_cells": len(null),
        "maximum_basis_replay_error": float(metrics["basis_replay_error"].max()),
        "maximum_signature_replay_error": float(metrics["signature_replay_error"].max()),
        "maximum_response_identity_error": float(metrics["response_identity_error"].max()),
        "maximum_null_absolute_gain": float(null["forced_r_gain"].abs().max()),
    }
    targets = config["candidate_targets"]
    integrity_pass = bool(
        integrity["sealed_cells"] == 432
        and integrity["main_cells"] == 360
        and integrity["maximum_basis_replay_error"] <= 1e-12
        and integrity["maximum_signature_replay_error"] <= 1e-12
        and integrity["maximum_response_identity_error"] <= 1e-12
        and integrity["maximum_null_absolute_gain"]
        <= targets["maximum_null_absolute_gain"]
    )
    lowo_pass = _passes(lowo, targets)
    loro_pass = _passes(loro, targets)
    if not integrity_pass:
        name = "M4_C35_DIRECTIONAL_INTEGRITY_STOP"
        interpretation = "Integrity or null controls failed; no policy result is interpretable."
    elif lowo_pass and loro_pass:
        name = "M4_C35_VECTOR_DOMAIN_CANDIDATE"
        interpretation = (
            "Q generalizes across both unseen worlds and unseen repetitions. "
            "A separate frozen routed-policy confirmation is warranted."
        )
    elif loro_pass and not lowo_pass:
        name = "M4_C35_WORLD_DEPENDENT_DOMAIN"
        interpretation = (
            "Q interpolates repeated worlds but fails unseen-world transport. "
            "Applicability is mechanism-local, not universal."
        )
    else:
        name = "M4_C35_PRE_RESPONSE_DOMAIN_NOT_IDENTIFIED"
        interpretation = (
            "The present pre-response signature does not identify a safe, "
            "positive-utility R/B0 routing domain. Stop threshold tuning and "
            "retain direction as descriptive applicability metadata."
        )
    decision = {
        "estimand_id": config["estimand_id"],
        "phase": "development",
        "decision": name,
        "diagnostics": {
            "integrity": integrity,
            "leave_one_world_out": lowo,
            "leave_one_repetition_out": loro,
            "feature_count": len(feature_names),
            "feature_names": feature_names,
            "lowo_pass": lowo_pass,
            "loro_pass": loro_pass,
        },
        "interpretation": interpretation,
        "confirmation_status": (
            "SEPARATE_CONFIRMATION_REQUIRED"
            if name == "M4_C35_VECTOR_DOMAIN_CANDIDATE"
            else "NOT_AUTHORIZED"
        ),
        "claim_boundary": (
            "Finite-synthetic fixed-coverage development only. No natural-text, "
            "personality, behavioral, diagnostic, clinical, or M4-D claim."
        ),
    }
    output = args.output_directory or Path(config["output_directory"])
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "cell_metrics.csv", index=False)
    lowo_predictions.to_csv(output / "predictions_leave_one_world_out.csv", index=False)
    loro_predictions.to_csv(output / "predictions_leave_one_repetition_out.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = args.report_path or Path(config["report_path"])
    if not report.is_absolute():
        report = ROOT / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, metrics), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
