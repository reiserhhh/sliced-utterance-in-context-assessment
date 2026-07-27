"""Offline geometry-to-behavior bridge utilities for SUICA V8.

The V7 geometry object is an ordered empirical distribution of distances to
anonymous reference landmarks.  Landmark identity is intentionally discarded,
so the profile must be treated as a discrete quantile function rather than as
ordinary landmark coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler


EVENT_CODES = (
    "discourse_stance",
    "affect_expression",
    "self_reference",
    "directive_expression",
    "novelty_expression",
    "interaction_response",
)


def effective_rank(values: np.ndarray) -> float:
    """Return covariance participation ratio for a finite matrix."""
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or len(matrix) < 2 or not np.isfinite(matrix).all():
        raise ValueError("effective_rank requires a finite matrix with >=2 rows")
    eigenvalues = np.linalg.eigvalsh(np.cov(matrix, rowvar=False, ddof=1))
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    denominator = float(np.square(eigenvalues).sum())
    return float(eigenvalues.sum() ** 2 / denominator) if denominator > 0 else 0.0


def _validate_distance_profiles(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] < 3 or not np.isfinite(matrix).all():
        raise ValueError("distance profiles must be a finite two-dimensional matrix")
    if np.any(np.diff(matrix, axis=1) < -1e-10):
        raise ValueError("distance profiles must be sorted within each row")
    return matrix


def _row_shape(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    location = values.mean(axis=1)
    scale = values.std(axis=1, ddof=0)
    safe = np.where(scale > 1e-10, scale, 1.0)
    shape = (values - location[:, None]) / safe[:, None]
    return location, scale, shape


@dataclass
class QuantileGeometryProjector:
    """Discovery-fitted representation of sorted landmark-distance profiles."""

    family: str
    variance_target: float = 0.95
    max_components: int = 8
    pca: PCA | None = None
    scaler: StandardScaler | None = None
    output_names: tuple[str, ...] = ()
    barycenter: np.ndarray | None = None
    stable_components: np.ndarray | None = None
    location_axis: np.ndarray | None = None
    scale_axis: np.ndarray | None = None
    gap_epsilon: float | None = None
    ilr_basis: np.ndarray | None = None

    def _base(self, values: np.ndarray, *, fit: bool) -> np.ndarray:
        matrix = _validate_distance_profiles(values)
        location, scale, shape = _row_shape(matrix)
        if self.family == "raw_quantile":
            base = matrix
            names = [f"Q{index + 1:02d}" for index in range(matrix.shape[1])]
        elif self.family == "location_scale":
            base = np.column_stack([
                location,
                scale,
                matrix[:, -1] - matrix[:, 0],
                np.quantile(matrix, 0.75, axis=1)
                - np.quantile(matrix, 0.25, axis=1),
            ])
            names = ("location", "scale", "range", "iqr")
        elif self.family in {
            "stable_fpca",
            "location_scale_shape",
            "spacing_ilr",
        }:
            if self.barycenter is None:
                raise RuntimeError("geometry projector has not been fitted")
            tangent = matrix - self.barycenter[None, :]
            if self.family == "stable_fpca":
                if self.stable_components is None:
                    raise RuntimeError("stable components are unavailable")
                base = tangent @ self.stable_components.T
                names = [
                    f"RFPC{index + 1:02d}" for index in range(base.shape[1])
                ]
            elif self.family == "location_scale_shape":
                if (
                    self.location_axis is None
                    or self.scale_axis is None
                    or self.pca is None
                ):
                    raise RuntimeError("location-scale-shape basis is unavailable")
                location_score = tangent @ self.location_axis
                scale_score = tangent @ self.scale_axis
                residual = (
                    tangent
                    - location_score[:, None] * self.location_axis[None, :]
                    - scale_score[:, None] * self.scale_axis[None, :]
                )
                shape_scores = self.pca.transform(residual)
                base = np.column_stack([
                    location_score,
                    scale_score,
                    shape_scores,
                ])
                names = [
                    "quantile_location",
                    "quantile_scale",
                    *[
                        f"quantile_shape_{index + 1:02d}"
                        for index in range(shape_scores.shape[1])
                    ],
                ]
            else:
                if self.gap_epsilon is None or self.ilr_basis is None or self.pca is None:
                    raise RuntimeError("spacing ILR basis is unavailable")
                gaps = np.diff(matrix, axis=1)
                composition = gaps + float(self.gap_epsilon)
                composition /= composition.sum(axis=1, keepdims=True)
                clr = np.log(composition) - np.log(composition).mean(
                    axis=1,
                    keepdims=True,
                )
                ilr = clr @ self.ilr_basis.T
                base = self.pca.transform(ilr)
                names = [
                    f"spacing_ilr_{index + 1:02d}"
                    for index in range(base.shape[1])
                ]
        else:
            if self.family == "tangent_fpca":
                source = matrix
                prefix = "T"
            elif self.family == "shape_fpca":
                source = shape
                prefix = "S"
            elif self.family == "gap_fpca":
                gaps = np.diff(matrix, axis=1)
                width = np.maximum(matrix[:, -1] - matrix[:, 0], 1e-10)
                source = gaps / width[:, None]
                prefix = "G"
            elif self.family == "hybrid":
                source = shape
                prefix = "S"
            else:
                raise ValueError(f"unsupported geometry family: {self.family}")
            if fit:
                full = PCA(svd_solver="full").fit(source)
                cumulative = np.cumsum(full.explained_variance_ratio_)
                count = int(np.searchsorted(cumulative, self.variance_target) + 1)
                count = max(1, min(count, self.max_components, source.shape[1]))
                self.pca = PCA(n_components=count, svd_solver="full").fit(source)
            if self.pca is None:
                raise RuntimeError("geometry projector has not been fitted")
            scores = self.pca.transform(source)
            names = [f"{prefix}PC{index + 1:02d}" for index in range(scores.shape[1])]
            if self.family == "hybrid":
                base = np.column_stack([location, scale, scores])
                names = ["location", "scale", *names]
            else:
                base = scores
        if fit:
            self.output_names = tuple(names)
        return np.asarray(base, dtype=float)

    def fit(
        self,
        values: np.ndarray,
        *,
        authors: np.ndarray | None = None,
        sides: np.ndarray | None = None,
    ) -> "QuantileGeometryProjector":
        """Fit all transforms and scaling on discovery rows only."""
        matrix = _validate_distance_profiles(values)
        if self.family in {
            "stable_fpca",
            "location_scale_shape",
            "spacing_ilr",
        }:
            self.barycenter = matrix.mean(axis=0)
        if self.family == "stable_fpca":
            if authors is None or sides is None:
                raise ValueError("stable_fpca requires paired author and side arrays")
            authors = np.asarray(authors, dtype=str)
            sides = np.asarray(sides, dtype=str)
            lookup = {
                (str(author), str(side)): index
                for index, (author, side) in enumerate(
                    zip(authors, sides, strict=True)
                )
            }
            paired = [
                author for author in np.unique(authors)
                if (author, "left") in lookup and (author, "right") in lookup
            ]
            if len(paired) < 3:
                raise ValueError("stable_fpca requires at least three paired authors")
            left = np.vstack([
                matrix[lookup[(author, "left")]] - self.barycenter
                for author in paired
            ])
            right = np.vstack([
                matrix[lookup[(author, "right")]] - self.barycenter
                for author in paired
            ])
            stable_covariance = (
                np.cov((left + right) / 2.0, rowvar=False, ddof=1)
                - np.cov((left - right) / 2.0, rowvar=False, ddof=1)
            )
            stable_covariance = 0.5 * (
                stable_covariance + stable_covariance.T
            )
            eigenvalues, eigenvectors = np.linalg.eigh(stable_covariance)
            order = np.argsort(eigenvalues)[::-1]
            positive = [
                index for index in order if eigenvalues[index] > 1e-10
            ]
            if not positive:
                raise ValueError("stable covariance has no positive component")
            count = min(len(positive), int(self.max_components))
            self.stable_components = eigenvectors[:, positive[:count]].T
        elif self.family == "location_scale_shape":
            width = matrix.shape[1]
            self.location_axis = np.ones(width, dtype=float) / np.sqrt(width)
            candidate = (
                self.barycenter
                - np.dot(self.barycenter, self.location_axis)
                * self.location_axis
            )
            if np.linalg.norm(candidate) <= 1e-10:
                candidate = np.linspace(-1.0, 1.0, width)
                candidate -= (
                    np.dot(candidate, self.location_axis)
                    * self.location_axis
                )
            self.scale_axis = candidate / np.linalg.norm(candidate)
            tangent = matrix - self.barycenter
            residual = (
                tangent
                - (tangent @ self.location_axis)[:, None]
                * self.location_axis[None, :]
                - (tangent @ self.scale_axis)[:, None]
                * self.scale_axis[None, :]
            )
            full = PCA(svd_solver="full").fit(residual)
            cumulative = np.cumsum(full.explained_variance_ratio_)
            count = int(np.searchsorted(cumulative, self.variance_target) + 1)
            count = max(1, min(count, self.max_components, residual.shape[1]))
            self.pca = PCA(n_components=count, svd_solver="full").fit(residual)
        elif self.family == "spacing_ilr":
            gaps = np.diff(matrix, axis=1)
            positive = gaps[gaps > 1e-12]
            median = float(np.median(positive)) if len(positive) else 1e-6
            self.gap_epsilon = max(1e-12, 0.01 * median)
            parts = gaps.shape[1]
            basis = np.zeros((parts - 1, parts), dtype=float)
            for index in range(1, parts):
                basis[index - 1, :index] = 1.0 / np.sqrt(
                    index * (index + 1)
                )
                basis[index - 1, index] = -index / np.sqrt(
                    index * (index + 1)
                )
            self.ilr_basis = basis
            composition = gaps + self.gap_epsilon
            composition /= composition.sum(axis=1, keepdims=True)
            clr = np.log(composition) - np.log(composition).mean(
                axis=1,
                keepdims=True,
            )
            ilr = clr @ basis.T
            full = PCA(svd_solver="full").fit(ilr)
            cumulative = np.cumsum(full.explained_variance_ratio_)
            count = int(np.searchsorted(cumulative, self.variance_target) + 1)
            count = max(1, min(count, self.max_components, ilr.shape[1]))
            self.pca = PCA(n_components=count, svd_solver="full").fit(ilr)
        base = self._base(values, fit=True)
        self.scaler = StandardScaler().fit(base)
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        """Transform profiles without changing the discovery-fitted basis."""
        if self.scaler is None:
            raise RuntimeError("geometry projector has not been fitted")
        return self.scaler.transform(self._base(values, fit=False))

    def fit_transform(
        self,
        values: np.ndarray,
        *,
        authors: np.ndarray | None = None,
        sides: np.ndarray | None = None,
    ) -> np.ndarray:
        """Fit on and transform discovery profiles."""
        return self.fit(values, authors=authors, sides=sides).transform(values)


@dataclass(frozen=True)
class OpportunityBaseline:
    """Empirical-Bayes event expectation conditional on observed context."""

    global_probability: dict[str, float]
    condition_probability: dict[str, dict[str, float]]
    shrinkage: float

    def probability(self, condition: str, event_code: str) -> float:
        return float(
            self.condition_probability.get(str(condition), {}).get(
                str(event_code),
                self.global_probability[str(event_code)],
            )
        )


def fit_opportunity_baseline(
    segments: pd.DataFrame,
    *,
    shrinkage: float = 10.0,
) -> OpportunityBaseline:
    """Fit context-conditioned event expectations on discovery segments."""
    if shrinkage <= 0:
        raise ValueError("shrinkage must be positive")
    required = {"condition", *EVENT_CODES}
    if not required.issubset(segments):
        raise ValueError("segment table is missing opportunity columns")
    global_probability = {
        code: float(segments[code].mean()) for code in EVENT_CODES
    }
    condition_probability: dict[str, dict[str, float]] = {}
    for condition, group in segments.groupby("condition", observed=True):
        count = float(len(group))
        condition_probability[str(condition)] = {
            code: float(
                (group[code].sum() + shrinkage * global_probability[code])
                / (count + shrinkage)
            )
            for code in EVENT_CODES
        }
    return OpportunityBaseline(
        global_probability=global_probability,
        condition_probability=condition_probability,
        shrinkage=float(shrinkage),
    )


def segment_event_frame(
    profiles: Iterable[dict[str, Any]],
    events_by_profile: dict[str, list[dict[str, Any]]],
    *,
    condition_by_segment: dict[str, str],
) -> pd.DataFrame:
    """Compile source-bound event observations into one row per segment."""
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        by_segment: dict[str, set[str]] = {}
        for event in events_by_profile.get(profile_id, []):
            by_segment.setdefault(str(event["segment_id"]), set()).add(
                str(event["event_code"])
            )
        for order, segment in enumerate(profile["segments"]):
            segment_id = str(segment["segment_id"])
            present = by_segment.get(segment_id, set())
            text = " ".join(
                str(span.get("text", "")) for span in segment.get("spans", [])
            )
            row: dict[str, Any] = {
                "profile_id": profile_id,
                "author_id": str(profile["author_id"]),
                "side": str(profile["side"]),
                "cohort_split": str(profile["cohort_split"]),
                "segment_id": segment_id,
                "segment_order": int(order),
                "condition": str(condition_by_segment.get(segment_id, "<unknown>")),
                "token_count": int(len(text.split())),
            }
            row.update({code: int(code in present) for code in EVENT_CODES})
            rows.append(row)
    return pd.DataFrame(rows)


def segment_event_repetition_frame(
    profiles: Iterable[dict[str, Any]],
    observer_runs: list[dict[str, Any]],
    *,
    condition_by_segment: dict[str, str],
) -> pd.DataFrame:
    """Compile all observer repetitions without collapsing observer variance."""
    rows: list[dict[str, Any]] = []
    for repetition, run in enumerate(observer_runs):
        events_by_profile = run["observer"]
        frame = segment_event_frame(
            profiles,
            events_by_profile,
            condition_by_segment=condition_by_segment,
        )
        frame.insert(
            frame.columns.get_loc("segment_order"),
            "observer_repetition",
            int(repetition),
        )
        rows.extend(frame.to_dict(orient="records"))
    return pd.DataFrame(rows)


def profile_behavior_features(
    segments: pd.DataFrame,
    *,
    opportunity: OpportunityBaseline,
) -> pd.DataFrame:
    """Aggregate event rates, opportunity residuals, pairs, and transitions."""
    rows: list[dict[str, Any]] = []
    pair_codes = list(combinations(EVENT_CODES, 2))
    for profile_id, group in segments.groupby("profile_id", observed=True, sort=False):
        group = group.sort_values("segment_order", kind="stable")
        matrix = group[list(EVENT_CODES)].to_numpy(float)
        row: dict[str, Any] = {
            "profile_id": str(profile_id),
            "author_id": str(group["author_id"].iloc[0]),
            "side": str(group["side"].iloc[0]),
            "cohort_split": str(group["cohort_split"].iloc[0]),
        }
        for index, code in enumerate(EVENT_CODES):
            expected = np.asarray([
                opportunity.probability(condition, code)
                for condition in group["condition"].astype(str)
            ])
            row[f"single::{code}"] = float(matrix[:, index].mean())
            row[f"residual::{code}"] = float(
                (matrix[:, index] - expected).mean()
            )
        for left, right in pair_codes:
            left_index = EVENT_CODES.index(left)
            right_index = EVENT_CODES.index(right)
            row[f"pair::{left}+{right}"] = float(
                (matrix[:, left_index] * matrix[:, right_index]).mean()
            )
        if len(matrix) >= 2:
            for left in EVENT_CODES:
                for right in EVENT_CODES:
                    left_index = EVENT_CODES.index(left)
                    right_index = EVENT_CODES.index(right)
                    row[f"transition::{left}->{right}"] = float(
                        (
                            matrix[:-1, left_index]
                            * matrix[1:, right_index]
                        ).mean()
                    )
            jaccard_changes = []
            for first, second in zip(matrix[:-1], matrix[1:], strict=True):
                union = np.maximum(first, second).sum()
                intersection = np.minimum(first, second).sum()
                jaccard_changes.append(
                    1.0 - intersection / union if union else 0.0
                )
            row["summary::switch_rate"] = float(np.mean(jaccard_changes))
        else:
            for left in EVENT_CODES:
                for right in EVENT_CODES:
                    row[f"transition::{left}->{right}"] = 0.0
            row["summary::switch_rate"] = 0.0
        counts = matrix.sum(axis=0)
        total = float(counts.sum())
        probabilities = counts[counts > 0] / total if total > 0 else np.array([])
        entropy = (
            -float(np.sum(probabilities * np.log(probabilities))) / np.log(len(EVENT_CODES))
            if len(probabilities) else 0.0
        )
        row["summary::event_density"] = float(matrix.mean())
        row["summary::active_segment_rate"] = float((matrix.sum(axis=1) > 0).mean())
        row["summary::code_diversity"] = float((counts > 0).mean())
        row["summary::code_entropy"] = entropy
        rows.append(row)
    return pd.DataFrame(rows)


def profile_repeated_behavior_features(
    segments: pd.DataFrame,
    *,
    opportunity: OpportunityBaseline,
) -> pd.DataFrame:
    """Build rate, pair, and exact order-null features from repeated coding."""
    required = {
        "profile_id",
        "observer_repetition",
        "segment_order",
        *EVENT_CODES,
    }
    if not required.issubset(segments):
        raise ValueError("repeated segment table is incomplete")
    rows: list[dict[str, Any]] = []
    orders = list(permutations(range(3)))
    for profile_id, group in segments.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        group = group.sort_values(
            ["observer_repetition", "segment_order"],
            kind="stable",
        )
        matrix = group[list(EVENT_CODES)].to_numpy(float)
        row: dict[str, Any] = {
            "profile_id": str(profile_id),
            "author_id": str(group["author_id"].iloc[0]),
            "side": str(group["side"].iloc[0]),
            "cohort_split": str(group["cohort_split"].iloc[0]),
        }
        exposure = float(len(matrix))
        for index, code in enumerate(EVENT_CODES):
            probability = (matrix[:, index].sum() + 0.5) / (exposure + 1.0)
            row[f"rate::{code}"] = float(
                np.log(probability / (1.0 - probability))
            )
            expected = np.asarray([
                opportunity.probability(condition, code)
                for condition in group["condition"].astype(str)
            ])
            row[f"opportunity::{code}"] = float(
                (matrix[:, index] - expected).mean()
            )
        for left, right in combinations(EVENT_CODES, 2):
            first = matrix[:, EVENT_CODES.index(left)].astype(bool)
            second = matrix[:, EVENT_CODES.index(right)].astype(bool)
            n11 = int(np.sum(first & second))
            n10 = int(np.sum(first & ~second))
            n01 = int(np.sum(~first & second))
            n00 = int(np.sum(~first & ~second))
            row[f"pair_log_or::{left}+{right}"] = float(np.log(
                ((n11 + 0.5) * (n00 + 0.5))
                / ((n10 + 0.5) * (n01 + 0.5))
            ))
        transition_observed = np.zeros((len(EVENT_CODES), len(EVENT_CODES)))
        transition_expected = np.zeros_like(transition_observed)
        transition_variance = np.zeros_like(transition_observed)
        for _, repetition in group.groupby(
            "observer_repetition",
            observed=True,
        ):
            repetition = repetition.sort_values("segment_order", kind="stable")
            values = repetition[list(EVENT_CODES)].to_numpy(float)
            if len(values) != 3:
                continue
            observed = (
                values[:-1, :, None] * values[1:, None, :]
            ).sum(axis=0)
            null = np.stack([
                (
                    values[list(order)][:-1, :, None]
                    * values[list(order)][1:, None, :]
                ).sum(axis=0)
                for order in orders
            ])
            transition_observed += observed
            transition_expected += null.mean(axis=0)
            transition_variance += null.var(axis=0, ddof=0)
        transition_z = np.divide(
            transition_observed - transition_expected,
            np.sqrt(transition_variance + 1e-6),
        )
        for left_index, left in enumerate(EVENT_CODES):
            for right_index, right in enumerate(EVENT_CODES):
                row[f"order_null::{left}->{right}"] = float(
                    transition_z[left_index, right_index]
                )
        counts = matrix.sum(axis=0)
        total = float(counts.sum())
        probabilities = counts[counts > 0] / total if total > 0 else np.array([])
        row["summary::event_density"] = float(matrix.mean())
        row["summary::code_diversity"] = float((counts > 0).mean())
        row["summary::code_entropy"] = (
            -float(np.sum(probabilities * np.log(probabilities)))
            / np.log(len(EVENT_CODES))
            if len(probabilities) else 0.0
        )
        rows.append(row)
    return pd.DataFrame(rows)


def select_behavior_columns(
    frame: pd.DataFrame,
    *,
    feature_set: str,
    discovery_mask: np.ndarray,
    minimum_nonzero_profiles: int = 8,
    maximum_nonzero_fraction: float = 0.95,
) -> list[str]:
    """Freeze non-degenerate behavior features using discovery rows only."""
    if feature_set == "single":
        prefixes = ("single::",)
    elif feature_set == "opportunity":
        prefixes = ("single::", "residual::", "summary::")
    elif feature_set == "patterns":
        prefixes = ("single::", "residual::", "pair::", "summary::")
    elif feature_set == "full":
        prefixes = ("single::", "residual::", "pair::", "transition::", "summary::")
    elif feature_set == "rates":
        prefixes = ("rate::",)
    elif feature_set == "rates_pairs":
        prefixes = ("rate::", "opportunity::", "pair_log_or::", "summary::")
    elif feature_set == "rates_transitions":
        prefixes = ("rate::", "opportunity::", "order_null::", "summary::")
    elif feature_set == "joint_repeated":
        prefixes = (
            "rate::",
            "opportunity::",
            "pair_log_or::",
            "order_null::",
            "summary::",
        )
    else:
        raise ValueError(f"unsupported behavior feature set: {feature_set}")
    candidates = [
        column for column in frame.columns if column.startswith(prefixes)
    ]
    discovery = frame.loc[np.asarray(discovery_mask, dtype=bool), candidates]
    selected = []
    for column in candidates:
        values = discovery[column].to_numpy(float)
        if not np.isfinite(values).all() or float(np.std(values)) <= 1e-10:
            continue
        if column.startswith(("pair::", "transition::", "single::")):
            active = int(np.count_nonzero(np.abs(values) > 1e-12))
            if active < int(minimum_nonzero_profiles):
                continue
            if active / len(values) > float(maximum_nonzero_fraction):
                continue
        selected.append(column)
    return selected


def _cosine_rows(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    numerator = np.sum(first * second, axis=1)
    denominator = np.linalg.norm(first, axis=1) * np.linalg.norm(second, axis=1)
    return np.divide(
        numerator,
        denominator,
        out=np.zeros(len(first), dtype=float),
        where=denominator > 1e-12,
    )


def cross_modal_author_auc(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str = "euclidean",
) -> float:
    """Rank opposite-half same-author behavior above opposite-half strangers."""
    predicted = np.asarray(predicted, dtype=float)
    observed = np.asarray(observed, dtype=float)
    authors = np.asarray(authors, dtype=str)
    sides = np.asarray(sides, dtype=str)
    labels: list[int] = []
    scores: list[float] = []
    for index in range(len(predicted)):
        targets = np.flatnonzero(sides != sides[index])
        for target in targets:
            labels.append(int(authors[target] == authors[index]))
            if metric == "euclidean":
                scores.append(float(
                    -np.linalg.norm(predicted[index] - observed[target])
                ))
            elif metric == "cosine":
                scores.append(float(_cosine_rows(
                    predicted[index:index + 1],
                    observed[target:target + 1],
                )[0]))
            else:
                raise ValueError(f"unsupported cross-modal metric: {metric}")
    if not labels or len(set(labels)) < 2:
        return float("nan")
    return float(roc_auc_score(labels, scores))


def select_ridge_alpha(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    alphas: Iterable[float],
    folds: int = 5,
) -> tuple[float, dict[float, float]]:
    """Select ridge strength by grouped discovery-only cross-modal AUC."""
    authors = np.asarray(authors, dtype=str)
    unique = np.unique(authors)
    splitter = GroupKFold(n_splits=min(int(folds), len(unique)))
    scores: dict[float, list[float]] = {float(alpha): [] for alpha in alphas}
    for train, valid in splitter.split(geometry, groups=authors):
        y_scaler = StandardScaler().fit(behavior[train])
        train_y = y_scaler.transform(behavior[train])
        valid_y = y_scaler.transform(behavior[valid])
        for alpha in scores:
            model = Ridge(alpha=alpha).fit(geometry[train], train_y)
            value = cross_modal_author_auc(
                model.predict(geometry[valid]),
                valid_y,
                authors[valid],
                np.asarray(sides)[valid],
            )
            if np.isfinite(value):
                scores[alpha].append(value)
    means = {
        alpha: float(np.mean(values)) if values else float("-inf")
        for alpha, values in scores.items()
    }
    best = max(sorted(means), key=lambda alpha: (means[alpha], -alpha))
    return float(best), means


@dataclass
class RidgeBehaviorBridge:
    """Discovery-fitted multivariate geometry-to-behavior map."""

    alpha: float
    behavior_scaler: StandardScaler | None = None
    model: Ridge | None = None

    def fit(self, geometry: np.ndarray, behavior: np.ndarray) -> "RidgeBehaviorBridge":
        self.behavior_scaler = StandardScaler().fit(behavior)
        target = self.behavior_scaler.transform(behavior)
        self.model = Ridge(alpha=float(self.alpha)).fit(geometry, target)
        return self

    def predict(self, geometry: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("bridge has not been fitted")
        return np.asarray(self.model.predict(geometry), dtype=float)

    def observed_z(self, behavior: np.ndarray) -> np.ndarray:
        if self.behavior_scaler is None:
            raise RuntimeError("bridge has not been fitted")
        return self.behavior_scaler.transform(behavior)


def opposite_half_targets(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Align every prediction to the same author's opposite source half."""
    lookup = {
        (str(author), str(side)): index
        for index, (author, side) in enumerate(zip(authors, sides, strict=True))
    }
    output_prediction = []
    output_observed = []
    for index, (author, side) in enumerate(zip(authors, sides, strict=True)):
        other = "right" if str(side) == "left" else "left"
        target = lookup.get((str(author), other))
        if target is None:
            continue
        output_prediction.append(predicted[index])
        output_observed.append(observed[target])
    return np.asarray(output_prediction), np.asarray(output_observed)


