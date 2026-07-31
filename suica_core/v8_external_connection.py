"""Leak-aware utilities for the exploratory V8 PANDORA external connection.

This module keeps the frozen text score separate from external labels.  It
contains only deterministic score transforms and fold-aware statistical
helpers; it does not define or name a psychological construct.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

from .suica import tokenize


BIG5_TRAITS = (
    "Extraversion",
    "Neuroticism",
    "Agreeableness",
    "Conscientiousness",
    "Openness",
)
MBTI_AXES = ("EI_cont", "SN_cont", "TF_cont", "JP_cont")


@dataclass(frozen=True)
class CVResult:
    """One target/view outer-CV result and its row-level predictions."""

    summary: dict[str, Any]
    predictions: pd.DataFrame
    folds: pd.DataFrame


def split_comment_units(
    text: str,
    *,
    min_tokens: int = 24,
    max_chars: int = 1500,
) -> list[dict[str, Any]]:
    """Recover prepared PANDORA comment units from the double-newline join.

    Official preparation joins already-cleaned comments with ``"\n\n"``.
    Clipping to ``max_chars`` matches the representation-development input.
    """
    output: list[dict[str, Any]] = []
    for raw in str(text or "").split("\n\n"):
        value = raw.strip()
        if not value:
            continue
        clipped = value[: int(max_chars)]
        token_count = len(tokenize(clipped))
        if token_count < int(min_tokens):
            continue
        output.append({"text": clipped, "token_count": int(token_count)})
    return output


def canonical_scale_residual(values: np.ndarray) -> np.ndarray:
    """Remove row-wide landmark radius while retaining canonical topology."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[1] < 2 or not np.isfinite(array).all():
        raise ValueError("canonical scale residual requires a finite 2D matrix")
    centered = array - array.mean(axis=1, keepdims=True)
    scale = centered.std(axis=1, keepdims=True)
    return centered / np.maximum(scale, 1e-12)


def nuisance_features(
    *,
    sampled_comment_count: float,
    available_clean_comments: float,
    approx_token_count: float,
    unit_token_counts: Iterable[int],
    text: str,
) -> dict[str, float]:
    """Return method-artifact controls that do not inspect personality labels."""
    counts = np.asarray(list(unit_token_counts), dtype=float)
    if not len(counts):
        counts = np.asarray([0.0])
    raw = str(text or "")
    alnum = sum(character.isalnum() for character in raw)
    punctuation = sum((not character.isalnum()) and (not character.isspace()) for character in raw)
    return {
        "nuisance_log_sampled_comments": float(np.log1p(max(0.0, sampled_comment_count))),
        "nuisance_log_available_comments": float(np.log1p(max(0.0, available_clean_comments))),
        "nuisance_log_approx_tokens": float(np.log1p(max(0.0, approx_token_count))),
        "nuisance_unit_count": float(len(counts) if counts[0] > 0 else 0),
        "nuisance_mean_unit_tokens": float(np.mean(counts)),
        "nuisance_std_unit_tokens": float(np.std(counts, ddof=0)),
        "nuisance_median_unit_tokens": float(np.median(counts)),
        "nuisance_punctuation_ratio": float(punctuation / max(1, alnum + punctuation)),
        "nuisance_chars_per_approx_token": float(len(raw) / max(1.0, approx_token_count)),
    }


def safe_pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Return Pearson r and two-sided p, refusing degenerate inputs."""
    first = np.asarray(x, dtype=float)
    second = np.asarray(y, dtype=float)
    mask = np.isfinite(first) & np.isfinite(second)
    if int(mask.sum()) < 3:
        return float("nan"), float("nan")
    first, second = first[mask], second[mask]
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return float("nan"), float("nan")
    result = stats.pearsonr(first, second)
    return float(result.statistic), float(result.pvalue)


def fisher_interval(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Fisher-z confidence interval for a finite Pearson correlation."""
    if not np.isfinite(r) or int(n) <= 3:
        return float("nan"), float("nan")
    clipped = float(np.clip(r, -0.999999, 0.999999))
    z = np.arctanh(clipped)
    width = stats.norm.ppf(1.0 - alpha / 2.0) / np.sqrt(int(n) - 3)
    return float(np.tanh(z - width)), float(np.tanh(z + width))


