"""Geometry-aware information-operator primitives for H4D-R2B."""
from __future__ import annotations

from typing import Any

import numpy as np

from suica_core.v8_minority_information_frontier import (
    _additive_design,
    complete_double_center,
    expected_panel_variance,
    local_double_center,
    minority_information_budget,
)
from suica_core.v8_reference_measure_frontier import ReferenceFrontierSpec


GEOMETRY_FAMILIES = (
    "iid_halo",
    "intrinsic_zero_sum",
    "author_concentrated",
    "condition_concentrated",
    "rank1_coherent",
    "balanced_antiphase",
    "halo_sweep",
)


def weighted_whitened_residual(
    residual: np.ndarray,
    variance: np.ndarray,
) -> np.ndarray:
    """Return a cell-preserving representative with exact precision energy."""
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
    return (
        np.sqrt(weights)[:, None] * remainder
    ).reshape(q.shape)


def _normalize(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(result))
    if norm <= 1e-12:
        raise ValueError("cannot normalize zero geometry")
    return result / norm


def _sparse_block(
    rng: np.random.Generator,
    *,
    authors: int,
    conditions: int,
    dimensions: int,
) -> np.ndarray:
    return rng.normal(size=(authors, conditions, dimensions))


def build_geometry_interaction(
    anchor_interaction: np.ndarray,
    *,
    spec: ReferenceFrontierSpec,
    test_authors: np.ndarray,
    active_test_authors: np.ndarray,
    active_conditions: np.ndarray,
    geometry_family: str,
    halo_lambda: float,
    seed: int,
) -> np.ndarray:
    """Construct one test-panel geometry while retaining paired non-test Q."""
    if geometry_family not in GEOMETRY_FAMILIES:
        raise ValueError(f"unknown geometry_family: {geometry_family}")
    rng = np.random.default_rng(int(seed))
    test = np.asarray(test_authors, dtype=int)
    active = np.asarray(active_test_authors, dtype=int)
    conditions = np.asarray(active_conditions, dtype=int)
    dimensions = np.arange(spec.dimensions)
    interaction = np.asarray(anchor_interaction, dtype=float).copy()
    interaction[test] = 0.0
    if geometry_family == "iid_halo":
        interaction[test] = np.asarray(anchor_interaction)[test]
        return interaction

    test_lookup = {int(author): index for index, author in enumerate(test)}
    active_local = np.asarray(
        [test_lookup[int(author)] for author in active],
        dtype=int,
    )
    test_geometry = np.zeros(
        (len(test), spec.conditions, spec.dimensions),
        dtype=float,
    )

    if geometry_family == "intrinsic_zero_sum":
        block = local_double_center(
            _sparse_block(
                rng,
                authors=len(active),
                conditions=len(conditions),
                dimensions=spec.dimensions,
            )
        )
        test_geometry[
            np.ix_(active_local, conditions, dimensions)
        ] = block
    elif geometry_family == "author_concentrated":
        hot_count = max(2, len(active) // 4)
        order = rng.permutation(len(active))
        hot = order[:hot_count]
        cold = order[hot_count:]
        block = np.zeros(
            (len(active), len(conditions), spec.dimensions),
            dtype=float,
        )
        hot_values = _normalize(
            _sparse_block(
                rng,
                authors=len(hot),
                conditions=len(conditions),
                dimensions=spec.dimensions,
            )
        )
        block[hot] = np.sqrt(0.90) * hot_values
        if len(cold):
            cold_values = _normalize(
                _sparse_block(
                    rng,
                    authors=len(cold),
                    conditions=len(conditions),
                    dimensions=spec.dimensions,
                )
            )
            block[cold] = np.sqrt(0.10) * cold_values
        test_geometry[
            np.ix_(active_local, conditions, dimensions)
        ] = block
    elif geometry_family == "condition_concentrated":
        hot_condition = int(rng.integers(0, len(conditions)))
        cold = [
            index
            for index in range(len(conditions))
            if index != hot_condition
        ]
        block = np.zeros(
            (len(active), len(conditions), spec.dimensions),
            dtype=float,
        )
        hot_values = _normalize(
            rng.normal(size=(len(active), 1, spec.dimensions))
        )
        block[:, hot_condition : hot_condition + 1] = (
            np.sqrt(0.90) * hot_values
        )
        cold_values = _normalize(
            rng.normal(
                size=(len(active), len(cold), spec.dimensions)
            )
        )
        block[:, cold] = np.sqrt(0.10) * cold_values
        test_geometry[
            np.ix_(active_local, conditions, dimensions)
        ] = block
    elif geometry_family == "rank1_coherent":
        author = np.abs(rng.normal(size=len(active)))
        condition = np.abs(rng.normal(size=len(conditions)))
        direction = rng.normal(size=spec.dimensions)
        block = np.einsum("u,c,d->ucd", author, condition, direction)
        test_geometry[
            np.ix_(active_local, conditions, dimensions)
        ] = block
    elif geometry_family == "balanced_antiphase":
        author_sign = np.ones(len(active))
        author_sign[len(active) // 2 :] = -1.0
        rng.shuffle(author_sign)
        condition_sign = np.asarray([1.0, -1.0, 1.0, -1.0])
        rng.shuffle(condition_sign)
        direction = rng.normal(size=spec.dimensions)
        block = np.einsum(
            "u,c,d->ucd",
            author_sign,
            condition_sign,
            direction,
        )
        test_geometry[
            np.ix_(active_local, conditions, dimensions)
        ] = block
    else:
        if not 0.0 <= float(halo_lambda) <= 1.0:
            raise ValueError("halo_lambda must be in [0, 1]")
        core = np.zeros_like(test_geometry)
        core_block = local_double_center(
            _sparse_block(
                rng,
                authors=len(active),
                conditions=len(conditions),
                dimensions=spec.dimensions,
            )
        )
        core[np.ix_(active_local, conditions, dimensions)] = core_block
        core = _normalize(complete_double_center(core))

        intended = np.zeros(test_geometry.shape[:2], dtype=bool)
        intended[np.ix_(active_local, conditions)] = True
        halo = rng.normal(size=test_geometry.shape)
        halo[intended] = 0.0
        halo = complete_double_center(halo)
        halo -= float(np.sum(halo * core)) * core
        halo = _normalize(halo)
        test_geometry = (
            np.sqrt(1.0 - float(halo_lambda)) * core
            + np.sqrt(float(halo_lambda)) * halo
        )

    interaction[test] = test_geometry
    return interaction


def apply_interaction(
    world: dict[str, Any],
    interaction: np.ndarray,
) -> dict[str, Any]:
    """Apply a deterministic interaction to the paired additive observations."""
    updated = dict(world)
    values = np.asarray(interaction, dtype=float)
    updated["interaction"] = values
    updated["cell_truth"] = world["main"] + values
    updated["means_by_k"] = {
        int(prefix): means + values[None, :, :, :]
        for prefix, means in world["means_by_k"].items()
    }
    return updated


def match_residual_information(
    world: dict[str, Any],
    interaction: np.ndarray,
    *,
    target_information: float,
    spec: ReferenceFrontierSpec,
    active_test_authors: np.ndarray,
    active_conditions: np.ndarray,
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> tuple[np.ndarray, dict[str, float]]:
    """Scale one geometry to the paired iid scalar-information anchor."""
    _, _, test = spec.author_split

    def _information(values: np.ndarray) -> float:
        audit = minority_information_budget(
            world,
            values,
            test_authors=test,
            active_test_authors=active_test_authors,
            active_conditions=active_conditions,
            primary_opportunities=primary_opportunities,
            panel_noise_amplitude=panel_noise_amplitude,
            technical_noise_amplitude=technical_noise_amplitude,
            heteroskedastic_strength=heteroskedastic_strength,
        )
        return float(audit["information_budget_residual"])

    raw_information = _information(interaction)
    if raw_information <= 1e-12:
        raise ValueError("geometry has zero residual information")
    scale = np.sqrt(float(target_information) / raw_information)
    matched = np.asarray(interaction, dtype=float) * scale
    achieved = _information(matched)
    relative_error = abs(achieved - float(target_information)) / max(
        float(target_information),
        1e-12,
    )
    return matched, {
        "raw_residual_information": raw_information,
        "target_residual_information": float(target_information),
        "matched_residual_information": achieved,
        "information_match_relative_error": relative_error,
        "information_match_scale": float(scale),
    }


def geometry_information_coordinates(
    world: dict[str, Any],
    interaction: np.ndarray,
    *,
    spec: ReferenceFrontierSpec,
    active_test_authors: np.ndarray,
    active_conditions: np.ndarray,
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    heteroskedastic_strength: float,
) -> dict[str, float]:
    """Compute the registered geometry-information operator coordinates."""
    _, _, test = spec.author_split
    test_lookup = {int(author): index for index, author in enumerate(test)}
    active_local = np.asarray(
        [test_lookup[int(author)] for author in active_test_authors],
        dtype=int,
    )
    conditions = np.asarray(active_conditions, dtype=int)
    dimensions = np.arange(spec.dimensions)
    q_test = np.asarray(interaction, dtype=float)[
        np.ix_(test, np.arange(spec.conditions), dimensions)
    ]
    q_residual = complete_double_center(q_test)
    whitened = []
    for panel in (2, 3):
        variance = expected_panel_variance(
            world,
            panel=panel,
            opportunities=primary_opportunities,
            panel_noise_amplitude=panel_noise_amplitude,
            technical_noise_amplitude=technical_noise_amplitude,
            heteroskedastic_strength=heteroskedastic_strength,
        )[test]
        whitened.append(
            weighted_whitened_residual(q_residual, variance)
        )
    left, right = whitened
    author_matrix = np.concatenate(
        [left.reshape(len(test), -1), right.reshape(len(test), -1)],
        axis=1,
    )
    author_energy = np.sum(author_matrix**2, axis=1)
    total_energy = float(author_energy.sum())
    author_share = author_energy / max(total_energy, 1e-12)
    neff_author = float(
        1.0 / max(float(np.sum(author_share**2)), 1e-12)
    )
    max_author_leverage = float(author_share.max(initial=0.0))

    cell_energy = np.sum(left**2 + right**2, axis=-1)
    cell_share = cell_energy / max(total_energy, 1e-12)
    neff_cell = float(
        1.0 / max(float(np.sum(cell_share**2)), 1e-12)
    )
    condition_energy = cell_energy.sum(axis=0)
    condition_share = condition_energy / max(total_energy, 1e-12)
    neff_condition = float(
        1.0 / max(float(np.sum(condition_share**2)), 1e-12)
    )

    left_features = left.reshape(len(test), -1)
    right_features = right.reshape(len(test), -1)
    cross = left_features.T @ right_features / max(len(test), 1)
    singular = np.linalg.svd(
        cross,
        full_matrices=False,
        compute_uv=False,
    )
    singular_energy = singular**2
    rho3 = float(
        singular_energy[:3].sum()
        / max(float(singular_energy.sum()), 1e-12)
    )

    intended = np.zeros(cell_energy.shape, dtype=bool)
    intended[np.ix_(active_local, conditions)] = True
    whitened_leakage = float(
        cell_energy[~intended].sum() / max(total_energy, 1e-12)
    )

    author_contribution = np.sum(left_features * right_features, axis=1)
    absolute_contribution = np.abs(author_contribution)
    neff_sign = float(
        absolute_contribution.sum() ** 2
        / max(float(np.sum(author_contribution**2)), 1e-12)
    )
    sign_coherence = float(
        abs(float(author_contribution.sum()))
        / max(float(absolute_contribution.sum()), 1e-12)
    )

    active_energy = 0.0
    coherent_energy = 0.0
    for panel_values in (left, right):
        block = panel_values[
            np.ix_(active_local, conditions, dimensions)
        ]
        active_energy += float(np.sum(block**2))
        coherent_energy += float(
            np.sum(np.sum(block, axis=1) ** 2)
        )
    condition_coherence = float(
        coherent_energy
        / max(len(conditions) * active_energy, 1e-12)
    )
    gram = author_matrix @ author_matrix.T
    gram_eigen = np.linalg.eigvalsh(gram)
    gram_eigen = np.maximum(gram_eigen, 0.0)
    gram_effective_rank = float(
        gram_eigen.sum() ** 2
        / max(float(np.sum(gram_eigen**2)), 1e-12)
    )
    return {
        "operator_total_information": total_energy,
        "operator_neff_author": neff_author,
        "operator_max_author_leverage": max_author_leverage,
        "operator_neff_cell": neff_cell,
        "operator_neff_condition": neff_condition,
        "operator_rho3": rho3,
        "operator_whitened_leakage": whitened_leakage,
        "operator_neff_sign": neff_sign,
        "operator_sign_coherence": sign_coherence,
        "operator_condition_coherence": condition_coherence,
        "operator_gram_effective_rank": gram_effective_rank,
    }