def cross_modal_feature_metrics(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
) -> dict[str, float]:
    """Summarize opposite-half prediction without psychological labels."""
    first, second = opposite_half_targets(predicted, observed, authors, sides)
    if not len(first):
        return {
            "element_spearman": float("nan"),
            "row_spearman_mean": float("nan"),
            "cosine_mean": float("nan"),
        }
    element = float(spearmanr(first.ravel(), second.ravel()).statistic)
    row_values = []
    for left, right in zip(first, second, strict=True):
        value = float(spearmanr(left, right).statistic)
        if np.isfinite(value):
            row_values.append(value)
    return {
        "element_spearman": element,
        "row_spearman_mean": float(np.mean(row_values)) if row_values else float("nan"),
        "cosine_mean": float(_cosine_rows(first, second).mean()),
    }


def distance_alignment(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
) -> dict[str, float]:
    """Compare author-mean geometry and behavior distance orderings."""
    frame = pd.DataFrame({"author_id": np.asarray(authors, dtype=str)})
    unique = frame["author_id"].drop_duplicates().tolist()
    geometry_mean = np.vstack([
        geometry[frame["author_id"].eq(author).to_numpy()].mean(axis=0)
        for author in unique
    ])
    behavior_mean = np.vstack([
        behavior[frame["author_id"].eq(author).to_numpy()].mean(axis=0)
        for author in unique
    ])
    if len(unique) < 3:
        return {"distance_spearman": float("nan"), "authors": len(unique)}
    geometry_distance = pdist(geometry_mean, metric="euclidean")
    behavior_distance = pdist(behavior_mean, metric="euclidean")
    return {
        "distance_spearman": float(
            spearmanr(geometry_distance, behavior_distance).statistic
        ),
        "authors": int(len(unique)),
        "geometry_distance_mean": float(geometry_distance.mean()),
        "behavior_distance_mean": float(behavior_distance.mean()),
    }


