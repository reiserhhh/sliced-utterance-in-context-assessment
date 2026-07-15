"""Condition and expression-opportunity controls for SUICA V7.

This module deliberately does *not* call conditions, subreddit selection, or
surface opportunity ``noise``.  It supplies a reproducible way to describe
those observable channels and to ask three separate questions:

1. how much an author-level text feature block is predictable from them;
2. whether same-author feature alignment survives a stranger matched on them;
3. what alignment remains after a declared, training-only partial model.

The third quantity is a sensitivity analysis, not a purified personality
score: condition selection can itself be author-conditioned and meaningful.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable

import numpy as np
import pandas as pd

from .suica import tokenize


@dataclass(frozen=True)
class ConditionOpportunityEncoder:
    """Discovery-fitted vocabulary for observable condition/opportunity data."""

    condition_vocabulary: tuple[str, ...]

    @property
    def opportunity_columns(self) -> list[str]:
        """Return nonsemantic visible-opportunity coordinates."""
        return [
            "opp::log_comment_count",
            "opp::log_total_tokens",
            "opp::mean_tokens",
            "opp::sd_tokens",
            "opp::mean_chars",
            "opp::sd_chars",
            "opp::url_rate",
            "opp::quote_rate",
            "opp::list_rate",
            "opp::code_rate",
            "opp::digit_rate",
            "opp::question_rate",
            "opp::exclamation_rate",
            "opp::punctuation_rate",
            "opp::log_span",
            "opp::log_median_gap",
            "opp::log_max_gap",
        ]

    @property
    def condition_columns(self) -> list[str]:
        """Return condition-choice distribution coordinates."""
        return [
            "condition::log_distinct",
            "condition::entropy",
            "condition::top_share",
            *[f"condition::share_{index:03d}" for index in range(len(self.condition_vocabulary))],
        ]

    def columns(self, group: str) -> list[str]:
        """Return a declared feature group without silently mixing channels."""
        groups = {
            "opportunity_only": self.opportunity_columns,
            "condition_choice_only": self.condition_columns,
            "combined": [*self.opportunity_columns, *self.condition_columns],
        }
        if group not in groups:
            raise ValueError(f"Unknown condition/opportunity group: {group}")
        return groups[group]


@dataclass(frozen=True)
class MatrixScaler:
    """Training-fitted finite-value centering and scaling for matrix controls."""

    center: np.ndarray
    scale: np.ndarray


@dataclass(frozen=True)
class CommentContextEncoder:
    """Discovery-fitted comment-level condition vocabulary and length bins.

    The encoder represents a recorded context, not its causal effect.  It is
    intentionally fit before any author-level geometry is inspected.
    """

    condition_vocabulary: tuple[str, ...]
    length_decile_edges: tuple[float, ...]

    @property
    def primary_columns(self) -> list[str]:
        """Return subreddit/time coordinates for the primary condition surface."""
        return [
            *[f"ctx::condition_{index:03d}" for index in range(len(self.condition_vocabulary))],
            "ctx::condition_other",
            *[f"ctx::quarter_{index}" for index in range(1, 5)],
            "ctx::hour_sin",
            "ctx::hour_cos",
            "ctx::weekday_sin",
            "ctx::weekday_cos",
        ]

    @property
    def surface_columns(self) -> list[str]:
        """Return the ten declared visible length/format sensitivity fields."""
        return [
            "surface::log_tokens",
            "surface::log_chars",
            "surface::url",
            "surface::quote",
            "surface::list",
            "surface::code",
            "surface::digit",
            "surface::question",
            "surface::exclamation",
            "surface::punctuation_rate",
        ]

    def columns(self, arm: str) -> list[str]:
        """Return either the primary or format-enriched condition coordinates."""
        if arm == "primary":
            return self.primary_columns
        if arm == "format_enriched":
            return [*self.primary_columns, *self.surface_columns]
        raise ValueError(f"Unknown comment-context arm: {arm}")


def _safe_log1p(value: float) -> float:
    return float(np.log1p(max(float(value), 0.0)))


def _surface_values(text: str) -> dict[str, float]:
    """Calculate visible, nonsemantic format affordances for one comment."""
    value = str(text)
    stripped = value.strip()
    tokens = tokenize(value)
    punctuation = sum(character in ".,;:!?-()[]{}\"'" for character in value)
    lines = value.splitlines()
    return {
        "tokens": float(len(tokens)),
        "chars": float(len(value)),
        "url": float("http://" in value.lower() or "https://" in value.lower() or "www." in value.lower()),
        "quote": float(any(line.lstrip().startswith(">") for line in lines)),
        "list": float(any(line.lstrip().startswith(("- ", "* ", "+ ")) for line in lines)),
        "code": float("```" in value or any(line.startswith("    ") for line in lines)),
        "digit": float(any(character.isdigit() for character in value)),
        "question": float("?" in value),
        "exclamation": float("!" in value),
        "punctuation": float(punctuation / max(len(stripped), 1)),
    }


def _utc_parts(order: float) -> tuple[int, float, float, float, float]:
    """Return quarter and cyclic UTC coordinates without text-content parsing."""
    try:
        value = datetime.fromtimestamp(float(order), tz=UTC)
    except (OverflowError, OSError, ValueError):
        return 1, 0.0, 1.0, 0.0, 1.0
    hour_angle = 2.0 * np.pi * (value.hour + value.minute / 60.0) / 24.0
    weekday_angle = 2.0 * np.pi * value.weekday() / 7.0
    quarter = (value.month - 1) // 3 + 1
    return quarter, float(np.sin(hour_angle)), float(np.cos(hour_angle)), float(np.sin(weekday_angle)), float(np.cos(weekday_angle))


def fit_comment_context_encoder(
    comments: pd.DataFrame,
    *,
    discovery_user_ids: Iterable[str],
    max_conditions: int,
) -> CommentContextEncoder:
    """Fit top condition labels and length-bin cutpoints on discovery only."""
    discovery_ids = {str(value) for value in discovery_user_ids}
    discovery = comments.loc[comments["user_id"].astype(str).isin(discovery_ids)]
    condition_counts = (
        discovery.loc[discovery["condition"].astype(str).ne("<unknown>"), "condition"]
        .astype(str)
        .value_counts()
    )
    token_counts = np.asarray([len(tokenize(value)) for value in discovery["text"].astype(str)], dtype=float)
    if len(token_counts):
        edges = np.quantile(token_counts, np.linspace(0.1, 0.9, 9))
    else:
        edges = np.zeros(9, dtype=float)
    return CommentContextEncoder(
        condition_vocabulary=tuple(condition_counts.index.astype(str).tolist()[: max(int(max_conditions), 0)]),
        length_decile_edges=tuple(float(value) for value in edges),
    )


def transform_comment_context(
    comments: pd.DataFrame,
    *,
    encoder: CommentContextEncoder,
) -> pd.DataFrame:
    """Encode comment-level primary and enriched context without fitting.

    Returned metadata is intentionally technical: it supports permutation
    strata and selection-profile analysis, but it does not name psychological
    states or infer author traits.
    """
    required = {"user_id", "text", "order", "condition"}
    missing = sorted(required.difference(comments.columns))
    if missing:
        raise ValueError(f"Comment context requires columns: {', '.join(missing)}")
    vocab_index = {value: index for index, value in enumerate(encoder.condition_vocabulary)}
    rows: list[dict[str, float | str | int]] = []
    for row_index, value in comments.reset_index(drop=True).iterrows():
        text = str(value["text"])
        surface = _surface_values(text)
        condition = str(value["condition"])
        quarter, hour_sin, hour_cos, weekday_sin, weekday_cos = _utc_parts(float(value["order"]))
        row: dict[str, float | str | int] = {
            "row_index": int(row_index),
            "user_id": str(value["user_id"]),
            "split": str(value.get("split", "<unknown>")),
            "condition_code": int(vocab_index.get(condition, -1)),
            "condition_label": str(condition) if condition in vocab_index else "<OTHER>",
            "quarter": int(quarter),
            "length_bin": int(np.searchsorted(np.asarray(encoder.length_decile_edges), surface["tokens"], side="right")),
            "token_count": float(surface["tokens"]),
        }
        for index in range(len(encoder.condition_vocabulary)):
            row[f"ctx::condition_{index:03d}"] = float(index == row["condition_code"])
        row["ctx::condition_other"] = float(row["condition_code"] < 0)
        for index in range(1, 5):
            row[f"ctx::quarter_{index}"] = float(quarter == index)
        row.update({
            "ctx::hour_sin": hour_sin,
            "ctx::hour_cos": hour_cos,
            "ctx::weekday_sin": weekday_sin,
            "ctx::weekday_cos": weekday_cos,
            "surface::log_tokens": _safe_log1p(surface["tokens"]),
            "surface::log_chars": _safe_log1p(surface["chars"]),
            "surface::url": surface["url"],
            "surface::quote": surface["quote"],
            "surface::list": surface["list"],
            "surface::code": surface["code"],
            "surface::digit": surface["digit"],
            "surface::question": surface["question"],
            "surface::exclamation": surface["exclamation"],
            "surface::punctuation_rate": surface["punctuation"],
        })
        rows.append(row)
    return pd.DataFrame(rows)


def fit_condition_opportunity_encoder(
    comments: pd.DataFrame,
    *,
    discovery_user_ids: Iterable[str],
    max_conditions: int,
) -> ConditionOpportunityEncoder:
    """Fit condition vocabulary on discovery authors only.

    The vocabulary is intentionally only an encoding device.  The names are
    not stored in public reports by the runner because observed communities are
    provenance, not an interpretation of an author.
    """
    discovery = comments.loc[comments["user_id"].astype(str).isin({str(value) for value in discovery_user_ids})]
    counts = (
        discovery.loc[discovery["condition"].astype(str).ne("<unknown>"), "condition"]
        .astype(str)
        .value_counts()
    )
    vocabulary = tuple(counts.index.astype(str).tolist()[: max(int(max_conditions), 0)])
    return ConditionOpportunityEncoder(condition_vocabulary=vocabulary)


def _gap_features(values: np.ndarray) -> tuple[float, float, float]:
    """Return log span, median positive gap, and max positive gap."""
    numeric = np.asarray(values, dtype=float)
    numeric = numeric[np.isfinite(numeric)]
    if len(numeric) < 2:
        return 0.0, 0.0, 0.0
    numeric = np.sort(numeric)
    gaps = np.diff(numeric)
    gaps = gaps[gaps >= 0.0]
    span = float(numeric[-1] - numeric[0])
    return (
        _safe_log1p(span),
        _safe_log1p(float(np.median(gaps))) if len(gaps) else 0.0,
        _safe_log1p(float(np.max(gaps))) if len(gaps) else 0.0,
    )


def transform_condition_opportunity(
    comments: pd.DataFrame,
    *,
    encoder: ConditionOpportunityEncoder,
    user_ids: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Build per-author observable condition/opportunity profiles.

    All values come from the supplied source panel.  No text representation,
    author ID, personality label, or future split information enters the
    profile.  A zero row is retained for a requested user without sources so
    alignment failures remain explicit rather than silently dropping users.
    """
    required = {"user_id", "text", "order", "condition"}
    missing = sorted(required.difference(comments.columns))
    if missing:
        raise ValueError(f"Condition/opportunity profiles require columns: {', '.join(missing)}")
    requested = None if user_ids is None else [str(value) for value in user_ids]
    groups = {str(user): group for user, group in comments.groupby("user_id", sort=False, observed=True)}
    users = requested if requested is not None else sorted(groups)
    rows: list[dict[str, float | str]] = []
    vocab_index = {value: index for index, value in enumerate(encoder.condition_vocabulary)}
    for user_id in users:
        group = groups.get(str(user_id))
        row: dict[str, float | str] = {"user_id": str(user_id)}
        for column in [*encoder.opportunity_columns, *encoder.condition_columns]:
            row[column] = 0.0
        if group is None or group.empty:
            rows.append(row)
            continue
        surface = [_surface_values(value) for value in group["text"].astype(str)]
        token_values = np.asarray([value["tokens"] for value in surface], dtype=float)
        char_values = np.asarray([value["chars"] for value in surface], dtype=float)
        row.update({
            "opp::log_comment_count": _safe_log1p(len(group)),
            "opp::log_total_tokens": _safe_log1p(float(token_values.sum())),
            "opp::mean_tokens": float(np.mean(token_values)),
            "opp::sd_tokens": float(np.std(token_values, ddof=1)) if len(token_values) > 1 else 0.0,
            "opp::mean_chars": float(np.mean(char_values)),
            "opp::sd_chars": float(np.std(char_values, ddof=1)) if len(char_values) > 1 else 0.0,
            "opp::url_rate": float(np.mean([value["url"] for value in surface])),
            "opp::quote_rate": float(np.mean([value["quote"] for value in surface])),
            "opp::list_rate": float(np.mean([value["list"] for value in surface])),
            "opp::code_rate": float(np.mean([value["code"] for value in surface])),
            "opp::digit_rate": float(np.mean([value["digit"] for value in surface])),
            "opp::question_rate": float(np.mean([value["question"] for value in surface])),
            "opp::exclamation_rate": float(np.mean([value["exclamation"] for value in surface])),
            "opp::punctuation_rate": float(np.mean([value["punctuation"] for value in surface])),
        })
        span, median_gap, max_gap = _gap_features(pd.to_numeric(group["order"], errors="coerce").to_numpy(float))
        row.update({
            "opp::log_span": span,
            "opp::log_median_gap": median_gap,
            "opp::log_max_gap": max_gap,
        })
        conditions = group["condition"].fillna("<unknown>").astype(str)
        shares = conditions.value_counts(normalize=True)
        nonzero = shares.to_numpy(float)
        row["condition::log_distinct"] = _safe_log1p(float(len(shares)))
        row["condition::entropy"] = float(-np.sum(nonzero * np.log(nonzero))) if len(nonzero) else 0.0
        row["condition::top_share"] = float(nonzero.max()) if len(nonzero) else 0.0
        for condition, share in shares.items():
            index = vocab_index.get(str(condition))
            if index is not None:
                row[f"condition::share_{index:03d}"] = float(share)
        rows.append(row)
    return pd.DataFrame(rows).loc[:, ["user_id", *encoder.opportunity_columns, *encoder.condition_columns]]


