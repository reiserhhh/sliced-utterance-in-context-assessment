#!/usr/bin/env python3
r"""Run SUICA V7 E2: condition/opportunity contribution accounting.

E2 is intentionally not a denoiser.  It fits a discovery-only comment-level
condition surface, then decomposes each author-half's operator-indexed text
geometry into total, context-carried, and partial components:

\[
T_{uh}=K_{uh}+A_{uh}.
\]

`K` is the component predicted by observed subreddit/time (and, in a declared
sensitivity arm, visible format) context.  `A` is what remains after that
particular surface.  Because condition choice can itself be author-conditioned,
neither component is called personality or noise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_operator_smoke import (  # noqa: E402
    DEFAULT_INPUT,
    _infer_column,
    _load_config,
    _read_table,
    _schema_report,
    _write_json,
)
from suica_core.v7_condition_opportunity import (  # noqa: E402
    CommentContextEncoder,
    MatrixScaler,
    fit_comment_context_encoder,
    fit_matrix_scaler,
    global_r2,
    row_cosines,
    transform_comment_context,
    transform_matrix,
)
from suica_core.v7_observations import (  # noqa: E402
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    prepare_source_panel,
    select_reference_authors,
)
from suica_core.v7_psychometric import RepresentationSpec, RepresentationRuntime, fit_representation  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v7_condition_opportunity.json"
DEFAULT_E0_EXCLUDE = ROOT / "results" / "v7_operator_boundary_audit" / "e0_full_20260714" / "scores_native.csv"
DEFAULT_E1_EXCLUDE = ROOT / "results" / "v7_multiview_projection" / "e1_full_20260714" / "author_features_native.csv"


@dataclass
class OperatorData:
    """One source-half under an observation operator and frozen representation."""

    frame: pd.DataFrame
    embeddings: np.ndarray
    contexts: dict[str, np.ndarray]


@dataclass
class SurfaceRuntime:
    """Discovery-fitted context surface and its input transformation."""

    arm: str
    columns: list[str]
    scaler: MatrixScaler
    model: Ridge

    def predict(self, data: OperatorData) -> np.ndarray:
        """Predict operator embedding coordinates from recorded context only."""
        values = transform_matrix(data.contexts[self.arm], self.scaler)
        return np.asarray(self.model.predict(values), dtype=float)


def parse_args() -> argparse.Namespace:
    """Parse an explicit, label-free E2 request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--exclude-e0", type=Path, default=DEFAULT_E0_EXCLUDE)
    parser.add_argument("--exclude-e1", type=Path, default=DEFAULT_E1_EXCLUDE)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use a small deterministic engineering smoke cohort.")
    parser.add_argument("--max-users", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--user-col", default=None)
    parser.add_argument("--text-col", default=None)
    parser.add_argument("--order-col", default=None)
    parser.add_argument("--condition-col", default=None)
    return parser.parse_args()


def _read_excluded_users(paths: Iterable[Path]) -> set[str]:
    """Read only previous-cohort IDs, never their feature values or labels."""
    users: set[str] = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Fresh E2 selection requires prior-cohort exclusion artifact: {path}. "
                "Pass a valid E0/E1 artifact rather than silently reusing authors."
            )
        frame = pd.read_csv(path, usecols=["user_id"])
        users.update(frame["user_id"].dropna().astype(str))
    return users


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    """Build declared E2 observation operators over a common source panel."""
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_units_per_user"]),
        "max_source_comments_per_user": int(config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(config["max_source_tokens_per_user"]),
    }
    return [ObservationSpec(**{**defaults, **raw}) for raw in config["operators"]]


def _eligible_users(canonical: pd.DataFrame, config: dict[str, Any]) -> set[str]:
    """Apply E2's declared repeated-context eligibility before sampling authors."""
    rows: list[dict[str, Any]] = []
    for user_id, group in canonical.groupby("user_id", sort=False, observed=True):
        order = pd.to_numeric(group["order"], errors="coerce").to_numpy(float)
        finite = order[np.isfinite(order)]
        rows.append({
            "user_id": str(user_id),
            "n_comments": int(len(group)),
            "n_conditions": int(group.loc[group["condition"].astype(str).ne("<unknown>"), "condition"].nunique()),
            "span_days": float((finite.max() - finite.min()) / 86400.0) if len(finite) >= 2 else 0.0,
        })
    summary = pd.DataFrame(rows)
    valid = summary.loc[
        summary["n_comments"].ge(int(config["min_comments_per_user"]))
        & summary["n_conditions"].ge(int(config["min_distinct_conditions"]))
        & summary["span_days"].ge(float(config["min_span_days"])),
        "user_id",
    ]
    return set(valid.astype(str))


def _alternating_source_partition(comments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the capped chronological panel into exact source-disjoint A/B halves."""
    left_rows: list[pd.DataFrame] = []
    right_rows: list[pd.DataFrame] = []
    for _, group in comments.groupby("user_id", sort=False, observed=True):
        ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
        if len(ordered) < 2:
            continue
        left_rows.append(ordered.iloc[::2].copy())
        right_rows.append(ordered.iloc[1::2].copy())
    if not left_rows or not right_rows:
        return comments.iloc[:0].copy(), comments.iloc[:0].copy()
    left = pd.concat(left_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    right = pd.concat(right_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    overlap = set(left["source_row"].astype(int)).intersection(right["source_row"].astype(int))
    if overlap:
        raise RuntimeError(f"E2 alternating source split leaked {len(overlap)} comments.")
    return left, right


def _parse_ints(value: object) -> list[int]:
    """Decode source provenance lists emitted by the V7 observation builder."""
    return [int(part) for part in str(value).split(",") if str(part).strip()]


def _unit_contexts(
    units: pd.DataFrame,
    source_context: pd.DataFrame,
    encoder: CommentContextEncoder,
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """Aggregate source contexts to units using exact token-provenance weights."""
    indexed = source_context.copy()
    if "source_row" not in indexed:
        raise ValueError("Source context needs source_row provenance.")
    indexed = indexed.set_index("source_row", drop=False)
    rows: dict[str, list[np.ndarray]] = {arm: [] for arm in ("primary", "format_enriched")}
    quarters: list[int] = []
    length_bins: list[int] = []
    for unit in units.itertuples(index=False):
        source_rows = _parse_ints(unit.source_rows)
        weights = _parse_ints(getattr(unit, "source_token_weights", ""))
        if len(weights) != len(source_rows) or not weights:
            weights = [1] * len(source_rows)
        source = indexed.reindex(source_rows)
        if source.isna().all(axis=None):
            raise RuntimeError("Observation provenance refers to a missing source context row.")
        weight = np.asarray(weights, dtype=float)
        weight = np.where(weight > 0, weight, 1.0)
        weight = weight / weight.sum()
        for arm in rows:
            matrix = source[encoder.columns(arm)].to_numpy(float)
            rows[arm].append(np.sum(matrix * weight[:, None], axis=0))
        quarter_values = source["quarter"].to_numpy(int)
        quarter_weights = np.bincount(quarter_values, weights=weight, minlength=5)
        quarters.append(int(np.argmax(quarter_weights[1:]) + 1))
        length_bins.append(int(round(float(np.average(source["length_bin"].to_numpy(float), weights=weight)))))
    return {arm: np.vstack(values) for arm, values in rows.items()}, np.asarray(quarters, dtype=int), np.asarray(length_bins, dtype=int)


def _build_operator_data(
    source: pd.DataFrame,
    *,
    spec: ObservationSpec,
    representation: RepresentationRuntime,
    encoder: CommentContextEncoder,
) -> OperatorData:
    """Create one operator's comment/slice embedding and context matrices."""
    source_context = transform_comment_context(source, encoder=encoder)
    source_context["source_row"] = source.reset_index(drop=True)["source_row"].astype(int).to_numpy()
    units = build_observations(source, spec)
    if units.empty:
        raise RuntimeError(f"E2 operator produced zero units: {spec.name}")
    contexts, quarter, length_bin = _unit_contexts(units, source_context, encoder)
    frame = units[["user_id", "split", "source_rows", "source_token_weights", "order_start", "order_end"]].copy()
    frame["quarter"] = quarter
    frame["length_bin"] = length_bin
    return OperatorData(
        frame=frame.reset_index(drop=True),
        embeddings=representation.transform(units["text"]),
        contexts=contexts,
    )


def _mask(data: OperatorData, splits: Iterable[str]) -> np.ndarray:
    return data.frame["split"].astype(str).isin({str(value) for value in splits}).to_numpy()


def _concat_data(parts: list[OperatorData]) -> OperatorData:
    """Concatenate source halves while preserving no-fit provenance boundaries."""
    return OperatorData(
        frame=pd.concat([part.frame for part in parts], ignore_index=True),
        embeddings=np.vstack([part.embeddings for part in parts]),
        contexts={arm: np.vstack([part.contexts[arm] for part in parts]) for arm in parts[0].contexts},
    )


def _fit_surface(data: OperatorData, *, arm: str, alpha: float) -> SurfaceRuntime:
    """Fit a multi-output context surface on discovery rows only."""
    values = data.contexts[arm]
    scaler = fit_matrix_scaler(values)
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(transform_matrix(values, scaler), data.embeddings)
    return SurfaceRuntime(arm=arm, columns=[], scaler=scaler, model=model)


def _select_surface_alpha(discovery: OperatorData, calibration: OperatorData, *, arm: str, grid: list[float]) -> pd.DataFrame:
    """Use calibration comment-level R2, not confirmation or author retrieval, for alpha selection."""
    rows: list[dict[str, Any]] = []
    for alpha in grid:
        runtime = _fit_surface(discovery, arm=arm, alpha=float(alpha))
        predicted = runtime.predict(calibration)
        rows.append({"ridge_alpha": float(alpha), "calibration_context_r2": global_r2(calibration.embeddings, predicted)})
    return pd.DataFrame(rows)


def _best_alpha(selection: pd.DataFrame) -> float:
    """Choose the smallest penalty among equal calibration optima."""
    ordered = selection.sort_values(["calibration_context_r2", "ridge_alpha"], ascending=[False, True])
    return float(ordered.iloc[0]["ridge_alpha"])


def _component_frame(
    data: OperatorData,
    predicted: np.ndarray,
    *,
    baseline_y: np.ndarray,
    baseline_k: np.ndarray,
    baseline_a: np.ndarray,
) -> pd.DataFrame:
    """Aggregate exact T=K+A author-half component vectors."""
    residual = data.embeddings - predicted
    rows: list[dict[str, Any]] = []
    for user_id, group in data.frame.groupby("user_id", sort=False, observed=True):
        index = group.index.to_numpy(int)
        t = np.mean(data.embeddings[index], axis=0) - baseline_y
        k = np.mean(predicted[index], axis=0) - baseline_k
        a = np.mean(residual[index], axis=0) - baseline_a
        row: dict[str, Any] = {
            "user_id": str(user_id),
            "split": str(group["split"].iloc[0]),
            "n_units": int(len(index)),
            "identity_max_abs_error": float(np.max(np.abs(t - k - a))),
        }
        for prefix, values in (("T", t), ("K", k), ("A", a)):
            for dimension, value in enumerate(values):
                row[f"{prefix}_{dimension:02d}"] = float(value)
        rows.append(row)
    return pd.DataFrame(rows)


def _component_matrix(frame: pd.DataFrame, *, users: list[str], prefix: str) -> np.ndarray:
    columns = [column for column in frame if column.startswith(f"{prefix}_")]
    return frame.set_index("user_id").reindex(users)[columns].to_numpy(float)


def _aligned_users(left: pd.DataFrame, right: pd.DataFrame, split: str) -> list[str]:
    """Return source-half authors present under one declared split."""
    left_ids = set(left.loc[left["split"].eq(split), "user_id"].astype(str))
    right_ids = set(right.loc[right["split"].eq(split), "user_id"].astype(str))
    return sorted(left_ids.intersection(right_ids))


def _derangement(n_rows: int, rng: np.random.Generator) -> np.ndarray:
    """Generate a finite derangement for correspondence-null controls."""
    if n_rows < 2:
        raise ValueError("A derangement needs at least two authors.")
    indices = np.arange(n_rows)
    for _ in range(100):
        candidate = rng.permutation(n_rows)
        if not np.any(candidate == indices):
            return candidate
    return np.roll(indices, 1)


def _bootstrap_ci(values: np.ndarray, *, seed: int, repetitions: int) -> tuple[float, float]:
    """Cluster-bootstrap a scalar author-level mean or metric draw vector."""
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not len(finite):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = np.asarray([np.mean(rng.choice(finite, size=len(finite), replace=True)) for _ in range(int(repetitions))])
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _r2_bootstrap(target: np.ndarray, prediction: np.ndarray, *, seed: int, repetitions: int) -> tuple[float, float]:
    """Author bootstrap for an already-held-out author-level R2."""
    n_rows = len(target)
    rng = np.random.default_rng(seed)
    draws = np.asarray([
        global_r2(target[index], prediction[index])
        for index in (rng.integers(0, n_rows, n_rows) for _ in range(int(repetitions)))
    ])
    draws = draws[np.isfinite(draws)]
    return (float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))) if len(draws) else (float("nan"), float("nan"))


