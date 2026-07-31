"""Task-specific routing over a declared hierarchy of frozen SUICA evidence.

The router may assemble multiple frozen layers inside one task head, but the
assembled matrix is ephemeral. It is never exported as a universal person
score. Route and hyperparameter selection are performed inside source-only
folds before an outer fold or external destination is predicted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

from .v8_external_connection import fisher_interval, safe_pearson


@dataclass(frozen=True)
class EvidenceLayer:
    """One frozen evidence object at a declared resolution level."""

    name: str
    level: str
    columns: tuple[str, ...]
    estimand: str

    def __post_init__(self) -> None:
        if not self.name or not self.level or not self.estimand:
            raise ValueError("Evidence layers require name, level, and estimand.")
        if not self.columns or len(set(self.columns)) != len(self.columns):
            raise ValueError(f"Layer {self.name} has empty or duplicate columns.")


@dataclass(frozen=True)
class TaskRoute:
    """A task-local read path through one or more frozen evidence layers."""

    name: str
    layers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.layers or len(set(self.layers)) != len(self.layers):
            raise ValueError("Task routes require a name and unique layer names.")


@dataclass(frozen=True)
class RoutedCVResult:
    """Nested source-fold predictions and route-selection records."""

    summary: dict[str, Any]
    predictions: pd.DataFrame
    selections: pd.DataFrame


def validate_hierarchy(
    layers: Mapping[str, EvidenceLayer],
    routes: Sequence[TaskRoute],
) -> None:
    """Refuse overlapping layers, unknown route edges, and duplicate routes."""
    if set(layers) != {layer.name for layer in layers.values()}:
        raise ValueError("Layer mapping keys must equal EvidenceLayer.name.")
    all_columns: list[str] = []
    for layer in layers.values():
        all_columns.extend(layer.columns)
    if len(all_columns) != len(set(all_columns)):
        raise ValueError("Evidence-layer columns must be disjoint.")
    route_names = [route.name for route in routes]
    if len(route_names) != len(set(route_names)):
        raise ValueError("Task-route names must be unique.")
    for route in routes:
        missing = set(route.layers) - set(layers)
        if missing:
            raise ValueError(f"Route {route.name} references unknown layers: {missing}")


def route_columns(
    layers: Mapping[str, EvidenceLayer],
    route: TaskRoute,
) -> list[str]:
    """Resolve one route without changing the declared layer objects."""
    return [
        column
        for layer_name in route.layers
        for column in layers[layer_name].columns
    ]


def _finite_design(
    train_values: np.ndarray,
    target_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    impute = np.nanmedian(train_values, axis=0)
    impute = np.where(np.isfinite(impute), impute, 0.0)
    complete = np.where(
        np.isfinite(train_values),
        train_values,
        impute[None, :],
    )
    scaler = StandardScaler().fit(complete)
    return scaler.transform(complete), impute, scaler


def _transform_design(
    values: np.ndarray,
    *,
    impute: np.ndarray,
    scaler: StandardScaler,
) -> np.ndarray:
    complete = np.where(np.isfinite(values), values, impute[None, :])
    return scaler.transform(complete)


def _fit_predict(
    train_x: np.ndarray,
    train_y: np.ndarray,
    test_x: np.ndarray,
    *,
    task: str,
    parameter: float,
) -> np.ndarray:
    if task == "continuous":
        model = Ridge(alpha=float(parameter)).fit(train_x, train_y)
        return np.asarray(model.predict(test_x), dtype=float)
    if task == "binary":
        labels = train_y.astype(int)
        if len(np.unique(labels)) < 2:
            raise ValueError("Binary training arm contains only one class.")
        model = LogisticRegression(
            C=float(parameter),
            class_weight="balanced",
            max_iter=5000,
            solver="lbfgs",
        ).fit(train_x, labels)
        return np.asarray(model.predict_proba(test_x)[:, 1], dtype=float)
    raise ValueError(f"Unsupported task: {task}")


def _prediction_score(
    truth: np.ndarray,
    prediction: np.ndarray,
    *,
    task: str,
) -> float:
    if task == "continuous":
        value = safe_pearson(prediction, truth)[0]
        if np.isfinite(value):
            return float(value)
        return -float(mean_squared_error(truth, prediction))
    if task == "binary":
        labels = truth.astype(int)
        if len(np.unique(labels)) < 2:
            return -float(mean_squared_error(labels, prediction))
        return float(roc_auc_score(labels, prediction))
    raise ValueError(f"Unsupported task: {task}")


def prediction_metrics(
    truth: np.ndarray,
    prediction: np.ndarray,
    *,
    task: str,
) -> dict[str, float]:
    """Compute task metrics without selecting or fitting a model."""
    truth = np.asarray(truth, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    correlation, p_value = safe_pearson(prediction, truth)
    lower, upper = fisher_interval(correlation, len(truth))
    base = {
        "probability_or_score_r": correlation,
        "probability_or_score_r_p": p_value,
        "probability_or_score_r_ci_lower": lower,
        "probability_or_score_r_ci_upper": upper,
    }
    if task == "continuous":
        return {
            **base,
            "pearson_r": correlation,
            "mae": float(mean_absolute_error(truth, prediction)),
            "rmse": float(np.sqrt(mean_squared_error(truth, prediction))),
        }
    if task == "binary":
        labels = truth.astype(int)
        predicted = (prediction >= 0.5).astype(int)
        return {
            **base,
            "roc_auc": (
                float(roc_auc_score(labels, prediction))
                if len(np.unique(labels)) == 2
                else float("nan")
            ),
            "balanced_accuracy": float(
                balanced_accuracy_score(labels, predicted)
            ),
            "macro_f1": float(f1_score(labels, predicted, average="macro")),
            "positive_rate_true": float(np.mean(labels)),
            "positive_rate_pred": float(np.mean(predicted)),
        }
    raise ValueError(f"Unsupported task: {task}")


def _candidate_key(
    row: dict[str, Any],
    *,
    routes: Mapping[str, TaskRoute],
    layers: Mapping[str, EvidenceLayer],
) -> tuple[float, int, int, str, float]:
    route = routes[str(row["route"])]
    columns = route_columns(layers, route)
    return (
        float(row["inner_score"]),
        -len(route.layers),
        -len(columns),
        str(row["route"]),
        -float(row["parameter"]),
    )


def select_source_route(
    frame: pd.DataFrame,
    *,
    layers: Mapping[str, EvidenceLayer],
    routes: Sequence[TaskRoute],
    target: str,
    fold_column: str,
    task: str,
    parameters: Iterable[float],
    excluded_fold: int | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Select route and model parameter by source-only inner-fold predictions."""
    validate_hierarchy(layers, routes)
    route_map = {route.name: route for route in routes}
    data = frame.dropna(subset=[target, fold_column]).reset_index(drop=True)
    folds = pd.to_numeric(data[fold_column]).astype(int).to_numpy()
    eligible = (
        np.ones(len(data), dtype=bool)
        if excluded_fold is None
        else folds != int(excluded_fold)
    )
    inner_folds = sorted(set(folds[eligible].tolist()))
    if len(inner_folds) < 3:
        raise ValueError("Route selection requires at least three inner folds.")
    rows: list[dict[str, Any]] = []
    for route in routes:
        columns = route_columns(layers, route)
        values = data[columns].to_numpy(float)
        for parameter in parameters:
            predictions = np.full(len(data), np.nan, dtype=float)
            valid_candidate = True
            for validation_fold in inner_folds:
                valid = eligible & (folds == validation_fold)
                train = eligible & (folds != validation_fold)
                if not train.any() or not valid.any():
                    valid_candidate = False
                    break
                train_x, impute, scaler = _finite_design(
                    values[train],
                    data.loc[train, target].to_numpy(float),
                )
                valid_x = _transform_design(
                    values[valid],
                    impute=impute,
                    scaler=scaler,
                )
                try:
                    predictions[valid] = _fit_predict(
                        train_x,
                        data.loc[train, target].to_numpy(float),
                        valid_x,
                        task=task,
                        parameter=float(parameter),
                    )
                except ValueError:
                    valid_candidate = False
                    break
            if not valid_candidate or not np.isfinite(predictions[eligible]).all():
                continue
            score = _prediction_score(
                data.loc[eligible, target].to_numpy(float),
                predictions[eligible],
                task=task,
            )
            rows.append({
                "route": route.name,
                "layers": "|".join(route.layers),
                "feature_count": int(len(columns)),
                "parameter": float(parameter),
                "inner_score": float(score),
                "inner_folds": int(len(inner_folds)),
                "inner_n": int(eligible.sum()),
            })
    candidates = pd.DataFrame(rows)
    if candidates.empty:
        raise RuntimeError(f"No valid route candidate for {target}.")
    best_index = max(
        candidates.index,
        key=lambda index: _candidate_key(
            candidates.loc[index].to_dict(),
            routes=route_map,
            layers=layers,
        ),
    )
    return candidates.loc[best_index].to_dict(), candidates