def fit_matrix_scaler(values: np.ndarray) -> MatrixScaler:
    """Fit finite-value center/scale on a declared training matrix only."""
    matrix = np.asarray(values, dtype=float)
    center = np.nanmean(matrix, axis=0)
    center = np.where(np.isfinite(center), center, 0.0)
    filled = np.where(np.isfinite(matrix), matrix, center[None, :])
    scale = np.nanstd(filled, axis=0, ddof=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-9), scale, 1.0)
    return MatrixScaler(center=center, scale=scale)


def transform_matrix(values: np.ndarray, scaler: MatrixScaler) -> np.ndarray:
    """Apply a training-only scaler and fill nonfinite values deterministically."""
    matrix = np.asarray(values, dtype=float)
    filled = np.where(np.isfinite(matrix), matrix, scaler.center[None, :])
    return (filled - scaler.center[None, :]) / scaler.scale[None, :]


def profile_matrix(
    profiles: pd.DataFrame,
    *,
    user_ids: Iterable[str],
    columns: list[str],
) -> np.ndarray:
    """Return requested authors in a stable order with explicit zero fallback."""
    if "user_id" not in profiles:
        raise ValueError("Profiles require a user_id column.")
    values = profiles.set_index("user_id").reindex([str(value) for value in user_ids])[columns].to_numpy(float)
    return np.where(np.isfinite(values), values, 0.0)