def _author_cluster_r2(data: OperatorData, prediction: np.ndarray, *, seed: int, repetitions: int) -> tuple[float, float]:
    """Bootstrap comment-level R2 by resampling authors, not individual rows."""
    users = data.frame["user_id"].astype(str).unique()
    groups = {user: np.flatnonzero(data.frame["user_id"].astype(str).to_numpy() == user) for user in users}
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(int(repetitions)):
        sampled = rng.choice(users, size=len(users), replace=True)
        rows = np.concatenate([groups[str(user)] for user in sampled])
        values.append(global_r2(data.embeddings[rows], prediction[rows]))
    draws = np.asarray(values, dtype=float)
    draws = draws[np.isfinite(draws)]
    if not len(draws):
        return float("nan"), float("nan")
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _stratified_prediction_permutation(
    data: OperatorData,
    prediction: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float]:
    """Break context-to-text pairing inside fixed quarter/length strata."""
    observed = global_r2(data.embeddings, prediction)
    strata = data.frame["quarter"].astype(str) + "::" + data.frame["length_bin"].astype(str)
    index_by_stratum = [group.index.to_numpy(int) for _, group in data.frame.assign(_stratum=strata).groupby("_stratum", sort=False)]
    rng = np.random.default_rng(seed)
    null: list[float] = []
    for _ in range(int(repetitions)):
        order = np.arange(len(data.frame))
        for indices in index_by_stratum:
            if len(indices) > 1:
                order[indices] = rng.permutation(indices)
        null.append(global_r2(data.embeddings, prediction[order]))
    null_values = np.asarray(null, dtype=float)
    p_value = float((1 + np.sum(null_values >= observed)) / (len(null_values) + 1))
    return observed, p_value


def _mean_component_covariance(frame: pd.DataFrame) -> dict[str, float]:
    """Return the non-orthogonal trace accounting behind T=K+A."""
    t = _component_matrix(frame, users=frame["user_id"].astype(str).tolist(), prefix="T")
    k = _component_matrix(frame, users=frame["user_id"].astype(str).tolist(), prefix="K")
    a = _component_matrix(frame, users=frame["user_id"].astype(str).tolist(), prefix="A")
    if len(t) < 2:
        return {key: float("nan") for key in ("trace_T", "trace_K", "trace_A", "trace_KA", "identity_trace_error", "max_identity_error")}
    center = lambda value: value - np.mean(value, axis=0, keepdims=True)
    denominator = float(len(t) - 1)
    trace_t = float(np.trace(center(t).T @ center(t) / denominator))
    trace_k = float(np.trace(center(k).T @ center(k) / denominator))
    trace_a = float(np.trace(center(a).T @ center(a) / denominator))
    trace_ka = float(np.trace(center(k).T @ center(a) / denominator))
    return {
        "trace_T": trace_t,
        "trace_K": trace_k,
        "trace_A": trace_a,
        "trace_KA": trace_ka,
        "identity_trace_error": float(trace_t - trace_k - trace_a - 2.0 * trace_ka),
        "max_identity_error": float(frame["identity_max_abs_error"].max()),
    }


def _auc_from_distances(
    own: np.ndarray,
    strangers: np.ndarray,
    *,
    seed: int,
    bootstrap_iterations: int,
    permutation_iterations: int,
    null_own_draws: np.ndarray | None = None,
    null_stranger_draws: np.ndarray | None = None,
) -> dict[str, float]:
    """Author-cluster AUC with bootstrap CI and a correspondence null.

    Most callers use a broken-correspondence null for an unrestricted stranger
    comparison.  The E2-B matched screen additionally supplies
    ``null_stranger_draws``.  In that case every null replicate draws its
    pseudo-own and pseudo-stranger B records from the *same conditional
    candidate distribution* for each A record.  This is required because an
    unmatched derangement is not exchangeable with a matched comparator.
    """
    own = np.asarray(own, dtype=float)
    strangers = np.asarray(strangers, dtype=float)
    valid = np.isfinite(own) & np.isfinite(strangers).all(axis=1)
    own, strangers = own[valid], strangers[valid]
    if len(own) < 20:
        return {"auc": float("nan"), "auc_ci_low": float("nan"), "auc_ci_high": float("nan"), "permutation_p": float("nan"), "n_authors": int(len(own))}
    def score(positive: np.ndarray, negative: np.ndarray) -> float:
        return float(roc_auc_score(np.r_[np.ones(len(positive)), np.zeros(negative.size)], -np.r_[positive, negative.ravel()]))
    observed = score(own, strangers)
    rng = np.random.default_rng(seed)
    bootstrap = np.asarray([
        score(own[index], strangers[index])
        for index in (rng.integers(0, len(own), len(own)) for _ in range(int(bootstrap_iterations)))
    ])
    if null_own_draws is None and null_stranger_draws is not None:
        raise ValueError("null_stranger_draws requires null_own_draws.")
    if null_own_draws is None:
        # Reordering an already-computed own-distance vector is not a valid
        # correspondence null.  Callers must supply pseudo-own distances made
        # after breaking the right-half author pairing.
        null = np.asarray([], dtype=float)
    else:
        candidates = np.asarray(null_own_draws, dtype=float)
        if candidates.ndim != 2 or candidates.shape[1] != len(valid):
            raise ValueError("null_own_draws must be [permutation, author] after validity filtering.")
        candidates = candidates[:, valid]
        if null_stranger_draws is None:
            null = np.asarray([score(candidate, strangers) for candidate in candidates])
        else:
            negative_candidates = np.asarray(null_stranger_draws, dtype=float)
            if negative_candidates.ndim != 3 or negative_candidates.shape[:2] != (len(candidates), len(valid)):
                raise ValueError("null_stranger_draws must be [permutation, author, draw] aligned with null_own_draws.")
            negative_candidates = negative_candidates[:, valid, :]
            if not np.isfinite(candidates).all() or not np.isfinite(negative_candidates).all():
                raise ValueError("Conditional null draws must be finite after validity filtering.")
            null = np.asarray([
                score(candidate, negative)
                for candidate, negative in zip(candidates, negative_candidates, strict=True)
            ])
    return {
        "auc": observed,
        "auc_ci_low": float(np.quantile(bootstrap, 0.025)),
        "auc_ci_high": float(np.quantile(bootstrap, 0.975)),
        "permutation_p": float((1 + np.sum(null >= observed)) / (len(null) + 1)) if len(null) else float("nan"),
        "n_authors": int(len(own)),
    }


def _component_auc(left: pd.DataFrame, right: pd.DataFrame, *, users: list[str], prefix: str, seed: int, bootstrap_iterations: int, permutation_iterations: int, draws: int) -> dict[str, float]:
    """Test whether a declared component retrieves source-disjoint same authors."""
    x = _component_matrix(left, users=users, prefix=prefix)
    y = _component_matrix(right, users=users, prefix=prefix)
    own = np.linalg.norm(x - y, axis=1)
    rng = np.random.default_rng(seed)
    strangers = np.empty((len(users), int(draws)), dtype=float)
    for index in range(len(users)):
        candidates = rng.integers(0, len(users) - 1, size=int(draws))
        candidates += candidates >= index
        strangers[index] = np.linalg.norm(x[index] - y[candidates], axis=1)
    null_own = np.asarray([
        np.linalg.norm(x - y[_derangement(len(users), rng)], axis=1)
        for _ in range(int(permutation_iterations))
    ])
    return _auc_from_distances(
        own, strangers, seed=seed + 1,
        bootstrap_iterations=bootstrap_iterations,
        permutation_iterations=permutation_iterations,
        null_own_draws=null_own,
    )


def _condition_profile_table(context: pd.DataFrame, *, users: list[str], categories: int) -> np.ndarray:
    """Create smoothed-count-ready subreddit choice profiles for selected authors."""
    output = np.zeros((len(users), categories), dtype=float)
    indexed = context.groupby("user_id", sort=False, observed=True)["condition_code"].apply(list).to_dict()
    for index, user in enumerate(users):
        codes = np.asarray(indexed.get(str(user), []), dtype=int)
        codes = np.where(codes >= 0, codes, categories - 1)
        if len(codes):
            output[index] = np.bincount(codes, minlength=categories)[:categories]
    return output


def _selection_baseline(discovery_context: pd.DataFrame, *, categories: int) -> np.ndarray:
    """Fit the population condition baseline on discovery source comments only."""
    users = discovery_context["user_id"].astype(str).unique().tolist()
    counts = _condition_profile_table(discovery_context, users=users, categories=categories).sum(axis=0)
    return counts / counts.sum() if counts.sum() > 0 else np.full(categories, 1.0 / categories)


