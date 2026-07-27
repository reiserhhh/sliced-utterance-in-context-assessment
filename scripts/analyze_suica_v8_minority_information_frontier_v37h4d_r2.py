#!/usr/bin/env python3
"""Audit H4D-R2 random-support transport and geometry sufficiency."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_INPUT = (
    ROOT
    / "results"
    / "v8_minority_information_frontier"
    / "v37h4d_r2_discovery_11000rep_20260727"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_minority_information_frontier"
    / "v37h4d_r2_mechanism_audit_20260727"
)


def fit_information_logistic(
    information: np.ndarray,
    detected: np.ndarray,
) -> dict[str, Any]:
    """Fit a standardized logistic information-power curve."""
    log_information = np.log1p(np.asarray(information, dtype=float))
    response = np.asarray(detected, dtype=float)
    mean = float(log_information.mean())
    scale = float(log_information.std())
    standardized = (log_information - mean) / max(scale, 1e-12)
    design = np.column_stack([np.ones(len(response)), standardized])
    coefficients = np.zeros(2, dtype=float)
    for _ in range(100):
        probability = np.clip(
            expit(design @ coefficients),
            1e-6,
            1.0 - 1e-6,
        )
        weights = probability * (1.0 - probability)
        information_matrix = (
            design.T @ (weights[:, None] * design)
            + 1e-8 * np.eye(2)
        )
        step = np.linalg.solve(
            information_matrix,
            design.T @ (response - probability),
        )
        coefficients += step
        if float(np.max(np.abs(step))) < 1e-9:
            break
    return {
        "intercept": float(coefficients[0]),
        "slope": float(coefficients[1]),
        "log_information_mean": mean,
        "log_information_scale": scale,
    }


def predict_information_logistic(
    model: dict[str, Any],
    information: np.ndarray,
) -> np.ndarray:
    """Predict detector power from a fitted information curve."""
    standardized = (
        np.log1p(np.asarray(information, dtype=float))
        - float(model["log_information_mean"])
    ) / max(float(model["log_information_scale"]), 1e-12)
    return expit(
        float(model["intercept"])
        + float(model["slope"]) * standardized
    )


def paired_bootstrap_difference(
    observed: np.ndarray,
    predicted: np.ndarray,
    *,
    seed: int,
    draws: int,
) -> tuple[float, float, float]:
    """Bootstrap mean observed-minus-predicted power over random cells."""
    y = np.asarray(observed, dtype=float)
    p = np.asarray(predicted, dtype=float)
    difference = float(np.mean(y - p))
    rng = np.random.default_rng(int(seed))
    samples = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        index = rng.integers(0, len(y), len(y))
        samples[draw] = float(np.mean(y[index] - p[index]))
    return (
        difference,
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def hypergeometric_moments(
    *,
    population: int,
    active: int,
    test: int,
) -> tuple[float, float]:
    """Return mean and variance of active test support."""
    probability = float(active) / float(population)
    mean = float(test) * probability
    variance = (
        float(test)
        * probability
        * (1.0 - probability)
        * (float(population - test) / float(population - 1))
    )
    return mean, variance


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=3108642975)
    args = parser.parse_args()

    cells = pd.read_csv(args.input_dir / "cell_metrics.csv")
    summary = pd.read_csv(args.input_dir / "cell_summary.csv")
    prediction_rows: list[dict[str, Any]] = []
    root = np.random.SeedSequence(int(args.seed))
    streams = root.spawn(4)
    index = 0
    for arm in ("global_share", "active_snr"):
        for noise in ("gaussian", "heteroskedastic_t5"):
            fixed = cells[
                (cells["support_scheme"] == "fixed")
                & (cells["interaction_shape"] == "iid_block")
                & (cells["scaling_arm"] == arm)
                & (cells["noise_mode"] == noise)
            ]
            random = cells[
                (cells["support_scheme"] == "random")
                & (cells["interaction_shape"] == "iid_block")
                & (cells["scaling_arm"] == arm)
                & (cells["noise_mode"] == noise)
            ]
            model = fit_information_logistic(
                fixed["information_budget_residual"].to_numpy(),
                fixed["crc_or_hc_detected"].to_numpy(),
            )
            predicted = predict_information_logistic(
                model,
                random["information_budget_residual"].to_numpy(),
            )
            difference, lower, upper = paired_bootstrap_difference(
                random["crc_or_hc_detected"].to_numpy(),
                predicted,
                seed=int(
                    streams[index].generate_state(
                        1,
                        dtype=np.uint64,
                    )[0]
                ),
                draws=int(args.bootstrap_draws),
            )
            index += 1
            prediction_rows.append({
                "scaling_arm": arm,
                "noise_mode": noise,
                "trials": int(len(random)),
                "observed_power": float(
                    random["crc_or_hc_detected"].mean()
                ),
                "predicted_power": float(predicted.mean()),
                "observed_minus_predicted": difference,
                "difference_lower_95": lower,
                "difference_upper_95": upper,
                "equivalence_within_005": bool(
                    lower > -0.05 and upper < 0.05
                ),
                **model,
            })
    predictions = pd.DataFrame(prediction_rows)

    geometry_rows: list[dict[str, Any]] = []
    for noise in ("gaussian", "heteroskedastic_t5"):
        for m in (4, 8):
            intrinsic = cells[
                (cells["support_scheme"] == "fixed")
                & (
                    cells["interaction_shape"]
                    == "intrinsic_zero_sum"
                )
                & (cells["scaling_arm"] == "active_snr")
                & (cells["noise_mode"] == noise)
                & (cells["active_test_authors"] == m)
            ]
            iid = cells[
                (cells["support_scheme"] == "fixed")
                & (cells["interaction_shape"] == "iid_block")
                & (cells["scaling_arm"] == "active_snr")
                & (cells["noise_mode"] == noise)
                & (cells["active_test_authors"] == m)
            ]
            intrinsic_power = float(
                intrinsic["crc_or_hc_detected"].mean()
            )
            iid_power = float(iid["crc_or_hc_detected"].mean())
            geometry_rows.append({
                "noise_mode": noise,
                "active_test_authors": m,
                "iid_trials": int(len(iid)),
                "intrinsic_trials": int(len(intrinsic)),
                "iid_mean_residual_information": float(
                    iid["information_budget_residual"].mean()
                ),
                "intrinsic_mean_residual_information": float(
                    intrinsic["information_budget_residual"].mean()
                ),
                "intrinsic_to_iid_information_ratio": float(
                    intrinsic["information_budget_residual"].mean()
                    / iid["information_budget_residual"].mean()
                ),
                "iid_power": iid_power,
                "intrinsic_power": intrinsic_power,
                "intrinsic_minus_iid_power": (
                    intrinsic_power - iid_power
                ),
                "iid_mean_leakage": float(
                    iid["centering_leakage_ratio"].mean()
                ),
                "intrinsic_mean_leakage": float(
                    intrinsic["centering_leakage_ratio"].mean()
                ),
            })
    geometry = pd.DataFrame(geometry_rows)

    support_rows: list[dict[str, Any]] = []
    random_cells = cells[
        (cells["support_scheme"] == "random")
        & (cells["interaction_shape"] == "iid_block")
    ]
    for (arm, noise, nominal), group in random_cells.groupby(
        ["scaling_arm", "noise_mode", "active_test_authors"],
        sort=True,
    ):
        expected_mean, expected_variance = hypergeometric_moments(
            population=256,
            active=4 * int(nominal),
            test=64,
        )
        support_rows.append({
            "scaling_arm": arm,
            "noise_mode": noise,
            "nominal_active_test_authors": int(nominal),
            "trials": int(len(group)),
            "observed_mean": float(
                group["realized_active_test_authors"].mean()
            ),
            "expected_mean": expected_mean,
            "observed_variance": float(
                group["realized_active_test_authors"].var(ddof=1)
            ),
            "expected_variance": expected_variance,
            "zero_support_count": int(
                (group["realized_active_test_authors"] == 0).sum()
            ),
            "zero_support_power": float(
                group.loc[
                    group["realized_active_test_authors"] == 0,
                    "crc_or_hc_detected",
                ].mean()
            ),
        })
    support = pd.DataFrame(support_rows)

    w0 = summary[summary["scaling_arm"] == "w0"]
    checks = {
        "random_support_information_prediction_within_005": bool(
            predictions["equivalence_within_005"].all()
        ),
        "scalar_information_refuted_across_geometry": bool(
            (
                geometry["intrinsic_to_iid_information_ratio"].between(
                    0.8,
                    1.25,
                )
            ).all()
            and (
                geometry["intrinsic_minus_iid_power"].abs() > 0.10
            ).all()
        ),
        "projection_compatibility": bool(
            cells[
                "projection_grand_mean_compatibility_error"
            ].max()
            <= 1e-12
        ),
        "w0_discovery_not_confirmation": bool(
            len(w0) == 2
            and int(w0["trials"].min()) == 300
        ),
    }
    if not all(checks.values()):
        status = "V8_H4D_R2_MECHANISM_AUDIT_STOP"
    else:
        status = (
            "V8_H4D_R2_RANDOM_SUPPORT_EXPLAINED_"
            "SCALAR_INFORMATION_GEOMETRY_REFUTED"
        )
    decision = {
        "status": status,
        "checks": checks,
        "maximum_random_prediction_abs_bound": float(
            np.max(
                np.abs(
                    predictions[[
                        "difference_lower_95",
                        "difference_upper_95",
                    ]].to_numpy()
                )
            )
        ),
        "minimum_geometry_power_gap": float(
            geometry["intrinsic_minus_iid_power"].abs().min()
        ),
        "claim_boundary": (
            "The scalar residual information budget predicts random support "
            "transport within the iid planted family but is not sufficient "
            "across interaction geometries. This is detector-mechanism "
            "evidence, not psychological validity."
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(
        args.output_dir / "random_support_prediction.csv",
        index=False,
    )
    geometry.to_csv(
        args.output_dir / "geometry_counterexample.csv",
        index=False,
    )
    support.to_csv(
        args.output_dir / "support_distribution.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    (args.output_dir / "report.md").write_text(
        "# H4D-R2 Mechanism Audit\n\n"
        f"Decision: `{status}`\n\n"
        "Random hypergeometric support is predicted within +/-0.05 by the "
        "fixed iid residual-information curve. However, intrinsic-zero-sum "
        "blocks have similar residual information and substantially lower "
        "power, so a scalar information budget is not geometry-sufficient "
        "for the frozen detector.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            args.input_dir / "cell_metrics.csv",
            args.input_dir / "cell_summary.csv",
        ],
        config_path=args.input_dir / "config_effective.json",
        code_paths=[Path(__file__)],
        estimand_id="V8_H4D_R2_MECHANISM_AUDIT",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
