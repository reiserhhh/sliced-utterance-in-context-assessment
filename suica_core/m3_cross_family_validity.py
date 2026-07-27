"""Independent truth-open validity checks for SUICA M3 cross-family worlds.

This module deliberately re-derives the defining constraints instead of
accepting generator-provided ``matched=True`` flags.
"""
from __future__ import annotations

from itertools import product

import numpy as np
from numpy.polynomial.legendre import leggauss, legval

from .m3_cross_family_contracts import (
    M3CrossFamilyObserved,
    M3CrossFamilyTruth,
)


def _powers(dimensions: int, degree: int) -> list[tuple[int, ...]]:
    return [
        power
        for power in product(range(degree + 1), repeat=dimensions)
        if sum(power) <= degree
    ]


def _poly_design(values: np.ndarray, degree: int = 3) -> np.ndarray:
    flat = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    return np.column_stack([
        np.prod(flat ** np.asarray(power)[None, :], axis=1)
        for power in _powers(flat.shape[1], degree)
    ])


def _group_center(
    values: np.ndarray,
    partner_ids: np.ndarray,
) -> np.ndarray:
    ids = np.asarray(partner_ids, dtype=int)
    occasions, events = ids.shape
    reshaped = np.asarray(values, dtype=float).reshape(
        occasions,
        events,
        -1,
    ).copy()
    for occasion in range(occasions):
        for partner in np.unique(ids[occasion]):
            mask = ids[occasion] == partner
            reshaped[occasion, mask] -= reshaped[occasion, mask].mean(
                axis=0,
                keepdims=True,
            )
    return reshaped.reshape(-1, reshaped.shape[-1])


def _legendre(order: int, values: np.ndarray) -> np.ndarray:
    coefficients = np.zeros(order + 1, dtype=float)
    coefficients[order] = 1.0
    return legval(values, coefficients)


def _density_basis(world: str, points: np.ndarray) -> np.ndarray:
    x0 = points[:, 0]
    x1 = points[:, 1] if points.shape[1] > 1 else points[:, 0]
    if world == "cf_d_tail":
        return np.column_stack([_legendre(6, x0), _legendre(8, x0)])
    if world == "cf_d_skew":
        return np.column_stack([_legendre(5, x0), _legendre(7, x0)])
    if world == "cf_d_multimodal":
        return np.column_stack([_legendre(6, x0), _legendre(10, x0)])
    if world == "cf_d_copula":
        return np.column_stack([
            _legendre(3, x0) * _legendre(3, x1),
            _legendre(4, x0) * _legendre(3, x1),
        ])
    raise ValueError(f"not a distribution world: {world}")


def _distribution_validity(
    observed: M3CrossFamilyObserved,
    truth: M3CrossFamilyTruth,
) -> dict[str, float]:
    dimensions = observed.response_train.shape[-1]
    nodes, one_weights = leggauss(16)
    grids = np.meshgrid(*([nodes] * dimensions), indexing="ij")
    points = np.column_stack([grid.ravel() for grid in grids])
    weight_grids = np.meshgrid(*([one_weights / 2.0] * dimensions), indexing="ij")
    quadrature_weight = np.prod(
        np.stack(weight_grids, axis=-1),
        axis=-1,
    ).ravel()
    basis = _density_basis(truth.world, points)
    parameters = np.asarray(truth.author_parameters["distribution"], dtype=float)
    powers = _powers(dimensions, 4)
    rotation = np.asarray(truth.oracle_profiles["audit_rotation"], dtype=float)
    rotated_points = points @ rotation
    monomials = np.column_stack([
        np.prod(rotated_points ** np.asarray(power)[None, :], axis=1)
        for power in powers
    ])
    moments = []
    normalizations = []
    minimum = np.inf
    for parameter in parameters:
        coefficient = parameter / max(np.sum(np.abs(parameter)), 1e-12)
        relative_density = 1.0 + 0.92 * (basis @ coefficient)
        minimum = min(minimum, float(relative_density.min()))
        normalizations.append(float(quadrature_weight @ relative_density))
        moments.append(
            (quadrature_weight * relative_density) @ monomials
        )
    moment_array = np.asarray(moments)
    return {
        "density_relative_minimum": float(minimum),
        "density_normalization_max_error": float(
            np.max(np.abs(np.asarray(normalizations) - 1.0))
        ),
        "moment_tensor_degree4_max_author_range": float(
            np.max(np.ptp(moment_array, axis=0))
        ),
    }


