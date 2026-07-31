"""Capacity-conditioned replicated-support coverage for SUICA V8.

This module compares anonymous technical support densities. It does not name
personality, emotion, state, or any other psychological construct.

For trace-one replicated density ``rho`` and capacity ``k``, the soft filter
is the regularized solution

    argmax  tr(P rho) - tau/2 ||P - k I/d||_F^2
    s.t.    0 <= P <= I, tr(P) = k.

The closed-form eigenvalue weights are

    p_i = clip(k/d + (lambda_i - mu)/tau, 0, 1),

with ``mu`` chosen to enforce the trace. Directional coverage evaluates a
source D0 filter on a target confirmation density and divides by the same
target density evaluated with its native D0 filter. This target-normalized
ratio is a capacity-conditioned coverage diagnostic, not literal set
inclusion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import (
    CorpusFeaturePanel,
    replicated_covariance,
    stable_bucket,
)


@dataclass(frozen=True)
class SupportContainmentSpec:
    """Frozen numerical choices for the exploratory coverage audit."""

    capacities: tuple[int, ...] = (4, 8, 16, 24, 32)
    tau_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0, 4.0)
    bootstrap_draws: int = 199
    rotation_draws: int = 99
    calibration_subsamples: int = 39
    maximum_calibration_authors: int = 420
    maximum_confirmation_authors: int = 256
    minimum_authors: int = 48
    denominator_floor: float = 1e-6
    minimum_grid_fraction: float = 0.80
    approximate_containment_floor: float = 0.80
    calibration_sign_fraction_floor: float = 0.80
    seed: int = 20260806

    def __post_init__(self) -> None:
        if not self.capacities or any(value < 1 for value in self.capacities):
            raise ValueError("capacities must contain positive integers.")
        if sorted(set(self.capacities)) != list(self.capacities):
            raise ValueError("capacities must be unique and increasing.")
        if not self.tau_multipliers or any(
            value <= 0 for value in self.tau_multipliers
        ):
            raise ValueError("tau_multipliers must be positive.")
        if self.bootstrap_draws < 19 or self.rotation_draws < 19:
            raise ValueError("Bootstrap and rotation budgets must be at least 19.")
        if self.calibration_subsamples < 9:
            raise ValueError("At least nine D0 sensitivity subsamples are required.")
        if self.minimum_authors < 16:
            raise ValueError("At least sixteen confirmation authors are required.")
        if not 0 < self.minimum_grid_fraction <= 1:
            raise ValueError("minimum_grid_fraction must lie in (0, 1].")
        if not 0 < self.approximate_containment_floor <= 1:
            raise ValueError("approximate_containment_floor must lie in (0, 1].")
        if not 0.5 <= self.calibration_sign_fraction_floor <= 1:
            raise ValueError(
                "calibration_sign_fraction_floor must lie in [0.5, 1]."
            )


@dataclass(frozen=True)
class PairGauge:
    """One equal-author, pair-symmetric robust diagonal D0 gauge."""

    center: np.ndarray
    scale: np.ndarray
    source_density: np.ndarray
    target_density: np.ndarray
    source_effective_rank: float
    target_effective_rank: float
    matched_authors: int


@dataclass(frozen=True)
class GlobalGauge:
    """One equal-corpus, equal-author D0 gauge shared by all corpora."""

    center: np.ndarray
    scale: np.ndarray
    densities: dict[str, np.ndarray]
    effective_ranks: dict[str, float]
    matched_authors: int


def _robust_standardizer(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fit a median/MAD diagonal metric with deterministic fallbacks."""
    pooled = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    center = np.median(pooled, axis=0)
    mad = 1.4826 * np.median(np.abs(pooled - center), axis=0)
    q25, q75 = np.quantile(pooled, (0.25, 0.75), axis=0)
    iqr = (q75 - q25) / 1.349
    standard = pooled.std(axis=0)
    scale = np.where(mad > 1e-8, mad, np.where(iqr > 1e-8, iqr, standard))
    return center, np.where(scale > 1e-8, scale, 1.0)