def global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Return global out-of-sample R2 across a matrix of feature targets."""
    truth = np.asarray(target, dtype=float)
    estimate = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((truth - np.mean(truth, axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-14:
        return float("nan")
    return float(1.0 - np.sum((truth - estimate) ** 2) / denominator)


def row_cosines(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return matched-row cosine values, with NaN for zero-norm rows."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    numerator = np.sum(x * y, axis=1)
    denominator = np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1)
    return np.divide(numerator, denominator, out=np.full(len(x), np.nan), where=denominator > 1e-14)


def nearest_condition_strangers(
    left_profiles: np.ndarray,
    right_profiles: np.ndarray,
    *,
    left_user_ids: Iterable[str],
    right_user_ids: Iterable[str],
    scale: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Choose each left author's nearest right-profile stranger.

    Matching is with replacement by design.  It is a contrast control, not a
    one-to-one causal matching estimator.  The returned indices always exclude
    the aligned author identity.
    """
    left = np.asarray(left_profiles, dtype=float)
    right = np.asarray(right_profiles, dtype=float)
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[1]:
        raise ValueError("Condition matching needs two compatible 2D profile matrices.")
    left_ids = [str(value) for value in left_user_ids]
    right_ids = [str(value) for value in right_user_ids]
    if len(left) != len(left_ids) or len(right) != len(right_ids):
        raise ValueError("Profile matrices and user IDs must have equal row counts.")
    if scale is None:
        joint = np.vstack([left, right])
        feature_scale = np.nanstd(joint, axis=0, ddof=1)
    else:
        feature_scale = np.asarray(scale, dtype=float)
        if feature_scale.shape != (left.shape[1],):
            raise ValueError("Matching scale must have one value per profile feature.")
    feature_scale = np.where(np.isfinite(feature_scale) & (feature_scale > 1e-9), feature_scale, 1.0)
    distances = np.sqrt(np.mean(((left[:, None, :] - right[None, :, :]) / feature_scale[None, None, :]) ** 2, axis=2))
    right_index = {user_id: index for index, user_id in enumerate(right_ids)}
    for index, user_id in enumerate(left_ids):
        own = right_index.get(user_id)
        if own is not None:
            distances[index, own] = np.inf
    indices = np.argmin(distances, axis=1)
    return indices.astype(int), distances[np.arange(len(left)), indices]


def bootstrap_mean_difference(
    left: np.ndarray,
    right: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> dict[str, float]:
    """Bootstrap the paired mean difference without normality assumptions."""
    delta = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    delta = delta[np.isfinite(delta)]
    if not len(delta):
        return {"mean_difference": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "n": 0.0}
    rng = np.random.default_rng(seed)
    draws = np.asarray([
        np.mean(rng.choice(delta, size=len(delta), replace=True))
        for _ in range(max(int(repetitions), 1))
    ])
    return {
        "mean_difference": float(np.mean(delta)),
        "ci_low": float(np.quantile(draws, 0.025)),
        "ci_high": float(np.quantile(draws, 0.975)),
        "n": float(len(delta)),
    }
