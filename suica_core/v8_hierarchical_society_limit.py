"""Hierarchical society-limit identities for SUICA V3.7H.4D-R2G.2.

This module contains synthetic Hilbert-space experiments only. It tests when
cross-view residual energy separates into society-, group-, and author-level
terms, and when dependence or leakage invalidates that simple separation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from scipy.optimize import least_squares


WORLDS = (
    "pure_iid",
    "author_iid",
    "group_iid",
    "society_completable",
    "group_ar1",
    "correlated_hierarchy",
    "unavailable_society_shock",
    "local_to_unity",
    "correlated_view_noise",
)


@dataclass(frozen=True)
class HierarchicalSocietySpec:
    """Dimensions and planted cross-view energies for one society panel."""

    societies: int = 96
    max_groups: int = 32
    max_authors: int = 64
    dimensions: int = 6
    society_energy: float = 0.06
    group_energy: float = 0.06
    author_energy: float = 0.08
    technical_energy: float = 0.06
    private_noise_energy: float = 0.25
    score_noise_energy: float = 0.50
    score_opportunities: int = 64
    raw_society_loading: float = 0.65
    raw_group_loading: float = 0.55
    local_to_unity_c: float = 2.0
    student_df: float = 5.0


def _standard_noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "student_t5":
        if student_df <= 2.0:
            raise ValueError("student_df must exceed two")
        return (
            rng.standard_t(student_df, size=shape)
            / np.sqrt(student_df / (student_df - 2.0))
        )
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def ar1_group_weight(groups: int, rho: float) -> float:
    """Return variance weight of a stationary AR(1) group mean."""
    count = int(groups)
    if count < 1:
        raise ValueError("groups must be positive")
    if not -1.0 < float(rho) < 1.0:
        raise ValueError("rho must lie in (-1, 1)")
    lags = np.arange(1, count, dtype=float)
    numerator = float(count)
    if len(lags):
        numerator += float(
            2.0
            * np.sum(
                (float(count) - lags)
                * np.power(float(rho), lags)
            )
        )
    return numerator / float(count**2)


def local_to_unity_group_weight(groups: int, c: float) -> float:
    """Return the triangular-array group weight for rho_G = 1 - c/G."""
    count = int(groups)
    if count < 1:
        raise ValueError("groups must be positive")
    rho = 1.0 - float(c) / float(count)
    if rho <= -1.0:
        raise ValueError("c is too large for the requested group count")
    if rho >= 1.0:
        raise ValueError("c must be positive")
    return ar1_group_weight(count, rho)


def local_to_unity_limit(c: float) -> float:
    """Return the positive limiting group-mean energy weight."""
    value = float(c)
    if value <= 0.0:
        raise ValueError("c must be positive")
    return float(
        2.0 * (value - 1.0 + np.exp(-value)) / (value**2)
    )


def _stationary_ar1(
    rng: np.random.Generator,
    shape: tuple[int, int, int],
    *,
    rho: float,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    societies, groups, dimensions = map(int, shape)
    values = np.empty((societies, groups, dimensions), dtype=float)
    values[:, 0, :] = _standard_noise(
        rng,
        (societies, dimensions),
        noise_mode=noise_mode,
        student_df=student_df,
    )
    innovation_scale = np.sqrt(max(1.0 - float(rho) ** 2, 0.0))
    for index in range(1, groups):
        innovation = _standard_noise(
            rng,
            (societies, dimensions),
            noise_mode=noise_mode,
            student_df=student_df,
        )
        values[:, index, :] = (
            float(rho) * values[:, index - 1, :]
            + innovation_scale * innovation
        )
    return values


def correlated_hierarchy_truth(
    spec: HierarchicalSocietySpec,
) -> dict[str, float]:
    """Return raw and martingale coefficient accounting for W4."""
    r_sg = float(spec.raw_society_loading)
    r_ga = float(spec.raw_group_loading)
    e_s = float(spec.society_energy)
    e_g = float(spec.group_energy)
    e_a = float(spec.author_energy)
    raw_group_energy = r_sg**2 * e_s + e_g
    raw_author_energy = r_ga**2 * raw_group_energy + e_a
    naive_sum = e_s + raw_group_energy + raw_author_energy
    effective_society = (1.0 + r_sg * (1.0 + r_ga)) ** 2 * e_s
    effective_group = (1.0 + r_ga) ** 2 * e_g
    effective_author = e_a
    return {
        "raw_naive_energy_sum": float(naive_sum),
        "martingale_society": float(effective_society),
        "martingale_group": float(effective_group),
        "martingale_author": float(effective_author),
        "raw_society_group_covariance": float(r_sg * e_s),
        "raw_society_author_covariance": float(r_ga * r_sg * e_s),
        "raw_group_author_covariance": float(
            r_ga * raw_group_energy
        ),
    }


def simulate_hierarchical_panel(
    *,
    seed: int,
    world: str,
    spec: HierarchicalSocietySpec,
    noise_mode: str,
    group_rho: float = 0.0,
) -> dict[str, Any]:
    """Generate two independent views and the registered oracle components."""
    if world not in WORLDS or world == "local_to_unity":
        raise ValueError(f"unsupported fixed-panel world: {world}")
    streams = np.random.SeedSequence(int(seed)).spawn(9)
    rngs = [np.random.default_rng(stream) for stream in streams]
    s = int(spec.societies)
    g = int(spec.max_groups)
    n = int(spec.max_authors)
    d = int(spec.dimensions)

    society_base = _standard_noise(
        rngs[0],
        (s, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    group_base = _standard_noise(
        rngs[1],
        (s, g, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    author_base = _standard_noise(
        rngs[2],
        (s, g, n, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )

    society = np.zeros((s, d), dtype=float)
    group = np.zeros((s, g, d), dtype=float)
    author = np.zeros((s, g, n, d), dtype=float)
    raw_components: dict[str, np.ndarray] = {}
    martingale_components: dict[str, np.ndarray] = {}
    technical = np.zeros((s, d), dtype=float)
    score_visible = False

    if world == "author_iid":
        author = np.sqrt(float(spec.author_energy)) * author_base
    elif world == "group_iid":
        group = np.sqrt(float(spec.group_energy)) * group_base
        author = np.sqrt(float(spec.author_energy)) * author_base
    elif world == "society_completable":
        society = np.sqrt(float(spec.society_energy)) * society_base
        score_visible = True
    elif world == "group_ar1":
        group = np.sqrt(float(spec.group_energy)) * _stationary_ar1(
            rngs[1],
            (s, g, d),
            rho=float(group_rho),
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        author = np.sqrt(float(spec.author_energy)) * author_base
    elif world == "correlated_hierarchy":
        independent_society = (
            np.sqrt(float(spec.society_energy)) * society_base
        )
        independent_group = (
            np.sqrt(float(spec.group_energy)) * group_base
        )
        independent_author = (
            np.sqrt(float(spec.author_energy)) * author_base
        )
        raw_society = independent_society
        raw_group = (
            float(spec.raw_society_loading)
            * independent_society[:, None, :]
            + independent_group
        )
        raw_author = (
            float(spec.raw_group_loading) * raw_group[:, :, None, :]
            + independent_author
        )
        society = (
            1.0
            + float(spec.raw_society_loading)
            * (1.0 + float(spec.raw_group_loading))
        ) * independent_society
        group = (
            1.0 + float(spec.raw_group_loading)
        ) * independent_group
        author = independent_author
        raw_components = {
            "society": raw_society,
            "group": raw_group,
            "author": raw_author,
        }
        martingale_components = {
            "society": society,
            "group": group,
            "author": author,
        }
    elif world == "unavailable_society_shock":
        society = np.sqrt(float(spec.society_energy)) * society_base
    elif world == "correlated_view_noise":
        technical = (
            np.sqrt(float(spec.technical_energy)) * society_base
        )

    stable = (
        society[:, None, None, :]
        + group[:, :, None, :]
        + author
    )
    technical_full = np.broadcast_to(
        technical[:, None, None, :],
        stable.shape,
    )
    private_scale = np.sqrt(float(spec.private_noise_energy))
    private_a = private_scale * _standard_noise(
        rngs[3],
        stable.shape,
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    private_b = private_scale * _standard_noise(
        rngs[4],
        stable.shape,
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    target_a = stable + technical_full + private_a
    target_b = stable + technical_full + private_b

    admissible_a = np.zeros_like(target_a)
    admissible_b = np.zeros_like(target_b)
    if score_visible:
        count = int(spec.score_opportunities)
        if count < 1:
            raise ValueError("score_opportunities must be positive")
        score_sd = np.sqrt(float(spec.score_noise_energy) / count)
        score_a = society + score_sd * _standard_noise(
            rngs[5],
            society.shape,
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        score_b = society + score_sd * _standard_noise(
            rngs[6],
            society.shape,
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        admissible_a = np.broadcast_to(
            score_a[:, None, None, :],
            target_a.shape,
        ).copy()
        admissible_b = np.broadcast_to(
            score_b[:, None, None, :],
            target_b.shape,
        ).copy()

    return {
        "target_a": target_a,
        "target_b": target_b,
        "admissible_prediction_a": admissible_a,
        "admissible_prediction_b": admissible_b,
        "stable_component": stable,
        "technical_component": technical_full,
        "raw_components": raw_components,
        "martingale_components": martingale_components,
        "group_rho": float(group_rho),
    }


def residual_arms(
    panel: dict[str, Any],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Build raw, admissible, structural-oracle, and full-oracle residuals."""
    target_a = np.asarray(panel["target_a"], dtype=float)
    target_b = np.asarray(panel["target_b"], dtype=float)
    stable = np.asarray(panel["stable_component"], dtype=float)
    technical = np.asarray(panel["technical_component"], dtype=float)
    return {
        "raw": (target_a, target_b),
        "admissible": (
            target_a
            - np.asarray(panel["admissible_prediction_a"], dtype=float),
            target_b
            - np.asarray(panel["admissible_prediction_b"], dtype=float),
        ),
        "structural_oracle": (
            target_a - stable,
            target_b - stable,
        ),
        "omniscient_oracle": (
            target_a - stable - technical,
            target_b - stable - technical,
        ),
    }