def run_nested_route_cv(
    frame: pd.DataFrame,
    *,
    layers: Mapping[str, EvidenceLayer],
    routes: Sequence[TaskRoute],
    target: str,
    fold_column: str,
    task: str,
    parameters: Iterable[float],
    view: str,
    cohort: str,
) -> RoutedCVResult:
    """Select a source route inside each outer fold and predict it once."""
    data = frame.dropna(subset=[target, fold_column]).reset_index(drop=True)
    folds = pd.to_numeric(data[fold_column]).astype(int).to_numpy()
    predictions = np.full(len(data), np.nan, dtype=float)
    selection_rows: list[dict[str, Any]] = []
    route_map = {route.name: route for route in routes}
    for test_fold in sorted(set(folds.tolist())):
        selected, _ = select_source_route(
            data,
            layers=layers,
            routes=routes,
            target=target,
            fold_column=fold_column,
            task=task,
            parameters=parameters,
            excluded_fold=int(test_fold),
        )
        route = route_map[str(selected["route"])]
        columns = route_columns(layers, route)
        train = folds != int(test_fold)
        test = ~train
        values = data[columns].to_numpy(float)
        train_x, impute, scaler = _finite_design(
            values[train],
            data.loc[train, target].to_numpy(float),
        )
        test_x = _transform_design(
            values[test],
            impute=impute,
            scaler=scaler,
        )
        predictions[test] = _fit_predict(
            train_x,
            data.loc[train, target].to_numpy(float),
            test_x,
            task=task,
            parameter=float(selected["parameter"]),
        )
        selection_rows.append({
            "cohort": cohort,
            "view": view,
            "target": target,
            "task": task,
            "test_fold": int(test_fold),
            "selected_route": route.name,
            "selected_layers": "|".join(route.layers),
            "selected_parameter": float(selected["parameter"]),
            "inner_score": float(selected["inner_score"]),
            "n_train": int(train.sum()),
            "n_test": int(test.sum()),
        })
    if not np.isfinite(predictions).all():
        raise RuntimeError("Nested router did not predict every outer-fold row.")
    metrics = prediction_metrics(
        data[target].to_numpy(float),
        predictions,
        task=task,
    )
    summary = {
        "cohort": cohort,
        "view": view,
        "target": target,
        "task": task,
        "n": int(len(data)),
        "candidate_routes": int(len(routes)),
        **metrics,
    }
    output = data[["pseudonymous_id", fold_column, target]].copy()
    output = output.rename(columns={target: "true_value"})
    output["prediction"] = predictions
    output["cohort"] = cohort
    output["view"] = view
    output["target"] = target
    output["task"] = task
    return RoutedCVResult(
        summary=summary,
        predictions=output,
        selections=pd.DataFrame(selection_rows),
    )