def supported_profile_rate(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    prediction_threshold: float = 0.25,
    evidence_threshold: float = 0.50,
    top_k: int = 3,
) -> float:
    """Rate profiles with at least one directionally supported top prediction."""
    first, second = opposite_half_targets(predicted, observed, authors, sides)
    supported = []
    for prediction, evidence in zip(first, second, strict=True):
        indices = np.argsort(np.abs(prediction), kind="stable")[-int(top_k):]
        match = np.any(
            (np.abs(prediction[indices]) >= float(prediction_threshold))
            & (np.abs(evidence[indices]) >= float(evidence_threshold))
            & (np.sign(prediction[indices]) == np.sign(evidence[indices]))
        )
        supported.append(bool(match))
    return float(np.mean(supported)) if supported else 0.0


def pairwise_distance_matrix(values: np.ndarray) -> np.ndarray:
    """Return a square Euclidean distance matrix for diagnostics."""
    return squareform(pdist(np.asarray(values, dtype=float), metric="euclidean"))


def _normalized_graph_laplacian(affinity: np.ndarray) -> np.ndarray:
    matrix = np.asarray(affinity, dtype=float)
    degree = matrix.sum(axis=1)
    inverse = np.divide(
        1.0,
        np.sqrt(degree),
        out=np.zeros_like(degree),
        where=degree > 1e-12,
    )
    return np.eye(len(matrix)) - (
        inverse[:, None] * matrix * inverse[None, :]
    )