def _standardize(
    values: np.ndarray,
    center: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    return (np.asarray(values, dtype=float) - center[None, None, :]) / scale[
        None, None, :
    ]


def positive_density(matrix: np.ndarray) -> tuple[np.ndarray, float, int]:
    """Return trace-one PSD part, participation rank, and positive rank."""
    symmetric = 0.5 * (np.asarray(matrix, dtype=float) + np.asarray(matrix).T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    positive = np.clip(eigenvalues, 0.0, None)
    total = float(positive.sum())
    if total <= 1e-12:
        return np.zeros_like(symmetric), 0.0, 0
    probabilities = positive / total
    density = (eigenvectors * probabilities) @ eigenvectors.T
    participation = float(1.0 / max(float(np.sum(probabilities**2)), 1e-12))
    return density, participation, int(np.sum(probabilities > 1e-12))


def replicated_density(
    raw: np.ndarray,
    *,
    center: np.ndarray,
    scale: np.ndarray,
) -> tuple[np.ndarray, float, int]:
    """Estimate a positive cross-replicate density in a frozen gauge."""
    standardized = _standardize(raw, center, scale)
    return positive_density(
        replicated_covariance(standardized[:, 0], standardized[:, 1])
    )


def effective_rank(density: np.ndarray) -> float:
    """Return participation effective rank of a trace-one PSD density."""
    eigenvalues = np.clip(
        np.linalg.eigvalsh(0.5 * (density + density.T)),
        0.0,
        None,
    )
    total = float(eigenvalues.sum())
    if total <= 1e-12:
        return 0.0
    probabilities = eigenvalues / total
    return float(1.0 / max(float(np.sum(probabilities**2)), 1e-12))


def _stable_indices(
    author_ids: Iterable[str],
    count: int,
    *,
    salt: str,
) -> np.ndarray:
    ids = np.asarray(list(map(str, author_ids)), dtype=object)
    order = np.argsort(
        [
            stable_bucket(value, salt=salt, modulus=2**63 - 1)
            for value in ids
        ],
        kind="stable",
    )
    return order[: int(count)]


def _split_raw(
    panel: CorpusFeaturePanel,
    family: str,
    split: str,
) -> tuple[np.ndarray, np.ndarray]:
    mask = panel.metadata["split"].eq(split).to_numpy()
    return (
        panel.raw[family][mask],
        panel.metadata.loc[mask, "author_id"].astype(str).to_numpy(),
    )


def fit_pair_gauge(
    source_raw: np.ndarray,
    source_ids: Iterable[str],
    target_raw: np.ndarray,
    target_ids: Iterable[str],
    *,
    maximum_authors: int,
    salt: str,
) -> PairGauge:
    """Fit an equal-author pair metric without pooled whitening."""
    count = min(len(source_raw), len(target_raw), int(maximum_authors))
    if count < 2:
        raise ValueError("At least two D0 authors per corpus are required.")
    source = source_raw[
        _stable_indices(source_ids, count, salt=f"{salt}-source")
    ]
    target = target_raw[
        _stable_indices(target_ids, count, salt=f"{salt}-target")
    ]
    center, scale = _robust_standardizer(
        np.concatenate([source, target], axis=0)
    )
    source_density, source_rank, _ = replicated_density(
        source,
        center=center,
        scale=scale,
    )
    target_density, target_rank, _ = replicated_density(
        target,
        center=center,
        scale=scale,
    )
    return PairGauge(
        center=center,
        scale=scale,
        source_density=source_density,
        target_density=target_density,
        source_effective_rank=source_rank,
        target_effective_rank=target_rank,
        matched_authors=int(count),
    )


def fit_global_gauge(
    panels: Mapping[str, CorpusFeaturePanel],
    family: str,
    *,
    maximum_authors: int,
    salt: str,
) -> GlobalGauge:
    """Fit one three-corpus equal-author D0 sensitivity metric."""
    raw_by_corpus: dict[str, np.ndarray] = {}
    ids_by_corpus: dict[str, np.ndarray] = {}
    for corpus, panel in panels.items():
        raw_by_corpus[corpus], ids_by_corpus[corpus] = _split_raw(
            panel,
            family,
            "D0",
        )
    count = min(
        int(maximum_authors),
        *(len(values) for values in raw_by_corpus.values()),
    )
    selected = {
        corpus: raw_by_corpus[corpus][
            _stable_indices(
                ids_by_corpus[corpus],
                count,
                salt=f"{salt}-{corpus}",
            )
        ]
        for corpus in sorted(raw_by_corpus)
    }
    center, scale = _robust_standardizer(
        np.concatenate(list(selected.values()), axis=0)
    )
    densities = {}
    ranks = {}
    for corpus, values in selected.items():
        densities[corpus], ranks[corpus], _ = replicated_density(
            values,
            center=center,
            scale=scale,
        )
    return GlobalGauge(
        center=center,
        scale=scale,
        densities=densities,
        effective_ranks=ranks,
        matched_authors=int(count),
    )


def soft_capacity_filter(
    density: np.ndarray,
    capacity: int,
    tau: float,
) -> np.ndarray:
    """Solve the quadratically regularized trace-capacity filter."""
    matrix = 0.5 * (np.asarray(density, dtype=float) + np.asarray(density).T)
    dimension = matrix.shape[0]
    k = int(capacity)
    if matrix.ndim != 2 or matrix.shape[1] != dimension:
        raise ValueError("density must be square.")
    if not 0 < k < dimension:
        raise ValueError("capacity must lie strictly between 0 and dimension.")
    if tau <= 0:
        raise ValueError("tau must be positive.")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    baseline = k / dimension

    def weights(mu: float) -> np.ndarray:
        return np.clip(
            baseline + (eigenvalues - mu) / tau,
            0.0,
            1.0,
        )

    lower = float(eigenvalues.min() - tau)
    upper = float(eigenvalues.max() + tau)
    for _ in range(100):
        midpoint = 0.5 * (lower + upper)
        if float(weights(midpoint).sum()) > k:
            lower = midpoint
        else:
            upper = midpoint
    final = weights(0.5 * (lower + upper))
    if not np.isclose(float(final.sum()), k, atol=1e-8):
        raise ValueError("Soft filter failed its trace constraint.")
    return (eigenvectors * final) @ eigenvectors.T


def _spectral_scale(left: np.ndarray, right: np.ndarray) -> float:
    dimension = left.shape[0]
    isotropic = np.eye(dimension) / dimension
    value = np.sqrt(
        (
            np.linalg.norm(left - isotropic) ** 2
            + np.linalg.norm(right - isotropic) ** 2
        )
        / (2.0 * dimension)
    )
    return float(max(value, 1e-8))


def _filter_bank(
    source_density: np.ndarray,
    target_density: np.ndarray,
    *,
    capacities: tuple[int, ...],
    tau_multipliers: tuple[float, ...],
) -> list[dict[str, Any]]:
    dimension = source_density.shape[0]
    scale = _spectral_scale(source_density, target_density)
    bank = []
    for capacity in capacities:
        if capacity >= dimension:
            continue
        for multiplier in tau_multipliers:
            tau = float(multiplier * scale)
            bank.append(
                {
                    "capacity": int(capacity),
                    "tau_multiplier": float(multiplier),
                    "tau": tau,
                    "source_filter": soft_capacity_filter(
                        source_density,
                        capacity,
                        tau,
                    ),
                    "target_filter": soft_capacity_filter(
                        target_density,
                        capacity,
                        tau,
                    ),
                }
            )
    return bank


def _objective(
    support_filter: np.ndarray,
    target_density: np.ndarray,
    *,
    capacity: int,
    tau: float,
) -> float:
    dimension = support_filter.shape[0]
    isotropic = np.eye(dimension) * (capacity / dimension)
    return float(
        np.sum(support_filter.T * target_density)
        - 0.5 * tau * np.linalg.norm(support_filter - isotropic) ** 2
    )


def _coverage(
    bank: list[dict[str, Any]],
    source_confirmation: np.ndarray,
    target_confirmation: np.ndarray,
    *,
    denominator_floor: float,
    minimum_grid_fraction: float,
) -> tuple[float, float, list[dict[str, float]]]:
    """Return source-covers-target, reverse coverage, and grid rows."""
    rows = []
    forward_values = []
    reverse_values = []
    for cell in bank:
        capacity = int(cell["capacity"])
        tau = float(cell["tau"])
        baseline = capacity / source_confirmation.shape[0]
        target_native = (
            _objective(
                cell["target_filter"],
                target_confirmation,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        target_cross = (
            _objective(
                cell["source_filter"],
                target_confirmation,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        source_native = (
            _objective(
                cell["source_filter"],
                source_confirmation,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        source_cross = (
            _objective(
                cell["target_filter"],
                source_confirmation,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        forward = (
            float(target_cross / target_native)
            if target_native > denominator_floor
            else float("nan")
        )
        reverse = (
            float(source_cross / source_native)
            if source_native > denominator_floor
            else float("nan")
        )
        forward_values.append(forward)
        reverse_values.append(reverse)
        rows.append(
            {
                "capacity": capacity,
                "tau_multiplier": float(cell["tau_multiplier"]),
                "tau": tau,
                "isotropic_baseline": baseline,
                "target_native_excess": target_native,
                "target_cross_excess": target_cross,
                "source_native_excess": source_native,
                "source_cross_excess": source_cross,
                "forward_coverage": forward,
                "reverse_coverage": reverse,
            }
        )
    required = int(np.ceil(minimum_grid_fraction * len(bank)))
    finite_forward = np.asarray(forward_values, dtype=float)
    finite_reverse = np.asarray(reverse_values, dtype=float)
    finite_forward = finite_forward[np.isfinite(finite_forward)]
    finite_reverse = finite_reverse[np.isfinite(finite_reverse)]
    forward_area = (
        float(finite_forward.mean())
        if len(finite_forward) >= required
        else float("nan")
    )
    reverse_area = (
        float(finite_reverse.mean())
        if len(finite_reverse) >= required
        else float("nan")
    )
    return forward_area, reverse_area, rows


def _eigenvectors_descending(density: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (density + density.T))
    return vectors[:, np.argsort(values)[::-1]]


def _spectrum_descending(density: np.ndarray) -> np.ndarray:
    values = np.clip(
        np.linalg.eigvalsh(0.5 * (density + density.T)),
        0.0,
        None,
    )[::-1]
    return values / max(float(values.sum()), 1e-12)


def impose_spectrum(density: np.ndarray, spectrum: np.ndarray) -> np.ndarray:
    """Preserve density eigenvectors while replacing the complete spectrum."""
    vectors = _eigenvectors_descending(density)
    template = np.asarray(spectrum, dtype=float)
    template = template / max(float(template.sum()), 1e-12)
    return (vectors * template) @ vectors.T


def _spectrum_matched_objects(
    source_fit: np.ndarray,
    target_fit: np.ndarray,
    source_confirmation: np.ndarray,
    target_confirmation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    template = 0.5 * (
        _spectrum_descending(source_fit)
        + _spectrum_descending(target_fit)
    )
    template /= float(template.sum())
    return (
        impose_spectrum(source_fit, template),
        impose_spectrum(target_fit, template),
        impose_spectrum(source_confirmation, template),
        impose_spectrum(target_confirmation, template),
    )


def _hs_alignment(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return (
        float(np.trace(left @ right) / denominator)
        if denominator > 1e-12
        else 0.0
    )


def _rotation_p(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> tuple[float, float]:
    observed = _hs_alignment(reference, candidate)
    rng = np.random.default_rng(seed)
    null = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        rotation, _ = np.linalg.qr(
            rng.normal(size=(candidate.shape[0], candidate.shape[0]))
        )
        null[draw] = _hs_alignment(
            reference,
            rotation @ candidate @ rotation.T,
        )
    p_value = float((1 + np.sum(null >= observed)) / (len(null) + 1))
    return observed, p_value


def _internal_reliability(
    raw: np.ndarray,
    ids: np.ndarray,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    draws: int,
    seed: int,
) -> tuple[float, float]:
    order = _stable_indices(ids, len(ids), salt=f"internal-{seed}")
    midpoint = len(order) // 2
    first, _, _ = replicated_density(
        raw[order[:midpoint]],
        center=center,
        scale=scale,
    )
    second, _, _ = replicated_density(
        raw[order[midpoint:]],
        center=center,
        scale=scale,
    )
    return _rotation_p(first, second, draws=draws, seed=seed)


def _finite_interval(values: list[float], low: float, high: float) -> tuple[float, float]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) < 10:
        return float("nan"), float("nan")
    return tuple(np.quantile(finite, (low, high)).astype(float))


def _coverage_for_gauge(
    source_fit: np.ndarray,
    target_fit: np.ndarray,
    source_confirmation: np.ndarray,
    target_confirmation: np.ndarray,
    *,
    spec: SupportContainmentSpec,
) -> dict[str, Any]:
    bank = _filter_bank(
        source_fit,
        target_fit,
        capacities=spec.capacities,
        tau_multipliers=spec.tau_multipliers,
    )
    forward, reverse, curve = _coverage(
        bank,
        source_confirmation,
        target_confirmation,
        denominator_floor=spec.denominator_floor,
        minimum_grid_fraction=spec.minimum_grid_fraction,
    )
    matched = _spectrum_matched_objects(
        source_fit,
        target_fit,
        source_confirmation,
        target_confirmation,
    )
    matched_bank = _filter_bank(
        matched[0],
        matched[1],
        capacities=spec.capacities,
        tau_multipliers=spec.tau_multipliers,
    )
    spectrum_forward, spectrum_reverse, spectrum_curve = _coverage(
        matched_bank,
        matched[2],
        matched[3],
        denominator_floor=spec.denominator_floor,
        minimum_grid_fraction=spec.minimum_grid_fraction,
    )
    return {
        "forward": forward,
        "reverse": reverse,
        "asymmetry": forward - reverse,
        "spectrum_forward": spectrum_forward,
        "spectrum_reverse": spectrum_reverse,
        "spectrum_asymmetry": spectrum_forward - spectrum_reverse,
        "curve": curve,
        "spectrum_curve": spectrum_curve,
    }


def _cross_objective_rotation_p(
    bank: list[dict[str, Any]],
    target_confirmation: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> tuple[float, float]:
    def statistic(candidate: np.ndarray) -> float:
        values = []
        for cell in bank:
            capacity = int(cell["capacity"])
            baseline = capacity / candidate.shape[0]
            values.append(
                _objective(
                    cell["source_filter"],
                    candidate,
                    capacity=capacity,
                    tau=float(cell["tau"]),
                )
                - baseline
            )
        return float(np.mean(values))

    observed = statistic(target_confirmation)
    rng = np.random.default_rng(seed)
    null = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        rotation, _ = np.linalg.qr(
            rng.normal(
                size=(
                    target_confirmation.shape[0],
                    target_confirmation.shape[0],
                )
            )
        )
        null[draw] = statistic(
            rotation @ target_confirmation @ rotation.T
        )
    return observed, float((1 + np.sum(null >= observed)) / (len(null) + 1))


def evaluate_pair(
    source_name: str,
    source_panel: CorpusFeaturePanel,
    target_name: str,
    target_panel: CorpusFeaturePanel,
    family: str,
    *,
    global_gauge: GlobalGauge,
    spec: SupportContainmentSpec,
) -> dict[str, list[dict[str, Any]]]:
    """Evaluate one unordered corpus pair and one feature family."""
    source_d0_raw, source_d0_ids = _split_raw(source_panel, family, "D0")
    target_d0_raw, target_d0_ids = _split_raw(target_panel, family, "D0")
    gauge = fit_pair_gauge(
        source_d0_raw,
        source_d0_ids,
        target_d0_raw,
        target_d0_ids,
        maximum_authors=spec.maximum_calibration_authors,
        salt=f"v8-coverage-{source_name}-{target_name}-{family}-{spec.seed}",
    )
    source_internal, source_internal_p = _internal_reliability(
        source_d0_raw,
        source_d0_ids,
        center=gauge.center,
        scale=gauge.scale,
        draws=spec.rotation_draws,
        seed=spec.seed
        + stable_bucket(source_name, salt=f"internal-{family}", modulus=100_000),
    )
    target_internal, target_internal_p = _internal_reliability(
        target_d0_raw,
        target_d0_ids,
        center=gauge.center,
        scale=gauge.scale,
        draws=spec.rotation_draws,
        seed=spec.seed
        + stable_bucket(target_name, salt=f"internal-{family}", modulus=100_000),
    )
    pair_bank = _filter_bank(
        gauge.source_density,
        gauge.target_density,
        capacities=spec.capacities,
        tau_multipliers=spec.tau_multipliers,
    )
    rows: list[dict[str, Any]] = []
    curves: list[dict[str, Any]] = []
    rng = np.random.default_rng(
        spec.seed
        + stable_bucket(
            f"{source_name}-{target_name}-{family}",
            salt="v8-coverage-bootstrap",
            modulus=2**31 - 1,
        )
    )
    for split in ("D1", "D2"):
        source_raw, source_ids = _split_raw(source_panel, family, split)
        target_raw, target_ids = _split_raw(target_panel, family, split)
        count = min(
            len(source_raw),
            len(target_raw),
            spec.maximum_confirmation_authors,
        )
        if count < spec.minimum_authors:
            rows.append(
                {
                    "source": source_name,
                    "target": target_name,
                    "family": family,
                    "split": split,
                    "status": "COVERAGE_UNDERRESOLVED",
                    "matched_authors": int(count),
                }
            )
            continue
        source_primary = source_raw[
            _stable_indices(
                source_ids,
                count,
                salt=f"primary-{source_name}-{target_name}-{family}-{split}",
            )
        ]
        target_primary = target_raw[
            _stable_indices(
                target_ids,
                count,
                salt=f"primary-{target_name}-{source_name}-{family}-{split}",
            )
        ]
        source_density, source_rank, _ = replicated_density(
            source_primary,
            center=gauge.center,
            scale=gauge.scale,
        )
        target_density, target_rank, _ = replicated_density(
            target_primary,
            center=gauge.center,
            scale=gauge.scale,
        )
        primary = _coverage_for_gauge(
            gauge.source_density,
            gauge.target_density,
            source_density,
            target_density,
            spec=spec,
        )
        global_source_density, _, _ = replicated_density(
            source_primary,
            center=global_gauge.center,
            scale=global_gauge.scale,
        )
        global_target_density, _, _ = replicated_density(
            target_primary,
            center=global_gauge.center,
            scale=global_gauge.scale,
        )
        global_result = _coverage_for_gauge(
            global_gauge.densities[source_name],
            global_gauge.densities[target_name],
            global_source_density,
            global_target_density,
            spec=spec,
        )

        d0_asymmetry = []
        d0_spectrum_asymmetry = []
        sensitivity_count = max(
            spec.minimum_authors,
            int(np.floor(0.8 * gauge.matched_authors)),
        )
        sensitivity_count = min(
            sensitivity_count,
            len(source_d0_raw),
            len(target_d0_raw),
        )
        for draw in range(spec.calibration_subsamples):
            sensitivity = fit_pair_gauge(
                source_d0_raw,
                source_d0_ids,
                target_d0_raw,
                target_d0_ids,
                maximum_authors=sensitivity_count,
                salt=(
                    f"d0-sensitivity-{source_name}-{target_name}-{family}-"
                    f"{split}-{draw}-{spec.seed}"
                ),
            )
            source_sensitivity, _, _ = replicated_density(
                source_primary,
                center=sensitivity.center,
                scale=sensitivity.scale,
            )
            target_sensitivity, _, _ = replicated_density(
                target_primary,
                center=sensitivity.center,
                scale=sensitivity.scale,
            )
            result = _coverage_for_gauge(
                sensitivity.source_density,
                sensitivity.target_density,
                source_sensitivity,
                target_sensitivity,
                spec=spec,
            )
            d0_asymmetry.append(result["asymmetry"])
            d0_spectrum_asymmetry.append(result["spectrum_asymmetry"])

        bootstrap: dict[str, list[float]] = {
            key: []
            for key in (
                "forward",
                "reverse",
                "asymmetry",
                "spectrum_forward",
                "spectrum_reverse",
                "spectrum_asymmetry",
                "global_forward",
                "global_reverse",
                "global_asymmetry",
                "global_spectrum_forward",
                "global_spectrum_reverse",
                "global_spectrum_asymmetry",
            )
        }
        for _ in range(spec.bootstrap_draws):
            source_draw = source_raw[rng.integers(0, len(source_raw), size=count)]
            target_draw = target_raw[rng.integers(0, len(target_raw), size=count)]
            source_draw_density, _, _ = replicated_density(
                source_draw,
                center=gauge.center,
                scale=gauge.scale,
            )
            target_draw_density, _, _ = replicated_density(
                target_draw,
                center=gauge.center,
                scale=gauge.scale,
            )
            pair_draw = _coverage_for_gauge(
                gauge.source_density,
                gauge.target_density,
                source_draw_density,
                target_draw_density,
                spec=spec,
            )
            for key in (
                "forward",
                "reverse",
                "asymmetry",
                "spectrum_forward",
                "spectrum_reverse",
                "spectrum_asymmetry",
            ):
                bootstrap[key].append(float(pair_draw[key]))
            global_source_draw, _, _ = replicated_density(
                source_draw,
                center=global_gauge.center,
                scale=global_gauge.scale,
            )
            global_target_draw, _, _ = replicated_density(
                target_draw,
                center=global_gauge.center,
                scale=global_gauge.scale,
            )
            global_draw = _coverage_for_gauge(
                global_gauge.densities[source_name],
                global_gauge.densities[target_name],
                global_source_draw,
                global_target_draw,
                spec=spec,
            )
            for key in (
                "forward",
                "reverse",
                "asymmetry",
                "spectrum_forward",
                "spectrum_reverse",
                "spectrum_asymmetry",
            ):
                bootstrap[f"global_{key}"].append(float(global_draw[key]))

        intervals = {
            key: _finite_interval(values, 0.025, 0.975)
            for key, values in bootstrap.items()
        }
        d0_interval = _finite_interval(d0_asymmetry, 0.05, 0.95)
        d0_spectrum_interval = _finite_interval(
            d0_spectrum_asymmetry,
            0.05,
            0.95,
        )
        raw_sign = np.sign(primary["asymmetry"])
        spectrum_sign = np.sign(primary["spectrum_asymmetry"])
        d0_sign_fraction = float(
            np.mean(np.sign(d0_asymmetry) == raw_sign)
        ) if raw_sign else 0.0
        d0_spectrum_sign_fraction = float(
            np.mean(np.sign(d0_spectrum_asymmetry) == spectrum_sign)
        ) if spectrum_sign else 0.0
        forward_excess, forward_rotation_p = _cross_objective_rotation_p(
            pair_bank,
            target_density,
            draws=spec.rotation_draws,
            seed=spec.seed
            + stable_bucket(
                f"{source_name}-{target_name}-{family}-{split}",
                salt="coverage-rotation",
                modulus=2**31 - 1,
            ),
        )
        reverse_bank = [
            {
                **cell,
                "source_filter": cell["target_filter"],
                "target_filter": cell["source_filter"],
            }
            for cell in pair_bank
        ]
        reverse_excess, reverse_rotation_p = _cross_objective_rotation_p(
            reverse_bank,
            source_density,
            draws=spec.rotation_draws,
            seed=spec.seed
            + stable_bucket(
                f"{target_name}-{source_name}-{family}-{split}",
                salt="coverage-rotation",
                modulus=2**31 - 1,
            ),
        )
        status = (
            "COVERAGE_ESTIMATED"
            if np.isfinite(
                [
                    primary["forward"],
                    primary["reverse"],
                    primary["spectrum_forward"],
                    primary["spectrum_reverse"],
                    global_result["forward"],
                    global_result["reverse"],
                    global_result["spectrum_forward"],
                    global_result["spectrum_reverse"],
                ]
            ).all()
            else "NATIVE_SUPPORT_UNDERRESOLVED"
        )
        row: dict[str, Any] = {
            "source": source_name,
            "target": target_name,
            "family": family,
            "split": split,
            "status": status,
            "feature_dimension": int(gauge.center.size),
            "matched_d0_authors": int(gauge.matched_authors),
            "matched_global_d0_authors": int(global_gauge.matched_authors),
            "matched_authors": int(count),
            "source_d0_effective_rank": gauge.source_effective_rank,
            "target_d0_effective_rank": gauge.target_effective_rank,
            "source_confirmation_effective_rank": source_rank,
            "target_confirmation_effective_rank": target_rank,
            "source_internal_hs": source_internal,
            "source_internal_p": source_internal_p,
            "target_internal_hs": target_internal,
            "target_internal_p": target_internal_p,
            "forward_area": primary["forward"],
            "reverse_area": primary["reverse"],
            "asymmetry": primary["asymmetry"],
            "spectrum_matched_forward_area": primary["spectrum_forward"],
            "spectrum_matched_reverse_area": primary["spectrum_reverse"],
            "spectrum_matched_asymmetry": primary["spectrum_asymmetry"],
            "global_forward_area": global_result["forward"],
            "global_reverse_area": global_result["reverse"],
            "global_asymmetry": global_result["asymmetry"],
            "global_spectrum_matched_forward_area": global_result[
                "spectrum_forward"
            ],
            "global_spectrum_matched_reverse_area": global_result[
                "spectrum_reverse"
            ],
            "global_spectrum_matched_asymmetry": global_result[
                "spectrum_asymmetry"
            ],
            "d0_sensitivity_authors": int(sensitivity_count),
            "d0_asymmetry_q05": d0_interval[0],
            "d0_asymmetry_q95": d0_interval[1],
            "d0_asymmetry_sign_fraction": d0_sign_fraction,
            "d0_spectrum_asymmetry_q05": d0_spectrum_interval[0],
            "d0_spectrum_asymmetry_q95": d0_spectrum_interval[1],
            "d0_spectrum_sign_fraction": d0_spectrum_sign_fraction,
            "forward_cross_objective_excess": forward_excess,
            "forward_rotation_p": forward_rotation_p,
            "reverse_cross_objective_excess": reverse_excess,
            "reverse_rotation_p": reverse_rotation_p,
        }
        for key, interval in intervals.items():
            row[f"{key}_ci_low"] = interval[0]
            row[f"{key}_ci_high"] = interval[1]
        rows.append(row)
        for arm, curve in (
            ("pair", primary["curve"]),
            ("pair_full_spectrum_matched", primary["spectrum_curve"]),
            ("global", global_result["curve"]),
            ("global_full_spectrum_matched", global_result["spectrum_curve"]),
        ):
            for cell in curve:
                curves.append(
                    {
                        "source": source_name,
                        "target": target_name,
                        "family": family,
                        "split": split,
                        "arm": arm,
                        **cell,
                    }
                )
    return {"summary": rows, "curves": curves}


def classify_pair(
    rows: pd.DataFrame,
    *,
    spec: SupportContainmentSpec,
) -> dict[str, Any]:
    """Classify a pair/family only under D1/D2 and control agreement."""
    if len(rows) != 2 or set(rows["split"]) != {"D1", "D2"}:
        return {"decision": "COVERAGE_UNDERRESOLVED", "direction": ""}
    if not rows["status"].eq("COVERAGE_ESTIMATED").all():
        return {"decision": "COVERAGE_UNDERRESOLVED", "direction": ""}
    if not (
        (rows["source_internal_p"] <= 0.05).all()
        and (rows["target_internal_p"] <= 0.05).all()
    ):
        return {"decision": "D0_SUPPORT_NOT_REPLICATED", "direction": ""}

    forward = bool(
        (rows["asymmetry_ci_low"] > 0).all()
        and (rows["spectrum_asymmetry_ci_low"] > 0).all()
        and (rows["global_asymmetry_ci_low"] > 0).all()
        and (rows["global_spectrum_asymmetry_ci_low"] > 0).all()
        and (
            rows["d0_asymmetry_sign_fraction"]
            >= spec.calibration_sign_fraction_floor
        ).all()
        and (
            rows["d0_spectrum_sign_fraction"]
            >= spec.calibration_sign_fraction_floor
        ).all()
        and (rows["forward_rotation_q"] <= 0.05).all()
    )
    reverse = bool(
        (rows["asymmetry_ci_high"] < 0).all()
        and (rows["spectrum_asymmetry_ci_high"] < 0).all()
        and (rows["global_asymmetry_ci_high"] < 0).all()
        and (rows["global_spectrum_asymmetry_ci_high"] < 0).all()
        and (
            rows["d0_asymmetry_sign_fraction"]
            >= spec.calibration_sign_fraction_floor
        ).all()
        and (
            rows["d0_spectrum_sign_fraction"]
            >= spec.calibration_sign_fraction_floor
        ).all()
        and (rows["reverse_rotation_q"] <= 0.05).all()
    )
    if forward:
        direction = f"{rows.iloc[0]['source']}->{rows.iloc[0]['target']}"
        chosen_low = rows["forward_ci_low"]
        rejected_high = rows["reverse_ci_high"]
    elif reverse:
        direction = f"{rows.iloc[0]['target']}->{rows.iloc[0]['source']}"
        chosen_low = rows["reverse_ci_low"]
        rejected_high = rows["forward_ci_high"]
    else:
        direction = ""
        chosen_low = pd.Series(dtype=float)
        rejected_high = pd.Series(dtype=float)
    if (
        direction
        and (chosen_low >= spec.approximate_containment_floor).all()
        and (rejected_high < spec.approximate_containment_floor).all()
    ):
        decision = "APPROXIMATE_DIRECTIONAL_COVERAGE_CANDIDATE"
    elif direction:
        decision = "DIRECTIONAL_COVERAGE_ASYMMETRY"
    elif (
        (rows["forward_rotation_q"] <= 0.05).all()
        and (rows["reverse_rotation_q"] <= 0.05).all()
    ):
        decision = "SHARED_ORIENTATION_NO_DIRECTION"
    else:
        decision = "COVERAGE_UNRESOLVED"
    return {
        "decision": decision,
        "direction": direction,
        "d1_asymmetry": float(
            rows.loc[rows["split"].eq("D1"), "asymmetry"].iloc[0]
        ),
        "d2_asymmetry": float(
            rows.loc[rows["split"].eq("D2"), "asymmetry"].iloc[0]
        ),
        "full_spectrum_control_pass": int(
            (
                np.sign(rows["asymmetry"])
                == np.sign(rows["spectrum_matched_asymmetry"])
            ).all()
        ),
        "global_metric_sign_pass": int(
            (
                np.sign(rows["asymmetry"])
                == np.sign(rows["global_asymmetry"])
            ).all()
        ),
    }
