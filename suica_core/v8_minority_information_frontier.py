"""Minority-local information-frontier primitives for V3.7H.4D R2.

This module plants sparse author-by-condition interactions into an additive
H.4D world.  It does not alter the frozen R1 detector.  It exposes both the
intended sparse block and the residual geometry actually seen after the
registered author/condition centering operator.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

from suica_core.v8_reference_measure_frontier import (
    ReferenceFrontierSpec,
    effective_rank,
    reference_score,
)


def local_double_center(values: np.ndarray) -> np.ndarray:
    """Remove row and column means inside one active interaction block."""
    block = np.asarray(values, dtype=float)
    return (
        block
        - block.mean(axis=1, keepdims=True)
        - block.mean(axis=0, keepdims=True)
        + block.mean(axis=(0, 1), keepdims=True)
    )


def complete_double_center(values: np.ndarray) -> np.ndarray:
    """Apply the complete author-by-condition residual projection."""
    matrix = np.asarray(values, dtype=float)
    return (
        matrix
        - matrix.mean(axis=1, keepdims=True)
        - matrix.mean(axis=0, keepdims=True)
        + matrix.mean(axis=(0, 1), keepdims=True)
    )


def _technical_scale(
    author_covariate: np.ndarray,
    *,
    conditions: int,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> np.ndarray:
    """Reconstruct the registered per-observation technical-noise scale."""
    hetero = 1.0 + float(heteroskedastic_strength) * (
        0.5
        + np.abs(np.asarray(author_covariate, dtype=float)[:, None])
        + np.linspace(0.0, 1.0, int(conditions))[None, :]
    ) / 2.5
    return float(technical_noise_amplitude) * hetero / np.sqrt(2.0)


def expected_panel_variance(
    world: dict[str, Any],
    *,
    panel: int,
    opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> np.ndarray:
    """Return expected cell-mean variance without using realized counts."""
    sigma = _technical_scale(
        world["author_covariate"],
        conditions=world["probabilities"].shape[-1],
        technical_noise_amplitude=technical_noise_amplitude,
        heteroskedastic_strength=heteroskedastic_strength,
    )
    expected_count = (
        float(opportunities)
        * np.asarray(world["probabilities"][int(panel)], dtype=float)
    )
    return (
        float(panel_noise_amplitude) ** 2
        + sigma**2 / np.maximum(expected_count, 1e-12)
    )


@lru_cache(maxsize=None)
def _additive_design(authors: int, conditions: int) -> np.ndarray:
    """Return a full-rank intercept/author/condition nuisance design."""
    n = int(authors)
    c = int(conditions)
    design = np.zeros((n * c, 1 + (n - 1) + (c - 1)), dtype=float)
    design[:, 0] = 1.0
    author_index = np.repeat(np.arange(n), c)
    condition_index = np.tile(np.arange(c), n)
    for author in range(1, n):
        design[:, author] = author_index == author
    offset = n
    for condition in range(1, c):
        design[:, offset + condition - 1] = (
            condition_index == condition
        )
    return design


def residual_precision_energy(
    residual: np.ndarray,
    variance: np.ndarray,
) -> float:
    """Evaluate q'(PDP)^+q using an equivalent weighted projection.

    For q in the row/column-centered subspace,

    q'(PDP)^+q = min_b (q - Xb)'D^-1(q - Xb),

    where X spans the additive author/condition null space.  This avoids an
    explicit pseudoinverse of the full Kronecker covariance.
    """
    q = np.asarray(residual, dtype=float)
    v = np.asarray(variance, dtype=float)
    if q.shape[:2] != v.shape:
        raise ValueError("residual and variance shapes are incompatible")
    design = _additive_design(q.shape[0], q.shape[1])
    response = q.reshape(-1, q.shape[-1])
    weights = 1.0 / np.maximum(v.reshape(-1), 1e-12)
    gram = design.T @ (weights[:, None] * design)
    rhs = design.T @ (weights[:, None] * response)
    coefficients = np.linalg.solve(
        gram + 1e-10 * np.eye(gram.shape[0]),
        rhs,
    )
    remainder = response - design @ coefficients
    return float(np.sum(weights[:, None] * remainder**2))


def _balanced_conditions(
    rng: np.random.Generator,
    *,
    conditions: int,
    active_conditions: int,
) -> np.ndarray:
    """Select one condition per propensity/reference quartile."""
    if int(active_conditions) != 4 or int(conditions) % 4:
        return np.sort(
            rng.choice(
                int(conditions),
                size=int(active_conditions),
                replace=False,
            )
        )
    quartiles = np.array_split(np.arange(int(conditions)), 4)
    return np.sort(
        np.asarray(
            [rng.choice(quartile) for quartile in quartiles],
            dtype=int,
        )
    )


def _select_authors(
    rng: np.random.Generator,
    *,
    spec: ReferenceFrontierSpec,
    active_test_authors: int,
    support_scheme: str,
) -> dict[str, np.ndarray]:
    """Select fixed-split or hypergeometric random minority support."""
    train, calibration, test = spec.author_split
    m = int(active_test_authors)
    if support_scheme == "fixed":
        return {
            "train": np.sort(rng.choice(train, size=2 * m, replace=False)),
            "calibration": np.sort(
                rng.choice(calibration, size=m, replace=False)
            ),
            "test": np.sort(rng.choice(test, size=m, replace=False)),
        }
    if support_scheme != "random":
        raise ValueError(f"unknown support_scheme: {support_scheme}")
    selected = np.sort(
        rng.choice(spec.authors, size=4 * m, replace=False)
    )
    return {
        "train": np.intersect1d(selected, train, assume_unique=True),
        "calibration": np.intersect1d(
            selected,
            calibration,
            assume_unique=True,
        ),
        "test": np.intersect1d(selected, test, assume_unique=True),
    }


def _active_noise_rms(
    world: dict[str, Any],
    *,
    authors: np.ndarray,
    conditions: np.ndarray,
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> float:
    """Return expected active-cell noise RMS without realized-count scaling."""
    selected = np.asarray(authors, dtype=int)
    if len(selected) == 0:
        raise ValueError("noise scaling support must be nonempty")
    variances = [
        expected_panel_variance(
            world,
            panel=panel,
            opportunities=primary_opportunities,
            panel_noise_amplitude=panel_noise_amplitude,
            technical_noise_amplitude=technical_noise_amplitude,
            heteroskedastic_strength=heteroskedastic_strength,
        )[np.ix_(selected, conditions)]
        for panel in (2, 3)
    ]
    return float(np.sqrt(np.mean(np.stack(variances))))


def minority_information_budget(
    world: dict[str, Any],
    interaction: np.ndarray,
    *,
    test_authors: np.ndarray,
    active_test_authors: np.ndarray,
    active_conditions: np.ndarray,
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> dict[str, float]:
    """Compute active-cell and residual-space information coordinates."""
    test = np.asarray(test_authors, dtype=int)
    active = np.asarray(active_test_authors, dtype=int)
    conditions = np.asarray(active_conditions, dtype=int)
    dimensions = np.arange(interaction.shape[-1])
    q_test = np.asarray(interaction, dtype=float)[
        np.ix_(test, np.arange(interaction.shape[1]), dimensions)
    ]
    q_residual = complete_double_center(q_test)

    test_lookup = {int(author): index for index, author in enumerate(test)}
    active_local = np.asarray(
        [test_lookup[int(author)] for author in active],
        dtype=int,
    )
    intended_mask = np.zeros(q_test.shape[:2], dtype=bool)
    if len(active_local):
        intended_mask[np.ix_(active_local, conditions)] = True
    residual_energy = float(np.sum(q_residual**2))
    planted_energy = float(np.sum(q_test**2))
    leakage_energy = float(np.sum(q_residual[~intended_mask] ** 2))

    active_information = 0.0
    residual_information = 0.0
    for panel in (2, 3):
        variance_all = expected_panel_variance(
            world,
            panel=panel,
            opportunities=primary_opportunities,
            panel_noise_amplitude=panel_noise_amplitude,
            technical_noise_amplitude=technical_noise_amplitude,
            heteroskedastic_strength=heteroskedastic_strength,
        )
        variance_test = variance_all[test]
        residual_information += residual_precision_energy(
            q_residual,
            variance_test,
        )
        if len(active):
            active_q = np.asarray(interaction)[
                np.ix_(active, conditions, dimensions)
            ]
            active_variance = variance_all[
                np.ix_(active, conditions)
            ]
            active_information += float(
                np.sum(
                    active_q**2
                    / active_variance[:, :, None]
                )
            )

    counts = world["counts_by_k"][int(primary_opportunities)]
    observed_both = 0
    if len(active):
        mask_2 = counts[2][np.ix_(active, conditions)] > 0
        mask_3 = counts[3][np.ix_(active, conditions)] > 0
        observed_both = int(np.sum(mask_2 & mask_3))
    return {
        "information_budget_active": active_information,
        "information_budget_residual": residual_information,
        "information_budget_residual_per_active_author": float(
            residual_information / max(len(active), 1)
        ),
        "centering_retention_ratio": (
            residual_energy / planted_energy
            if planted_energy > 1e-15
            else 0.0
        ),
        "centering_leakage_ratio": (
            leakage_energy / residual_energy
            if residual_energy > 1e-15
            else 0.0
        ),
        "observed_active_cells_both_panels": float(observed_both),
        "active_cells_total": float(len(active) * len(conditions)),
    }


def plant_minority_interaction(
    world: dict[str, Any],
    *,
    spec: ReferenceFrontierSpec,
    seed: int,
    active_test_authors: int,
    active_conditions: int,
    support_scheme: str,
    interaction_shape: str,
    scaling_arm: str,
    global_effect_share: float,
    active_cell_snr: float,
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Plant a sparse interaction and return its complete geometry audit."""
    rng = np.random.default_rng(int(seed))
    train, calibration, test = spec.author_split
    m = int(active_test_authors)
    q_conditions = int(active_conditions)
    if m < 2:
        raise ValueError("active_test_authors must be at least 2")
    if 2 * m > len(train) or m > len(calibration) or m > len(test):
        raise ValueError("active author count exceeds a registered split")
    if not 2 <= q_conditions <= spec.conditions:
        raise ValueError("active_conditions must be in [2, conditions]")
    if scaling_arm not in {"global_share", "active_snr"}:
        raise ValueError(f"unknown scaling_arm: {scaling_arm}")
    if interaction_shape not in {"iid_block", "intrinsic_zero_sum"}:
        raise ValueError(f"unknown interaction_shape: {interaction_shape}")

    selected_conditions = _balanced_conditions(
        rng,
        conditions=spec.conditions,
        active_conditions=q_conditions,
    )
    selections = _select_authors(
        rng,
        spec=spec,
        active_test_authors=m,
        support_scheme=support_scheme,
    )
    all_active = np.concatenate(list(selections.values()))
    dimensions = np.arange(spec.dimensions)
    interaction = np.zeros_like(world["cell_truth"], dtype=float)
    if interaction_shape == "iid_block":
        block = rng.normal(
            size=(len(all_active), q_conditions, spec.dimensions)
        )
        block /= max(float(np.sqrt(np.mean(block**2))), 1e-12)
        interaction[
            np.ix_(all_active, selected_conditions, dimensions)
        ] = block
    else:
        for authors in selections.values():
            if len(authors) < 2:
                continue
            block = local_double_center(
                rng.normal(
                    size=(
                        len(authors),
                        q_conditions,
                        spec.dimensions,
                    )
                )
            )
            block /= max(float(np.sqrt(np.mean(block**2))), 1e-12)
            interaction[
                np.ix_(authors, selected_conditions, dimensions)
            ] = block

    raw_global_energy = float(np.mean(interaction**2))
    if raw_global_energy <= 1e-15:
        raise ValueError("planted interaction has zero energy")
    if scaling_arm == "global_share":
        base_energy = float(np.mean(world["main"] ** 2))
        target_energy = (
            float(global_effect_share)
            / max(1.0 - float(global_effect_share), 1e-12)
            * base_energy
        )
        scale = np.sqrt(target_energy / raw_global_energy)
        target_noise_rms = float("nan")
        noise_fallback_used = False
    else:
        noise_scale_authors = (
            all_active
            if support_scheme == "random"
            else selections["test"]
        )
        target_noise_rms = _active_noise_rms(
            world,
            authors=noise_scale_authors,
            conditions=selected_conditions,
            primary_opportunities=primary_opportunities,
            panel_noise_amplitude=panel_noise_amplitude,
            technical_noise_amplitude=technical_noise_amplitude,
            heteroskedastic_strength=heteroskedastic_strength,
        )
        scale = (
            float(active_cell_snr)
            * target_noise_rms
        )
    interaction *= scale

    updated = dict(world)
    updated["interaction"] = interaction
    updated["cell_truth"] = world["main"] + interaction
    updated["theta_star"] = reference_score(
        updated["cell_truth"],
        world["reference"],
    )
    updated["means_by_k"] = {
        int(prefix): means + interaction[None, :, :, :]
        for prefix, means in world["means_by_k"].items()
    }
    updated["effective_rank"] = effective_rank(interaction)

    test_values = interaction[
        np.ix_(selections["test"], selected_conditions, dimensions)
    ]
    q_test = interaction[
        np.ix_(test, np.arange(spec.conditions), dimensions)
    ]
    grand_mean = interaction.mean(axis=(0, 1), keepdims=True)
    compatibility_error = float(
        np.max(
            np.abs(
                complete_double_center(q_test)
                - complete_double_center(q_test - grand_mean)
            )
        )
    )
    budgets = minority_information_budget(
        updated,
        interaction,
        test_authors=test,
        active_test_authors=selections["test"],
        active_conditions=selected_conditions,
        primary_opportunities=primary_opportunities,
        panel_noise_amplitude=panel_noise_amplitude,
        technical_noise_amplitude=technical_noise_amplitude,
        heteroskedastic_strength=heteroskedastic_strength,
    )
    realized_energy = float(np.mean(interaction**2))
    base_energy = float(np.mean(world["main"] ** 2))
    intended_support_fraction = float(
        len(all_active)
        * len(selected_conditions)
        / (spec.authors * spec.conditions)
    )
    audit = {
        "support_scheme": support_scheme,
        "interaction_shape": interaction_shape,
        "nominal_active_test_authors": m,
        "realized_active_train_authors": int(len(selections["train"])),
        "realized_active_calibration_authors": int(
            len(selections["calibration"])
        ),
        "realized_active_test_authors": int(len(selections["test"])),
        "active_conditions": q_conditions,
        "selected_test_authors": selections["test"].tolist(),
        "selected_conditions": selected_conditions.tolist(),
        "realized_global_effect_share": float(
            realized_energy / max(base_energy + realized_energy, 1e-12)
        ),
        "realized_active_test_rms": (
            float(np.sqrt(np.mean(test_values**2)))
            if test_values.size
            else 0.0
        ),
        "registered_active_noise_rms": target_noise_rms,
        "realized_active_cell_snr": (
            float(np.sqrt(np.mean(test_values**2))) / target_noise_rms
            if test_values.size
            and np.isfinite(target_noise_rms)
            and target_noise_rms > 0
            else float("nan")
        ),
        "registered_active_cell_snr": (
            float(active_cell_snr)
            if scaling_arm == "active_snr"
            else float("nan")
        ),
        "interaction_effective_rank": float(updated["effective_rank"]),
        "intended_support_fraction": intended_support_fraction,
        "projection_grand_mean_compatibility_error": compatibility_error,
        **budgets,
    }
    return updated, audit