def _eigenvalue_groups(
    eigenvalues: np.ndarray,
    *,
    tolerance: float = 1e-7,
) -> list[np.ndarray]:
    groups: list[list[int]] = []
    for index, value in enumerate(np.asarray(eigenvalues, dtype=float)):
        if not groups:
            groups.append([index])
            continue
        previous = float(eigenvalues[groups[-1][-1]])
        scale = max(1.0, abs(previous), abs(float(value)))
        if abs(float(value) - previous) <= tolerance * scale:
            groups[-1].append(index)
        else:
            groups.append([index])
    return [np.asarray(group, dtype=int) for group in groups]


def landmark_spectral_signatures(
    query_points: np.ndarray,
    landmarks: np.ndarray,
    *,
    mode: str = "combined",
    scale_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0),
    heat_times: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0, 4.0),
) -> tuple[np.ndarray, list[str]]:
    """Create permutation- and isometry-invariant query/landmark signatures.

    A query-to-landmark distance vector is treated as a signal on the frozen
    landmark graph. Spectral energy is summed within degenerate eigenspaces,
    so arbitrary eigenvector signs, bases, and landmark permutations do not
    change the result.
    """
    queries = np.asarray(query_points, dtype=float)
    reference = np.asarray(landmarks, dtype=float)
    if (
        queries.ndim != 2
        or reference.ndim != 2
        or queries.shape[1] != reference.shape[1]
        or len(reference) < 3
        or not np.isfinite(queries).all()
        or not np.isfinite(reference).all()
    ):
        raise ValueError("queries and landmarks must be compatible finite matrices")
    if mode not in {"energy", "scattering", "combined"}:
        raise ValueError(f"unsupported spectral signature mode: {mode}")
    landmark_distance = squareform(pdist(reference, metric="euclidean"))
    positive = landmark_distance[landmark_distance > 1e-12]
    base_scale = float(np.median(positive))
    if not np.isfinite(base_scale) or base_scale <= 0:
        raise ValueError("landmark configuration has no positive distance scale")
    query_distance = cdist(queries, reference, metric="euclidean")
    output: list[list[float]] = [[] for _ in range(len(queries))]
    names: list[str] = []
    for scale_multiplier in scale_multipliers:
        sigma = float(scale_multiplier) * base_scale
        landmark_affinity = np.exp(
            -(landmark_distance**2) / (2.0 * sigma**2)
        )
        np.fill_diagonal(landmark_affinity, 0.0)
        laplacian = _normalized_graph_laplacian(landmark_affinity)
        eigenvalues, eigenvectors = np.linalg.eigh(
            0.5 * (laplacian + laplacian.T)
        )
        groups = _eigenvalue_groups(eigenvalues)
        scale_label = f"s{scale_multiplier:g}"
        if mode in {"energy", "combined"}:
            names.extend([
                f"{scale_label}::spectral_energy_group_{index + 1:02d}"
                for index in range(len(groups))
            ])
            names.extend([
                f"{scale_label}::signal_l1",
                f"{scale_label}::signal_l2",
                f"{scale_label}::query_degree",
            ])
        if mode in {"scattering", "combined"}:
            for heat_time in heat_times:
                names.extend([
                    f"{scale_label}::heat_{heat_time:g}::std",
                    f"{scale_label}::heat_{heat_time:g}::energy",
                    f"{scale_label}::heat_{heat_time:g}::variation",
                    f"{scale_label}::heat_{heat_time:g}::trace_shift",
                ])
        for query_index, distances in enumerate(query_distance):
            signal = np.exp(-(distances**2) / (2.0 * sigma**2))
            centered = signal - signal.mean()
            coefficients = eigenvectors.T @ centered
            row: list[float] = []
            if mode in {"energy", "combined"}:
                row.extend([
                    float(np.square(coefficients[group]).sum())
                    for group in groups
                ])
                row.extend([
                    float(np.abs(centered).sum()),
                    float(np.linalg.norm(centered)),
                    float(signal.sum()),
                ])
            if mode in {"scattering", "combined"}:
                augmented_distance = np.zeros(
                    (len(reference) + 1, len(reference) + 1),
                    dtype=float,
                )
                augmented_distance[:-1, :-1] = landmark_distance
                augmented_distance[-1, :-1] = distances
                augmented_distance[:-1, -1] = distances
                augmented_affinity = np.exp(
                    -(augmented_distance**2) / (2.0 * sigma**2)
                )
                np.fill_diagonal(augmented_affinity, 0.0)
                augmented_eigenvalues = np.linalg.eigvalsh(
                    _normalized_graph_laplacian(augmented_affinity)
                )
                for heat_time in heat_times:
                    attenuation = np.exp(-float(heat_time) * eigenvalues)
                    diffused = eigenvectors @ (attenuation * coefficients)
                    row.extend([
                        float(np.std(diffused)),
                        float(np.dot(diffused, diffused)),
                        float(diffused @ laplacian @ diffused),
                        float(
                            np.exp(
                                -float(heat_time) * augmented_eigenvalues
                            ).sum()
                            - np.exp(
                                -float(heat_time) * eigenvalues
                            ).sum()
                        ),
                    ])
            output[query_index].extend(row)
    return np.asarray(output, dtype=float), names


