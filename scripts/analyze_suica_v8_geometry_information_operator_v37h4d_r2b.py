#!/usr/bin/env python3
"""Evaluate the H4D-R2B geometry operator by family-and-seed holdout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

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
    / "v8_geometry_information_operator"
    / "v37h4d_r2b_discovery_12600rows_20260727"
)
DEFAULT_CONFIG = (
    ROOT
    / "configs"
    / "v8_geometry_information_operator_v37h4d_r2b_analysis.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_geometry_information_operator"
    / "v37h4d_r2b_logo_audit_20260727"
)


def build_feature_frame(rows: pd.DataFrame) -> pd.DataFrame:
    """Construct frozen scalar and operator features without family labels."""
    epsilon = 1e-6
    information = np.log1p(
        rows["operator_total_information"].to_numpy(dtype=float)
    )
    rho3 = np.clip(
        rows["operator_rho3"].to_numpy(dtype=float),
        epsilon,
        1.0 - epsilon,
    )
    leakage = np.clip(
        rows["operator_whitened_leakage"].to_numpy(dtype=float),
        epsilon,
        1.0 - epsilon,
    )
    return pd.DataFrame({
        "log_information": information,
        "log_information_squared": information**2,
        "log_active_authors": np.log(
            rows["active_test_authors"].to_numpy(dtype=float)
        ),
        "noise_t5": (
            rows["noise_mode"].to_numpy()
            == "heteroskedastic_t5"
        ).astype(float),
        "log_neff_author": np.log(
            np.maximum(
                rows["operator_neff_author"].to_numpy(dtype=float),
                epsilon,
            )
        ),
        "log_neff_cell": np.log(
            np.maximum(
                rows["operator_neff_cell"].to_numpy(dtype=float),
                epsilon,
            )
        ),
        "logit_rho3": logit(rho3),
        "logit_whitened_leakage": logit(leakage),
        "condition_coherence": rows[
            "operator_condition_coherence"
        ].to_numpy(dtype=float),
        "log_neff_sign": np.log(
            np.maximum(
                rows["operator_neff_sign"].to_numpy(dtype=float),
                epsilon,
            )
        ),
    })


def _model(c_value: float) -> Any:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(
            C=float(c_value),
            penalty="l2",
            solver="lbfgs",
            max_iter=2000,
        ),
    )


def select_ridge_c(
    features: np.ndarray,
    response: np.ndarray,
    groups: np.ndarray,
    *,
    candidates: list[float],
    folds: int,
) -> float:
    """Select ridge strength using only grouped inner-training folds."""
    unique_groups = np.unique(groups)
    splitter = GroupKFold(
        n_splits=min(int(folds), len(unique_groups))
    )
    losses = {float(candidate): [] for candidate in candidates}
    for train_index, valid_index in splitter.split(
        features,
        response,
        groups,
    ):
        for candidate in candidates:
            model = _model(float(candidate))
            model.fit(features[train_index], response[train_index])
            probability = model.predict_proba(
                features[valid_index]
            )[:, 1]
            losses[float(candidate)].append(
                log_loss(
                    response[valid_index],
                    probability,
                    labels=[0, 1],
                )
            )
    return min(
        losses,
        key=lambda candidate: (
            float(np.mean(losses[candidate])),
            candidate,
        ),
    )


def logo_group_predictions(
    rows: pd.DataFrame,
    features: pd.DataFrame,
    *,
    scalar_columns: list[str],
    operator_columns: list[str],
    candidates: list[float],
    outer_folds: int,
    inner_folds: int,
) -> pd.DataFrame:
    """Predict each row with its family and base seed absent from training."""
    output: list[pd.DataFrame] = []
    response = rows["crc_or_hc_detected"].to_numpy(dtype=int)
    all_columns = [*scalar_columns, *operator_columns]
    for family in sorted(rows["geometry_family"].unique()):
        family_index = np.flatnonzero(
            rows["geometry_family"].to_numpy() == family
        )
        family_groups = rows.iloc[family_index][
            "base_id"
        ].to_numpy()
        outer = GroupKFold(
            n_splits=min(int(outer_folds), len(np.unique(family_groups)))
        )
        dummy = np.zeros(len(family_index))
        for fold, (_, local_test) in enumerate(
            outer.split(dummy, groups=family_groups)
        ):
            test_index = family_index[local_test]
            test_base = set(rows.iloc[test_index]["base_id"])
            train_mask = (
                (rows["geometry_family"] != family)
                & (~rows["base_id"].isin(test_base))
            )
            train_index = np.flatnonzero(train_mask.to_numpy())
            if set(rows.iloc[train_index]["base_id"]) & test_base:
                raise RuntimeError("base seed leaked across outer fold")
            train_groups = rows.iloc[train_index][
                "base_id"
            ].to_numpy()
            predictions: dict[str, np.ndarray] = {}
            selected: dict[str, float] = {}
            for name, columns in {
                "scalar": scalar_columns,
                "operator": all_columns,
            }.items():
                x_train = features.iloc[train_index][
                    columns
                ].to_numpy(dtype=float)
                x_test = features.iloc[test_index][
                    columns
                ].to_numpy(dtype=float)
                selected_c = select_ridge_c(
                    x_train,
                    response[train_index],
                    train_groups,
                    candidates=candidates,
                    folds=inner_folds,
                )
                model = _model(selected_c)
                model.fit(x_train, response[train_index])
                predictions[name] = model.predict_proba(x_test)[:, 1]
                selected[name] = selected_c
            frame = rows.iloc[test_index][[
                "base_id",
                "geometry_family",
                "noise_mode",
                "active_test_authors",
                "halo_lambda",
                "crc_or_hc_detected",
            ]].copy()
            frame["outer_fold"] = int(fold)
            frame["scalar_probability"] = predictions["scalar"]
            frame["operator_probability"] = predictions["operator"]
            frame["scalar_selected_c"] = selected["scalar"]
            frame["operator_selected_c"] = selected["operator"]
            output.append(frame)
    predictions = pd.concat(output, ignore_index=True)
    if len(predictions) != len(rows):
        raise RuntimeError("LOGO predictions do not cover every row")
    return predictions


def _binary_log_loss(response: np.ndarray, probability: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(probability, dtype=float), 1e-12, 1.0 - 1e-12)
    y = np.asarray(response, dtype=float)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def cluster_bootstrap_mean(
    values: pd.Series,
    groups: pd.Series,
    *,
    seed: int,
    draws: int,
) -> dict[str, float]:
    """Bootstrap an equal-base-seed mean."""
    frame = pd.DataFrame({
        "value": values.to_numpy(dtype=float),
        "group": groups.to_numpy(),
    })
    group_mean = frame.groupby("group")["value"].mean().to_numpy()
    point = float(group_mean.mean())
    rng = np.random.default_rng(int(seed))
    samples = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        index = rng.integers(0, len(group_mean), len(group_mean))
        samples[draw] = float(group_mean[index].mean())
    return {
        "mean": point,
        "lower_95": float(np.quantile(samples, 0.025)),
        "upper_95": float(np.quantile(samples, 0.975)),
    }


def paired_counterexample(
    rows: pd.DataFrame,
    *,
    seed: int,
    draws: int,
) -> pd.DataFrame:
    """Bootstrap iid-minus-intrinsic power within paired base worlds."""
    selected = rows[
        rows["geometry_family"].isin([
            "iid_halo",
            "intrinsic_zero_sum",
        ])
        & rows["active_test_authors"].isin([4, 8])
    ]
    records = []
    root = np.random.SeedSequence(int(seed))
    streams = root.spawn(4)
    index = 0
    for (noise, m), group in selected.groupby(
        ["noise_mode", "active_test_authors"],
        sort=True,
    ):
        pivot = group.pivot(
            index="base_id",
            columns="geometry_family",
            values="crc_or_hc_detected",
        )
        difference = (
            pivot["iid_halo"].to_numpy(dtype=float)
            - pivot["intrinsic_zero_sum"].to_numpy(dtype=float)
        )
        rng = np.random.default_rng(
            int(streams[index].generate_state(1, dtype=np.uint64)[0])
        )
        index += 1
        samples = np.empty(int(draws))
        for draw in range(int(draws)):
            sample = rng.integers(0, len(difference), len(difference))
            samples[draw] = float(difference[sample].mean())
        records.append({
            "noise_mode": noise,
            "active_test_authors": int(m),
            "pairs": int(len(difference)),
            "iid_minus_intrinsic_power": float(difference.mean()),
            "difference_lower_95": float(
                np.quantile(samples, 0.025)
            ),
            "difference_upper_95": float(
                np.quantile(samples, 0.975)
            ),
        })
    return pd.DataFrame(records)


def neff_sign_cluster_coefficient(
    rows: pd.DataFrame,
    features: pd.DataFrame,
    *,
    columns: list[str],
) -> dict[str, Any]:
    """Estimate the registered sign-support direction with clustered SE."""
    standardized = (
        features[columns] - features[columns].mean()
    ) / features[columns].std().replace(0.0, 1.0)
    design = sm.add_constant(standardized, has_constant="add")
    try:
        result = sm.GLM(
            rows["crc_or_hc_detected"].to_numpy(dtype=float),
            design,
            family=sm.families.Binomial(),
        ).fit(
            cov_type="cluster",
            cov_kwds={"groups": rows["base_id"].to_numpy()},
            maxiter=200,
        )
        interval = result.conf_int().loc["log_neff_sign"]
        return {
            "fit_success": True,
            "coefficient": float(result.params["log_neff_sign"]),
            "lower_95": float(interval.iloc[0]),
            "upper_95": float(interval.iloc[1]),
        }
    except Exception as error:  # pragma: no cover - defensive audit path
        return {
            "fit_success": False,
            "coefficient": float("nan"),
            "lower_95": float("nan"),
            "upper_95": float("nan"),
            "error": repr(error),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    rows = pd.read_csv(args.input_dir / "geometry_rows.csv")
    source_decision = _read(args.input_dir / "decision.json")
    features = build_feature_frame(rows)
    scalar_columns = list(map(str, config["scalar_features"]))
    operator_columns = list(map(str, config["operator_features"]))
    predictions = logo_group_predictions(
        rows,
        features,
        scalar_columns=scalar_columns,
        operator_columns=operator_columns,
        candidates=list(map(float, config["ridge_c_grid"])),
        outer_folds=int(config["outer_folds"]),
        inner_folds=int(config["inner_folds"]),
    )
    response = predictions["crc_or_hc_detected"].to_numpy(dtype=float)
    scalar_loss = _binary_log_loss(
        response,
        predictions["scalar_probability"].to_numpy(),
    )
    operator_loss = _binary_log_loss(
        response,
        predictions["operator_probability"].to_numpy(),
    )
    scalar_brier = (
        response - predictions["scalar_probability"].to_numpy()
    ) ** 2
    operator_brier = (
        response - predictions["operator_probability"].to_numpy()
    ) ** 2
    predictions["log_loss_improvement"] = scalar_loss - operator_loss
    predictions["brier_improvement"] = scalar_brier - operator_brier

    root = np.random.SeedSequence(int(config["seed"]))
    streams = root.spawn(4)
    log_loss_gain = cluster_bootstrap_mean(
        predictions["log_loss_improvement"],
        predictions["base_id"],
        seed=int(streams[0].generate_state(1, dtype=np.uint64)[0]),
        draws=int(config["bootstrap_draws"]),
    )
    brier_gain = cluster_bootstrap_mean(
        predictions["brier_improvement"],
        predictions["base_id"],
        seed=int(streams[1].generate_state(1, dtype=np.uint64)[0]),
        draws=int(config["bootstrap_draws"]),
    )
    intrinsic = predictions[
        predictions["geometry_family"] == "intrinsic_zero_sum"
    ]
    intrinsic_gain = cluster_bootstrap_mean(
        intrinsic["log_loss_improvement"],
        intrinsic["base_id"],
        seed=int(streams[2].generate_state(1, dtype=np.uint64)[0]),
        draws=int(config["bootstrap_draws"]),
    )
    counterexample = paired_counterexample(
        rows,
        seed=int(streams[3].generate_state(1, dtype=np.uint64)[0]),
        draws=int(config["bootstrap_draws"]),
    )

    family_rows = []
    for family, group in predictions.groupby(
        "geometry_family",
        sort=True,
    ):
        y = group["crc_or_hc_detected"].to_numpy(dtype=float)
        scalar_p = group["scalar_probability"].to_numpy(dtype=float)
        operator_p = group["operator_probability"].to_numpy(dtype=float)
        family_rows.append({
            "geometry_family": family,
            "trials": int(len(group)),
            "observed_power": float(y.mean()),
            "scalar_predicted_power": float(scalar_p.mean()),
            "operator_predicted_power": float(operator_p.mean()),
            "scalar_calibration_error": float(
                abs(y.mean() - scalar_p.mean())
            ),
            "operator_calibration_error": float(
                abs(y.mean() - operator_p.mean())
            ),
            "scalar_log_loss": float(
                _binary_log_loss(y, scalar_p).mean()
            ),
            "operator_log_loss": float(
                _binary_log_loss(y, operator_p).mean()
            ),
            "scalar_brier": float(np.mean((y - scalar_p) ** 2)),
            "operator_brier": float(np.mean((y - operator_p) ** 2)),
        })
    family = pd.DataFrame(family_rows)
    all_columns = [*scalar_columns, *operator_columns]
    coefficient = neff_sign_cluster_coefficient(
        rows,
        features,
        columns=all_columns,
    )
    gates = config["gates"]
    checks = {
        "source_discovery_valid": bool(
            all(source_decision["checks"].values())
        ),
        "counterexample_replicated": bool(
            len(counterexample) == 4
            and counterexample["difference_lower_95"].min()
            > float(gates["minimum_counterexample_power_gap_lower"])
        ),
        "log_loss_improvement": bool(
            log_loss_gain["lower_95"]
            > float(gates["minimum_log_loss_improvement_lower"])
        ),
        "brier_improvement": bool(
            brier_gain["lower_95"]
            > float(gates["minimum_brier_improvement_lower"])
        ),
        "intrinsic_log_loss_improvement": bool(
            intrinsic_gain["lower_95"]
            > float(
                gates["minimum_intrinsic_log_loss_improvement_lower"]
            )
        ),
        "neff_sign_direction": bool(
            coefficient["fit_success"]
            and coefficient["lower_95"]
            > float(gates["minimum_neff_sign_coefficient_lower"])
        ),
        "family_calibration": bool(
            family["operator_calibration_error"].max()
            <= float(gates["maximum_family_calibration_error"])
        ),
        "prediction_coverage": bool(len(predictions) == len(rows)),
    }
    core_gain = (
        checks["log_loss_improvement"]
        and checks["brier_improvement"]
        and checks["intrinsic_log_loss_improvement"]
    )
    if not (
        checks["source_discovery_valid"]
        and checks["counterexample_replicated"]
        and checks["prediction_coverage"]
    ):
        status = (
            "V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_"
            "STOP_INVALID_DESIGN"
        )
    elif all(checks.values()):
        status = (
            "V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_"
            "PASS_GEOMETRY_INFORMATION_OPERATOR"
        )
    elif core_gain:
        status = (
            "V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_"
            "PARTIAL_OPERATOR_PREDICTIVE_NOT_SUFFICIENT"
        )
    else:
        status = (
            "V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_"
            "REFUTED_SELECTED_GEOMETRY_COORDINATES"
        )
    decision = {
        "status": status,
        "checks": checks,
        "log_loss_improvement": log_loss_gain,
        "brier_improvement": brier_gain,
        "intrinsic_log_loss_improvement": intrinsic_gain,
        "neff_sign_coefficient": coefficient,
        "maximum_operator_family_calibration_error": float(
            family["operator_calibration_error"].max()
        ),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output_dir / "logo_predictions.csv", index=False)
    family.to_csv(args.output_dir / "family_metrics.csv", index=False)
    counterexample.to_csv(
        args.output_dir / "counterexample_bootstrap.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        "# H4D-R2B LOGO Geometry Operator Audit\n\n"
        f"Decision: `{status}`\n\n"
        "The scalar and operator models were evaluated with simultaneous "
        "geometry-family and base-seed holdout. Geometry labels were not "
        "predictor features.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            args.input_dir / "geometry_rows.csv",
            args.input_dir / "decision.json",
        ],
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
    return 0 if checks["source_discovery_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
