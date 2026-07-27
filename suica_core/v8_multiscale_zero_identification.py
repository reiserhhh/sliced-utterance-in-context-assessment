"""Multiscale component identification for SUICA V3.7H.3.

The module contains only synthetic score-space machinery. It separates
balanced society, group, author, condition, response, opportunity, and
technical components and exposes the limits where each component can or
cannot be identified.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


STABLE_COMPONENTS = (
    "social",
    "group",
    "author",
    "condition",
    "response",
)
TRANSIENT_COMPONENTS = ("opportunity", "technical")
ALL_COMPONENTS = STABLE_COMPONENTS + TRANSIENT_COMPONENTS


@dataclass(frozen=True)
class MultiscaleZeroSpec:
    """Dimensions of one balanced multiscale planted world."""

    societies: int = 8
    groups_per_society: int = 4
    authors_per_group: int = 8
    conditions: int = 6
    response_rank: int = 2
    opportunities: int = 4
    technical_streams: int = 2
    dimensions: int = 6
    student_df: float = 5.0
    heteroskedastic_strength: float = 0.35


def _draw_standardized(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "heteroskedastic_t5":
        if student_df <= 2.0:
            raise ValueError("student_df must exceed two")
        return (
            rng.standard_t(student_df, size=shape)
            / np.sqrt(student_df / (student_df - 2.0))
        )
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def _normalize_rms(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    scale = float(np.sqrt(np.mean(array**2)))
    if scale <= 1e-12:
        raise ValueError("cannot normalize a zero-energy component")
    return array / scale


def _normalize_sample_variance(
    values: np.ndarray,
    *,
    axis: int,
) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    energy = float(np.var(array, axis=axis, ddof=1).mean())
    if energy <= 1e-12:
        raise ValueError("cannot normalize a zero-variance component")
    return array / np.sqrt(energy)


def _condition_basis(
    rng: np.random.Generator,
    conditions: int,
    rank: int,
) -> np.ndarray:
    if rank < 1 or rank >= conditions:
        raise ValueError("response_rank must be in [1, conditions)")
    raw = rng.normal(size=(conditions, rank))
    raw -= raw.mean(axis=0, keepdims=True)
    basis, _ = np.linalg.qr(raw)
    basis = basis[:, :rank]
    basis -= basis.mean(axis=0, keepdims=True)
    return basis


def generate_multiscale_basis(
    *,
    seed: int,
    spec: MultiscaleZeroSpec,
    noise_mode: str,
) -> dict[str, np.ndarray]:
    """Generate unit-energy components satisfying the frozen constraints."""
    streams = np.random.SeedSequence(int(seed)).spawn(8)
    rngs = [np.random.default_rng(stream) for stream in streams]
    s = int(spec.societies)
    g = int(spec.groups_per_society)
    u = int(spec.authors_per_group)
    c = int(spec.conditions)
    q = int(spec.response_rank)
    k = int(spec.opportunities)
    r = int(spec.technical_streams)
    d = int(spec.dimensions)

    social = rngs[0].normal(size=(s, d))
    social -= social.mean(axis=0, keepdims=True)
    social = _normalize_rms(social)

    group = rngs[1].normal(size=(s, g, d))
    group -= group.mean(axis=1, keepdims=True)
    group = _normalize_rms(group)

    author = rngs[2].normal(size=(s, g, u, d))
    author -= author.mean(axis=2, keepdims=True)
    author = _normalize_rms(author)

    condition = rngs[3].normal(size=(c, d))
    condition -= condition.mean(axis=0, keepdims=True)
    condition = _normalize_rms(condition)

    condition_basis = _condition_basis(rngs[4], c, q)
    coefficient = rngs[5].normal(size=(s, g, u, q, d))
    coefficient -= coefficient.mean(axis=2, keepdims=True)
    response = np.einsum(
        "cq,sguqd->sgucd",
        condition_basis,
        coefficient,
    )
    response = _normalize_rms(response)

    opportunity = _draw_standardized(
        rngs[6],
        (2, s, g, u, c, k, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    if noise_mode == "heteroskedastic_t5":
        author_anchor = author[..., 0]
        scale = np.exp(
            float(spec.heteroskedastic_strength)
            * author_anchor
            / max(float(author_anchor.std(ddof=1)), 1e-12)
        )
        scale = np.clip(scale, 0.45, 2.20)
        opportunity *= scale[None, :, :, :, None, None, None]
    opportunity = _normalize_sample_variance(opportunity, axis=5)

    technical = _draw_standardized(
        rngs[7],
        (2, s, g, u, c, k, r, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    if noise_mode == "heteroskedastic_t5":
        author_anchor = author[..., 0]
        scale = np.exp(
            float(spec.heteroskedastic_strength)
            * author_anchor
            / max(float(author_anchor.std(ddof=1)), 1e-12)
        )
        scale = np.clip(scale, 0.45, 2.20)
        technical *= scale[
            None, :, :, :, None, None, None, None
        ]
    technical = _normalize_sample_variance(technical, axis=6)

    return {
        "social": social,
        "group": group,
        "author": author,
        "condition": condition,
        "response": response,
        "opportunity": opportunity,
        "technical": technical,
        "condition_basis": condition_basis,
    }


def simulate_multiscale_panel(
    basis: dict[str, np.ndarray],
    *,
    scales: dict[str, float],
    opportunities: int | None = None,
) -> np.ndarray:
    """Assemble two independent panels from one planted component basis."""
    k_max = int(np.asarray(basis["opportunity"]).shape[5])
    k = k_max if opportunities is None else int(opportunities)
    if not 1 <= k <= k_max:
        raise ValueError("opportunities must be within the planted range")
    required = set(ALL_COMPONENTS)
    missing = required.difference(scales)
    if missing:
        raise ValueError(f"missing component scales: {sorted(missing)}")

    social = (
        float(scales["social"])
        * np.asarray(basis["social"])[
            None, :, None, None, None, None, None, :
        ]
    )
    group = (
        float(scales["group"])
        * np.asarray(basis["group"])[
            None, :, :, None, None, None, None, :
        ]
    )
    author = (
        float(scales["author"])
        * np.asarray(basis["author"])[
            None, :, :, :, None, None, None, :
        ]
    )
    condition = (
        float(scales["condition"])
        * np.asarray(basis["condition"])[
            None, None, None, None, :, None, None, :
        ]
    )
    response = (
        float(scales["response"])
        * np.asarray(basis["response"])[
            None, :, :, :, :, None, None, :
        ]
    )
    opportunity = (
        float(scales["opportunity"])
        * np.asarray(basis["opportunity"])[
            :, :, :, :, :, :k, None, :
        ]
    )
    technical = (
        float(scales["technical"])
        * np.asarray(basis["technical"])[
            :, :, :, :, :, :k, :, :
        ]
    )
    return (
        social
        + group
        + author
        + condition
        + response
        + opportunity
        + technical
    )


def decompose_balanced_panel(values: np.ndarray) -> dict[str, np.ndarray]:
    """Apply the frozen balanced hierarchical conditional-mean projections."""
    panel = np.asarray(values, dtype=float)
    if panel.ndim != 8 or panel.shape[0] != 2:
        raise ValueError(
            "panel must be halves x societies x groups x authors x "
            "conditions x opportunities x streams x dimensions"
        )
    cell = panel.mean(axis=(5, 6))
    mean = cell.mean(axis=(1, 2, 3, 4))
    social = (
        cell.mean(axis=(2, 3, 4))
        - mean[:, None, :]
    )
    group = (
        cell.mean(axis=(3, 4))
        - mean[:, None, None, :]
        - social[:, :, None, :]
    )
    condition = (
        cell.mean(axis=(1, 2, 3))
        - mean[:, None, :]
    )
    author = (
        cell.mean(axis=4)
        - mean[:, None, None, None, :]
        - social[:, :, None, None, :]
        - group[:, :, :, None, :]
    )
    response = (
        cell
        - mean[:, None, None, None, None, :]
        - social[:, :, None, None, None, :]
        - group[:, :, :, None, None, :]
        - author[:, :, :, :, None, :]
        - condition[:, None, None, None, :, :]
    )
    reconstructed = (
        mean[:, None, None, None, None, :]
        + social[:, :, None, None, None, :]
        + group[:, :, :, None, None, :]
        + author[:, :, :, :, None, :]
        + condition[:, None, None, None, :, :]
        + response
    )
    return {
        "mean": mean,
        "social": social,
        "group": group,
        "author": author,
        "condition": condition,
        "response": response,
        "cell_mean": cell,
        "reconstruction_error": np.asarray(
            np.max(np.abs(reconstructed - cell)),
        ),
    }


def measurement_energies(
    values: np.ndarray,
    decomposition: dict[str, np.ndarray] | None = None,
) -> dict[str, float]:
    """Estimate stable, opportunity, and technical component energies."""
    panel = np.asarray(values, dtype=float)
    fitted = (
        decompose_balanced_panel(panel)
        if decomposition is None
        else decomposition
    )
    energies = {
        component: float(
            np.mean(
                np.asarray(fitted[component][0])
                * np.asarray(fitted[component][1])
            )
        )
        for component in STABLE_COMPONENTS
    }
    stream_variance = np.var(panel, axis=6, ddof=1)
    technical = float(stream_variance.mean())
    occasion_mean = panel.mean(axis=6)
    opportunity_raw = float(
        np.var(occasion_mean, axis=5, ddof=1).mean()
    )
    energies["opportunity"] = float(
        opportunity_raw - technical / panel.shape[6]
    )
    energies["technical"] = technical
    return energies


def _flatten_correlation(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float).ravel()
    b = np.asarray(right, dtype=float).ravel()
    if a.std(ddof=1) <= 1e-12 or b.std(ddof=1) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _recovery_r2(truth: np.ndarray, estimate: np.ndarray) -> float:
    target = np.asarray(truth, dtype=float).ravel()
    predicted = np.asarray(estimate, dtype=float).ravel()
    denominator = float(
        np.sum((target - target.mean()) ** 2)
    )
    if denominator <= 1e-12:
        return float("nan")
    return float(
        1.0 - np.sum((predicted - target) ** 2) / denominator
    )


def stable_recovery_metrics(
    decomposition: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    stable_amplitude: float,
) -> list[dict[str, float | str]]:
    """Measure truth recovery and split-panel stability for stable terms."""
    rows: list[dict[str, float | str]] = []
    for component in STABLE_COMPONENTS:
        estimate = np.asarray(decomposition[component], dtype=float)
        truth = (
            float(stable_amplitude)
            * np.asarray(basis[component], dtype=float)
        )
        rows.append({
            "component": component,
            "recovery_r2_panel_a": _recovery_r2(truth, estimate[0]),
            "recovery_r2_panel_b": _recovery_r2(truth, estimate[1]),
            "recovery_r2_mean": _recovery_r2(
                truth,
                estimate.mean(axis=0),
            ),
            "truth_correlation_mean": _flatten_correlation(
                truth,
                estimate.mean(axis=0),
            ),
            "split_panel_correlation": _flatten_correlation(
                estimate[0],
                estimate[1],
            ),
        })
    return rows


def projection_commutator(
    values: np.ndarray,
    group_labels: np.ndarray,
    condition_labels: np.ndarray,
) -> float:
    """Return normalized empirical conditional-mean projection commutator."""
    y = np.asarray(values, dtype=float)
    groups = np.asarray(group_labels)
    conditions = np.asarray(condition_labels)
    if not (len(y) == len(groups) == len(conditions)):
        raise ValueError("values and labels must have equal length")

    def project(data: np.ndarray, labels: np.ndarray) -> np.ndarray:
        result = np.empty_like(data, dtype=float)
        for label in np.unique(labels):
            mask = labels == label
            result[mask] = data[mask].mean(axis=0)
        return result

    group_after_condition = project(
        project(y, conditions),
        groups,
    )
    condition_after_group = project(
        project(y, groups),
        conditions,
    )
    denominator = max(
        float(np.linalg.norm(y - y.mean(axis=0))),
        1e-12,
    )
    return float(
        np.linalg.norm(group_after_condition - condition_after_group)
        / denominator
    )


def simulate_selection_assay(
    *,
    seed: int,
    authors: int,
    conditions: int,
    forced_per_condition: int,
    extra_draws: int,
    selection_strength: float,
    author_effect: float,
    condition_effect: float,
    noise_sd: float,
) -> dict[str, float]:
    """Create a Simpson-style author-dependent condition-selection assay."""
    if authors % 8:
        raise ValueError("selection_authors must be divisible by eight")
    rng = np.random.default_rng(int(seed))
    group_labels = np.repeat(np.arange(8), authors // 8)
    group_anchor = np.linspace(-1.25, 1.25, 8)
    author_latent = (
        group_anchor[group_labels]
        + rng.normal(scale=0.45, size=authors)
    )
    condition_score = np.linspace(-1.0, 1.0, conditions)
    rows_y: list[float] = []
    rows_group: list[int] = []
    rows_condition: list[int] = []
    rows_author: list[int] = []
    cell_mean = np.empty((authors, conditions), dtype=float)
    for author_index in range(authors):
        logits = (
            float(selection_strength)
            * author_latent[author_index]
            * condition_score
        )
        logits -= logits.max()
        probability = np.exp(logits)
        probability /= probability.sum()
        counts = (
            np.full(conditions, int(forced_per_condition), dtype=int)
            + rng.multinomial(int(extra_draws), probability)
        )
        for condition_index, count in enumerate(counts):
            location = (
                float(author_effect) * author_latent[author_index]
                - float(condition_effect)
                * condition_score[condition_index]
            )
            draws = location + rng.normal(
                scale=float(noise_sd),
                size=int(count),
            )
            cell_mean[author_index, condition_index] = float(
                draws.mean()
            )
            rows_y.extend(draws.tolist())
            rows_group.extend(
                [int(group_labels[author_index])] * int(count)
            )
            rows_condition.extend(
                [int(condition_index)] * int(count)
            )
            rows_author.extend([author_index] * int(count))
    y = np.asarray(rows_y, dtype=float)
    author_index = np.asarray(rows_author, dtype=int)
    naive = np.asarray([
        y[author_index == index].mean()
        for index in range(authors)
    ])
    standardized = cell_mean.mean(axis=1)
    raw_commutator = projection_commutator(
        y[:, None],
        np.asarray(rows_group),
        np.asarray(rows_condition),
    )

    balanced_y = cell_mean.reshape(-1, 1)
    balanced_group = np.repeat(group_labels, conditions)
    balanced_condition = np.tile(np.arange(conditions), authors)
    balanced_commutator = projection_commutator(
        balanced_y,
        balanced_group,
        balanced_condition,
    )
    return {
        "naive_author_correlation": _flatten_correlation(
            naive,
            author_latent,
        ),
        "standardized_author_correlation": _flatten_correlation(
            standardized,
            author_latent,
        ),
        "raw_commutator": raw_commutator,
        "balanced_commutator": balanced_commutator,
        "balanced_to_raw_ratio": float(
            balanced_commutator / max(raw_commutator, 1e-12)
        ),
    }


def coarse_graining_assay(
    *,
    seed: int,
    sizes: tuple[int, ...],
    units: int,
    dimensions: int,
) -> list[dict[str, float | int | str]]:
    """Measure which random components vanish under aggregation."""
    rng = np.random.default_rng(int(seed))
    maximum = max(map(int, sizes))
    rows: list[dict[str, float | int | str]] = []

    def append_family(
        family: str,
        common: np.ndarray,
        independent: np.ndarray,
        *,
        rho: float,
    ) -> None:
        for size in sizes:
            n = int(size)
            values = (
                np.sqrt(float(rho)) * common[:, None, :]
                + np.sqrt(1.0 - float(rho))
                * independent[:, :n, :]
            )
            aggregate = values.mean(axis=1)
            rows.append({
                "family": family,
                "size": n,
                "energy": float(np.mean(aggregate**2)),
                "rho": float(rho),
            })

    author_common = rng.normal(size=(units, dimensions))
    author_independent = rng.normal(
        size=(units, maximum, dimensions)
    )
    append_family(
        "author_independent_to_group_mean",
        author_common,
        author_independent,
        rho=0.0,
    )
    append_family(
        "author_intraclass_to_group_mean",
        author_common,
        author_independent,
        rho=0.30,
    )
    append_family(
        "group_common_across_authors",
        author_common,
        author_independent,
        rho=1.0,
    )

    society_common = rng.normal(size=(units, dimensions))
    group_independent = rng.normal(
        size=(units, maximum, dimensions)
    )
    append_family(
        "group_independent_to_society_mean",
        society_common,
        group_independent,
        rho=0.0,
    )
    append_family(
        "society_common_across_groups",
        society_common,
        group_independent,
        rho=1.0,
    )
    return rows


def persistent_alias_assay(*, seed: int, shape: tuple[int, ...]) -> dict[str, Any]:
    """Construct observationally identical response and confound worlds."""
    streams = np.random.SeedSequence(int(seed)).spawn(2)
    base = np.random.default_rng(streams[0]).normal(size=shape)
    persistent = np.random.default_rng(streams[1]).normal(size=shape)
    response_world = base + persistent
    confound_world = base + persistent
    return {
        "identity_error": float(
            np.max(np.abs(response_world - confound_world))
        ),
        "classification": "CAUSE_UNIDENTIFIED",
    }


def minority_near_kernel_assay(
    *,
    seed: int,
    authors: int,
    dimensions: int,
    prevalence: tuple[float, ...],
    observable_fraction: tuple[float, ...],
    individual_energy: float,
) -> list[dict[str, float]]:
    """Verify the population attenuation law for sparse near-kernel effects."""
    if dimensions < 3:
        raise ValueError("near-kernel assay requires at least three dimensions")
    rng = np.random.default_rng(int(seed))
    basis, _ = np.linalg.qr(rng.normal(size=(dimensions, dimensions)))
    score_dimensions = max(1, dimensions // 2)
    operator = basis[:, :score_dimensions].T
    range_vector = basis[:, 0]
    kernel_vector = basis[:, -1]
    order = rng.permutation(authors)
    rows: list[dict[str, float]] = []
    for requested_p in prevalence:
        affected_count = max(1, int(round(float(requested_p) * authors)))
        affected = np.zeros(authors, dtype=bool)
        affected[order[:affected_count]] = True
        achieved_p = float(affected.mean())
        signs = rng.choice([-1.0, 1.0], size=authors)
        for alpha in observable_fraction:
            direction = (
                np.sqrt(float(alpha)) * range_vector
                + np.sqrt(1.0 - float(alpha)) * kernel_vector
            )
            response = np.zeros((authors, dimensions), dtype=float)
            response[affected] = (
                np.sqrt(float(individual_energy))
                * signs[affected, None]
                * direction[None, :]
            )
            score = response @ operator.T
            observed = float(np.mean(np.sum(score**2, axis=1)))
            expected = float(
                achieved_p
                * float(alpha)
                * float(individual_energy)
            )
            error = abs(observed - expected)
            rows.append({
                "requested_prevalence": float(requested_p),
                "achieved_prevalence": achieved_p,
                "observable_fraction": float(alpha),
                "individual_energy": float(individual_energy),
                "observed_population_energy": observed,
                "expected_population_energy": expected,
                "absolute_error": float(error),
                "relative_error": float(
                    error / max(expected, 1e-12)
                    if expected > 0.0
                    else error
                ),
            })
    return rows