def _selection_gain_values(left: np.ndarray, right: np.ndarray, baseline: np.ndarray, *, shrinkage: float) -> np.ndarray:
    r"""Return symmetric cross-half log-score gains using an EB population prior.

    \(q_{uh}=(n_{uh}+\tau q_D)/(N_{uh}+\tau)\) prevents a 24-comment,
    129-category profile from being treated as a fully observed personal
    distribution.  ``tau`` is selected strictly on calibration authors.
    """
    tau = max(float(shrinkage), 0.0)
    left_q = (left + tau * baseline[None, :]) / (left.sum(axis=1, keepdims=True) + tau)
    right_q = (right + tau * baseline[None, :]) / (right.sum(axis=1, keepdims=True) + tau)
    def direction(profile: np.ndarray, target: np.ndarray) -> np.ndarray:
        values = []
        for index in range(len(profile)):
            counts = target[index]
            total = counts.sum()
            values.append(0.0 if total <= 0 else float(np.sum(counts * (np.log(profile[index]) - np.log(baseline))) / total))
        return np.asarray(values, dtype=float)
    return 0.5 * (direction(left_q, right) + direction(right_q, left))


def _select_selection_shrinkage(
    left_context: pd.DataFrame,
    right_context: pd.DataFrame,
    discovery_context: pd.DataFrame,
    *,
    calibration_users: list[str],
    categories: int,
    grid: list[float],
) -> pd.DataFrame:
    """Select empirical-Bayes profile shrinkage using calibration only."""
    left = _condition_profile_table(left_context, users=calibration_users, categories=categories)
    right = _condition_profile_table(right_context, users=calibration_users, categories=categories)
    baseline = _selection_baseline(discovery_context, categories=categories)
    return pd.DataFrame([
        {
            "selection_shrinkage": float(value),
            "calibration_mean_logscore_gain": float(np.mean(_selection_gain_values(left, right, baseline, shrinkage=float(value)))),
            "n_calibration_authors": int(len(calibration_users)),
        }
        for value in grid
    ])


def _selection_gain(
    left_context: pd.DataFrame,
    right_context: pd.DataFrame,
    discovery_context: pd.DataFrame,
    *,
    users: list[str],
    categories: int,
    shrinkage: float,
    seed: int,
    bootstrap_iterations: int,
    permutation_iterations: int,
) -> dict[str, float]:
    """Measure recurrence of observed condition choice, not exposure or preference."""
    left = _condition_profile_table(left_context, users=users, categories=categories)
    right = _condition_profile_table(right_context, users=users, categories=categories)
    baseline = _selection_baseline(discovery_context, categories=categories)
    gains = _selection_gain_values(left, right, baseline, shrinkage=shrinkage)
    low, high = _bootstrap_ci(gains, seed=seed, repetitions=bootstrap_iterations)
    rng = np.random.default_rng(seed + 1)
    null = []
    for _ in range(int(permutation_iterations)):
        left_perm = left[_derangement(len(users), rng)]
        right_perm = right[_derangement(len(users), rng)]
        null.append(float(np.mean(_selection_gain_values(left_perm, right, baseline, shrinkage=shrinkage) + _selection_gain_values(left, right_perm, baseline, shrinkage=shrinkage)) / 2.0))
    observed = float(np.mean(gains))
    return {
        "selection_logscore_gain": observed,
        "selection_logscore_ci_low": low,
        "selection_logscore_ci_high": high,
        "selection_permutation_p": float((1 + np.sum(np.asarray(null) >= observed)) / (len(null) + 1)),
        "selection_shrinkage": float(shrinkage),
        "n_authors": int(len(users)),
    }


def _author_map_metric(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    train_users: list[str],
    confirmation_users: list[str],
    alpha: float,
    seed: int,
    bootstrap_iterations: int,
    permutation_iterations: int,
) -> dict[str, float]:
    """Test whether context-carried K in one half predicts total T in the other."""
    k_left_train = _component_matrix(left, users=train_users, prefix="K")
    t_right_train = _component_matrix(right, users=train_users, prefix="T")
    k_left_test = _component_matrix(left, users=confirmation_users, prefix="K")
    t_right_test = _component_matrix(right, users=confirmation_users, prefix="T")
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(k_left_train, t_right_train)
    prediction = model.predict(k_left_test)
    observed = global_r2(t_right_test, prediction)
    low, high = _r2_bootstrap(t_right_test, prediction, seed=seed, repetitions=bootstrap_iterations)
    rng = np.random.default_rng(seed + 1)
    null = []
    for _ in range(int(permutation_iterations)):
        permuted = Ridge(alpha=float(alpha), fit_intercept=True).fit(k_left_train, t_right_train[rng.permutation(len(t_right_train))])
        null.append(global_r2(t_right_test, permuted.predict(k_left_test)))
    return {
        "k_to_t_r2": observed,
        "k_to_t_ci_low": low,
        "k_to_t_ci_high": high,
        "k_to_t_permutation_p": float((1 + np.sum(np.asarray(null) >= observed)) / (len(null) + 1)),
        "n_train": int(len(train_users)),
        "n_confirmation": int(len(confirmation_users)),
    }


def _select_author_map_alpha(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    discovery_users: list[str],
    calibration_users: list[str],
    grid: list[float],
) -> pd.DataFrame:
    """Select K-to-T map regularization on calibration author pairs only."""
    k_left_train = _component_matrix(left, users=discovery_users, prefix="K")
    t_right_train = _component_matrix(right, users=discovery_users, prefix="T")
    k_left_calibration = _component_matrix(left, users=calibration_users, prefix="K")
    t_right_calibration = _component_matrix(right, users=calibration_users, prefix="T")
    return pd.DataFrame([
        {
            "author_map_ridge_alpha": float(alpha),
            "calibration_k_to_t_r2": global_r2(
                t_right_calibration,
                Ridge(alpha=float(alpha), fit_intercept=True).fit(k_left_train, t_right_train).predict(k_left_calibration),
            ),
            "n_discovery_authors": int(len(discovery_users)),
            "n_calibration_authors": int(len(calibration_users)),
        }
        for alpha in grid
    ])


def _match_comment_pairs(left: pd.DataFrame, right: pd.DataFrame, *, caliper_days: float | None) -> pd.DataFrame:
    """Greedily pair exact-subreddit A/B comments by nearest time without replacement."""
    rows: list[dict[str, Any]] = []
    left_groups = {str(user): group for user, group in left.groupby("user_id", sort=False, observed=True)}
    right_groups = {str(user): group for user, group in right.groupby("user_id", sort=False, observed=True)}
    cap_seconds = np.inf if caliper_days is None else float(caliper_days) * 86400.0
    for user in sorted(set(left_groups).intersection(right_groups)):
        a, b = left_groups[user], right_groups[user]
        for condition in sorted(set(a["condition"].astype(str)).intersection(b["condition"].astype(str))):
            a_rows = a.loc[a["condition"].astype(str).eq(condition)]
            b_rows = b.loc[b["condition"].astype(str).eq(condition)]
            candidates: list[tuple[float, int, int]] = []
            for a_value in a_rows.itertuples(index=False):
                for b_value in b_rows.itertuples(index=False):
                    delta = abs(float(a_value.order) - float(b_value.order))
                    if delta <= cap_seconds:
                        candidates.append((delta, int(a_value.source_row), int(b_value.source_row)))
            used_a: set[int] = set()
            used_b: set[int] = set()
            for delta, source_a, source_b in sorted(candidates):
                if source_a in used_a or source_b in used_b:
                    continue
                used_a.add(source_a)
                used_b.add(source_b)
                rows.append({"user_id": user, "left_source_row": source_a, "right_source_row": source_b, "condition": condition, "delta_days": delta / 86400.0})
    return pd.DataFrame(rows)


def _matched_support(pairs: pd.DataFrame, users: list[str], config: dict[str, Any]) -> tuple[list[str], float]:
    """Apply support requirements without inspecting embeddings or outcomes."""
    if pairs.empty:
        return [], 0.0
    count = pairs.groupby("user_id", observed=True).size()
    conditions = pairs.groupby("user_id", observed=True)["condition"].nunique()
    accepted = [
        str(user) for user in users
        if int(count.get(user, 0)) >= int(config["minimum_pair_count"])
        and int(conditions.get(user, 0)) >= int(config["minimum_pair_conditions"])
    ]
    return accepted, float(len(accepted) / len(users)) if users else 0.0


def _select_caliper(left: pd.DataFrame, right: pd.DataFrame, calibration_users: list[str], config: dict[str, Any]) -> tuple[float | None, pd.DataFrame, float]:
    """Choose the smallest feasible time caliper from calibration support only."""
    rows: list[dict[str, Any]] = []
    selected: float | None = None
    selected_coverage = 0.0
    for value in config["time_calipers_days"]:
        caliper = None if value is None else float(value)
        pairs = _match_comment_pairs(left, right, caliper_days=caliper)
        _, coverage = _matched_support(pairs, calibration_users, config)
        rows.append({"caliper_days": "infinity" if caliper is None else caliper, "calibration_coverage": coverage})
        if selected is None and coverage >= float(config["minimum_matched_coverage"]):
            selected, selected_coverage = caliper, coverage
    return selected, pd.DataFrame(rows), selected_coverage


def _metadata_by_user(
    source: pd.DataFrame,
    primary_context: pd.DataFrame,
    components: pd.DataFrame,
    *,
    users: list[str],
    source_rows_by_user: dict[str, set[int]] | None = None,
) -> tuple[np.ndarray, list[set[str]]]:
    """Build recorded-selection/K/opportunity metadata for E2-B matching.

    When ``source_rows_by_user`` is supplied, all selection and opportunity
    summaries use only exact-condition matched source comments.  The frozen K
    coordinates remain the declared operator-level context surface summary.
    """
    primary_columns = [column for column in primary_context if column.startswith("ctx::")]
    context = primary_context[[*primary_columns]].copy()
    context["source_row"] = source.reset_index(drop=True)["source_row"].astype(int).to_numpy()
    merged = source[["user_id", "source_row", "order", "condition", "text"]].merge(context, on="source_row", how="left")
    comp = components.set_index("user_id")
    rows: list[np.ndarray] = []
    condition_sets: list[set[str]] = []
    k_columns = [column for column in components if column.startswith("K_")]
    for user in users:
        group = merged.loc[merged["user_id"].astype(str).eq(str(user))]
        if source_rows_by_user is not None:
            allowed = source_rows_by_user.get(str(user), set())
            group = group.loc[group["source_row"].astype(int).isin(allowed)]
        if group.empty:
            raise ValueError(f"No recorded source rows remain for E2-B matching user {user!r}.")
        selection = group[primary_columns].to_numpy(float).mean(axis=0)
        order = group["order"].to_numpy(float)
        span = np.log1p(max(float(order.max() - order.min()), 0.0)) if len(order) > 1 else 0.0
        tokens = group["text"].fillna("").astype(str).str.split().map(len).sum()
        rows.append(np.r_[
            selection,
            comp.loc[str(user), k_columns].to_numpy(float),
            np.log1p(float(len(group))),
            span,
            np.log1p(float(tokens)),
        ])
        condition_sets.append(set(group["condition"].astype(str)))
    return np.vstack(rows), condition_sets