def cross_view_surface(
    left: np.ndarray,
    right: np.ndarray,
    *,
    group_sizes: Iterable[int],
    author_sizes: Iterable[int],
) -> list[dict[str, Any]]:
    """Measure cross-view energy of nested society means."""
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.shape != b.shape or a.ndim != 4:
        raise ValueError(
            "views must share societies x groups x authors x dimensions"
        )
    rows: list[dict[str, Any]] = []
    for groups in map(int, group_sizes):
        if groups < 1 or groups > a.shape[1]:
            raise ValueError("group prefix exceeds panel")
        for authors in map(int, author_sizes):
            if authors < 1 or authors > a.shape[2]:
                raise ValueError("author prefix exceeds panel")
            mean_a = a[:, :groups, :authors, :].mean(axis=(1, 2))
            mean_b = b[:, :groups, :authors, :].mean(axis=(1, 2))
            per_society_cross = np.mean(mean_a * mean_b, axis=1)
            per_society_self = 0.5 * np.mean(
                mean_a**2 + mean_b**2,
                axis=1,
            )
            rows.append({
                "groups": groups,
                "authors": authors,
                "cross_energy": float(per_society_cross.mean()),
                "self_energy": float(per_society_self.mean()),
                "cross_se": float(
                    per_society_cross.std(ddof=1)
                    / np.sqrt(len(per_society_cross))
                ),
                "self_se": float(
                    per_society_self.std(ddof=1)
                    / np.sqrt(len(per_society_self))
                ),
            })
    return rows