def benjamini_hochberg(values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg q-values preserving the original row order."""
    p_values = pd.to_numeric(values, errors="coerce")
    output = pd.Series(np.nan, index=p_values.index, dtype=float)
    valid = p_values.dropna()
    if valid.empty:
        return output
    ordered = valid.sort_values().index.tolist()
    previous = 1.0
    total = len(ordered)
    for rank, index in reversed(list(enumerate(ordered, start=1))):
        adjusted = min(previous, float(valid.loc[index]) * total / rank)
        output.loc[index] = adjusted
        previous = adjusted
    return output.clip(upper=1.0)


def univariate_connections(
    frame: pd.DataFrame,
    *,
    feature_groups: dict[str, list[str]],
    targets: Iterable[str],
    cohort: str,
) -> pd.DataFrame:
    """Screen frozen coordinates against anchors with within-target/view FDR."""
    rows: list[dict[str, Any]] = []
    for view, columns in feature_groups.items():
        for target in targets:
            if target not in frame:
                continue
            for feature in columns:
                subset = frame[[feature, target]].dropna()
                r_value, p_value = safe_pearson(
                    subset[feature].to_numpy(float),
                    subset[target].to_numpy(float),
                )
                lower, upper = fisher_interval(r_value, len(subset))
                rows.append({
                    "cohort": cohort,
                    "view": view,
                    "target": target,
                    "feature": feature,
                    "n": int(len(subset)),
                    "pearson_r": r_value,
                    "ci_lower": lower,
                    "ci_upper": upper,
                    "p_value": p_value,
                })
    output = pd.DataFrame(rows)
    if output.empty:
        return output
    output["q_value_within_target_view"] = output.groupby(
        ["cohort", "view", "target"], observed=True
    )["p_value"].transform(benjamini_hochberg)
    output["abs_pearson_r"] = output["pearson_r"].abs()
    return output.sort_values(
        ["cohort", "target", "view", "abs_pearson_r"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)


def _standardized_matrices(
    frame: pd.DataFrame,
    columns: list[str],
    train: np.ndarray,
    valid: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = frame[columns].to_numpy(float)
    impute = np.nanmedian(values[train], axis=0)
    impute = np.where(np.isfinite(impute), impute, 0.0)
    complete = np.where(np.isfinite(values), values, impute[None, :])
    scaler = StandardScaler().fit(complete[train])
    return (
        scaler.transform(complete[train]),
        scaler.transform(complete[valid]),
        scaler.transform(complete[test]),
    )


def _continuous_metrics(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    r_value, p_value = safe_pearson(prediction, y_true)
    spearman = stats.spearmanr(prediction, y_true)
    lower, upper = fisher_interval(r_value, len(y_true))
    return {
        "pearson_r": r_value,
        "pearson_p": p_value,
        "pearson_ci_lower": lower,
        "pearson_ci_upper": upper,
        "spearman_rho": float(spearman.statistic),
        "mae": float(mean_absolute_error(y_true, prediction)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, prediction))),
    }


def _binary_metrics(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    predicted = (np.asarray(probability) >= 0.5).astype(int)
    point_biserial, p_value = safe_pearson(probability, y_true)
    lower, upper = fisher_interval(point_biserial, len(y_true))
    auc = (
        float(roc_auc_score(y_true, probability))
        if len(np.unique(y_true)) == 2
        else float("nan")
    )
    return {
        "roc_auc": auc,
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predicted)),
        "macro_f1": float(f1_score(y_true, predicted, average="macro")),
        "probability_r": point_biserial,
        "probability_r_p": p_value,
        "probability_r_ci_lower": lower,
        "probability_r_ci_upper": upper,
        "positive_rate_true": float(np.mean(y_true)),
        "positive_rate_pred": float(np.mean(predicted)),
    }


def _select_ridge_alpha(
    train_x: np.ndarray,
    train_y: np.ndarray,
    valid_x: np.ndarray,
    valid_y: np.ndarray,
    alphas: Iterable[float],
) -> tuple[float, float]:
    best_alpha, best_score = float("nan"), -np.inf
    for alpha in alphas:
        model = Ridge(alpha=float(alpha)).fit(train_x, train_y)
        score, _ = safe_pearson(model.predict(valid_x), valid_y)
        score = -float(mean_squared_error(valid_y, model.predict(valid_x))) if not np.isfinite(score) else score
        if score > best_score:
            best_alpha, best_score = float(alpha), float(score)
    return best_alpha, best_score


def _select_logistic_c(
    train_x: np.ndarray,
    train_y: np.ndarray,
    valid_x: np.ndarray,
    valid_y: np.ndarray,
    c_values: Iterable[float],
) -> tuple[float, float]:
    best_c, best_score = float("nan"), -np.inf
    for c_value in c_values:
        if len(np.unique(train_y)) < 2:
            raise ValueError("Binary training arm contains only one class.")
        model = LogisticRegression(
            C=float(c_value),
            class_weight="balanced",
            max_iter=5000,
            solver="lbfgs",
        ).fit(train_x, train_y)
        probability = model.predict_proba(valid_x)[:, 1]
        score = (
            float(roc_auc_score(valid_y, probability))
            if len(np.unique(valid_y)) == 2
            else -float(mean_squared_error(valid_y, probability))
        )
        if score > best_score:
            best_c, best_score = float(c_value), score
    return best_c, best_score


def run_official_cv(
    frame: pd.DataFrame,
    *,
    columns: list[str],
    target: str,
    fold_column: str,
    task: str,
    view: str,
    cohort: str,
    ridge_alphas: Iterable[float],
    logistic_c: Iterable[float],
) -> CVResult:
    """Run five outer official folds with a distinct adjacent validation fold."""
    data = frame.dropna(subset=[target, fold_column]).reset_index(drop=True)
    fold_values = sorted(pd.to_numeric(data[fold_column]).astype(int).unique().tolist())
    if len(fold_values) < 3:
        raise ValueError(f"{target} requires at least three official folds")
    predictions = np.full(len(data), np.nan, dtype=float)
    fold_rows: list[dict[str, Any]] = []
    for position, test_fold in enumerate(fold_values):
        valid_fold = fold_values[(position + 1) % len(fold_values)]
        test = pd.to_numeric(data[fold_column]).astype(int).eq(test_fold).to_numpy()
        valid = pd.to_numeric(data[fold_column]).astype(int).eq(valid_fold).to_numpy()
        train = ~(test | valid)
        if not train.any() or not valid.any() or not test.any():
            raise RuntimeError("official-fold partition produced an empty arm")
        train_x, valid_x, test_x = _standardized_matrices(data, columns, train, valid, test)
        train_y = data.loc[train, target].to_numpy(float)
        valid_y = data.loc[valid, target].to_numpy(float)
        test_y = data.loc[test, target].to_numpy(float)
        train_valid = train | valid
        full_x, _, held_x = _standardized_matrices(data, columns, train_valid, valid, test)
        full_y = data.loc[train_valid, target].to_numpy(float)
        if task == "continuous":
            parameter, validation_score = _select_ridge_alpha(
                train_x, train_y, valid_x, valid_y, ridge_alphas
            )
            model = Ridge(alpha=parameter).fit(full_x, full_y)
            held_prediction = model.predict(held_x)
            metrics = _continuous_metrics(test_y, held_prediction)
            parameter_name = "alpha"
        elif task == "binary":
            parameter, validation_score = _select_logistic_c(
                train_x,
                train_y.astype(int),
                valid_x,
                valid_y.astype(int),
                logistic_c,
            )
            model = LogisticRegression(
                C=parameter,
                class_weight="balanced",
                max_iter=5000,
                solver="lbfgs",
            ).fit(full_x, full_y.astype(int))
            held_prediction = model.predict_proba(held_x)[:, 1]
            metrics = _binary_metrics(test_y.astype(int), held_prediction)
            parameter_name = "C"
        else:
            raise ValueError(f"unsupported task: {task}")
        predictions[test] = held_prediction
        fold_rows.append({
            "cohort": cohort,
            "view": view,
            "target": target,
            "task": task,
            "test_fold": int(test_fold),
            "validation_fold": int(valid_fold),
            "n_train": int(train.sum()),
            "n_valid": int(valid.sum()),
            "n_test": int(test.sum()),
            "selected_parameter": parameter,
            "parameter_name": parameter_name,
            "validation_score": validation_score,
            **metrics,
        })
    if not np.isfinite(predictions).all():
        raise RuntimeError("outer-CV did not predict every eligible row exactly once")
    target_values = data[target].to_numpy(float)
    summary_metrics = (
        _continuous_metrics(target_values, predictions)
        if task == "continuous"
        else _binary_metrics(target_values.astype(int), predictions)
    )
    summary = {
        "cohort": cohort,
        "view": view,
        "target": target,
        "task": task,
        "n": int(len(data)),
        "features": int(len(columns)),
        **summary_metrics,
    }
    prediction_frame = data[["pseudonymous_id", fold_column, target]].copy()
    prediction_frame = prediction_frame.rename(columns={target: "true_value"})
    prediction_frame["prediction"] = predictions
    prediction_frame["cohort"] = cohort
    prediction_frame["view"] = view
    prediction_frame["target"] = target
    prediction_frame["task"] = task
    return CVResult(
        summary=summary,
        predictions=prediction_frame,
        folds=pd.DataFrame(fold_rows),
    )


def select_final_parameter(
    frame: pd.DataFrame,
    *,
    columns: list[str],
    target: str,
    fold_column: str,
    task: str,
    ridge_alphas: Iterable[float],
    logistic_c: Iterable[float],
) -> float:
    """Select one final head parameter from source-only official folds."""
    data = frame.dropna(subset=[target, fold_column]).reset_index(drop=True)
    folds = pd.to_numeric(data[fold_column]).astype(int).to_numpy()
    values = data[columns].to_numpy(float)
    target_values = data[target].to_numpy(float)
    candidates = list(ridge_alphas if task == "continuous" else logistic_c)
    rows: list[tuple[float, float]] = []
    for candidate in candidates:
        predictions = np.full(len(data), np.nan)
        for fold in sorted(set(folds.tolist())):
            test = folds == fold
            train = ~test
            impute = np.nanmedian(values[train], axis=0)
            impute = np.where(np.isfinite(impute), impute, 0.0)
            complete = np.where(np.isfinite(values), values, impute[None, :])
            scaler = StandardScaler().fit(complete[train])
            train_x, test_x = scaler.transform(complete[train]), scaler.transform(complete[test])
            if task == "continuous":
                model = Ridge(alpha=float(candidate)).fit(train_x, target_values[train])
                predictions[test] = model.predict(test_x)
            else:
                model = LogisticRegression(
                    C=float(candidate),
                    class_weight="balanced",
                    max_iter=5000,
                    solver="lbfgs",
                ).fit(train_x, target_values[train].astype(int))
                predictions[test] = model.predict_proba(test_x)[:, 1]
        score = (
            safe_pearson(predictions, target_values)[0]
            if task == "continuous"
            else float(roc_auc_score(target_values.astype(int), predictions))
        )
        rows.append((float(candidate), float(score)))
    return max(rows, key=lambda row: row[1])[0]


def fit_source_head_predict(
    source: pd.DataFrame,
    destination: pd.DataFrame,
    *,
    columns: list[str],
    target: str,
    fold_column: str,
    task: str,
    ridge_alphas: Iterable[float],
    logistic_c: Iterable[float],
) -> tuple[np.ndarray, float]:
    """Fit one source-only head and predict a label-held-out destination."""
    source = source.dropna(subset=[target, fold_column]).reset_index(drop=True)
    parameter = select_final_parameter(
        source,
        columns=columns,
        target=target,
        fold_column=fold_column,
        task=task,
        ridge_alphas=ridge_alphas,
        logistic_c=logistic_c,
    )
    train_values = source[columns].to_numpy(float)
    destination_values = destination[columns].to_numpy(float)
    impute = np.nanmedian(train_values, axis=0)
    impute = np.where(np.isfinite(impute), impute, 0.0)
    train_values = np.where(np.isfinite(train_values), train_values, impute[None, :])
    destination_values = np.where(
        np.isfinite(destination_values),
        destination_values,
        impute[None, :],
    )
    scaler = StandardScaler().fit(train_values)
    train_x = scaler.transform(train_values)
    destination_x = scaler.transform(destination_values)
    target_values = source[target].to_numpy(float)
    if task == "continuous":
        model = Ridge(alpha=parameter).fit(train_x, target_values)
        prediction = model.predict(destination_x)
    elif task == "binary":
        model = LogisticRegression(
            C=parameter,
            class_weight="balanced",
            max_iter=5000,
            solver="lbfgs",
        ).fit(train_x, target_values.astype(int))
        prediction = model.predict_proba(destination_x)[:, 1]
    else:
        raise ValueError(f"unsupported task: {task}")
    return np.asarray(prediction, dtype=float), float(parameter)


def relation_matrix(
    frame: pd.DataFrame,
    *,
    big5_columns: Iterable[str],
    mbti_columns: Iterable[str],
) -> np.ndarray:
    """Return the cross-scale Pearson relation matrix over matched users."""
    big5 = list(big5_columns)
    mbti = list(mbti_columns)
    output = np.full((len(big5), len(mbti)), np.nan)
    for row, first in enumerate(big5):
        for column, second in enumerate(mbti):
            output[row, column] = safe_pearson(
                frame[first].to_numpy(float),
                frame[second].to_numpy(float),
            )[0]
    return output


def matrix_alignment(
    predicted: np.ndarray,
    observed: np.ndarray,
) -> dict[str, float]:
    """Compare two finite cross-scale relation matrices."""
    first = np.asarray(predicted, dtype=float).ravel()
    second = np.asarray(observed, dtype=float).ravel()
    correlation, p_value = safe_pearson(first, second)
    return {
        "element_r": correlation,
        "element_r_p": p_value,
        "frobenius_distance": float(np.linalg.norm(first - second)),
        "mean_absolute_cell_error": float(np.mean(np.abs(first - second))),
    }


def bridge_permutation_p(
    frame: pd.DataFrame,
    *,
    predicted_big5: Iterable[str],
    predicted_mbti: Iterable[str],
    observed_matrix: np.ndarray,
    observed_alignment: float,
    permutations: int,
    seed: int,
) -> float:
    """Permutation p for predicted cross-scale matrix alignment."""
    rng = np.random.default_rng(seed)
    exceedances = 0
    predicted_big5 = list(predicted_big5)
    predicted_mbti = list(predicted_mbti)
    for _ in range(int(permutations)):
        shuffled = frame.copy()
        order = rng.permutation(len(shuffled))
        shuffled.loc[:, predicted_mbti] = (
            shuffled[predicted_mbti].to_numpy(float)[order]
        )
        matrix = relation_matrix(
            shuffled,
            big5_columns=predicted_big5,
            mbti_columns=predicted_mbti,
        )
        alignment = matrix_alignment(matrix, observed_matrix)["element_r"]
        exceedances += int(alignment >= float(observed_alignment))
    return float((1 + exceedances) / (int(permutations) + 1))
