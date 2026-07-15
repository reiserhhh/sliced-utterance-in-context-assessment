"""Synthetic V6 audit for continuous condition-manifold coverage.

The earlier two-phase world represents condition as a discrete label.  Real
topic, situation, and opportunity descriptions are not safely assumed to be
categorical.  This module tests a narrower mathematical question: in a planted
continuous context space, does a balanced fixed schedule identify an
author-by-context response function only when both the *context representation*
and the *covered region* are adequate?

It is intentionally a simulation-only identifiability test.  It neither reads
human text nor makes a personality or clinical claim.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np


def _corr(left: np.ndarray, right: np.ndarray) -> float:
    """Return a finite flattened Pearson correlation, otherwise NaN."""
    a, b = np.asarray(left, dtype=float).ravel(), np.asarray(right, dtype=float).ravel()
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _grid(side: int) -> np.ndarray:
    """Return a deterministic square grid over the two-dimensional condition space."""
    values = np.linspace(-1.0, 1.0, side)
    first, second = np.meshgrid(values, values, indexing="ij")
    return np.column_stack([first.ravel(), second.ravel()])


def _rbf(points: np.ndarray, centers: np.ndarray, width: float) -> np.ndarray:
    """Map contexts to a smooth RBF basis."""
    squared = ((np.asarray(points)[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    return np.exp(-squared / (2.0 * width**2))


def _ridge(design: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    """Fit multivariate ridge with an unpenalized leading intercept column."""
    penalty = np.eye(design.shape[1]) * alpha
    penalty[0, 0] = 0.0
    return np.linalg.solve(design.T @ design + penalty, design.T @ target)


def _summary(rows: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    """Summarize repetition outcomes by central 95% simulation intervals."""
    return {
        name: {
            "mean": float(np.nanmean([row[name] for row in rows])),
            "q025": float(np.nanquantile([row[name] for row in rows], 0.025)),
            "q975": float(np.nanquantile([row[name] for row in rows], 0.975)),
        }
        for name in rows[0]
    }


def _nearest_radius(query: np.ndarray, support: np.ndarray) -> float:
    """Return mean nearest-support distance as a simple coverage diagnostic."""
    distances = np.sqrt(((query[:, None, :] - support[None, :, :]) ** 2).sum(axis=2))
    return float(distances.min(axis=1).mean())


def _scenario_support(name: str, full_grid: np.ndarray, repeats: int) -> tuple[np.ndarray, int]:
    """Return equal-budget wide or narrow fixed supports.

    The narrow arm receives the same total observations as the wide arm, but
    only covers the left half of the first context coordinate.  Thus any loss
    cannot be attributed simply to fewer written units.
    """
    if name == "wide_exact" or name == "wide_coarse_proxy":
        return full_grid, repeats
    if name == "narrow_exact_same_budget":
        narrow = full_grid[full_grid[:, 0] <= 0.0]
        return narrow, repeats * 2
    raise ValueError(f"Unknown scenario: {name}")


def _make_features(
    full_grid: np.ndarray,
    basis_side: int,
    width: float,
) -> tuple[Callable[[np.ndarray], np.ndarray], Callable[[np.ndarray], np.ndarray]]:
    """Return true/full and deliberately coarse observable condition maps."""
    centers = _grid(basis_side)
    true_mean = _rbf(full_grid, centers, width).mean(axis=0, keepdims=True)

    def exact(points: np.ndarray) -> np.ndarray:
        return _rbf(points, centers, width) - true_mean

    coarse_reference = np.column_stack([full_grid[:, 0], full_grid[:, 0] ** 2]).mean(axis=0)

    def coarse(points: np.ndarray) -> np.ndarray:
        values = np.column_stack([points[:, 0], points[:, 0] ** 2])
        return values - coarse_reference

    return exact, coarse


def _evaluate_scenario(
    rng: np.random.Generator,
    *,
    name: str,
    persons: int,
    text_features: int,
    full_grid: np.ndarray,
    test_contexts: int,
    repeats: int,
    true_map: Callable[[np.ndarray], np.ndarray],
    proxy_map: Callable[[np.ndarray], np.ndarray],
    noise_scale: float,
    ridge_alpha: float,
) -> dict[str, float]:
    """Evaluate one author-disjoint fixed-condition estimator configuration."""
    support, used_repeats = _scenario_support(name, full_grid, repeats)
    context = np.repeat(support, used_repeats, axis=0)
    observed_map = true_map if name != "wide_coarse_proxy" else proxy_map
    phi_true = true_map(context)
    phi_observed = observed_map(context)
    test = rng.uniform(-1.0, 1.0, size=(test_contexts, 2))
    phi_test_true = true_map(test)
    phi_test_observed = observed_map(test)

    author = rng.normal(0.0, 0.65, size=(persons, text_features))
    response = rng.normal(0.0, 0.30, size=(persons, text_features, phi_true.shape[1]))
    shared = rng.normal(0.0, 0.45, size=(phi_true.shape[1], text_features))
    y = (
        author[:, None, :]
        + phi_true[None, :, :] @ shared
        + np.einsum("ufp,ip->uif", response, phi_true)
        + rng.normal(0.0, noise_scale, size=(persons, len(context), text_features))
    )

    discovery = np.arange(persons) % 2 == 0
    confirmation = ~discovery
    reference_design = np.column_stack([np.ones(len(context)), phi_observed])
    shared_hat = _ridge(
        np.tile(reference_design, (int(discovery.sum()), 1)),
        y[discovery].reshape(-1, text_features),
        ridge_alpha,
    )
    residual = y - reference_design @ shared_hat

    response_hat = np.empty((int(confirmation.sum()), text_features, phi_observed.shape[1]))
    level_hat = np.empty((int(confirmation.sum()), text_features))
    for output_index, user in enumerate(np.flatnonzero(confirmation)):
        coefficients = _ridge(reference_design, residual[user], ridge_alpha)
        level_hat[output_index] = coefficients[0]
        response_hat[output_index] = coefficients[1:].T

    true_response_test = np.einsum("ufp,ip->uif", response[confirmation], phi_test_true)
    predicted_response_test = np.einsum("ufp,ip->uif", response_hat, phi_test_observed)
    return {
        "response_function_recovery_r": _corr(predicted_response_test, true_response_test),
        "response_function_mse": float(np.mean((predicted_response_test - true_response_test) ** 2)),
        "author_level_recovery_r": _corr(level_hat, author[confirmation]),
        "context_coverage_radius": _nearest_radius(test, support),
        "fixed_total_observations": float(len(context)),
    }


def run_continuous_condition_coverage(config: dict[str, Any]) -> dict[str, Any]:
    r"""Run a continuous-manifold coverage audit with frozen competing arms.

    The planted world is

    \[
    Y_{ui}=a_u+m(z_{ui})+B_u\phi(z_{ui})+\epsilon_{ui},
    \]

    where \(z\in\mathbb{R}^2\) is a continuous condition location.  The wide
    exact arm observes \(\phi(z)\) across the full fixed grid.  The narrow arm
    has the same observation budget but poorer domain coverage; the coarse arm
    has the full schedule but loses the second condition coordinate.
    """
    if int(config["grid_side"]) < 3 or int(config["basis_side"]) < 2:
        raise ValueError("grid_side must be >= 3 and basis_side must be >= 2")
    if int(config["repetitions"]) < 2 or int(config["fixed_repeats"]) < 1:
        raise ValueError("repetitions >= 2 and fixed_repeats >= 1 are required")
    full_grid = _grid(int(config["grid_side"]))
    true_map, proxy_map = _make_features(
        full_grid,
        int(config["basis_side"]),
        float(config["rbf_width"]),
    )
    scenarios: dict[str, dict[str, dict[str, float]]] = {}
    for scenario_index, name in enumerate(
        ("wide_exact", "narrow_exact_same_budget", "wide_coarse_proxy")
    ):
        rows = [
            _evaluate_scenario(
                np.random.default_rng(config["seed"] + scenario_index * 1_000_000 + replicate),
                name=name,
                persons=int(config["persons"]),
                text_features=int(config["text_features"]),
                full_grid=full_grid,
                test_contexts=int(config["test_contexts"]),
                repeats=int(config["fixed_repeats"]),
                true_map=true_map,
                proxy_map=proxy_map,
                noise_scale=float(config["noise_scale"]),
                ridge_alpha=float(config["ridge_alpha"]),
            )
            for replicate in range(int(config["repetitions"]))
        ]
        scenarios[name] = _summary(rows)

    wide = scenarios["wide_exact"]
    narrow = scenarios["narrow_exact_same_budget"]
    coarse = scenarios["wide_coarse_proxy"]
    material = float(config["material_response_gap"])
    return {
        "profile": config["profile"],
        "config": config,
        "scenarios": scenarios,
        "gates": {
            "wide_exact_recovers_response": (
                wide["response_function_recovery_r"]["q025"]
                >= float(config["minimum_wide_response_recovery_r"])
            ),
            "narrow_coverage_materially_harms_response": (
                wide["response_function_recovery_r"]["q025"]
                > narrow["response_function_recovery_r"]["q975"] + material
            ),
            "coarse_proxy_materially_harms_response": (
                wide["response_function_recovery_r"]["q025"]
                > coarse["response_function_recovery_r"]["q975"] + material
            ),
            "narrow_has_less_context_coverage": (
                narrow["context_coverage_radius"]["q025"]
                > wide["context_coverage_radius"]["q975"]
            ),
        },
    }
