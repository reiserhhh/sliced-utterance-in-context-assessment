#!/usr/bin/env python3
"""Run the post-hoc Gate-0 audit before expensive R2D simulation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_INPUT = (
    ROOT
    / "results"
    / "v8_permutation_orbit_frontier"
    / "v37h4d_r2c_discovery_10800rows_20260727"
)
DEFAULT_CONFIG = (
    ROOT / "configs/v8_r2d_conditional_target_preflight.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_posterior_predictive_orbit"
    / "v37h4d_r2d_gate0_posthoc_20260727"
)


def _logit_probability(values: pd.Series) -> np.ndarray:
    epsilon = 1e-4
    probability = np.clip(
        values.to_numpy(dtype=float),
        epsilon,
        1.0 - epsilon,
    )
    return np.log(probability / (1.0 - probability))[:, None]


def _binary_losses(
    response: np.ndarray,
    probability: np.ndarray,
) -> np.ndarray:
    p = np.clip(np.asarray(probability, dtype=float), 1e-12, 1 - 1e-12)
    y = np.asarray(response, dtype=float)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def _crossfit_predictions(
    rows: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    cell_columns = list(map(str, config["cell_columns"]))
    cell_key = rows[cell_columns].astype(str).agg("|".join, axis=1)
    cell_matrix = pd.get_dummies(
        rows[cell_columns].astype(str),
        drop_first=False,
        dtype=float,
    ).to_numpy()
    orbit = _logit_probability(rows["orbit_rejection_probability"])
    mechanism = np.column_stack([
        orbit,
        rows[list(map(str, config["mechanism_columns"]))].to_numpy(
            dtype=float
        ),
    ])
    oracle = rows[
        list(map(str, config["oracle_columns"]))
    ].to_numpy(dtype=float)
    response = rows["crc_or_hc_detected"].to_numpy(dtype=int)
    groups = rows["base_id"].to_numpy()
    output = pd.DataFrame({
        "base_id": groups,
        "cell_key": cell_key,
        "response": response,
        "cell_probability": np.nan,
        "platt_orbit_probability": np.nan,
        "mechanism_probability": np.nan,
        "oracle_probability": np.nan,
    })
    variants = {
        "platt_orbit_probability": orbit,
        "mechanism_probability": mechanism,
        "oracle_probability": oracle,
    }
    splitter = GroupKFold(n_splits=int(config["folds"]))
    for train, test in splitter.split(cell_matrix, response, groups):
        train_mean = pd.Series(
            response[train],
            index=cell_key.iloc[train].to_numpy(),
        ).groupby(level=0).mean()
        output.loc[test, "cell_probability"] = [
            train_mean.get(key, float(response[train].mean()))
            for key in cell_key.iloc[test]
        ]
        for name, extra in variants.items():
            features = np.column_stack([cell_matrix, extra])
            scaler = StandardScaler()
            train_features = scaler.fit_transform(features[train])
            test_features = scaler.transform(features[test])
            model = LogisticRegression(
                C=float(config["logistic_c"]),
                solver="lbfgs",
                max_iter=2000,
            )
            model.fit(train_features, response[train])
            output.loc[test, name] = model.predict_proba(
                test_features
            )[:, 1]
    return output


def _within_cell_auc(
    predictions: pd.DataFrame,
    column: str,
) -> dict[str, float]:
    values = []
    for _, group in predictions.groupby("cell_key"):
        if group["response"].nunique() == 2:
            values.append(
                roc_auc_score(group["response"], group[column])
            )
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "eligible_cells": int(len(values)),
    }


def _cluster_gain(
    predictions: pd.DataFrame,
    column: str,
    *,
    seed: int,
    draws: int,
) -> dict[str, dict[str, float]]:
    response = predictions["response"].to_numpy(dtype=float)
    baseline = predictions["cell_probability"].to_numpy(dtype=float)
    candidate = predictions[column].to_numpy(dtype=float)
    frame = pd.DataFrame({
        "base_id": predictions["base_id"],
        "log_loss_gain": (
            _binary_losses(response, baseline)
            - _binary_losses(response, candidate)
        ),
        "brier_gain": (
            (response - baseline) ** 2
            - (response - candidate) ** 2
        ),
    })
    grouped = frame.groupby("base_id")[
        ["log_loss_gain", "brier_gain"]
    ].mean().to_numpy()
    rng = np.random.default_rng(int(seed))
    bootstrap = np.empty((int(draws), 2))
    for draw in range(int(draws)):
        sample = rng.integers(0, len(grouped), len(grouped))
        bootstrap[draw] = grouped[sample].mean(axis=0)
    return {
        name: {
            "mean": float(grouped[:, index].mean()),
            "lower_95": float(np.quantile(bootstrap[:, index], 0.025)),
            "upper_95": float(np.quantile(bootstrap[:, index], 0.975)),
        }
        for index, name in enumerate(["log_loss_gain", "brier_gain"])
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    rows_path = args.input_dir / "orbit_rows.csv"
    rows = pd.read_csv(rows_path)
    predictions = _crossfit_predictions(rows, config)
    response = predictions["response"].to_numpy(dtype=int)
    model_columns = [
        "cell_probability",
        "platt_orbit_probability",
        "mechanism_probability",
        "oracle_probability",
    ]
    metrics = {}
    root = np.random.SeedSequence(int(config["seed"]))
    streams = root.spawn(len(model_columns) - 1)
    for column in model_columns:
        probability = predictions[column].to_numpy(dtype=float)
        record = {
            "log_loss": float(log_loss(response, probability)),
            "brier": float(np.mean((response - probability) ** 2)),
            "auc": float(roc_auc_score(response, probability)),
            "within_cell_auc": _within_cell_auc(
                predictions,
                column,
            ),
        }
        if column != "cell_probability":
            stream = streams[model_columns[1:].index(column)]
            record["gain_vs_cell"] = _cluster_gain(
                predictions,
                column,
                seed=int(
                    stream.generate_state(1, dtype=np.uint64)[0]
                ),
                draws=int(config["bootstrap_draws"]),
            )
        metrics[column] = record

    candidates = [
        metrics[column]["gain_vs_cell"]
        for column in model_columns[1:]
    ]
    conditional_target_demonstrated = bool(
        any(
            candidate["log_loss_gain"]["lower_95"] > 0.0
            and candidate["brier_gain"]["lower_95"] > 0.0
            for candidate in candidates
        )
    )
    status = (
        "V8_R2D_GATE0_POSTHOC_"
        + (
            "CONDITIONAL_TARGET_SIGNAL_PRESENT"
            if conditional_target_demonstrated
            else "NO_GO_CONDITIONAL_TARGET_NOT_DEMONSTRATED"
        )
    )
    decision = {
        "status": status,
        "posthoc": True,
        "conditional_target_demonstrated": conditional_target_demonstrated,
        "metrics": metrics,
        "next_required_test": (
            "Fresh repeated-outcome oracle heterogeneity and predictability "
            "upper-bound preflight before any full posterior R2D."
        ),
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(
        args.output_dir / "crossfit_predictions.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "metrics.json", metrics)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        "# R2D Conditional-Target Gate-0\n\n"
        f"Decision: `{status}`\n\n"
        "This is an outcome-informed post-hoc resource gate. It cannot "
        "confirm or refute latent conditional heterogeneity.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[rows_path],
        config_path=args.config,
        code_paths=[Path(__file__)],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