def expected_surface_coefficients(
    world: str,
    spec: HierarchicalSocietySpec,
) -> dict[str, float]:
    """Return independent-level coefficients for worlds where they exist."""
    if world == "correlated_hierarchy":
        truth = correlated_hierarchy_truth(spec)
        return {
            "society": truth["martingale_society"],
            "group": truth["martingale_group"],
            "author": truth["martingale_author"],
        }
    society = 0.0
    group = 0.0
    author = 0.0
    if world == "author_iid":
        author = float(spec.author_energy)
    elif world == "group_iid":
        group = float(spec.group_energy)
        author = float(spec.author_energy)
    elif world in {
        "society_completable",
        "unavailable_society_shock",
    }:
        society = float(spec.society_energy)
    elif world == "correlated_view_noise":
        society = float(spec.technical_energy)
    return {
        "society": society,
        "group": group,
        "author": author,
    }


def expected_cross_energy(
    *,
    world: str,
    spec: HierarchicalSocietySpec,
    groups: int,
    authors: int,
    group_rho: float = 0.0,
) -> float:
    """Return the registered finite-design cross-view expectation."""
    coefficients = expected_surface_coefficients(world, spec)
    if world == "group_ar1":
        return float(
            coefficients["society"]
            + float(spec.group_energy)
            * ar1_group_weight(groups, group_rho)
            + float(spec.author_energy) / (groups * authors)
        )
    return float(
        coefficients["society"]
        + coefficients["group"] / groups
        + coefficients["author"] / (groups * authors)
    )


