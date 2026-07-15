"""Time-separated, label-free geometry controls for SUICA V7.

This module keeps two distinct objects separate:

* **selection/context** (for example subreddit choice) is part of the observed
  text process and is reported, not automatically removed; and
* **structural opportunity** (amount of text, formatting, quotation/code/list
  affordances) can make a language feature observable more or less often.

Opportunity adjustment is therefore a declared sensitivity analysis.  It is
not a personality ``denoiser`` and cannot establish a causal author core.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

from .suica import sentence_split, tokenize


_URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", flags=re.MULTILINE)
_QUOTE_RE = re.compile(r"^\s*>", flags=re.MULTILINE)


@dataclass(frozen=True)
class TemporalTextRuntime:
    """A train-fitted lexical representation for time-separated panels."""

    name: str
    vectorizer: TfidfVectorizer
    reducer: TruncatedSVD


@dataclass(frozen=True)
class FeatureScaler:
    """Column standardizer fitted only on declared training authors."""

    mean: np.ndarray
    scale: np.ndarray

    def transform(self, values: np.ndarray) -> np.ndarray:
        """Apply training-only centering and scaling."""
        return (np.asarray(values, dtype=float) - self.mean) / self.scale


@dataclass(frozen=True)
class OpportunityResidualizer:
    """Training-fitted sensitivity model from structural opportunity to features."""

    opportunity_scaler: FeatureScaler
    model: Ridge

    def residualize(self, features: np.ndarray, opportunity: np.ndarray) -> np.ndarray:
        """Return feature residuals without refitting on calibration/test authors."""
        predicted = self.model.predict(self.opportunity_scaler.transform(opportunity))
        return np.asarray(features, dtype=float) - np.asarray(predicted, dtype=float)


def _evenly_spaced_indices(length: int, limit: int | None) -> np.ndarray:
    """Select a bounded panel while preserving coverage of its time interval."""
    if limit is None or int(limit) <= 0 or length <= int(limit):
        return np.arange(length, dtype=int)
    return np.unique(np.linspace(0, length - 1, num=int(limit), dtype=int))


def temporal_source_partition(
    comments: pd.DataFrame,
    *,
    min_comments_per_half: int,
    max_comments_per_half: int | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create earliest/latest source-comment panels before any text slicing.

    The two panels have no shared source rows.  When a cap is supplied, each
    temporal half is sampled evenly rather than taking only the nearest boundary
    comments.  The returned diagnostics retain no text and can be safely saved
    after identifiers are removed.
    """
    early_rows: list[pd.DataFrame] = []
    late_rows: list[pd.DataFrame] = []
    diagnostics: list[dict[str, float | int | str]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
        split_at = len(ordered) // 2
        early_candidate = ordered.iloc[:split_at].copy()
        late_candidate = ordered.iloc[split_at:].copy()
        if min(len(early_candidate), len(late_candidate)) < int(min_comments_per_half):
            continue
        early = early_candidate.iloc[_evenly_spaced_indices(len(early_candidate), max_comments_per_half)].copy()
        late = late_candidate.iloc[_evenly_spaced_indices(len(late_candidate), max_comments_per_half)].copy()
        early["temporal_panel"] = "early"
        late["temporal_panel"] = "late"
        overlap = set(early["source_row"].astype(int)).intersection(set(late["source_row"].astype(int)))
        if overlap:
            raise RuntimeError(f"Temporal source partition leaked {len(overlap)} comments for one author.")
        early_rows.append(early)
        late_rows.append(late)
        diagnostics.append({
            "user_id": str(user_id),
            "split": str(ordered["split"].iloc[0]),
            "early_source_comments": int(len(early)),
            "late_source_comments": int(len(late)),
            "early_tokens": int(early["token_count"].sum()),
            "late_tokens": int(late["token_count"].sum()),
            "temporal_gap": float(late["order"].min() - early["order"].max()),
            "source_overlap_count": int(len(overlap)),
        })
    if not early_rows or not late_rows:
        empty = comments.iloc[:0].copy()
        return empty, empty, pd.DataFrame(diagnostics)
    early = pd.concat(early_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    late = pd.concat(late_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    overlap = set(early["source_row"].astype(int)).intersection(set(late["source_row"].astype(int)))
    if overlap:
        raise RuntimeError(f"Temporal source partition leaked {len(overlap)} source comments globally.")
    return early, late, pd.DataFrame(diagnostics)


def random_source_partition(
    comments: pd.DataFrame,
    *,
    seed: int,
    min_comments_per_half: int,
    max_comments_per_half: int | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create a source-disjoint random-half baseline on the same authors.

    This does not substitute for time separation.  It isolates the ordinary
    sampling cost of dividing an author's corpus from extra drift introduced by
    the earliest-versus-latest design.
    """
    rng = np.random.default_rng(int(seed))
    left_rows: list[pd.DataFrame] = []
    right_rows: list[pd.DataFrame] = []
    diagnostics: list[dict[str, float | int | str]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
        shuffled = rng.permutation(len(ordered))
        split_at = len(ordered) // 2
        left_candidate = ordered.iloc[np.sort(shuffled[:split_at])].copy()
        right_candidate = ordered.iloc[np.sort(shuffled[split_at:])].copy()
        if min(len(left_candidate), len(right_candidate)) < int(min_comments_per_half):
            continue
        left = left_candidate.iloc[_evenly_spaced_indices(len(left_candidate), max_comments_per_half)].copy()
        right = right_candidate.iloc[_evenly_spaced_indices(len(right_candidate), max_comments_per_half)].copy()
        left["temporal_panel"] = "random_left"
        right["temporal_panel"] = "random_right"
        overlap = set(left["source_row"].astype(int)).intersection(set(right["source_row"].astype(int)))
        if overlap:
            raise RuntimeError(f"Random source partition leaked {len(overlap)} comments for one author.")
        left_rows.append(left)
        right_rows.append(right)
        diagnostics.append({
            "user_id": str(user_id),
            "split": str(ordered["split"].iloc[0]),
            "left_source_comments": int(len(left)),
            "right_source_comments": int(len(right)),
            "left_tokens": int(left["token_count"].sum()),
            "right_tokens": int(right["token_count"].sum()),
            "source_overlap_count": int(len(overlap)),
        })
    if not left_rows or not right_rows:
        empty = comments.iloc[:0].copy()
        return empty, empty, pd.DataFrame(diagnostics)
    left = pd.concat(left_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    right = pd.concat(right_rows, ignore_index=True).sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)
    overlap = set(left["source_row"].astype(int)).intersection(set(right["source_row"].astype(int)))
    if overlap:
        raise RuntimeError(f"Random source partition leaked {len(overlap)} source comments globally.")
    return left, right, pd.DataFrame(diagnostics)


def _safe_ratio(numerator: float, denominator: float) -> float:
    """Avoid introducing infinities into structural opportunity profiles."""
    return float(numerator / denominator) if denominator > 0 else 0.0


def structural_opportunity_profiles(comments: pd.DataFrame) -> pd.DataFrame:
    """Summarize non-semantic expression opportunities at author-panel level.

    Pronouns, affect, stance, topic, and subreddit labels are intentionally not
    included here.  Removing them would redefine substantive expression as
    nuisance.  The profile captures only exposure/format constraints that can
    determine whether an expression is even possible to observe.
    """
    rows: list[dict[str, float | int | str]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        texts = group["text"].fillna("").astype(str).tolist()
        token_counts = np.asarray([len(tokenize(text)) for text in texts], dtype=float)
        char_counts = np.asarray([len(text) for text in texts], dtype=float)
        sentence_counts = np.asarray([len(sentence_split(text)) for text in texts], dtype=float)
        characters = float(char_counts.sum())
        source = "\n".join(texts)
        rows.append({
            "user_id": str(user_id),
            "split": str(group["split"].iloc[0]),
            "n_source_comments": int(len(group)),
            "total_tokens": float(token_counts.sum()),
            "mean_tokens_per_comment": float(token_counts.mean()),
            "sd_tokens_per_comment": float(token_counts.std(ddof=0)),
            "total_characters": characters,
            "mean_characters_per_comment": float(char_counts.mean()),
            "mean_sentences_per_comment": float(sentence_counts.mean()),
            "newline_density": _safe_ratio(source.count("\n"), characters),
            "digit_density": _safe_ratio(sum(character.isdigit() for character in source), characters),
            "url_comment_rate": float(np.mean([bool(_URL_RE.search(text)) for text in texts])),
            "quote_comment_rate": float(np.mean([bool(_QUOTE_RE.search(text)) for text in texts])),
            "list_comment_rate": float(np.mean([bool(_LIST_RE.search(text)) for text in texts])),
            "code_comment_rate": float(np.mean(["`" in text for text in texts])),
        })
    return pd.DataFrame(rows)


def condition_transition_profiles(early: pd.DataFrame, late: pd.DataFrame) -> pd.DataFrame:
    """Describe context-selection overlap without treating selection as nuisance."""
    rows: list[dict[str, float | int | str]] = []
    early_groups = {str(user): group for user, group in early.groupby("user_id", sort=False, observed=True)}
    late_groups = {str(user): group for user, group in late.groupby("user_id", sort=False, observed=True)}
    for user_id in sorted(set(early_groups).intersection(late_groups)):
        early_conditions = set(early_groups[user_id]["condition"].astype(str))
        late_conditions = set(late_groups[user_id]["condition"].astype(str))
        union = early_conditions.union(late_conditions)
        rows.append({
            "user_id": user_id,
            "split": str(early_groups[user_id]["split"].iloc[0]),
            "early_condition_count": int(len(early_conditions)),
            "late_condition_count": int(len(late_conditions)),
            "condition_jaccard": _safe_ratio(len(early_conditions.intersection(late_conditions)), len(union)),
        })
    return pd.DataFrame(rows)


def fit_text_representation(texts: pd.Series, spec: dict[str, Any], *, seed: int) -> TemporalTextRuntime:
    """Fit TF-IDF/SVD on discovery text only."""
    vectorizer = TfidfVectorizer(
        analyzer=str(spec["analyzer"]),
        lowercase=True,
        strip_accents="unicode",
        ngram_range=tuple(int(value) for value in spec["ngram_range"]),
        max_features=int(spec["max_features"]),
        min_df=int(spec.get("min_df", 1)),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts.fillna("").astype(str))
    components = min(int(spec["svd_dimensions"]), matrix.shape[0] - 1, matrix.shape[1] - 1)
    if components < 2:
        raise RuntimeError(f"Representation {spec['name']} has insufficient discovery rank: {matrix.shape}")
    reducer = TruncatedSVD(n_components=components, random_state=int(seed))
    reducer.fit(matrix)
    return TemporalTextRuntime(name=str(spec["name"]), vectorizer=vectorizer, reducer=reducer)


def author_mean_text_features(comments: pd.DataFrame, runtime: TemporalTextRuntime) -> tuple[pd.DataFrame, list[str]]:
    """Transform source comments and aggregate a common representation per author."""
    embedding = runtime.reducer.transform(runtime.vectorizer.transform(comments["text"].fillna("").astype(str)))
    names = [f"feature_{index:03d}" for index in range(embedding.shape[1])]
    frame = pd.DataFrame(embedding, columns=names)
    frame["user_id"] = comments["user_id"].astype(str).to_numpy()
    frame["split"] = comments["split"].astype(str).to_numpy()
    return frame.groupby(["user_id", "split"], observed=True, as_index=False)[names].mean(), names


def _stable_normal(source_row: int, dimensions: int, seed: int) -> np.ndarray:
    """Generate source-local deterministic noise without author-ID input."""
    digest = hashlib.sha256(f"v7-noise::{seed}::{source_row}".encode("utf-8")).digest()
    local_seed = int.from_bytes(digest[:8], "big", signed=False)
    return np.random.default_rng(local_seed).normal(size=int(dimensions))


def author_mean_deterministic_noise(comments: pd.DataFrame, *, dimensions: int, seed: int) -> tuple[pd.DataFrame, list[str]]:
    """Aggregate independent source noise as a negative-control representation."""
    values = np.vstack([_stable_normal(int(row), int(dimensions), int(seed)) for row in comments["source_row"].astype(int)])
    names = [f"feature_{index:03d}" for index in range(values.shape[1])]
    frame = pd.DataFrame(values, columns=names)
    frame["user_id"] = comments["user_id"].astype(str).to_numpy()
    frame["split"] = comments["split"].astype(str).to_numpy()
    return frame.groupby(["user_id", "split"], observed=True, as_index=False)[names].mean(), names


def align_author_panels(
    early: pd.DataFrame,
    late: pd.DataFrame,
    *,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return identically ordered early/late author matrices with split guards."""
    left = early[["user_id", "split", *feature_columns]].copy()
    right = late[["user_id", "split", *feature_columns]].copy()
    merged = left.merge(right, on=["user_id", "split"], suffixes=("_early", "_late"), validate="one_to_one")
    ordered = merged.sort_values(["split", "user_id"], kind="stable").reset_index(drop=True)
    left_out = ordered[["user_id", "split", *[f"{column}_early" for column in feature_columns]]].copy()
    right_out = ordered[["user_id", "split", *[f"{column}_late" for column in feature_columns]]].copy()
    left_out.columns = ["user_id", "split", *feature_columns]
    right_out.columns = ["user_id", "split", *feature_columns]
    return left_out, right_out


def fit_feature_scaler(left: pd.DataFrame, right: pd.DataFrame, *, feature_columns: list[str], train_user_ids: set[str]) -> FeatureScaler:
    """Fit a shared scaler on early/late training authors only."""
    masks = [left["user_id"].astype(str).isin(train_user_ids), right["user_id"].astype(str).isin(train_user_ids)]
    values = np.vstack([
        left.loc[masks[0], feature_columns].to_numpy(float),
        right.loc[masks[1], feature_columns].to_numpy(float),
    ])
    if len(values) < 2:
        raise RuntimeError("Need at least two training author-panels to fit a feature scaler.")
    mean = values.mean(axis=0, keepdims=True)
    scale = np.maximum(values.std(axis=0, keepdims=True), 1e-12)
    return FeatureScaler(mean=mean, scale=scale)


def fit_opportunity_residualizer(
    left_features: np.ndarray,
    right_features: np.ndarray,
    left_opportunity: np.ndarray,
    right_opportunity: np.ndarray,
    *,
    train_mask: np.ndarray,
    alpha: float,
) -> OpportunityResidualizer:
    """Fit only on training panels; confirmation panels never affect the surface."""
    x = np.vstack([left_features[train_mask], right_features[train_mask]])
    z = np.vstack([left_opportunity[train_mask], right_opportunity[train_mask]])
    if len(x) < 4:
        raise RuntimeError("Insufficient training author-panels for opportunity sensitivity model.")
    scaler = FeatureScaler(
        mean=z.mean(axis=0, keepdims=True),
        scale=np.maximum(z.std(axis=0, keepdims=True), 1e-12),
    )
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(scaler.transform(z), x)
    return OpportunityResidualizer(opportunity_scaler=scaler, model=model)


def alignment_contributions(left: np.ndarray, right: np.ndarray, *, pairing: np.ndarray | None = None) -> np.ndarray:
    """Return one own-vs-stranger rank contribution per author.

    The vector is useful for paired comparisons of two panel designs on the
    same authors.  It remains a registered-coordinate statistic, not a
    personality score.
    """
    x, y = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if x.shape != y.shape or len(x) < 2:
        return np.asarray([], dtype=float)
    selected = np.arange(len(x), dtype=int) if pairing is None else np.asarray(pairing, dtype=int)
    distance = np.linalg.norm(x[:, None, :] - y[None, :, :], axis=2)
    values = []
    for index, own_index in enumerate(selected):
        own = distance[index, own_index]
        stranger = np.delete(distance[index], own_index)
        values.append(np.mean(own < stranger) + 0.5 * np.mean(own == stranger))
    return np.asarray(values, dtype=float)


def alignment_auc(left: np.ndarray, right: np.ndarray, *, pairing: np.ndarray | None = None) -> float:
    """Compute mean own-vs-stranger alignment in a common coordinate space."""
    values = alignment_contributions(left, right, pairing=pairing)
    return float(np.mean(values)) if len(values) else float("nan")


def relative_distance_spearman(left: np.ndarray, right: np.ndarray, *, pairing: np.ndarray | None = None) -> float:
    """Compare within-panel pairwise-distance ranks without requiring an axis name."""
    x, y = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if x.shape != y.shape or len(x) < 3:
        return float("nan")
    if pairing is not None:
        y = y[np.asarray(pairing, dtype=int)]
    upper = np.triu_indices(len(x), k=1)
    left_distance = np.linalg.norm(x[:, None, :] - x[None, :, :], axis=2)[upper]
    right_distance = np.linalg.norm(y[:, None, :] - y[None, :, :], axis=2)[upper]
    value = spearmanr(left_distance, right_distance).statistic
    return float(value) if np.isfinite(value) else float("nan")


def global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Return a multivariate held-out R2 against a global-mean baseline."""
    target = np.asarray(target, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((target - target.mean(axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator)


def linear_transport_r2(
    left_train: np.ndarray,
    right_train: np.ndarray,
    left_test: np.ndarray,
    right_test: np.ndarray,
    *,
    alpha: float,
) -> float:
    """Fit a fixed coordinate map only on train authors and score confirmation."""
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(left_train, right_train)
    return global_r2(right_test, model.predict(left_test))


def summarize_numeric(frame: pd.DataFrame, *, columns: list[str], group_column: str = "split") -> pd.DataFrame:
    """Produce non-identifying group summaries for report artifacts."""
    rows: list[dict[str, float | int | str]] = []
    for group, subset in frame.groupby(group_column, observed=True, sort=True):
        for column in columns:
            values = pd.to_numeric(subset[column], errors="coerce").dropna().to_numpy(float)
            if not len(values):
                continue
            rows.append({
                group_column: str(group), "variable": column, "n": int(len(values)),
                "mean": float(values.mean()), "median": float(np.median(values)),
                "q025": float(np.quantile(values, 0.025)), "q975": float(np.quantile(values, 0.975)),
            })
    return pd.DataFrame(rows)