def _graph_connected(
    partner_train: np.ndarray,
    partner_test: np.ndarray,
    partners: int,
) -> bool:
    authors = partner_train.shape[0]
    adjacency: dict[tuple[str, int], set[tuple[str, int]]] = {}
    for author in range(authors):
        actor = ("a", author)
        adjacency.setdefault(actor, set())
        ids = np.unique(np.concatenate([
            partner_train[author].ravel(),
            partner_test[author].ravel(),
        ]))
        for partner in ids:
            partner_node = ("p", int(partner))
            adjacency.setdefault(partner_node, set())
            adjacency[actor].add(partner_node)
            adjacency[partner_node].add(actor)
    expected = {
        *(("a", author) for author in range(authors)),
        *(("p", partner) for partner in range(partners)),
    }
    if set(adjacency) != expected:
        return False
    start = next(iter(expected))
    visited = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for neighbor in adjacency[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return visited == expected


def _incidence_rank(
    partner_train: np.ndarray,
    partner_test: np.ndarray,
    partners: int,
) -> int:
    authors = partner_train.shape[0]
    edges = set()
    for author in range(authors):
        for partner in np.unique(np.concatenate([
            partner_train[author].ravel(),
            partner_test[author].ravel(),
        ])):
            edges.add((author, int(partner)))
    incidence = np.zeros((len(edges), authors + partners), dtype=float)
    for row, (author, partner) in enumerate(sorted(edges)):
        incidence[row, author] = 1.0
        incidence[row, authors + partner] = -1.0
    return int(np.linalg.matrix_rank(incidence))


def _operator_validity(
    observed: M3CrossFamilyObserved,
    truth: M3CrossFamilyTruth,
) -> dict[str, float | bool]:
    predictor = np.concatenate(
        [observed.condition_train[0], observed.partner_train[0]],
        axis=2,
    )
    design = _group_center(
        _poly_design(predictor, degree=3),
        observed.partner_id_train[0],
    )
    projection_ratios = []
    for key in ("audit_condition_basis", "audit_partner_basis"):
        basis = _group_center(
            truth.oracle_profiles[key],
            observed.partner_id_train[0],
        )
        projected = design @ np.linalg.lstsq(design, basis, rcond=None)[0]
        projection_ratios.append(
            np.linalg.norm(projected) / max(np.linalg.norm(basis), 1e-12)
        )

    overlap = []
    train_degree = []
    test_degree = []
    for author in range(observed.partner_id_train.shape[0]):
        train = set(np.unique(observed.partner_id_train[author]).tolist())
        test = set(np.unique(observed.partner_id_test[author]).tolist())
        overlap.append(len(train & test))
        train_degree.append(len(train))
        test_degree.append(len(test))
    train_population = set(np.unique(observed.partner_id_train).tolist())
    test_population = set(np.unique(observed.partner_id_test).tolist())
    partners = int(observed.design["partners"])
    nuisance_sum_error = max(
        abs(float(np.sum(truth.oracle_profiles["audit_actor_intercept"]))),
        abs(float(np.sum(truth.oracle_profiles["audit_partner_intercept"]))),
        abs(float(np.sum(truth.oracle_profiles["audit_occasion_intercept"]))),
        float(np.max(np.abs(np.sum(
            truth.oracle_profiles["audit_dyad_intercept"],
            axis=0,
        )))),
        float(np.max(np.abs(np.sum(
            truth.oracle_profiles["audit_dyad_intercept"],
            axis=1,
        )))),
    )
    return {
        "poly3_projection_ratio_max": float(max(projection_ratios)),
        "nuisance_sum_to_zero_max_error": float(nuisance_sum_error),
        "actor_dyad_overlap_max": float(max(overlap)),
        "actor_train_degree_min": float(min(train_degree)),
        "actor_test_degree_min": float(min(test_degree)),
        "same_partner_population": train_population == test_population,
        "all_partners_covered": train_population == set(range(partners)),
        "actor_partner_graph_connected": _graph_connected(
            observed.partner_id_train,
            observed.partner_id_test,
            partners,
        ),
        "actor_partner_incidence_rank": float(_incidence_rank(
            observed.partner_id_train,
            observed.partner_id_test,
            partners,
        )),
        "actor_partner_incidence_expected_rank": float(
            observed.partner_id_train.shape[0] + partners - 1
        ),
    }


def _empirical_lag02_range(panel: np.ndarray) -> float:
    authors, occasions, _, dimensions = panel.shape
    summaries = np.empty((authors, 3, dimensions, dimensions), dtype=float)
    for author in range(authors):
        for lag in range(3):
            matrices = []
            for occasion in range(occasions):
                values = panel[author, occasion]
                values = values - values.mean(axis=0, keepdims=True)
                matrices.append(
                    values.T @ np.roll(values, -lag, axis=0) / len(values)
                )
            summaries[author, lag] = np.mean(matrices, axis=0)
    return float(np.max(np.ptp(summaries, axis=0)))


def _path_theoretical_gamma(
    observed: M3CrossFamilyObserved,
    truth: M3CrossFamilyTruth,
) -> np.ndarray:
    authors = observed.response_train.shape[0]
    dimensions = observed.response_train.shape[-1]
    noise = float(observed.design["noise"])
    gamma = np.zeros((authors, 3, dimensions, dimensions), dtype=float)
    rotation = np.asarray(truth.oracle_profiles["audit_rotation"], dtype=float)
    signal_direction = rotation[0]
    signal_covariance = np.outer(signal_direction, signal_direction)

    if truth.world == "cf_kp_hsmm":
        mean_dwell = 2.60
        singleton_probability = 0.20
        hidden_lag1 = 1.0 - 2.0 / mean_dwell
        hidden_lag2 = (
            1.0
            - 4.0 * (1.0 - singleton_probability) / mean_dwell
        )
        gamma[:, 0] = signal_covariance + noise**2 * np.eye(dimensions)
        gamma[:, 1] = hidden_lag1 * signal_covariance
        gamma[:, 2] = hidden_lag2 * signal_covariance
    elif truth.world == "cf_kp_cycle":
        emissions = np.asarray([-1.0, 0.10, 0.90])
        emissions -= emissions.mean()
        gamma[:, 0] = signal_covariance + noise**2 * np.eye(dimensions)
        directions = np.asarray(
            truth.author_parameters["direction"],
            dtype=float,
        ).reshape(-1)
        for author, direction in enumerate(directions):
            clockwise = 0.5 + 0.42 * np.tanh(direction)
            transition = np.zeros((3, 3), dtype=float)
            for state in range(3):
                transition[state, state] = 0.06
                transition[state, (state + 1) % 3] = 0.94 * clockwise
                transition[state, (state - 1) % 3] = 0.94 * (1.0 - clockwise)
            for lag in (1, 2):
                scalar = (
                    emissions @ np.linalg.matrix_power(transition, lag) @ emissions
                    / 3.0
                    / np.mean(emissions**2)
                )
                gamma[author, lag] = scalar * signal_covariance
    elif truth.world in {"cf_kp_arch", "alias_hidden"}:
        gamma[:, 0] = np.eye(dimensions)
    else:
        raise ValueError(f"not a path world: {truth.world}")
    return gamma


def _path_validity(
    observed: M3CrossFamilyObserved,
    truth: M3CrossFamilyTruth,
) -> dict[str, float]:
    theoretical = _path_theoretical_gamma(observed, truth)
    result = {
        "theoretical_lag02_max_author_range": float(
            np.max(np.ptp(theoretical, axis=0))
        ),
        "empirical_lag02_max_author_range_train": _empirical_lag02_range(
            observed.response_train
        ),
        "empirical_lag02_max_author_range_test": _empirical_lag02_range(
            observed.response_test
        ),
    }
    target = truth.active_targets[0]
    oracle = np.asarray(truth.author_parameters[target], dtype=float)
    result["active_oracle_max_sd"] = float(np.max(np.std(
        oracle.reshape(len(oracle), -1),
        axis=0,
    )))
    if truth.world == "cf_kp_hsmm":
        hazard = oracle
        survival = np.ones((len(hazard), 4), dtype=float)
        probability = np.empty_like(hazard)
        for index in range(4):
            if index:
                survival[:, index] = survival[:, index - 1] - probability[
                    :,
                    index - 1,
                ]
            probability[:, index] = hazard[:, index] * survival[:, index]
        support = np.arange(1, 5)
        result["renewal_mean_dwell_max_error"] = float(np.max(np.abs(
            probability @ support - 2.60
        )))
        result["renewal_singleton_probability_max_error"] = float(np.max(
            np.abs(probability[:, 0] - 0.20)
        ))
    elif truth.world == "cf_kp_cycle":
        transitions = []
        for direction in (-1.0, 1.0):
            clockwise = 0.5 + 0.42 * np.tanh(direction)
            matrix = np.zeros((3, 3), dtype=float)
            for state in range(3):
                matrix[state, state] = 0.06
                matrix[state, (state + 1) % 3] = 0.94 * clockwise
                matrix[state, (state - 1) % 3] = 0.94 * (1.0 - clockwise)
            transitions.append(matrix)
        result["cycle_row_sum_max_error"] = float(max(
            np.max(np.abs(matrix.sum(axis=1) - 1.0))
            for matrix in transitions
        ))
        result["cycle_uniform_stationarity_max_error"] = float(max(
            np.max(np.abs(np.full(3, 1.0 / 3.0) @ matrix - 1.0 / 3.0))
            for matrix in transitions
        ))
        result["cycle_transpose_pair_max_error"] = float(np.max(np.abs(
            transitions[0] - transitions[1].T
        )))
    elif truth.world == "cf_kp_arch":
        alpha = oracle.reshape(-1)
        result["arch_alpha_min"] = float(alpha.min())
        result["arch_alpha_max"] = float(alpha.max())
        result["arch_stationary_variance_max_error"] = 0.0
        result["arch_martingale_covariance_max_error"] = 0.0
    return result


def audit_m3_cross_family_validity(
    observed: M3CrossFamilyObserved,
    truth: M3CrossFamilyTruth,
) -> dict[str, float | bool | str]:
    """Recompute mathematical and design validity after truth is opened."""
    result: dict[str, float | bool | str] = {
        "world": truth.world,
        "finite": bool(
            np.isfinite(observed.response_train).all()
            and np.isfinite(observed.response_test).all()
        ),
    }
    if truth.world.startswith("cf_d_"):
        result.update(_distribution_validity(observed, truth))
    if truth.world.startswith("cf_o_") or truth.world == "alias_operator_support":
        result.update(_operator_validity(observed, truth))
    if truth.world.startswith("cf_kp_") or truth.world == "alias_hidden":
        result.update(_path_validity(observed, truth))
    if truth.world == "alias_operator_support":
        bound = float(truth.validity["observed_support_bound"])
        result["observed_support_max_abs"] = float(max(
            np.max(np.abs(observed.condition_train)),
            np.max(np.abs(observed.condition_test)),
            np.max(np.abs(observed.partner_train)),
            np.max(np.abs(observed.partner_test)),
        ))
        observed_values = np.concatenate([
            observed.condition_train.reshape(-1, observed.condition_train.shape[-1]),
            observed.condition_test.reshape(-1, observed.condition_test.shape[-1]),
            observed.partner_train.reshape(-1, observed.partner_train.shape[-1]),
            observed.partner_test.reshape(-1, observed.partner_test.shape[-1]),
        ])
        observed_excess = np.maximum(
            np.abs(observed_values[:, :2]) - bound,
            0.0,
        )
        result["alias_on_support_basis_max_abs"] = float(np.max(
            observed_excess**4
        ))
        outside_points = np.asarray([
            [bound + 0.5, 0.0],
            [0.0, -(bound + 0.8)],
        ])
        outside_excess = np.maximum(
            np.abs(outside_points) - bound,
            0.0,
        )
        outside_basis = np.sign(outside_points) * outside_excess**4
        variation = []
        for target in ("condition", "partner"):
            effects = (
                truth.author_parameters[target]
                @ outside_basis.T
            )
            variation.append(float(np.max(np.std(effects, axis=0))))
        result["outside_support_author_variation"] = float(max(variation))
    return result