def canonical_orbit_distance_signatures(
    query_points: np.ndarray,
    landmarks: np.ndarray,
    *,
    relative_tolerance: float = 1e-8,
) -> tuple[np.ndarray, list[str], dict[str, Any]]:
    """Canonicalize anonymous landmarks by their internal distance fingerprints.

    A generic landmark graph has structurally unique nodes. Equal distance
    fingerprints do not prove automorphism equivalence, so this implementation
    refuses collisions instead of applying an unjustified within-group sort.
    The unique-fingerprint result is invariant to landmark input order and
    common Euclidean isometries without globally discarding topology.
    """
    queries = np.asarray(query_points, dtype=float)
    reference = np.asarray(landmarks, dtype=float)
    if (
        queries.ndim != 2
        or reference.ndim != 2
        or queries.shape[1] != reference.shape[1]
        or len(reference) < 3
        or relative_tolerance <= 0
        or not np.isfinite(queries).all()
        or not np.isfinite(reference).all()
    ):
        raise ValueError("canonical orbit signatures require compatible matrices")
    distance = squareform(pdist(reference, metric="euclidean"))
    positive = distance[distance > 1e-12]
    scale = float(np.median(positive))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("landmark configuration has no positive distance scale")
    fingerprints = np.sort(distance / scale, axis=1)
    quantized = np.rint(fingerprints / float(relative_tolerance)).astype(np.int64)
    order = sorted(
        range(len(reference)),
        key=lambda index: tuple(quantized[index].tolist()),
    )
    groups: list[list[int]] = []
    for index in order:
        if (
            not groups
            or not np.array_equal(quantized[index], quantized[groups[-1][0]])
        ):
            groups.append([index])
        else:
            groups[-1].append(index)
    collisions = [group for group in groups if len(group) > 1]
    if collisions:
        raise ValueError(
            "CANONICAL_ORBIT_REFUSE_FINGERPRINT_COLLISION: exact weighted "
            "graph automorphism quotient is required"
        )
    query_distance = cdist(queries, reference, metric="euclidean")
    rows = []
    names = []
    for group_index, group in enumerate(groups):
        names.extend([
            f"orbit_{group_index + 1:02d}::rank_{rank + 1:02d}"
            for rank in range(len(group))
        ])
    for distances in query_distance:
        row = []
        for group in groups:
            row.append(float(distances[group[0]]))
        rows.append(row)
    diagnostics = {
        "landmarks": int(len(reference)),
        "canonical_orbits": int(len(groups)),
        "orbit_sizes": [int(len(group)) for group in groups],
        "largest_orbit": int(max(map(len, groups))),
        "all_landmarks_structurally_unique": bool(
            all(len(group) == 1 for group in groups)
        ),
        "relative_tolerance": float(relative_tolerance),
        "minimum_fingerprint_l2": float(
            np.min(pdist(np.sort(distance, axis=1), metric="euclidean"))
        ),
        "conservative_per_distance_stability_radius": float(
            np.min(pdist(np.sort(distance, axis=1), metric="euclidean"))
            / (2.0 * np.sqrt(max(1, len(reference) - 1)))
        ),
        "unique_fingerprints_by_decimal": {
            str(decimals): int(
                len({
                    tuple(row)
                    for row in np.round(
                        np.sort(distance, axis=1),
                        decimals=decimals,
                    )
                })
            )
            for decimals in (3, 6, 9, 12)
        },
    }
    return np.asarray(rows, dtype=float), names, diagnostics