def _pair_source_rows(pairs: pd.DataFrame, users: list[str]) -> tuple[dict[str, set[int]], dict[str, set[int]]]:
    """Return source-row provenance for exact-condition matched users only."""
    left_rows: dict[str, set[int]] = {}
    right_rows: dict[str, set[int]] = {}
    selected = pairs.loc[pairs["user_id"].astype(str).isin({str(user) for user in users})]
    for user, group in selected.groupby("user_id", sort=False, observed=True):
        left_rows[str(user)] = {int(value) for value in group["left_source_row"].tolist()}
        right_rows[str(user)] = {int(value) for value in group["right_source_row"].tolist()}
    return left_rows, right_rows


def _source_language_labels(
    left_source: pd.DataFrame,
    right_source: pd.DataFrame,
    left_rows: dict[str, set[int]],
    right_rows: dict[str, set[int]],
    *,
    users: list[str],
) -> list[str]:
    """Return a recorded language class or an explicit unobserved sentinel."""
    language_column = next((column for column in ("language", "lang") if column in left_source.columns and column in right_source.columns), None)
    if language_column is None:
        return ["language_unrecorded" for _ in users]
    labels: list[str] = []
    for user in users:
        left = left_source.loc[left_source["source_row"].astype(int).isin(left_rows.get(str(user), set())), language_column]
        right = right_source.loc[right_source["source_row"].astype(int).isin(right_rows.get(str(user), set())), language_column]
        values = {str(value).strip().lower() for value in pd.concat([left, right]) if str(value).strip()}
        labels.append(next(iter(values)) if len(values) == 1 else "language_mixed_or_missing")
    return labels


def _support_classes(pairs: pd.DataFrame, *, users: list[str], config: dict[str, Any]) -> list[str]:
    """Assign the registered exact-condition support class without outcomes.

    E2-B already requires every retained author to have the same minimum exact
    pair and distinct-condition support.  Further post-hoc bins such as
    ``8--11`` versus ``12--15`` pairs would create arbitrary power loss while
    matched count and token amount are already numeric matching coordinates.
    """
    counts = pairs.groupby("user_id", observed=True).size()
    conditions = pairs.groupby("user_id", observed=True)["condition"].nunique()
    minimum_pairs = int(config["minimum_pair_count"])
    minimum_conditions = int(config["minimum_pair_conditions"])
    label = f"exact_pair_support_ge_{minimum_pairs}_and_conditions_ge_{minimum_conditions}"
    labels: list[str] = []
    for user in users:
        count = int(counts.get(str(user), 0))
        condition_count = int(conditions.get(str(user), 0))
        if count < minimum_pairs or condition_count < minimum_conditions:
            raise ValueError(f"User {user!r} does not meet the registered E2-B support class.")
        labels.append(label)
    return labels


def _matched_strata_inputs(
    left_source: pd.DataFrame,
    right_source: pd.DataFrame,
    source_context_left: pd.DataFrame,
    source_context_right: pd.DataFrame,
    left_components: pd.DataFrame,
    right_components: pd.DataFrame,
    pairs: pd.DataFrame,
    *,
    users: list[str],
    config: dict[str, Any],
) -> tuple[np.ndarray, list[set[str]], list[str]]:
    """Build symmetric recorded-condition inputs for E2-B strata.

    No residual embeddings are supplied here.  The metadata combines matched
    A/B selection, frozen K coordinates, log comment count, span, and token
    amount.  Exact classes encode constants required by the registered design.
    """
    left_rows, right_rows = _pair_source_rows(pairs, users)
    left_metadata, left_sets = _metadata_by_user(
        left_source, source_context_left, left_components,
        users=users, source_rows_by_user=left_rows,
    )
    right_metadata, right_sets = _metadata_by_user(
        right_source, source_context_right, right_components,
        users=users, source_rows_by_user=right_rows,
    )
    language = _source_language_labels(left_source, right_source, left_rows, right_rows, users=users)
    support = _support_classes(pairs, users=users, config=config)
    exact_classes = [
        f"operator=native|representation=common_tfidf_svd|source_arm=paired|{language_value}|{support_value}"
        for language_value, support_value in zip(language, support, strict=True)
    ]
    return 0.5 * (left_metadata + right_metadata), [left | right for left, right in zip(left_sets, right_sets, strict=True)], exact_classes


def _select_matching_calipers(
    metadata: np.ndarray,
    condition_sets: list[set[str]],
    exact_classes: list[str],
    *,
    metadata_scaler: MatrixScaler,
    population_size: int,
    config: dict[str, Any],
) -> tuple[dict[str, float] | None, pd.DataFrame, MatchedStrata | None]:
    """Select the strictest feasible E2-B stratum calipers on calibration only."""
    rows: list[dict[str, Any]] = []
    selected: dict[str, float] | None = None
    selected_strata: MatchedStrata | None = None
    for minimum_jaccard in sorted((float(value) for value in config["condition_jaccard_grid"]), reverse=True):
        for numeric_caliper in sorted(float(value) for value in config["numeric_caliper_grid"]):
            strata = _build_matched_strata(
                metadata, condition_sets, exact_classes,
                metadata_scaler=metadata_scaler,
                numeric_caliper=numeric_caliper,
                minimum_jaccard=minimum_jaccard,
                min_size=int(config["matched_block_size_min"]),
                max_size=int(config["matched_block_size_max"]),
            )
            coverage = strata.coverage(population_size)
            rows.append({
                "minimum_jaccard": minimum_jaccard,
                "numeric_caliper": numeric_caliper,
                "n_strata": int(len(strata.groups)),
                "n_retained_authors": int(sum(len(group) for group in strata.groups)),
                "coverage": coverage,
                "feasible": bool(coverage >= float(config["minimum_matched_coverage"]) and len(strata.groups) >= 2),
            })
            if selected is None and coverage >= float(config["minimum_matched_coverage"]) and len(strata.groups) >= 2:
                selected = {"minimum_jaccard": minimum_jaccard, "numeric_caliper": numeric_caliper}
                selected_strata = strata
    return selected, pd.DataFrame(rows), selected_strata


@dataclass(frozen=True)
class MatchedStrata:
    """Disjoint E2-B strata frozen solely from recorded condition metadata."""

    groups: tuple[np.ndarray, ...]
    numeric_distance: np.ndarray
    jaccard: np.ndarray
    exact_class: tuple[str, ...]
    numeric_caliper: float
    minimum_jaccard: float

    def coverage(self, population_size: int) -> float:
        """Return the share of the declared population retained in strata."""
        used = int(sum(len(group) for group in self.groups))
        return float(used / population_size) if population_size else 0.0

    def diagnostics(self) -> dict[str, float | int | str | bool]:
        """Summarize matching support without serializing author identities."""
        sizes = np.asarray([len(group) for group in self.groups], dtype=int)
        return {
            "matched_null_method": "within_stratum_identity_permutation_rank",
            "matched_null_exchangeable": True,
            "matching_surface": "paired_A_B_metadata_plus_condition_jaccard",
            "n_strata": int(len(self.groups)),
            "stratum_size_min": int(sizes.min()) if len(sizes) else 0,
            "stratum_size_median": float(np.median(sizes)) if len(sizes) else float("nan"),
            "stratum_size_max": int(sizes.max()) if len(sizes) else 0,
            "numeric_caliper": float(self.numeric_caliper),
            "minimum_jaccard": float(self.minimum_jaccard),
        }


