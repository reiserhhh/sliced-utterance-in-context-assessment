"""Opportunity and content-sensitivity filtration for V8 M quotients.

The filtration is deliberately a sensitivity analysis, not a denoiser.  It
fits D0-only ridge maps from declared opportunity profiles to replicated
background-quotient coordinates, then applies those maps unchanged to D1/D2.
Removing a component does not establish that the component was noise.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import EventTensor
from suica_core.v8_realtext_relation_field import RealTextRelationSpec, stable_bucket


NUISANCE_GROUPS = (
    "opportunity",
    "template",
    "collection",
    "content_proxy",
)


@dataclass(frozen=True)
class NuisanceProfiles:
    """Replicate-specific author profiles aligned to an ``EventTensor``."""

    metadata: pd.DataFrame
    values: np.ndarray
    columns: tuple[str, ...]
    groups: dict[str, tuple[int, ...]]


@dataclass(frozen=True)
class FrozenNuisanceResidualizer:
    """D0-frozen scaler and replicate-specific ridge coefficients."""

    center: np.ndarray
    scale: np.ndarray
    active_columns: np.ndarray
    coefficients: np.ndarray
    ridge_ratio: float

    def transform(
        self,
        values: np.ndarray,
        nuisance: np.ndarray,
    ) -> np.ndarray:
        """Apply the frozen nuisance map without refitting."""
        target = np.asarray(values, dtype=float)
        profile = np.asarray(nuisance, dtype=float)
        if target.ndim != 3 or target.shape[1] != 2:
            raise ValueError("values must have shape author x 2 x dimensions.")
        if profile.shape[:2] != target.shape[:2]:
            raise ValueError("nuisance profiles must align with values.")
        standardized = (
            profile[..., self.active_columns] - self.center
        ) / self.scale
        result = np.empty_like(target, dtype=float)
        for replicate in range(2):
            design = np.column_stack(
                [np.ones(len(target)), standardized[:, replicate]]
            )
            result[:, replicate] = (
                target[:, replicate] - design @ self.coefficients[replicate]
            )
        return result


def _safe_rate(numerator: float, denominator: float) -> float:
    return float(numerator / max(denominator, 1.0))


def text_opportunity_vector(text: str) -> tuple[np.ndarray, tuple[str, ...]]:
    """Return language-light length and formatting opportunity features."""
    value = str(text or "")
    words = value.split()
    characters = max(len(value), 1)
    tokens = max(len(words), 1)
    letters = [character for character in value if character.isalpha()]
    uppercase = sum(character.isupper() for character in letters)
    punctuation = sum(character in ".,;:!?" for character in value)
    brackets = sum(character in "()[]{}" for character in value)
    quotes = sum(character in "\"'`" for character in value)
    urls = len(re.findall(r"https?://|www\.", value, flags=re.IGNORECASE))
    mentions = len(re.findall(r"(?<!\w)@\w+", value))
    hashtags = len(re.findall(r"(?<!\w)#\w+", value))
    list_lines = len(
        re.findall(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+", value)
    )
    code_marks = value.count("```") + value.count("`")
    columns = (
        "log_tokens",
        "log_characters",
        "characters_per_token",
        "newline_rate",
        "punctuation_rate",
        "question_rate",
        "exclamation_rate",
        "bracket_rate",
        "quote_rate",
        "digit_rate",
        "uppercase_rate",
        "url_rate",
        "mention_rate",
        "hashtag_rate",
        "list_rate",
        "code_mark_rate",
    )
    values = np.asarray(
        [
            np.log1p(tokens),
            np.log1p(characters),
            characters / tokens,
            _safe_rate(value.count("\n"), characters),
            _safe_rate(punctuation, characters),
            _safe_rate(value.count("?"), characters),
            _safe_rate(value.count("!"), characters),
            _safe_rate(brackets, characters),
            _safe_rate(quotes, characters),
            _safe_rate(sum(character.isdigit() for character in value), characters),
            _safe_rate(uppercase, len(letters)),
            _safe_rate(urls, tokens),
            _safe_rate(mentions, tokens),
            _safe_rate(hashtags, tokens),
            _safe_rate(list_lines, max(value.count("\n") + 1, 1)),
            _safe_rate(code_marks, tokens),
        ],
        dtype=float,
    )
    return values, columns


def _profile_moments(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    positions = np.linspace(-1.0, 1.0, num=len(matrix))
    slope_denominator = max(float(np.sum(positions**2)), 1e-12)
    slope = positions @ (matrix - matrix.mean(axis=0)) / slope_denominator
    return np.concatenate([matrix.mean(axis=0), matrix.std(axis=0), slope])


def _categorical_hash(
    values: Iterable[str],
    *,
    dimensions: int,
    salt: str,
) -> np.ndarray:
    materialized = tuple(map(str, values))
    result = np.zeros((len(materialized), dimensions), dtype=float)
    for row, value in enumerate(materialized):
        bucket = stable_bucket(value, salt=salt, modulus=dimensions)
        sign = (
            1.0
            if stable_bucket(value, salt=f"{salt}-sign", modulus=2)
            else -1.0
        )
        result[row, bucket] = sign
    return result


def _pair_similarity(values: np.ndarray) -> np.ndarray:
    vectors = np.asarray(values, dtype=float)
    vectors = vectors / np.maximum(
        np.linalg.norm(vectors, axis=1, keepdims=True),
        1e-12,
    )
    similarity = vectors @ vectors.T
    upper = similarity[np.triu_indices(len(vectors), k=1)]
    return np.asarray(
        [
            float(upper.mean()) if len(upper) else 0.0,
            float(upper.max()) if len(upper) else 0.0,
            float(np.mean(upper >= 0.95)) if len(upper) else 0.0,
        ]
    )


def _time_profile(group: pd.DataFrame, indices: np.ndarray) -> np.ndarray:
    if "timestamp" not in group.columns:
        return np.zeros(3, dtype=float)
    source = group.iloc[indices]["timestamp"]
    numeric = pd.to_numeric(source, errors="coerce").to_numpy(dtype=float)
    if np.isfinite(numeric).sum() >= 2 and np.nanmedian(numeric) > 1e8:
        timestamps = numeric[np.isfinite(numeric)]
    else:
        parsed = pd.to_datetime(source, utc=True, errors="coerce")
        raw = parsed.astype("int64").to_numpy(dtype=float)
        valid = raw > np.iinfo("int64").min / 2
        timestamps = raw[valid] / 1e9
    if len(timestamps) < 2:
        return np.zeros(3, dtype=float)
    gaps = np.abs(np.diff(timestamps))
    return np.asarray(
        [
            np.log1p(float(np.ptp(timestamps))),
            np.log1p(float(np.mean(gaps))),
            float(np.std(gaps) / max(np.mean(gaps), 1.0)),
        ]
    )


def build_nuisance_profiles(
    event_rows: pd.DataFrame,
    tensor: EventTensor,
    *,
    feature_spec: RealTextRelationSpec,
    content_directions: int = 8,
) -> NuisanceProfiles:
    """Build opportunity, template, collection, and content-proxy profiles."""
    required = {"author_id", "order", "text"}
    if not required.issubset(event_rows.columns):
        raise ValueError(f"event_rows must contain {sorted(required)}")
    rng = np.random.default_rng(feature_spec.seed + 911)
    directions = rng.normal(
        size=(content_directions, tensor.vectors.shape[-1])
    )
    directions /= np.maximum(
        np.linalg.norm(directions, axis=1, keepdims=True),
        1e-12,
    )
    by_author = {
        str(author): group.sort_values("order", kind="stable").reset_index(drop=True)
        for author, group in event_rows.groupby(
            "author_id",
            observed=True,
            sort=False,
        )
    }
    opportunity_columns: tuple[str, ...] | None = None
    event_count = int(tensor.vectors.shape[1])
    if event_count < 4 or event_count % 2:
        raise ValueError("Nuisance profiles require an even event count >= 4.")
    author_profiles = []
    for row_index, metadata in tensor.metadata.reset_index(drop=True).iterrows():
        author = str(metadata["author_id"])
        group = by_author.get(author)
        if group is None or len(group) != event_count:
            raise ValueError(
                f"No aligned {event_count}-event profile for {author}."
            )
        event_opportunity = []
        for text in group["text"].astype(str):
            vector, columns = text_opportunity_vector(text)
            opportunity_columns = columns
            event_opportunity.append(vector)
        event_opportunity_array = np.vstack(event_opportunity)
        replicate_profiles = []
        for replicate, indices in enumerate(
            (
                np.arange(0, event_count, 2),
                np.arange(1, event_count, 2),
            )
        ):
            opportunity = np.concatenate(
                [
                    _profile_moments(event_opportunity_array[indices]),
                    _time_profile(group, indices),
                ]
            )
            template = _pair_similarity(tensor.vectors[row_index, indices])
            language = _categorical_hash(
                group.iloc[indices].get(
                    "lang",
                    pd.Series(["<missing>"] * len(indices)),
                ),
                dimensions=4,
                salt="v8-nuisance-language",
            ).mean(axis=0)
            symbol = _categorical_hash(
                group.iloc[indices].get(
                    "symbol",
                    pd.Series(["<missing>"] * len(indices)),
                ),
                dimensions=8,
                salt="v8-nuisance-symbol",
            ).mean(axis=0)
            collection = np.concatenate([language, symbol])
            projections = tensor.vectors[row_index, indices] @ directions.T
            content = np.concatenate(
                [projections.mean(axis=0), projections.std(axis=0)]
            )
            replicate_profiles.append(
                np.concatenate([opportunity, template, collection, content])
            )
        author_profiles.append(np.stack(replicate_profiles))
    if opportunity_columns is None:
        raise ValueError("No opportunity profiles were built.")
    opportunity_names = tuple(
        f"{summary}_{column}"
        for summary in ("mean", "std", "slope")
        for column in opportunity_columns
    ) + ("log_time_span", "log_time_gap", "time_gap_cv")
    template_names = (
        "within_replicate_pair_cosine_mean",
        "within_replicate_pair_cosine_max",
        "within_replicate_near_duplicate_rate",
    )
    collection_names = tuple(
        [f"language_hash_{index}" for index in range(4)]
        + [f"symbol_hash_{index}" for index in range(8)]
    )
    content_names = tuple(
        [f"content_projection_mean_{index}" for index in range(content_directions)]
        + [f"content_projection_std_{index}" for index in range(content_directions)]
    )
    names = opportunity_names + template_names + collection_names + content_names
    starts = np.cumsum(
        [
            0,
            len(opportunity_names),
            len(template_names),
            len(collection_names),
        ]
    )
    groups = {
        "opportunity": tuple(range(starts[0], starts[1])),
        "template": tuple(range(starts[1], starts[2])),
        "collection": tuple(range(starts[2], starts[3])),
        "content_proxy": tuple(range(starts[3], len(names))),
    }
    values = np.stack(author_profiles)
    if values.shape[-1] != len(names):
        raise RuntimeError("Nuisance profile schema does not match values.")
    return NuisanceProfiles(
        metadata=tensor.metadata.copy(),
        values=values,
        columns=names,
        groups=groups,
    )


def fit_nuisance_residualizer(
    values: np.ndarray,
    nuisance: np.ndarray,
    calibration_mask: np.ndarray,
    *,
    columns: Iterable[int],
    ridge_ratio: float = 0.10,
) -> FrozenNuisanceResidualizer:
    """Fit replicate-specific ridge maps on the calibration panel only."""
    target = np.asarray(values, dtype=float)
    profile = np.asarray(nuisance, dtype=float)
    mask = np.asarray(calibration_mask, dtype=bool)
    selected = np.asarray(tuple(columns), dtype=int)
    if not len(selected):
        raise ValueError("At least one nuisance column is required.")
    calibration = profile[mask][..., selected].reshape(-1, len(selected))
    center = calibration.mean(axis=0)
    scale = calibration.std(axis=0)
    active = scale > 1e-8
    if not np.any(active):
        raise ValueError("Selected nuisance columns have no D0 variation.")
    selected = selected[active]
    center = center[active]
    scale = scale[active]
    standardized = (profile[..., selected] - center) / scale
    coefficients = []
    for replicate in range(2):
        design = np.column_stack(
            [np.ones(mask.sum()), standardized[mask, replicate]]
        )
        gram = design.T @ design
        penalty_scale = max(
            float(np.trace(gram[1:, 1:])) / max(gram.shape[0] - 1, 1),
            1e-12,
        )
        penalty = np.eye(gram.shape[0]) * ridge_ratio * penalty_scale
        penalty[0, 0] = 0.0
        coefficients.append(
            np.linalg.solve(
                gram + penalty,
                design.T @ target[mask, replicate],
            )
        )
    return FrozenNuisanceResidualizer(
        center=center,
        scale=scale,
        active_columns=selected,
        coefficients=np.stack(coefficients),
        ridge_ratio=float(ridge_ratio),
    )


def signed_link(values: np.ndarray) -> float:
    """Compute the same-minus-stranger normalized link in linear time."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 3 or array.shape[1] != 2:
        raise ValueError("values must have shape author x 2 x dimensions.")
    if len(array) < 2:
        raise ValueError("At least two authors are required.")
    first = array[:, 0] - array[:, 0].mean(axis=0, keepdims=True)
    second = array[:, 1] - array[:, 1].mean(axis=0, keepdims=True)
    same_mean = float(np.mean(np.einsum("ij,ij->i", first, second)))
    denominator = np.sqrt(
        max(float(np.mean(np.sum(first**2, axis=1))), 1e-12)
        * max(float(np.mean(np.sum(second**2, axis=1))), 1e-12)
    )
    # Centering makes the sum of all n^2 cross-products zero, so the
    # off-diagonal mean is -same_mean/(n-1).
    return float(len(array) / (len(array) - 1) * same_mean / denominator)