@dataclass
class SpectralGeometryProjector:
    """Discovery-fitted compression of invariant landmark-graph signatures."""

    landmarks: np.ndarray
    mode: str = "combined"
    variance_target: float = 0.95
    max_components: int = 16
    signature_scaler: StandardScaler | None = None
    pca: PCA | None = None
    score_scaler: StandardScaler | None = None
    signature_names: tuple[str, ...] = ()
    output_names: tuple[str, ...] = ()

    def fit(self, query_points: np.ndarray) -> "SpectralGeometryProjector":
        signatures, names = landmark_spectral_signatures(
            query_points,
            self.landmarks,
            mode=self.mode,
        )
        self.signature_names = tuple(names)
        self.signature_scaler = StandardScaler().fit(signatures)
        standardized = self.signature_scaler.transform(signatures)
        full = PCA(svd_solver="full").fit(standardized)
        cumulative = np.cumsum(full.explained_variance_ratio_)
        count = int(np.searchsorted(cumulative, self.variance_target) + 1)
        count = max(
            1,
            min(count, self.max_components, standardized.shape[1], len(standardized)),
        )
        self.pca = PCA(n_components=count, svd_solver="full").fit(standardized)
        scores = self.pca.transform(standardized)
        self.score_scaler = StandardScaler().fit(scores)
        self.output_names = tuple(
            f"{self.mode}_graph_pc_{index + 1:02d}" for index in range(count)
        )
        return self

    def transform(self, query_points: np.ndarray) -> np.ndarray:
        if (
            self.signature_scaler is None
            or self.pca is None
            or self.score_scaler is None
        ):
            raise RuntimeError("spectral geometry projector has not been fitted")
        signatures, names = landmark_spectral_signatures(
            query_points,
            self.landmarks,
            mode=self.mode,
        )
        if tuple(names) != self.signature_names:
            raise RuntimeError("spectral signature schema changed after fit")
        standardized = self.signature_scaler.transform(signatures)
        return self.score_scaler.transform(self.pca.transform(standardized))