def _checkerboard_mask(
    groups: np.ndarray,
    authors: np.ndarray,
) -> np.ndarray:
    return (
        np.rint(np.log2(groups)).astype(int)
        + np.rint(np.log2(authors)).astype(int)
    ) % 2 == 0


def _fit_linear_design(
    design: np.ndarray,
    outcome: np.ndarray,
) -> np.ndarray:
    return np.linalg.lstsq(design, outcome, rcond=None)[0]


def _error_metrics(
    truth: np.ndarray,
    prediction: np.ndarray,
) -> dict[str, float]:
    residual = np.asarray(truth) - np.asarray(prediction)
    scale = max(float(np.max(np.abs(truth))), 0.01)
    return {
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "nrmse": float(np.sqrt(np.mean(residual**2)) / scale),
        "max_abs_error": float(np.max(np.abs(residual))),
        "normalized_max_error": float(
            np.max(np.abs(residual)) / scale
        ),
    }


def fit_independent_surface(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Fit b_S + b_G/G + b_A/(G*n) with checkerboard validation."""
    groups = np.asarray([row["groups"] for row in rows], dtype=float)
    authors = np.asarray([row["authors"] for row in rows], dtype=float)
    outcome = np.asarray(
        [row["cross_energy"] for row in rows],
        dtype=float,
    )
    design = np.column_stack([
        np.ones(len(rows)),
        1.0 / groups,
        1.0 / (groups * authors),
    ])
    train = _checkerboard_mask(groups, authors)
    coefficient = _fit_linear_design(design[train], outcome[train])
    prediction = design @ coefficient
    full_coefficient = _fit_linear_design(design, outcome)
    return {
        "model": "independent_hierarchy",
        "society": float(full_coefficient[0]),
        "group": float(full_coefficient[1]),
        "author": float(full_coefficient[2]),
        "checkerboard_society": float(coefficient[0]),
        "checkerboard_group": float(coefficient[1]),
        "checkerboard_author": float(coefficient[2]),
        "train": _error_metrics(
            outcome[train],
            prediction[train],
        ),
        "test": _error_metrics(
            outcome[~train],
            prediction[~train],
        ),
    }


def fit_ar1_surface(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Fit b_S + b_G*q_G(rho) + b_A/(G*n)."""
    groups = np.asarray([row["groups"] for row in rows], dtype=int)
    authors = np.asarray([row["authors"] for row in rows], dtype=float)
    outcome = np.asarray(
        [row["cross_energy"] for row in rows],
        dtype=float,
    )
    train = _checkerboard_mask(groups.astype(float), authors)

    def predict(parameters: np.ndarray) -> np.ndarray:
        b_s, b_g, b_a, rho = parameters
        weights = np.asarray(
            [ar1_group_weight(int(value), float(rho)) for value in groups],
            dtype=float,
        )
        return b_s + b_g * weights + b_a / (groups * authors)

    best = None
    for rho_start in (-0.5, 0.0, 0.5, 0.8, 0.95):
        candidate = least_squares(
            lambda value: (
                predict(value)[train] - outcome[train]
            ),
            x0=np.asarray([0.0, 0.05, 0.05, rho_start]),
            bounds=(
                np.asarray([-1.0, -1.0, -1.0, -0.98]),
                np.asarray([1.0, 1.0, 1.0, 0.98]),
            ),
            max_nfev=10_000,
        )
        loss = float(np.sum(candidate.fun**2))
        if best is None or loss < best[0]:
            best = (loss, candidate.x)
    assert best is not None
    parameters = best[1]
    prediction = predict(parameters)
    return {
        "model": "ar1_hierarchy",
        "society": float(parameters[0]),
        "group": float(parameters[1]),
        "author": float(parameters[2]),
        "rho": float(parameters[3]),
        "train": _error_metrics(outcome[train], prediction[train]),
        "test": _error_metrics(outcome[~train], prediction[~train]),
    }


def hierarchy_cross_level_covariances(
    components: dict[str, np.ndarray],
) -> dict[str, float]:
    """Measure pairwise cross-level inner products in their native support."""
    if not components:
        return {}
    society = np.asarray(components["society"], dtype=float)
    group = np.asarray(components["group"], dtype=float)
    author = np.asarray(components["author"], dtype=float)
    society_group = float(
        np.mean(society[:, None, :] * group)
    )
    society_author = float(
        np.mean(society[:, None, None, :] * author)
    )
    group_author = float(
        np.mean(group[:, :, None, :] * author)
    )
    return {
        "society_group": society_group,
        "society_author": society_author,
        "group_author": group_author,
        "maximum_absolute": float(
            max(
                abs(society_group),
                abs(society_author),
                abs(group_author),
            )
        ),
    }


def test_centered_full_mean_energy(
    left: np.ndarray,
    right: np.ndarray,
) -> dict[str, float]:
    """Expose the false zero created by per-society test centering."""
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    mean_a = a.mean(axis=(1, 2))
    mean_b = b.mean(axis=(1, 2))
    raw = float(np.mean(mean_a * mean_b))
    leaky_a = a - mean_a[:, None, None, :]
    leaky_b = b - mean_b[:, None, None, :]
    centered_a = leaky_a.mean(axis=(1, 2))
    centered_b = leaky_b.mean(axis=(1, 2))
    return {
        "raw_cross_energy": raw,
        "leaky_test_centered_cross_energy": float(
            np.mean(centered_a * centered_b)
        ),
    }


def simulate_local_to_unity_surface(
    *,
    seed: int,
    spec: HierarchicalSocietySpec,
    noise_mode: str,
    group_sizes: Iterable[int],
    author_sizes: Iterable[int],
) -> list[dict[str, Any]]:
    """Generate a triangular array with rho_G = 1 - c/G."""
    group_values = list(map(int, group_sizes))
    author_values = list(map(int, author_sizes))
    children = np.random.SeedSequence(int(seed)).spawn(len(group_values))
    rows: list[dict[str, Any]] = []
    for groups, child in zip(group_values, children, strict=True):
        streams = child.spawn(4)
        rngs = [np.random.default_rng(stream) for stream in streams]
        rho = 1.0 - float(spec.local_to_unity_c) / float(groups)
        if rho <= -1.0:
            raise ValueError(
                "local_to_unity_c is incompatible with group_sizes"
            )
        group = np.sqrt(float(spec.group_energy)) * _stationary_ar1(
            rngs[0],
            (int(spec.societies), groups, int(spec.dimensions)),
            rho=rho,
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        author = np.sqrt(float(spec.author_energy)) * _standard_noise(
            rngs[1],
            (
                int(spec.societies),
                groups,
                int(spec.max_authors),
                int(spec.dimensions),
            ),
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        stable = group[:, :, None, :] + author
        scale = np.sqrt(float(spec.private_noise_energy))
        left = stable + scale * _standard_noise(
            rngs[2],
            stable.shape,
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        right = stable + scale * _standard_noise(
            rngs[3],
            stable.shape,
            noise_mode=noise_mode,
            student_df=float(spec.student_df),
        )
        for authors in author_values:
            mean_a = left[:, :, :authors, :].mean(axis=(1, 2))
            mean_b = right[:, :, :authors, :].mean(axis=(1, 2))
            rows.append({
                "groups": groups,
                "authors": authors,
                "rho": rho,
                "cross_energy": float(np.mean(mean_a * mean_b)),
                "self_energy": float(
                    0.5 * np.mean(mean_a**2 + mean_b**2)
                ),
            })
    return rows


def fit_local_to_unity_surface(
    rows: list[dict[str, Any]],
    *,
    c: float,
) -> dict[str, Any]:
    """Fit the known triangular-array covariance sum."""
    groups = np.asarray([row["groups"] for row in rows], dtype=int)
    authors = np.asarray([row["authors"] for row in rows], dtype=float)
    outcome = np.asarray(
        [row["cross_energy"] for row in rows],
        dtype=float,
    )
    weight = np.asarray(
        [local_to_unity_group_weight(int(value), c) for value in groups],
        dtype=float,
    )
    design = np.column_stack([
        np.ones(len(rows)),
        weight,
        1.0 / (groups * authors),
    ])
    train = _checkerboard_mask(groups.astype(float), authors)
    coefficient = _fit_linear_design(design[train], outcome[train])
    prediction = design @ coefficient
    full = _fit_linear_design(design, outcome)
    return {
        "model": "local_to_unity_known_c",
        "society": float(full[0]),
        "group": float(full[1]),
        "author": float(full[2]),
        "c": float(c),
        "asymptotic_group_weight": local_to_unity_limit(c),
        "train": _error_metrics(outcome[train], prediction[train]),
        "test": _error_metrics(outcome[~train], prediction[~train]),
    }