def within_context_link_null(
    values: np.ndarray,
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[float, np.ndarray]:
    """Permute replicate-two author correspondence within context strata."""
    natural = np.asarray(values, dtype=float)
    labels = np.asarray(contexts).astype(str)
    observed = signed_link(natural)
    null = np.empty(draws, dtype=float)
    for draw in range(draws):
        order = np.arange(len(natural))
        for context in np.unique(labels):
            indices = np.flatnonzero(labels == context)
            order[indices] = rng.permutation(indices)
        permuted = natural.copy()
        permuted[:, 1] = natural[order, 1]
        null[draw] = signed_link(permuted)
    return float(observed), null


def bootstrap_link_interval(
    values: np.ndarray,
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Return a context-stratified centered bootstrap interval for link."""
    natural = np.asarray(values, dtype=float)
    labels = np.asarray(contexts).astype(str)
    observed = signed_link(natural)
    samples = np.empty(draws, dtype=float)
    context_indices = {
        context: np.flatnonzero(labels == context)
        for context in np.unique(labels)
    }
    for draw in range(draws):
        indices = np.concatenate(
            [
                rng.choice(values, size=len(values), replace=True)
                for values in context_indices.values()
            ]
        )
        samples[draw] = signed_link(natural[indices])
    centered = samples - samples.mean()
    return (
        float(observed + np.quantile(centered, alpha / 2)),
        float(observed + np.quantile(centered, 1 - alpha / 2)),
    )


def cross_trace_decomposition(
    raw: np.ndarray,
    residual: np.ndarray,
) -> dict[str, float]:
    """Exactly decompose the normalized observed link into four channels.

    If ``raw = predictable + residual``, bilinearity gives one predictable,
    one residual, and two directional coupling terms. All terms use the raw
    link denominator, so they sum exactly to ``quotient_statistics(raw)``.
    """
    observed = np.asarray(raw, dtype=float)
    remainder = np.asarray(residual, dtype=float)
    if observed.shape != remainder.shape:
        raise ValueError("raw and residual must have identical shape.")
    if observed.ndim != 3 or observed.shape[1] != 2:
        raise ValueError("arrays must have shape author x 2 x dimensions.")
    predictable = observed - remainder

    def centered(values: np.ndarray, replicate: int) -> np.ndarray:
        selected = values[:, replicate]
        return selected - selected.mean(axis=0, keepdims=True)

    raw_first = centered(observed, 0)
    raw_second = centered(observed, 1)
    denominator = np.sqrt(
        max(float(np.mean(np.sum(raw_first**2, axis=1))), 1e-12)
        * max(float(np.mean(np.sum(raw_second**2, axis=1))), 1e-12)
    )
    finite_sample = len(observed) / max(len(observed) - 1, 1)

    def component(
        left: np.ndarray,
        right: np.ndarray,
    ) -> float:
        trace = float(
            np.mean(
                np.einsum(
                    "ij,ij->i",
                    centered(left, 0),
                    centered(right, 1),
                )
            )
        )
        return float(finite_sample * trace / denominator)

    values = {
        "profile_predictable": component(predictable, predictable),
        "residual": component(remainder, remainder),
        "profile_to_residual": component(predictable, remainder),
        "residual_to_profile": component(remainder, predictable),
    }
    values["sum"] = float(sum(values.values()))
    values["observed_link"] = signed_link(observed)
    values["closure_error"] = float(values["sum"] - values["observed_link"])
    return values


def within_context_decomposition_null(
    raw: np.ndarray,
    residual: np.ndarray,
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    """Recompute the exact four-channel decomposition in every null world."""
    observed_raw = np.asarray(raw, dtype=float)
    observed_residual = np.asarray(residual, dtype=float)
    labels = np.asarray(contexts).astype(str)
    if observed_raw.shape != observed_residual.shape:
        raise ValueError("raw and residual must align.")
    observed = cross_trace_decomposition(observed_raw, observed_residual)
    names = (
        "profile_predictable",
        "residual",
        "profile_to_residual",
        "residual_to_profile",
        "sum",
        "observed_link",
    )
    null = {name: np.empty(draws, dtype=float) for name in names}
    for draw in range(draws):
        order = np.arange(len(observed_raw))
        for context in np.unique(labels):
            indices = np.flatnonzero(labels == context)
            order[indices] = rng.permutation(indices)
        raw_world = observed_raw.copy()
        residual_world = observed_residual.copy()
        raw_world[:, 1] = observed_raw[order, 1]
        residual_world[:, 1] = observed_residual[order, 1]
        world = cross_trace_decomposition(raw_world, residual_world)
        for name in names:
            null[name][draw] = world[name]
    return observed, null