def _pairwise_match_surfaces(
    metadata: np.ndarray,
    condition_sets: list[set[str]],
    exact_classes: list[str],
    *,
    metadata_scaler: MatrixScaler,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct label-free numeric, condition, and exact-class constraints."""
    metadata = np.asarray(metadata, dtype=float)
    if len(metadata) != len(condition_sets) or len(metadata) != len(exact_classes):
        raise ValueError("Matched strata require metadata, condition sets, and exact classes for every author.")
    scaled = transform_matrix(metadata, metadata_scaler)
    numeric = np.sqrt(np.mean((scaled[:, None, :] - scaled[None, :, :]) ** 2, axis=2))
    jaccard = np.ones_like(numeric)
    for left_index, left_set in enumerate(condition_sets):
        for right_index, right_set in enumerate(condition_sets):
            union = left_set | right_set
            jaccard[left_index, right_index] = float(len(left_set & right_set) / len(union)) if union else 1.0
    exact = np.equal.outer(np.asarray(exact_classes, dtype=object), np.asarray(exact_classes, dtype=object))
    np.fill_diagonal(exact, False)
    return numeric, jaccard, exact


def _greedy_disjoint_strata(
    numeric: np.ndarray,
    jaccard: np.ndarray,
    exact: np.ndarray,
    exact_classes: list[str],
    *,
    numeric_caliper: float,
    minimum_jaccard: float,
    min_size: int,
    max_size: int,
) -> MatchedStrata:
    """Create deterministic all-pairs-compatible strata without residual access.

    The grouping is deliberately a registered design procedure rather than an
    outcome optimization.  A group is retained only when every pair satisfies
    the same numeric, Jaccard, and exact-class constraints; unmatched authors
    remain outside the E2-B confirmation statistic.
    """
    if min_size < 2 or max_size < min_size:
        raise ValueError("Matched strata require 2 <= min_size <= max_size.")
    eligible = (numeric <= float(numeric_caliper)) & (jaccard >= float(minimum_jaccard)) & exact
    np.fill_diagonal(eligible, False)
    unassigned: set[int] = set(range(len(numeric)))
    groups: list[np.ndarray] = []
    while len(unassigned) >= min_size:
        available = np.asarray(sorted(unassigned), dtype=int)
        degrees = {index: int(np.sum(eligible[index, available])) for index in available}
        seed = min(available.tolist(), key=lambda index: (degrees[index], index))
        group = [seed]
        while len(group) < max_size:
            candidates = [
                index for index in available.tolist()
                if index not in group and all(bool(eligible[index, member]) for member in group)
            ]
            if not candidates:
                break
            # Preserve future clique support first; tie-break by tighter
            # recorded-condition match and then a deterministic index.
            candidate = min(
                candidates,
                key=lambda index: (
                    -sum(bool(eligible[index, other]) for other in available.tolist() if other not in group),
                    float(np.mean([numeric[index, member] for member in group])),
                    -float(np.mean([jaccard[index, member] for member in group])),
                    index,
                ),
            )
            group.append(candidate)
        if len(group) >= min_size:
            groups.append(np.asarray(sorted(group), dtype=int))
            unassigned.difference_update(group)
        else:
            unassigned.remove(seed)
    return MatchedStrata(
        groups=tuple(groups),
        numeric_distance=np.asarray(numeric, dtype=float),
        jaccard=np.asarray(jaccard, dtype=float),
        exact_class=tuple(str(value) for value in exact_classes),
        numeric_caliper=float(numeric_caliper),
        minimum_jaccard=float(minimum_jaccard),
    )


def _build_matched_strata(
    metadata: np.ndarray,
    condition_sets: list[set[str]],
    exact_classes: list[str],
    *,
    metadata_scaler: MatrixScaler,
    numeric_caliper: float,
    minimum_jaccard: float,
    min_size: int,
    max_size: int,
) -> MatchedStrata:
    """Build disjoint matched strata and retain the actual exact-class labels."""
    numeric, jaccard, exact = _pairwise_match_surfaces(
        metadata, condition_sets, exact_classes, metadata_scaler=metadata_scaler
    )
    strata = _greedy_disjoint_strata(
        numeric, jaccard, exact, exact_classes,
        numeric_caliper=numeric_caliper, minimum_jaccard=minimum_jaccard,
        min_size=min_size, max_size=max_size,
    )
    return strata


def _stratum_rank_statistic(left: np.ndarray, right: np.ndarray, strata: MatchedStrata, *, permutations: tuple[np.ndarray, ...] | None = None) -> tuple[float, np.ndarray]:
    """Compute the registered linked-vs-stranger rank statistic by stratum."""
    contributions: list[float] = []
    stratum_scores: list[float] = []
    for stratum_index, group in enumerate(strata.groups):
        right_order = group if permutations is None else permutations[stratum_index]
        distances = np.linalg.norm(left[group][:, None, :] - right[right_order][None, :, :], axis=2)
        values: list[float] = []
        for local_index in range(len(group)):
            own = distances[local_index, local_index]
            strangers = np.delete(distances[local_index], local_index)
            values.append(float(np.mean(own < strangers) + 0.5 * np.mean(own == strangers)))
        contributions.extend(values)
        stratum_scores.append(float(np.mean(values)))
    if not contributions:
        return float("nan"), np.asarray([], dtype=float)
    return float(np.mean(contributions)), np.asarray(stratum_scores, dtype=float)


def _matched_stratified_metric(
    left: np.ndarray,
    right: np.ndarray,
    strata: MatchedStrata,
    *,
    bootstrap_iterations: int,
    permutation_iterations: int,
    seed: int,
) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate E2-B with cluster bootstrap and exact-class permutation null."""
    observed, per_stratum = _stratum_rank_statistic(left, right, strata)
    if not np.isfinite(observed) or len(strata.groups) < 2:
        raise ValueError("E2-B needs at least two disjoint matched strata.")
    rng = np.random.default_rng(seed)
    sizes = np.asarray([len(group) for group in strata.groups], dtype=float)
    bootstrap = np.asarray([
        float(np.average(per_stratum[index], weights=sizes[index]))
        for index in (rng.integers(0, len(strata.groups), len(strata.groups)) for _ in range(int(bootstrap_iterations)))
    ])
    null_values: list[float] = []
    for _ in range(int(permutation_iterations)):
        permutations = tuple(group[rng.permutation(len(group))] for group in strata.groups)
        value, _ = _stratum_rank_statistic(left, right, strata, permutations=permutations)
        null_values.append(value)
    null = np.asarray(null_values, dtype=float)
    stratum_rows: list[dict[str, Any]] = []
    balance_rows: list[dict[str, Any]] = []
    for index, group in enumerate(strata.groups, start=1):
        matrix = np.ix_(group, group)
        numeric = strata.numeric_distance[matrix]
        jaccard = strata.jaccard[matrix]
        mask = ~np.eye(len(group), dtype=bool)
        stratum_rows.append({
            "stratum_id": index,
            "n_authors": int(len(group)),
            "numeric_distance_mean": float(np.mean(numeric[mask])),
            "numeric_distance_max": float(np.max(numeric[mask])),
            "condition_jaccard_mean": float(np.mean(jaccard[mask])),
            "condition_jaccard_min": float(np.min(jaccard[mask])),
            "numeric_caliper": float(strata.numeric_caliper),
            "minimum_jaccard": float(strata.minimum_jaccard),
        })
        balance_rows.append({
            "stratum_id": index,
            "all_numeric_pairs_within_caliper": bool(np.all(numeric[mask] <= strata.numeric_caliper)),
            "all_condition_pairs_within_caliper": bool(np.all(jaccard[mask] >= strata.minimum_jaccard)),
            "exact_class_uniform": len({strata.exact_class[value] for value in group}) == 1,
        })
    metrics = {
        "auc": float(observed),
        "auc_ci_low": float(np.quantile(bootstrap, 0.025)),
        "auc_ci_high": float(np.quantile(bootstrap, 0.975)),
        "permutation_p": float((1 + np.sum(null >= observed)) / (len(null) + 1)),
        "n_authors": int(sum(len(group) for group in strata.groups)),
        "n_strata": int(len(strata.groups)),
    }
    null_frame = pd.DataFrame({
        "permutation": np.arange(1, len(null) + 1, dtype=int),
        "conditional_rank_auc": null,
        "observed_conditional_rank_auc": float(observed),
        "method": "within_stratum_identity_permutation_rank",
    })
    return metrics, null_frame, pd.DataFrame(stratum_rows), pd.DataFrame(balance_rows)


def _holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Apply Holm correction to the declared primary confirmation endpoint family."""
    finite = [(key, value) for key, value in p_values.items() if np.isfinite(value)]
    ordered = sorted(finite, key=lambda item: item[1])
    output = {key: float("nan") for key in p_values}
    running = 0.0
    m = len(ordered)
    for index, (key, value) in enumerate(ordered):
        running = max(running, min(1.0, (m - index) * float(value)))
        output[key] = running
    return output


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decision(
    primary: dict[str, Any],
    *,
    matched_available: bool,
    matched_status: str | None = None,
    config: dict[str, Any],
) -> tuple[str, str]:
    """Apply E2's bounded primary-native screen, never a personality verdict."""
    thresholds = config["screen_thresholds"]
    alpha = float(thresholds["alpha"])
    total = primary["total_auc"] >= float(thresholds["minimum_auc"]) and primary["total_auc_ci_low"] > 0.5 and primary["total_auc_q"] <= alpha
    selection_recurrence = primary["selection_gain_ci_low"] > 0.0 and primary["selection_gain_q"] <= alpha
    context_surface = (
        primary["context_r2"] >= float(thresholds["minimum_context_r2"])
        and primary["context_r2_ci_low"] > 0.0
        and primary["context_r2_q"] <= alpha
    )
    context_transport = (
        primary["k_to_t_r2"] >= float(thresholds["minimum_context_r2"])
        and primary["k_to_t_ci_low"] > 0.0
        and primary["k_to_t_q"] <= alpha
    )
    if not matched_available:
        if matched_status == "REFUSE_MATCH_BALANCE":
            return "REFUSE_MATCH_BALANCE", "No predeclared numeric/Jaccard matching surface produced enough balanced disjoint confirmation strata; E2-B is intentionally not evaluated."
        if matched_status == "REFUSE_INCOMPLETE_EXACT_CONDITION_SUPPORT":
            return "REFUSE_INCOMPLETE_EXACT_CONDITION_SUPPORT", "Source-row provenance did not retain complete A/B condition-pair support for every retained author, so E2-B is intentionally not evaluated."
        return "REFUSE_INSUFFICIENT_MATCHED_SUPPORT", "The declared source-pair support screen did not retain enough confirmation authors for E2-B."
    if not bool(primary.get("partial_null_exchangeable", False)):
        return "REFUSE_INVALID_MATCHED_NULL", "The matched partial statistic lacks a conditionally exchangeable null constructed within its frozen strata, so it cannot enter the E2 decision."
    partial = primary["partial_auc"] >= float(thresholds["minimum_auc"]) and primary["partial_auc_ci_low"] > 0.5 and primary["partial_auc_q"] <= alpha
    if total and selection_recurrence and partial and context_surface and context_transport:
        return "TOTAL_SELECTION_CONTEXT_AND_PARTIAL_STRUCTURE_SUPPORTED", "The native primary view passes total alignment, observed-selection recurrence, material context-surface, context-to-total transport, and matched partial-structure screens under the declared no-label protocol."
    if total and selection_recurrence and partial:
        return "TOTAL_SELECTION_AND_PARTIAL_STRUCTURE_SUPPORTED_WITH_UNRESOLVED_CONTEXT_TRANSPORT", "Total alignment, observed-selection recurrence, and matched partial structure pass. The recorded primary condition surface and/or its K-to-T transport does not meet the material lower-confidence-bound rule, so condition accounting remains unresolved."
    if total:
        return "TOTAL_STRUCTURE_REPRODUCED_WITH_UNRESOLVED_SELECTION_OR_PARTIAL_ACCOUNTING", "Total source-disjoint author alignment is reproduced, but observed-selection recurrence and/or the matched partial screen is not fully supported."
    return "NONTRIVIAL_TOTAL_STRUCTURE_NOT_SUPPORTED", "The native primary total-structure endpoint did not pass its declared AUC/CI/Holm screen; sensitivity arms cannot rescue it."


def _write_report(
    path: Path,
    *,
    output_dir: Path,
    manifest: dict[str, Any],
    selection: pd.DataFrame,
    condition_metrics: pd.DataFrame,
    variance: pd.DataFrame,
    retrieval: pd.DataFrame,
    matched: pd.DataFrame,
    primary: dict[str, Any],
    decision: str,
    rationale: str,
) -> None:
    """Write a human-auditable E2 report without text or author identities."""
    text = rf"""# SUICA V7 E2: Condition/Opportunity Contribution Accounting

## Scope

E2 tests an operator-indexed text-geometry accounting relation, not a
psychological scale:

\[
y_{{ui}}=\Phi_D(x_{{ui}}),\qquad
\widehat m(d)=\widehat E_D[y\mid d],
\]
\[
T_{{uh}}=\bar y_{{uh}}-\bar y_D,
\quad K_{{uh}}=\overline{{\widehat m(d)}}_{{uh}}-\overline{{\widehat m(d)}}_D,
\quad A_{{uh}}=\overline{{y-\widehat m(d)}}_{{uh}}-\overline{{y-\widehat m(d)}}_D,
\quad \boxed{{T=K+A}}.
\]

`d` consists of recorded subreddit/time context in the primary arm; the
format-enriched arm adds visible length/format opportunity.  Reddit selection
is explicitly retained as an observed author-conditioned process rather than
subtracted as nuisance.

## Design

- Fresh selected authors: `{manifest['n_selected_authors']:,}` after excluding E0/E1 cohorts.
- Declared source panel: exactly `{manifest['source_comments_per_author']}` chronologically spaced comments per author, then alternating source-disjoint A/B halves.
- Split counts: discovery `{manifest['split_counts']['discovery']}`, calibration `{manifest['split_counts']['calibration']}`, confirmation `{manifest['split_counts']['confirmation']}`.
- Representation, context vocabulary, length deciles and surfaces: discovery only. Ridge alpha: calibration only. Confirmation: evaluation only.
- External labels / Big Five / MBTI / clinical values: `not read`.
- Raw text, subreddit names, and author IDs: `not exported`.

## Calibration selection

{selection.to_markdown(index=False, floatfmt='.3f')}

## Condition-surface and selection metrics

`context_r2` is comment-level confirmation R2 from the frozen surface; its
permutation breaks context-to-text pairing within year-quarter/length-decile
strata. `selection_logscore_gain` compares each author's A-half subreddit
profile predicting B against the discovery population profile, symmetrized
over A/B. `K_to_T_r2` maps context-carried A-half structure to total B-half
structure. Only the native/primary row licenses the decision below; other rows
are sensitivity descriptions and cannot rescue a failed primary test.

{condition_metrics.to_markdown(index=False, floatfmt='.3f')}

## Non-orthogonal variance accounting

The traces obey
\[
\operatorname{{tr}}\Sigma_T=
\operatorname{{tr}}\Sigma_K+
\operatorname{{tr}}\Sigma_A+2\operatorname{{tr}}\Sigma_{{KA}}.
\]
`trace_K / trace_T` is intentionally not reported as standalone “variance
explained”: the covariance term can be positive or negative.

{variance.to_markdown(index=False, floatfmt='.3f')}

## Source-disjoint component retrieval

Each AUC asks whether A-side component vectors are closer to their own B-side
vector than to sampled B-side strangers. These are author-alignment metrics,
not personality validity coefficients.

{retrieval.to_markdown(index=False, floatfmt='.3f')}

## Matched partial screen (native primary only)

The partial screen is deliberately not a generic A/B retrieval test. First,
source-disjoint A/B comment pairs are restricted by the registered exact
condition/time support rule.  On calibration authors only, we select the first
registered pair of condition-overlap and numeric calipers that reaches the
coverage gate.  Numeric distance is computed from the frozen paired selection
profile, frozen context-carried configuration `K`, matched comment count,
matched time span, and matched token count. Exact fields are operator,
representation, source arm, language, and the registered support class.

Confirmation authors are packed into disjoint 4--8-author strata only when
every within-stratum pair satisfies the frozen calipers. The observed statistic
compares each author's A residual to its linked B residual against the other B
residuals *within its own stratum*. Its null permutes B identities independently
within each frozen stratum and recomputes the same rank statistic. This makes
the null conditionally exchangeable under the declared matching surface; it is
not an unrestricted author derangement or an iid candidate-pool draw.

If the selected Jaccard caliper is zero, the result is conditional on the
numeric matching coordinates but does **not** establish literal matched-topic
or matched-subreddit equivalence. That limitation is recorded rather than
silently converted into a fixed-condition claim.

{matched.to_markdown(index=False, floatfmt='.3f')}

## Registered primary-native summary

```json
{json.dumps(primary, indent=2, sort_keys=True)}
```

**{decision}** — {rationale}

## Claim boundary

E2 may establish observed-selection recurrence, held-out context predictability,
exact algebraic component accounting, and survival/collapse under a declared
matched partial screen. It does **not** identify exposure opportunity, causal
context effects, a fixed-condition response operator, temporal personality,
external validity, a clinical score, or a human psychological construct.

## Artifacts

- `{output_dir / 'run_manifest.json'}`
- `{output_dir / 'condition_model_metrics.csv'}`
- `{output_dir / 'author_map_selection.csv'}`
- `{output_dir / 'selection_profile_selection.csv'}`
- `{output_dir / 'selection_metrics.csv'}`
- `{output_dir / 'variance_accounting.csv'}`
- `{output_dir / 'component_retrieval_metrics.csv'}`
- `{output_dir / 'matched_partial_metrics.csv'}`
- `{output_dir / 'matched_caliper_selection.csv'}`
- `{output_dir / 'matched_strata.csv'}`
- `{output_dir / 'matching_balance.csv'}`
- `{output_dir / 'matched_partial_null.parquet'}` (or CSV fallback)
- `{output_dir / 'permutation_null.csv'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    """Execute the E2 protocol and write only aggregate, label-free artifacts."""
    args = parse_args()
    config = _load_config(args.config)
    if args.seed is not None:
        config["seed"] = int(args.seed)
    if args.max_users is not None:
        config["max_users"] = int(args.max_users)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["max_source_comments_per_user"] = min(int(config["max_source_comments_per_user"]), 24)
        config["min_comments_per_user"] = min(int(config["min_comments_per_user"]), 24)
        config["min_distinct_conditions"] = min(int(config["min_distinct_conditions"]), 3)
        config["min_span_days"] = min(int(config["min_span_days"]), 90)
        config["representation"]["max_features"] = min(int(config["representation"]["max_features"]), 2000)
        config["bootstrap_iterations"] = min(int(config["bootstrap_iterations"]), 199)
        config["permutation_iterations"] = min(int(config["permutation_iterations"]), 99)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir or ROOT / "results" / "v7_condition_opportunity" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or ROOT / "reports" / "V7_CONDITION_OPPORTUNITY.md"

    excluded = _read_excluded_users([args.exclude_e0, args.exclude_e1])
    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], args.user_col, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], args.text_col, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], args.order_col, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], args.condition_col, required=False),
    }
    canonical = canonicalize_comments(
        raw,
        user_col=str(column_map["user"]),
        text_col=str(column_map["text"]),
        order_col=column_map["order"],
        condition_col=column_map["condition"],
        min_tokens=int(config["min_tokens_per_unit"]),
        mask_personality_terms=bool(config["mask_personality_terms"]),
    )
    eligible = _eligible_users(canonical, config)
    candidate = canonical.loc[canonical["user_id"].astype(str).isin(eligible)].copy()
    selected = select_reference_authors(
        candidate,
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_users=int(config["max_users"]),
        seed=int(config["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.1-e2-condition-opportunity-v1",
    )
    specs = _operator_specs(config)
    source_panel = prepare_source_panel(selected, specs[0])
    source_counts = source_panel.groupby("user_id", observed=True).size()
    if not source_counts.eq(int(config["max_source_comments_per_user"])).all():
        raise RuntimeError("E2 requires exactly the declared source-comment count per selected author.")
    if set(source_panel["user_id"].astype(str)).intersection(excluded):
        raise RuntimeError("E2 fresh cohort leaked an E0/E1 author.")
    split_counts = source_panel.groupby("split", observed=True)["user_id"].nunique().to_dict()
    minimum_split_support = 16 if args.quick else 40
    if any(int(split_counts.get(split, 0)) < minimum_split_support for split in ("discovery", "calibration", "confirmation")):
        raise RuntimeError(f"E2 cohort cannot support the declared three-way protocol: {split_counts}")
    _schema_report(
        output_dir / "data_schema.md",
        source=args.input,
        raw=raw,
        column_map=column_map,
        canonical=canonical,
        selected=source_panel,
        mask_personality_terms=bool(config["mask_personality_terms"]),
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_comments_per_user=int(config["max_source_comments_per_user"]),
    )
    left_source, right_source = _alternating_source_partition(source_panel)
    if set(left_source["source_row"].astype(int)).intersection(right_source["source_row"].astype(int)):
        raise RuntimeError("E2 source provenance overlap after alternating split.")

    discovery_users = sorted(source_panel.loc[source_panel["split"].eq("discovery"), "user_id"].astype(str).unique())
    representation = fit_representation(
        source_panel.loc[source_panel["split"].eq("discovery")],
        RepresentationSpec(
            max_features=int(config["representation"]["max_features"]),
            ngram_min=int(config["representation"]["ngram_range"][0]),
            ngram_max=int(config["representation"]["ngram_range"][1]),
            svd_dimensions=int(config["representation"]["svd_dimensions"]),
            factor_count=1,
            seed=int(config["seed"]),
        ),
    )
    encoder = fit_comment_context_encoder(
        source_panel,
        discovery_user_ids=discovery_users,
        max_conditions=int(config["max_condition_vocabulary"]),
    )
    source_context_left = transform_comment_context(left_source, encoder=encoder)
    source_context_left["source_row"] = left_source.reset_index(drop=True)["source_row"].astype(int).to_numpy()
    source_context_right = transform_comment_context(right_source, encoder=encoder)
    source_context_right["source_row"] = right_source.reset_index(drop=True)["source_row"].astype(int).to_numpy()
    source_context_discovery = pd.concat([
        source_context_left.loc[left_source["split"].reset_index(drop=True).eq("discovery")],
        source_context_right.loc[right_source["split"].reset_index(drop=True).eq("discovery")],
    ], ignore_index=True)
    left_data = {spec.name: _build_operator_data(left_source, spec=spec, representation=representation, encoder=encoder) for spec in specs}
    right_data = {spec.name: _build_operator_data(right_source, spec=spec, representation=representation, encoder=encoder) for spec in specs}
    runtime_dir = output_dir / "artifacts"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(representation, runtime_dir / "common_comment_representation.joblib")

    selection_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []
    variance_rows: list[dict[str, Any]] = []
    retrieval_rows: list[dict[str, Any]] = []
    surface_components: dict[tuple[str, str], tuple[pd.DataFrame, pd.DataFrame, SurfaceRuntime]] = {}
    primary_inference: dict[str, Any] = {}
    permutation_rows: list[dict[str, Any]] = []
    author_map_selection = pd.DataFrame()

    for view_index, spec in enumerate(specs):
        view = spec.name
        left, right = left_data[view], right_data[view]
        discovery = _concat_data([
            OperatorData(left.frame.loc[_mask(left, ["discovery"])].reset_index(drop=True), left.embeddings[_mask(left, ["discovery"])], {arm: value[_mask(left, ["discovery"])] for arm, value in left.contexts.items()}),
            OperatorData(right.frame.loc[_mask(right, ["discovery"])].reset_index(drop=True), right.embeddings[_mask(right, ["discovery"])], {arm: value[_mask(right, ["discovery"])] for arm, value in right.contexts.items()}),
        ])
        calibration = _concat_data([
            OperatorData(left.frame.loc[_mask(left, ["calibration"])].reset_index(drop=True), left.embeddings[_mask(left, ["calibration"])], {arm: value[_mask(left, ["calibration"])] for arm, value in left.contexts.items()}),
            OperatorData(right.frame.loc[_mask(right, ["calibration"])].reset_index(drop=True), right.embeddings[_mask(right, ["calibration"])], {arm: value[_mask(right, ["calibration"])] for arm, value in right.contexts.items()}),
        ])
        confirmation = _concat_data([
            OperatorData(left.frame.loc[_mask(left, ["confirmation"])].reset_index(drop=True), left.embeddings[_mask(left, ["confirmation"])], {arm: value[_mask(left, ["confirmation"])] for arm, value in left.contexts.items()}),
            OperatorData(right.frame.loc[_mask(right, ["confirmation"])].reset_index(drop=True), right.embeddings[_mask(right, ["confirmation"])], {arm: value[_mask(right, ["confirmation"])] for arm, value in right.contexts.items()}),
        ])
        for arm_index, arm in enumerate(("primary", "format_enriched")):
            selected = _select_surface_alpha(discovery, calibration, arm=arm, grid=[float(value) for value in config["ridge_alpha_grid"]])
            selected["operator"] = view
            selected["arm"] = arm
            selection_rows.extend(selected.to_dict("records"))
            alpha = _best_alpha(selected)
            surface = _fit_surface(discovery, arm=arm, alpha=alpha)
            artifact = runtime_dir / f"context_surface_{view}_{arm}.joblib"
            joblib.dump(surface, artifact)
            pred_discovery = surface.predict(discovery)
            pred_confirmation = surface.predict(confirmation)
            predicted_left = surface.predict(left)
            predicted_right = surface.predict(right)
            context_r2 = global_r2(confirmation.embeddings, pred_confirmation)
            if view == "native" and arm == "primary":
                context_low, context_high = _author_cluster_r2(confirmation, pred_confirmation, seed=int(config["seed"]) + 10, repetitions=int(config["bootstrap_iterations"]))
                _, context_p = _stratified_prediction_permutation(confirmation, pred_confirmation, seed=int(config["seed"]) + 20, repetitions=int(config["permutation_iterations"]))
            else:
                context_low, context_high, context_p = float("nan"), float("nan"), float("nan")
            condition_rows.append({
                "operator": view,
                "arm": arm,
                "ridge_alpha": alpha,
                "n_discovery_units": int(len(discovery.frame)),
                "n_calibration_units": int(len(calibration.frame)),
                "n_confirmation_units": int(len(confirmation.frame)),
                "context_r2": context_r2,
                "context_r2_ci_low": context_low,
                "context_r2_ci_high": context_high,
                "context_permutation_p": context_p,
                "artifact_sha256": _sha256(artifact),
            })
            baseline_y = np.mean(discovery.embeddings, axis=0)
            baseline_k = np.mean(pred_discovery, axis=0)
            baseline_a = np.mean(discovery.embeddings - pred_discovery, axis=0)
            left_components = _component_frame(left, predicted_left, baseline_y=baseline_y, baseline_k=baseline_k, baseline_a=baseline_a)
            right_components = _component_frame(right, predicted_right, baseline_y=baseline_y, baseline_k=baseline_k, baseline_a=baseline_a)
            surface_components[(view, arm)] = (left_components, right_components, surface)
            for split in ("discovery", "calibration", "confirmation"):
                users = _aligned_users(left_components, right_components, split)
                if not users:
                    continue
                covariance = _mean_component_covariance(left_components.loc[left_components["user_id"].isin(users)])
                covariance.update({"operator": view, "arm": arm, "half": "left", "split": split, "n_authors": int(len(users))})
                variance_rows.append(covariance)
                for prefix in ("T", "K", "A"):
                    if split == "confirmation":
                        metric = _component_auc(
                            left_components, right_components, users=users, prefix=prefix,
                            seed=int(config["seed"]) + 1000 * view_index + 100 * arm_index + ord(prefix),
                            bootstrap_iterations=int(config["bootstrap_iterations"]),
                            permutation_iterations=int(config["permutation_iterations"]),
                            draws=int(config["stranger_draws"]),
                        )
                    else:
                        metric = {"auc": float("nan"), "auc_ci_low": float("nan"), "auc_ci_high": float("nan"), "permutation_p": float("nan"), "n_authors": int(len(users))}
                    metric.update({"operator": view, "arm": arm, "component": prefix, "split": split})
                    retrieval_rows.append(metric)
            if view == "native" and arm == "primary":
                discovery_users_components = _aligned_users(left_components, right_components, "discovery")
                calibration_users_components = _aligned_users(left_components, right_components, "calibration")
                confirmation_users_components = _aligned_users(left_components, right_components, "confirmation")
                author_map_selection = _select_author_map_alpha(
                    left_components,
                    right_components,
                    discovery_users=discovery_users_components,
                    calibration_users=calibration_users_components,
                    grid=[float(value) for value in config["author_map_ridge_alpha_grid"]],
                )
                selected_author_map_alpha = float(author_map_selection.sort_values(
                    ["calibration_k_to_t_r2", "author_map_ridge_alpha"], ascending=[False, True]
                ).iloc[0]["author_map_ridge_alpha"])
                map_metric = _author_map_metric(
                    left_components, right_components,
                    train_users=discovery_users_components,
                    confirmation_users=confirmation_users_components,
                    alpha=selected_author_map_alpha,
                    seed=int(config["seed"]) + 31,
                    bootstrap_iterations=int(config["bootstrap_iterations"]),
                    permutation_iterations=int(config["permutation_iterations"]),
                )
                condition_rows[-1]["author_map_ridge_alpha"] = selected_author_map_alpha
                condition_rows[-1].update(map_metric)
                primary_inference.update({
                    "context_r2": context_r2,
                    "context_r2_ci_low": context_low,
                    "context_r2_ci_high": context_high,
                    "context_r2_p": context_p,
                    **map_metric,
                })
                permutation_rows.extend([
                    {"endpoint": "context_r2", "raw_p": context_p},
                    {"endpoint": "k_to_t_r2", "raw_p": map_metric["k_to_t_permutation_p"]},
                ])

    selection = pd.DataFrame(selection_rows)
    condition_metrics = pd.DataFrame(condition_rows)
    variance = pd.DataFrame(variance_rows)
    retrieval = pd.DataFrame(retrieval_rows)
    native_primary_left, native_primary_right, native_primary_surface = surface_components[("native", "primary")]
    confirmation_users = _aligned_users(native_primary_left, native_primary_right, "confirmation")
    total_row = retrieval.loc[(retrieval["operator"].eq("native")) & (retrieval["arm"].eq("primary")) & (retrieval["component"].eq("T")) & (retrieval["split"].eq("confirmation"))].iloc[0]
    primary_inference.update({
        "total_auc": float(total_row["auc"]),
        "total_auc_ci_low": float(total_row["auc_ci_low"]),
        "total_auc_ci_high": float(total_row["auc_ci_high"]),
        "total_auc_p": float(total_row["permutation_p"]),
    })
    permutation_rows.append({"endpoint": "total_auc", "raw_p": float(total_row["permutation_p"])})
    calibration_users = _aligned_users(native_primary_left, native_primary_right, "calibration")
    selection_profile_selection = _select_selection_shrinkage(
        source_context_left,
        source_context_right,
        source_context_discovery,
        calibration_users=calibration_users,
        categories=len(encoder.condition_vocabulary) + 1,
        grid=[float(value) for value in config["selection_shrinkage_grid"]],
    )
    selected_shrinkage = float(selection_profile_selection.sort_values(
        ["calibration_mean_logscore_gain", "selection_shrinkage"], ascending=[False, True]
    ).iloc[0]["selection_shrinkage"])
    selection_metric = _selection_gain(
        source_context_left, source_context_right, source_context_discovery,
        users=confirmation_users,
        categories=len(encoder.condition_vocabulary) + 1,
        shrinkage=selected_shrinkage,
        seed=int(config["seed"]) + 41,
        bootstrap_iterations=int(config["bootstrap_iterations"]),
        permutation_iterations=int(config["permutation_iterations"]),
    )
    primary_inference.update({
        "selection_gain": selection_metric["selection_logscore_gain"],
        "selection_gain_ci_low": selection_metric["selection_logscore_ci_low"],
        "selection_gain_ci_high": selection_metric["selection_logscore_ci_high"],
        "selection_gain_p": selection_metric["selection_permutation_p"],
    })
    permutation_rows.append({"endpoint": "selection_gain", "raw_p": selection_metric["selection_permutation_p"]})

    caliper, caliper_table, calibration_coverage = _select_caliper(left_source, right_source, calibration_users, config)
    matched_rows: list[dict[str, Any]] = []
    matched_null_summary: dict[str, Any] = {
        "matched_null_method": "not_evaluated",
        "matched_null_exchangeable": False,
    }
    matched_caliper_selection = pd.DataFrame()
    matched_strata = pd.DataFrame()
    matching_balance = pd.DataFrame()
    matched_partial_null = pd.DataFrame()
    partial_endpoint_recorded = False
    partial_available = False
    if caliper is None:
        matched_rows.append({"operator": "native", "arm": "primary", "status": "REFUSE_INSUFFICIENT_MATCHED_SUPPORT", "calibration_coverage": calibration_coverage, "confirmation_coverage": float("nan")})
    else:
        pairs = _match_comment_pairs(left_source, right_source, caliper_days=caliper)
        calibration_matched_users, calibration_pair_coverage = _matched_support(pairs, calibration_users, config)
        matched_users, confirmation_coverage = _matched_support(pairs, confirmation_users, config)
        if calibration_pair_coverage < float(config["minimum_matched_coverage"]) or confirmation_coverage < float(config["minimum_matched_coverage"]):
            matched_rows.append({
                "operator": "native", "arm": "primary", "status": "REFUSE_INSUFFICIENT_MATCHED_SUPPORT",
                "caliper_days": caliper, "calibration_coverage": calibration_pair_coverage,
                "confirmation_coverage": confirmation_coverage,
            })
        else:
            train_users = _aligned_users(native_primary_left, native_primary_right, "discovery")
            train_left_meta, _ = _metadata_by_user(
                left_source, source_context_left, native_primary_left, users=train_users
            )
            train_right_meta, _ = _metadata_by_user(
                right_source, source_context_right, native_primary_right, users=train_users
            )
            metadata_scaler = fit_matrix_scaler(0.5 * (train_left_meta + train_right_meta))
            calibration_metadata, calibration_sets, calibration_classes = _matched_strata_inputs(
                left_source, right_source, source_context_left, source_context_right,
                native_primary_left, native_primary_right, pairs,
                users=calibration_matched_users, config=config,
            )
            selected_match, matched_caliper_selection, _ = _select_matching_calipers(
                calibration_metadata, calibration_sets, calibration_classes,
                metadata_scaler=metadata_scaler, population_size=len(calibration_users), config=config,
            )
            if selected_match is None:
                matched_rows.append({
                    "operator": "native", "arm": "primary", "status": "REFUSE_MATCH_BALANCE",
                    "caliper_days": caliper, "calibration_coverage": calibration_pair_coverage,
                    "confirmation_coverage": confirmation_coverage,
                    "reason": "No registered numeric/Jaccard caliper produced at least two disjoint calibration strata with required coverage.",
                })
            else:
                confirmation_metadata, confirmation_sets, confirmation_classes = _matched_strata_inputs(
                    left_source, right_source, source_context_left, source_context_right,
                    native_primary_left, native_primary_right, pairs,
                    users=matched_users, config=config,
                )
                confirmation_strata = _build_matched_strata(
                    confirmation_metadata, confirmation_sets, confirmation_classes,
                    metadata_scaler=metadata_scaler,
                    numeric_caliper=float(selected_match["numeric_caliper"]),
                    minimum_jaccard=float(selected_match["minimum_jaccard"]),
                    min_size=int(config["matched_block_size_min"]),
                    max_size=int(config["matched_block_size_max"]),
                )
                stratum_coverage = confirmation_strata.coverage(len(confirmation_users))
                if stratum_coverage < float(config["minimum_matched_coverage"]) or len(confirmation_strata.groups) < 2:
                    matched_rows.append({
                        "operator": "native", "arm": "primary", "status": "REFUSE_MATCH_BALANCE",
                        "caliper_days": caliper, "calibration_coverage": calibration_pair_coverage,
                        "confirmation_coverage": confirmation_coverage, "stratum_coverage": stratum_coverage,
                        **confirmation_strata.diagnostics(),
                    })
                else:
                    left_mask = _mask(left_data["native"], ["confirmation"])
                    right_mask = _mask(right_data["native"], ["confirmation"])
                    left_native = OperatorData(left_data["native"].frame.loc[left_mask].reset_index(drop=True), left_data["native"].embeddings[left_mask], {arm: values[left_mask] for arm, values in left_data["native"].contexts.items()})
                    right_native = OperatorData(right_data["native"].frame.loc[right_mask].reset_index(drop=True), right_data["native"].embeddings[right_mask], {arm: values[right_mask] for arm, values in right_data["native"].contexts.items()})
                    left_residual = left_native.embeddings - native_primary_surface.predict(left_native)
                    right_residual = right_native.embeddings - native_primary_surface.predict(right_native)
                    left_index = {int(row.source_rows): index for index, row in enumerate(left_native.frame.itertuples(index=False))}
                    right_index = {int(row.source_rows): index for index, row in enumerate(right_native.frame.itertuples(index=False))}
                    matched_left: list[np.ndarray] = []
                    matched_right: list[np.ndarray] = []
                    retained_users: list[str] = []
                    for user in matched_users:
                        user_pairs = pairs.loc[pairs["user_id"].astype(str).eq(user)]
                        left_indices = [left_index.get(int(value)) for value in user_pairs["left_source_row"]]
                        right_indices = [right_index.get(int(value)) for value in user_pairs["right_source_row"]]
                        valid = [(a, b) for a, b in zip(left_indices, right_indices) if a is not None and b is not None]
                        if len(valid) < int(config["minimum_pair_count"]):
                            continue
                        retained_users.append(user)
                        matched_left.append(np.mean(left_residual[[a for a, _ in valid]], axis=0))
                        matched_right.append(np.mean(right_residual[[b for _, b in valid]], axis=0))
                    if retained_users != matched_users:
                        matched_rows.append({
                            "operator": "native", "arm": "primary", "status": "REFUSE_INCOMPLETE_EXACT_CONDITION_SUPPORT",
                            "caliper_days": caliper, "calibration_coverage": calibration_pair_coverage,
                            "confirmation_coverage": confirmation_coverage,
                            "reason": "Source-row provenance did not retain every matched confirmation author.",
                        })
                    else:
                        matched_left_array, matched_right_array = np.vstack(matched_left), np.vstack(matched_right)
                        partial_metric, matched_partial_null, matched_strata, matching_balance = _matched_stratified_metric(
                            matched_left_array, matched_right_array, confirmation_strata,
                            bootstrap_iterations=int(config["bootstrap_iterations"]),
                            permutation_iterations=int(config["permutation_iterations"]),
                            seed=int(config["seed"]) + 54,
                        )
                        partial_available = True
                        matched_null_summary = {
                            **confirmation_strata.diagnostics(),
                            "calibration_pair_coverage": calibration_pair_coverage,
                            "confirmation_pair_coverage": confirmation_coverage,
                            "confirmation_stratum_coverage": stratum_coverage,
                        }
                        matched_rows.append({
                            "operator": "native", "arm": "primary", "status": "MATCHED_PARTIAL_EVALUATED", "caliper_days": caliper,
                            "calibration_coverage": calibration_pair_coverage, "confirmation_coverage": confirmation_coverage,
                            "stratum_coverage": stratum_coverage, **matched_null_summary, **partial_metric,
                        })
                        primary_inference.update({
                            "partial_auc": partial_metric["auc"],
                            "partial_auc_ci_low": partial_metric["auc_ci_low"],
                            "partial_auc_ci_high": partial_metric["auc_ci_high"],
                            "partial_auc_p": partial_metric["permutation_p"],
                            "partial_null_exchangeable": True,
                        })
                        permutation_rows.append({"endpoint": "partial_auc", "raw_p": partial_metric["permutation_p"]})
                        partial_endpoint_recorded = True
    matched = pd.DataFrame(matched_rows)
    caliper_table.to_csv(output_dir / "caliper_support.csv", index=False)
    matched_caliper_selection.to_csv(output_dir / "matched_caliper_selection.csv", index=False)
    matched_strata.to_csv(output_dir / "matched_strata.csv", index=False)
    matching_balance.to_csv(output_dir / "matching_balance.csv", index=False)
    matched_null_artifact = output_dir / "matched_partial_null.parquet"
    if matched_partial_null.empty:
        matched_partial_null = pd.DataFrame({
            "permutation": pd.Series(dtype=int),
            "conditional_rank_auc": pd.Series(dtype=float),
            "observed_conditional_rank_auc": pd.Series(dtype=float),
            "method": pd.Series(dtype=str),
        })
    try:
        matched_partial_null.to_parquet(matched_null_artifact, index=False)
        matched_null_artifact_format = "parquet"
    except (ImportError, ModuleNotFoundError):
        matched_null_artifact = output_dir / "matched_partial_null.csv"
        matched_partial_null.to_csv(matched_null_artifact, index=False)
        matched_null_artifact_format = "csv_fallback_missing_parquet_engine"
    if not partial_endpoint_recorded:
        # This endpoint remains in the registered five-endpoint family even
        # when its support gate refuses evaluation; it cannot reduce the
        # multiplicity burden by disappearing after confirmation is opened.
        permutation_rows.append({"endpoint": "partial_auc", "raw_p": 1.0})
    condition_metrics = pd.concat([condition_metrics, pd.DataFrame([{
        "operator": "native", "arm": "primary", "selection_logscore_gain": selection_metric["selection_logscore_gain"],
        "selection_logscore_ci_low": selection_metric["selection_logscore_ci_low"], "selection_logscore_ci_high": selection_metric["selection_logscore_ci_high"],
        "selection_permutation_p": selection_metric["selection_permutation_p"], "selection_shrinkage": selected_shrinkage,
        "n_confirmation_authors": selection_metric["n_authors"],
    }])], ignore_index=True, sort=False)

    raw_p = {str(row["endpoint"]): float(row["raw_p"]) for row in permutation_rows}
    adjusted = _holm_adjust(raw_p)
    permutation = pd.DataFrame([{"endpoint": key, "raw_p": value, "holm_q": adjusted[key], "family": "primary_native_five_endpoint"} for key, value in raw_p.items()])
    primary_inference.update({
        "total_auc_q": adjusted.get("total_auc", float("nan")),
        "context_r2_q": adjusted.get("context_r2", float("nan")),
        "selection_gain_q": adjusted.get("selection_gain", float("nan")),
        "k_to_t_q": adjusted.get("k_to_t_r2", float("nan")),
        "partial_auc_q": adjusted.get("partial_auc", float("nan")),
    })
    if not partial_available:
        primary_inference.update({
            "partial_auc": float("nan"), "partial_auc_ci_low": float("nan"), "partial_auc_ci_high": float("nan"),
            "partial_auc_p": 1.0, "partial_auc_q": adjusted.get("partial_auc", 1.0), "partial_null_exchangeable": False,
        })
    matched_status = str(matched.iloc[0]["status"]) if not matched.empty else None
    decision, rationale = _decision(
        primary_inference,
        matched_available=partial_available,
        matched_status=matched_status,
        config=config,
    )
    manifest = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input": str(args.input),
        "column_map": column_map,
        "excluded_prior_authors": int(len(excluded)),
        "n_eligible_authors_before_prior_exclusion": int(len(eligible)),
        "n_selected_authors": int(source_panel["user_id"].nunique()),
        "source_comments_per_author": int(config["max_source_comments_per_user"]),
        "split_counts": {key: int(value) for key, value in split_counts.items()},
        "source_overlap_count": 0,
        "context_vocabulary_size": int(len(encoder.condition_vocabulary) + 1),
        "external_labels_read": False,
        "raw_text_persisted": False,
        "author_ids_persisted": False,
        "claim_boundary": "E2 measures observed condition/selection contribution to operator-indexed text geometry; it does not establish personality, causality, or clinical validity.",
        "screen_decision": decision,
        "screen_rationale": rationale,
        "matched_null_artifact": str(matched_null_artifact),
        "matched_null_artifact_format": matched_null_artifact_format,
        **matched_null_summary,
    }
    _write_json(output_dir / "run_manifest.json", manifest)
    _write_json(output_dir / "context_encoder_summary.json", {
        "n_top_subreddits": int(len(encoder.condition_vocabulary)),
        "other_bucket": True,
        "primary_dimension": int(len(encoder.primary_columns)),
        "format_enriched_dimension": int(len(encoder.columns("format_enriched"))),
        "condition_names_persisted": False,
        "fit_population": "discovery_authors_only",
    })
    selection.to_csv(output_dir / "model_selection.csv", index=False)
    author_map_selection.to_csv(output_dir / "author_map_selection.csv", index=False)
    selection_profile_selection.to_csv(output_dir / "selection_profile_selection.csv", index=False)
    condition_metrics.to_csv(output_dir / "condition_model_metrics.csv", index=False)
    pd.DataFrame([selection_metric]).to_csv(output_dir / "selection_metrics.csv", index=False)
    variance.to_csv(output_dir / "variance_accounting.csv", index=False)
    retrieval.to_csv(output_dir / "component_retrieval_metrics.csv", index=False)
    matched.to_csv(output_dir / "matched_partial_metrics.csv", index=False)
    permutation.to_csv(output_dir / "permutation_null.csv", index=False)
    _write_report(
        report_path,
        output_dir=output_dir,
        manifest=manifest,
        selection=selection,
        condition_metrics=condition_metrics,
        variance=variance,
        retrieval=retrieval,
        matched=matched,
        primary=primary_inference,
        decision=decision,
        rationale=rationale,
    )
    print(json.dumps({
        "output_dir": str(output_dir), "report": str(report_path), "decision": decision,
        "n_selected_authors": manifest["n_selected_authors"], "split_counts": manifest["split_counts"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