def fit_source_router_predict(
    source: pd.DataFrame,
    destination: pd.DataFrame,
    *,
    layers: Mapping[str, EvidenceLayer],
    routes: Sequence[TaskRoute],
    target: str,
    fold_column: str,
    task: str,
    parameters: Iterable[float],
) -> tuple[np.ndarray, dict[str, Any]]:
    """Select on all source folds, fit all source rows, and predict destination."""
    data = source.dropna(subset=[target, fold_column]).reset_index(drop=True)
    selected, _ = select_source_route(
        data,
        layers=layers,
        routes=routes,
        target=target,
        fold_column=fold_column,
        task=task,
        parameters=parameters,
    )
    route_map = {route.name: route for route in routes}
    route = route_map[str(selected["route"])]
    columns = route_columns(layers, route)
    train_values = data[columns].to_numpy(float)
    destination_values = destination[columns].to_numpy(float)
    train_x, impute, scaler = _finite_design(
        train_values,
        data[target].to_numpy(float),
    )
    destination_x = _transform_design(
        destination_values,
        impute=impute,
        scaler=scaler,
    )
    prediction = _fit_predict(
        train_x,
        data[target].to_numpy(float),
        destination_x,
        task=task,
        parameter=float(selected["parameter"]),
    )
    return prediction, {
        "target": target,
        "task": task,
        "selected_route": route.name,
        "selected_layers": "|".join(route.layers),
        "selected_parameter": float(selected["parameter"]),
        "inner_score": float(selected["inner_score"]),
        "source_n": int(len(data)),
        "destination_n": int(len(destination)),
    }


def fit_selected_route_predict(
    source: pd.DataFrame,
    destination: pd.DataFrame,
    *,
    layers: Mapping[str, EvidenceLayer],
    route: TaskRoute,
    target: str,
    fold_column: str,
    task: str,
    parameter: float,
) -> np.ndarray:
    """Fit a previously frozen source route without performing selection."""
    validate_hierarchy(layers, [route])
    data = source.dropna(subset=[target, fold_column]).reset_index(drop=True)
    columns = route_columns(layers, route)
    train_values = data[columns].to_numpy(float)
    destination_values = destination[columns].to_numpy(float)
    train_x, impute, scaler = _finite_design(
        train_values,
        data[target].to_numpy(float),
    )
    destination_x = _transform_design(
        destination_values,
        impute=impute,
        scaler=scaler,
    )
    return _fit_predict(
        train_x,
        data[target].to_numpy(float),
        destination_x,
        task=task,
        parameter=float(parameter),
    )
