#!/usr/bin/env python3
"""Pilot scalar versus vector pre-response applicability signatures."""
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

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _load,
    _rcca_parameters,
)
from suica_core.m4_applicability_signature import (  # noqa: E402
    m4_applicability_signature,
)
from suica_core.m4_boundary_ecology import (  # noqa: E402
    intervene_evaluation_support,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    pre_response_digest,
    read_basis_bundle,
    runtime_fingerprint,
    verify_source_hash_manifest,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    fit_response_safe_rcca_chart,
)


def _replay(observed, chart, metadata, config):
    if metadata["target_count"] is None:
        current = observed
    else:
        current = intervene_evaluation_support(
            observed,
            chart,
            target_count=int(metadata["target_count"]),
            amplitude_multiplier=float(
                config["support_intervention_amplitude"]
            ),
        ).observed
    if pre_response_digest(current) != metadata["pre_response_digest"]:
        raise ValueError("signature replay does not match the Stage-A seal")
    return current


def _oof_predictions(
    frame: pd.DataFrame,
    feature_names: list[str],
    groups: pd.Series,
) -> tuple[np.ndarray, np.ndarray]:
    x = frame[feature_names].to_numpy(dtype=float)
    y = frame["forced_r_gain"].to_numpy(dtype=float)
    harmful = frame["harmful"].astype(int).to_numpy()
    predicted = np.full(len(frame), np.nan)
    probability = np.full(len(frame), np.nan)
    splitter = LeaveOneGroupOut()
    for train, test in splitter.split(x, y, groups.to_numpy()):
        regression = make_pipeline(
            StandardScaler(),
            Ridge(alpha=10.0),
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
                    C=0.1,
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


def _metrics(
    frame: pd.DataFrame,
    predicted: np.ndarray,
    probability: np.ndarray,
    *,
    harm_threshold: float,
) -> dict[str, float]:
    truth = frame["forced_r_gain"].to_numpy(dtype=float)
    harmful = frame["harmful"].astype(int).to_numpy()
    use_r = predicted >= harm_threshold
    routing_value = np.where(use_r, 0.0, -truth)
    policy_value = np.where(use_r, truth, 0.0)
    return {
        "r2": float(r2_score(truth, predicted)),
        "spearman_rho": float(spearmanr(truth, predicted).statistic),
        "mae": float(mean_absolute_error(truth, predicted)),
        "harm_auc": (
            float(roc_auc_score(harmful, probability))
            if len(np.unique(harmful)) > 1
            else float("nan")
        ),
        "routing_value_over_forced_r": float(np.mean(routing_value)),
        "policy_value_over_b0": float(np.mean(policy_value)),
        "use_r_rate": float(np.mean(use_r)),
    }


def _evaluate(
    frame: pd.DataFrame,
    feature_names: list[str],
    *,
    group_column: str,
    harm_threshold: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    rows = frame.reset_index(drop=True).copy()
    scalar_features = ["support_minimum_coverage"]
    outputs = {}
    predictions = rows[
        ["repetition", "world", "variant", "forced_r_gain", "harmful"]
    ].copy()
    for model, names in (
        ("scalar", scalar_features),
        ("vector_q", feature_names),
    ):
        predicted, probability = _oof_predictions(
            rows,
            names,
            rows[group_column],
        )
        outputs[model] = _metrics(
            rows,
            predicted,
            probability,
            harm_threshold=harm_threshold,
        )
        predictions[f"{model}_predicted_gain"] = predicted
        predictions[f"{model}_harm_probability"] = probability
        predictions[f"{model}_use_r"] = predicted >= harm_threshold
    historical_use = (
        rows["support_minimum_coverage"].to_numpy() >= 0.8
    )
    truth = rows["forced_r_gain"].to_numpy(dtype=float)
    outputs["historical_threshold"] = {
        "routing_value_over_forced_r": float(np.mean(
            np.where(historical_use, 0.0, -truth)
        )),
        "policy_value_over_b0": float(np.mean(
            np.where(historical_use, truth, 0.0)
        )),
        "use_r_rate": float(np.mean(historical_use)),
    }
    outputs["vector_minus_scalar"] = {
        key: outputs["vector_q"][key] - outputs["scalar"][key]
        for key in (
            "r2",
            "spearman_rho",
            "harm_auc",
            "routing_value_over_forced_r",
            "policy_value_over_b0",
        )
    }
    return outputs, predictions


def _report(decision: dict[str, Any]) -> str:
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4 Vector Applicability Signature Pilot

## Decision

`{decision["decision"]}`

This post-seal development pilot compares scalar coverage with a fixed
response-safe vector signature `q`. All preprocessing and model fitting are
inside leave-one-group-out folds.

## Diagnostics

{diagnostics}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    args = parser.parse_args()
    config = _load(args.config)
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    manifest_path = bundle_root / "stage_a_manifest.json"
    if file_sha256(manifest_path) != args.expected_manifest_sha256:
        raise ValueError("boundary manifest hash mismatch")
    manifest = _load(manifest_path)
    if manifest["config_sha256"] != file_sha256(args.config):
        raise ValueError("boundary config changed")
    if manifest["runtime"] != runtime_fingerprint():
        raise ValueError("boundary runtime changed")
    verify_source_hash_manifest(ROOT, manifest["source_sha256"])

    spec = M4ChartEcologySpec(**config["spec"])
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for cell in manifest["cells"]:
        key = (int(cell["repetition"]), str(cell["world"]))
        grouped.setdefault(key, []).append(cell)
    feature_rows = []
    for _, cells in sorted(grouped.items()):
        first = cells[0]
        observed = generate_m4_pre_response_condition(
            world=first["generator_world"],
            spec=spec,
            seed=int(first["seed"]),
        )
        chart = fit_response_safe_rcca_chart(
            observed,
            **_rcca_parameters(config, seed=int(first["seed"])),
        )
        for metadata in cells:
            current = _replay(observed, chart, metadata, config)
            bases = read_basis_bundle(
                bundle_root / metadata["bundle"],
                expected_sha256=metadata["bundle_sha256"],
            )
            signature = m4_applicability_signature(
                current,
                chart,
                bases,
            )
            feature_rows.append(
                {
                    "repetition": int(metadata["repetition"]),
                    "world": str(metadata["world"]),
                    "world_type": str(metadata["world_type"]),
                    "variant": str(metadata["variant"]),
                    **signature,
                }
            )
    features = pd.DataFrame(feature_rows)
    metrics_path = args.metrics
    if not metrics_path.is_absolute():
        metrics_path = ROOT / metrics_path
    outcomes = pd.read_csv(metrics_path)
    rows = features.merge(
        outcomes[
            [
                "repetition",
                "world",
                "world_type",
                "variant",
                "stratum",
                "forced_r_gain",
                "harmful",
            ]
        ],
        on=["repetition", "world", "world_type", "variant"],
        validate="one_to_one",
    )
    eligible = rows[rows["stratum"].eq("eligible")].reset_index(drop=True)
    identifier = {
        "repetition",
        "world",
        "world_type",
        "variant",
        "stratum",
        "forced_r_gain",
        "harmful",
    }
    feature_names = [
        name for name in features.columns if name not in identifier
    ]
    lowo, lowo_predictions = _evaluate(
        eligible,
        feature_names,
        group_column="world",
        harm_threshold=float(config["harm_threshold"]),
    )
    loro, loro_predictions = _evaluate(
        eligible,
        feature_names,
        group_column="repetition",
        harm_threshold=float(config["harm_threshold"]),
    )
    lowo_q = lowo["vector_q"]
    loro_q = loro["vector_q"]
    lowo_delta = lowo["vector_minus_scalar"]
    loro_delta = loro["vector_minus_scalar"]
    lowo_pass = (
        lowo_q["harm_auc"] >= 0.65
        and lowo_q["r2"] > 0.10
        and lowo_q["routing_value_over_forced_r"] > 0.0
        and lowo_delta["harm_auc"] >= 0.05
        and lowo_delta["routing_value_over_forced_r"] > 0.0
    )
    loro_pass = (
        loro_q["harm_auc"] >= 0.65
        and loro_q["r2"] > 0.10
        and loro_q["routing_value_over_forced_r"] > 0.0
        and loro_delta["harm_auc"] >= 0.05
        and loro_delta["routing_value_over_forced_r"] > 0.0
    )
    if lowo_pass and loro_pass:
        decision_name = "VECTOR_SIGNATURE_PILOT_PROMISING"
    elif loro_pass and not lowo_pass:
        decision_name = "WORLD_DEPENDENT_SIGNATURE"
    else:
        decision_name = "VECTOR_SIGNATURE_NOT_RESOLVED"
    decision = {
        "estimand_id": (
            "SUICA_M4_C35_R2C_VECTOR_APPLICABILITY_SIGNATURE_PILOT_V1"
        ),
        "phase": "post_seal_development",
        "decision": decision_name,
        "diagnostics": {
            "leave_one_world_out": lowo,
            "leave_one_repetition_out": loro,
            "feature_count": len(feature_names),
            "eligible_cells": len(eligible),
            "feature_names": feature_names,
        },
        "claim_boundary": (
            "Post-seal finite-synthetic pilot only. It can prioritize a "
            "fresh vector-applicability experiment but cannot validate a "
            "gate or support natural-text, personality, behavioral, "
            "clinical, or M4-D claims."
        ),
    }
    output = args.output_directory
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    rows.to_csv(output / "features_with_outcomes.csv", index=False)
    lowo_predictions.to_csv(
        output / "predictions_leave_one_world_out.csv",
        index=False,
    )
    loro_predictions.to_csv(
        output / "predictions_leave_one_repetition_out.csv",
        index=False,
    )
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = args.report_path
    if not report.is_absolute():
        report = ROOT / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
