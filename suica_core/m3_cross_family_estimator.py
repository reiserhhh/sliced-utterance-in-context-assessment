"""Frozen, generator-blind estimators for SUICA M3 cross-family worlds."""
from __future__ import annotations

from itertools import product
from typing import Iterable

import numpy as np
from sklearn.kernel_approximation import Nystroem

from .m3_cross_family_contracts import (
    M3CrossFamilyEstimate,
    M3CrossFamilyObserved,
    validate_cross_family_observed,
)


CROSS_FAMILY_FEATURES = (
    "moments_degree4",
    "distribution_ecf",
    "condition_poly3",
    "condition_laplace",
    "partner_poly3",
    "partner_laplace",
    "path_second_order",
    "path_hazard",
    "path_time_reversal",
    "path_delay_vamp",
)


def _standardize_pair(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    train_values = np.asarray(train, dtype=float)
    test_values = np.asarray(test, dtype=float)
    center = train_values.mean(axis=0, keepdims=True)
    variance = train_values.var(axis=0, ddof=0)
    keep = variance > 1e-12
    if not np.any(keep):
        zeros = np.zeros((len(train_values), 1), dtype=float)
        return zeros, zeros.copy()
    scale = np.sqrt(np.mean(variance[keep]))
    return (
        (train_values[:, keep] - center[:, keep]) / max(scale, 1e-8),
        (test_values[:, keep] - center[:, keep]) / max(scale, 1e-8),
    )


def _pooled_whiten(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    dimensions = train.shape[-1]
    pooled = train.reshape(-1, dimensions)
    center = pooled.mean(axis=0)
    covariance = np.cov(pooled, rowvar=False, ddof=0)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    inverse_root = eigenvectors @ np.diag(
        1.0 / np.sqrt(np.maximum(eigenvalues, 1e-8))
    ) @ eigenvectors.T
    return (
        (train - center) @ inverse_root,
        (test - center) @ inverse_root,
    )


def _pooled_pca_whiten(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Train-frozen PCA coordinates followed by variance whitening."""
    dimensions = train.shape[-1]
    pooled = train.reshape(-1, dimensions)
    center = pooled.mean(axis=0)
    covariance = np.cov(pooled, rowvar=False, ddof=0)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    basis = eigenvectors[:, order]
    scale = np.sqrt(np.maximum(eigenvalues[order], 1e-8))
    return (
        ((train - center) @ basis) / scale,
        ((test - center) @ basis) / scale,
    )


def _polynomial_powers(dimensions: int, degree: int) -> list[tuple[int, ...]]:
    return [
        power
        for power in product(range(degree + 1), repeat=dimensions)
        if sum(power) <= degree
    ]


def _moment_profile(panel: np.ndarray, degree: int = 4) -> np.ndarray:
    values = np.asarray(panel, dtype=float).reshape(
        panel.shape[0],
        -1,
        panel.shape[-1],
    )
    powers = _polynomial_powers(values.shape[-1], degree)
    return np.column_stack([
        np.prod(values ** np.asarray(power)[None, None, :], axis=2).mean(axis=1)
        for power in powers
    ])


def _moment_profile_by_occasion(
    panel: np.ndarray,
    degree: int = 4,
) -> np.ndarray:
    return np.stack([
        _moment_profile(panel[:, occasion:occasion + 1], degree)
        for occasion in range(panel.shape[1])
    ], axis=1)


def _random_frequency_set(
    *,
    dimensions: int,
    directions: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    unit = rng.normal(size=(directions, dimensions))
    unit /= np.maximum(np.linalg.norm(unit, axis=1, keepdims=True), 1e-12)
    # Geometric scales are fixed independently of every generator family.
    scales = np.asarray([0.50, 1.00, 2.00, 4.00])
    return np.concatenate([unit * scale for scale in scales], axis=0)


def _heldout_feature_score(
    train: np.ndarray,
    test: np.ndarray,
) -> np.ndarray:
    """Return author-wise held-out kernel/feature score improvement.

    Positive values mean the author's train representation predicts its
    independent test representation better than the pooled train reference.
    For characteristic/RKHS mean embeddings this is a proper squared-kernel
    score difference up to constants shared by both forecasts.
    """
    train_values = np.asarray(train, dtype=float)
    test_values = np.asarray(test, dtype=float)
    authors = len(train_values)
    if authors < 2:
        return np.zeros(authors, dtype=float)
    pooled = (
        train_values.sum(axis=0, keepdims=True) - train_values
    ) / (authors - 1)
    own_loss = np.mean((test_values - train_values) ** 2, axis=1)
    pooled_loss = np.mean((test_values - pooled) ** 2, axis=1)
    return pooled_loss - own_loss


def _ecf_proper_score_gain(
    train_by_occasion: np.ndarray,
    test_by_occasion: np.ndarray,
    *,
    samples_per_author: int,
) -> np.ndarray:
    """Unbiased random-feature kernel score gain over leave-author-out pool."""
    train = np.asarray(train_by_occasion, dtype=float).mean(axis=1)
    test = np.asarray(test_by_occasion, dtype=float).mean(axis=1)
    authors = len(train)
    if authors < 2 or samples_per_author < 2:
        return np.zeros(authors, dtype=float)
    frequency_count = train.shape[1] // 2

    def score(
        forecast_mean: np.ndarray,
        count: int,
        target_mean: np.ndarray,
    ) -> float:
        within = (
            count * count * float(forecast_mean @ forecast_mean)
            - count * frequency_count
        ) / (count * (count - 1))
        return within - 2.0 * float(forecast_mean @ target_mean)

    total = train.sum(axis=0)
    pooled_count = (authors - 1) * samples_per_author
    gains = np.empty(authors, dtype=float)
    for author in range(authors):
        pooled = (total - train[author]) / (authors - 1)
        gains[author] = (
            score(pooled, pooled_count, test[author])
            - score(train[author], samples_per_author, test[author])
        )
    return gains


def _rpecf(panel: np.ndarray, frequencies: np.ndarray) -> np.ndarray:
    values = np.asarray(panel, dtype=float).reshape(
        panel.shape[0],
        -1,
        panel.shape[-1],
    )
    output = np.empty((len(values), frequencies.shape[0] * 2), dtype=float)
    for author, author_values in enumerate(values):
        projection = author_values @ frequencies.T
        output[author] = np.concatenate([
            np.cos(projection).mean(axis=0),
            np.sin(projection).mean(axis=0),
        ])
    return output


def _rpecf_by_occasion(
    panel: np.ndarray,
    frequencies: np.ndarray,
) -> np.ndarray:
    return np.stack([
        _rpecf(panel[:, occasion:occasion + 1], frequencies)
        for occasion in range(panel.shape[1])
    ], axis=1)


def _sliced_quantile_by_occasion(
    panel: np.ndarray,
    directions: np.ndarray,
) -> np.ndarray:
    unit = directions[: max(len(directions) // 4, 1)].copy()
    unit /= np.maximum(np.linalg.norm(unit, axis=1, keepdims=True), 1e-12)
    quantiles = np.asarray([0.03, 0.08, 0.16, 0.30, 0.50, 0.70, 0.84, 0.92, 0.97])
    output = []
    for occasion in range(panel.shape[1]):
        values = panel[:, occasion]
        author_profiles = []
        for author in range(panel.shape[0]):
            projected = values[author] @ unit.T
            author_profiles.append(
                np.quantile(projected, quantiles, axis=0).T.ravel()
            )
        output.append(np.asarray(author_profiles))
    return np.stack(output, axis=1)


def _rank_uniform(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(1, len(values) + 1, dtype=float)
    return ranks / (len(values) + 1.0)


def _copula_fourier_by_occasion(
    panel: np.ndarray,
    directions: np.ndarray,
    pairs: int = 32,
) -> np.ndarray:
    unit = directions[: max(len(directions) // 4, 2)].copy()
    unit /= np.maximum(np.linalg.norm(unit, axis=1, keepdims=True), 1e-12)
    pairs = min(pairs, len(unit) // 2)
    harmonics = ((1, 1), (1, -1), (1, 2), (2, 1), (2, 2), (3, 1), (1, 3))
    occasion_features = []
    for occasion in range(panel.shape[1]):
        author_features = []
        for author in range(panel.shape[0]):
            projected = panel[author, occasion] @ unit[: pairs * 2].T
            profile: list[float] = []
            for pair in range(pairs):
                first = _rank_uniform(projected[:, pair * 2])
                second = _rank_uniform(projected[:, pair * 2 + 1])
                for one, two in harmonics:
                    phase = 2.0 * np.pi * (one * first + two * second)
                    profile.extend((float(np.cos(phase).mean()),
                                    float(np.sin(phase).mean())))
            author_features.append(profile)
        occasion_features.append(np.asarray(author_features))
    return np.stack(occasion_features, axis=1)


def _stability_weighted_views(
    train: np.ndarray,
    test: np.ndarray,
    *,
    minimum_features: int = 12,
    minimum_reliability: float = 0.12,
) -> tuple[np.ndarray, np.ndarray]:
    """Weight coordinates by train-only split-occasion reliability."""
    if train.shape[1] < 2:
        return train.mean(axis=1), test.mean(axis=1)
    even = train[:, ::2].mean(axis=1)
    odd = train[:, 1::2].mean(axis=1)
    weights = np.zeros(train.shape[2], dtype=float)
    for index in range(train.shape[2]):
        if np.std(even[:, index]) <= 1e-12 or np.std(odd[:, index]) <= 1e-12:
            continue
        weights[index] = max(
            float(np.corrcoef(even[:, index], odd[:, index])[0, 1]),
            0.0,
        )
    stable = weights >= minimum_reliability
    if np.count_nonzero(stable) < min(minimum_features, len(weights)):
        order = np.argsort(weights)[::-1]
        keep = order[: min(minimum_features, len(order))]
    else:
        keep = np.flatnonzero(stable)
    scale = np.sqrt(np.maximum(weights[keep], 1e-4))
    return (
        train.mean(axis=1)[:, keep] * scale,
        test.mean(axis=1)[:, keep] * scale,
    )


def _kernel_mean_by_occasion(
    train: np.ndarray,
    test: np.ndarray,
    *,
    seed: int,
    anchors: int = 72,
) -> tuple[np.ndarray, np.ndarray]:
    """Multiscale characteristic-kernel means with train-frozen anchors."""
    rng = np.random.default_rng(seed)
    pooled = train.reshape(-1, train.shape[-1])
    count = min(anchors, len(pooled))
    selected = pooled[rng.choice(len(pooled), size=count, replace=False)]
    scales = (0.20, 0.55, 1.40, 3.50)

    def transform(panel: np.ndarray) -> np.ndarray:
        output = np.empty(
            (
                panel.shape[0],
                panel.shape[1],
                count * len(scales),
            ),
            dtype=float,
        )
        for author in range(panel.shape[0]):
            for occasion in range(panel.shape[1]):
                values = panel[author, occasion]
                squared = np.sum(
                    (values[:, None, :] - selected[None, :, :]) ** 2,
                    axis=2,
                )
                output[author, occasion] = np.concatenate([
                    np.exp(-gamma * squared).mean(axis=0)
                    for gamma in scales
                ])
        return output

    return transform(train), transform(test)


def _poly_design(values: np.ndarray, degree: int = 3) -> np.ndarray:
    flat = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    powers = _polynomial_powers(flat.shape[1], degree)
    return np.column_stack([
        np.prod(flat ** np.asarray(power)[None, :], axis=1)
        for power in powers
    ])


def _group_center(
    values: np.ndarray,
    *,
    occasions: int,
    events: int,
    partner_ids: np.ndarray,
) -> np.ndarray:
    centered = np.asarray(values, dtype=float).copy()
    ids = np.asarray(partner_ids, dtype=int).reshape(occasions, events)
    reshaped = centered.reshape(occasions, events, -1)
    for occasion in range(occasions):
        for partner_id in np.unique(ids[occasion]):
            mask = ids[occasion] == partner_id
            reshaped[occasion, mask] -= reshaped[occasion, mask].mean(
                axis=0,
                keepdims=True,
            )
    return reshaped.reshape(len(centered), -1)


def _ridge_coefficients(
    design: np.ndarray,
    target: np.ndarray,
    ridge: float,
) -> np.ndarray:
    return np.linalg.solve(
        design.T @ design + ridge * np.eye(design.shape[1]),
        design.T @ target,
    )


def _r2(target: np.ndarray, prediction: np.ndarray) -> float:
    denominator = float(np.sum((target - target.mean(axis=0)) ** 2))
    if denominator <= 1e-12:
        return 0.0
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator)


def _common_operator_design(
    condition: np.ndarray,
    partner: np.ndarray,
) -> np.ndarray:
    condition_poly = _poly_design(condition, degree=3)
    partner_poly = _poly_design(partner, degree=3)
    return np.column_stack([
        np.ones(len(condition_poly)),
        condition_poly[:, 1:],
        partner_poly[:, 1:],
    ])


def _nuisance_residuals(
    observed: M3CrossFamilyObserved,
    *,
    ridge: float,
    iterations: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit nuisance effects on train only and apply them unchanged to test."""
    train = observed.response_train
    test = observed.response_test
    authors, occasions, events, dimensions = train.shape
    partners = int(observed.design["partners"])
    train_design = np.stack([
        _common_operator_design(
            observed.condition_train[author],
            observed.partner_train[author],
        )
        for author in range(authors)
    ])
    test_design = np.stack([
        _common_operator_design(
            observed.condition_test[author],
            observed.partner_test[author],
        )
        for author in range(authors)
    ])
    train_values = train.reshape(authors, occasions * events, dimensions)
    test_values = test.reshape(authors, occasions * events, dimensions)
    train_ids = observed.partner_id_train.reshape(authors, -1)
    test_ids = observed.partner_id_test.reshape(authors, -1)
    occasion_index = np.tile(np.repeat(np.arange(occasions), events), authors)
    author_index = np.repeat(np.arange(authors), occasions * events)
    partner_index = train_ids.ravel()

    actor_effect = np.zeros((authors, dimensions), dtype=float)
    partner_effect = np.zeros((partners, dimensions), dtype=float)
    occasion_effect = np.zeros((occasions, dimensions), dtype=float)
    dyad_effect = np.zeros((authors, partners, dimensions), dtype=float)
    seen_dyad = np.zeros((authors, partners), dtype=bool)
    for author in range(authors):
        seen_dyad[author, np.unique(train_ids[author])] = True

    beta = np.zeros((train_design.shape[-1], dimensions), dtype=float)
    flat_design = train_design.reshape(-1, train_design.shape[-1])
    flat_target = train_values.reshape(-1, dimensions)
    for _ in range(iterations):
        known = (
            actor_effect[author_index]
            + partner_effect[partner_index]
            + occasion_effect[occasion_index]
            + dyad_effect[author_index, partner_index]
        )
        beta = _ridge_coefficients(
            flat_design,
            flat_target - known,
            ridge,
        )
        residual = flat_target - flat_design @ beta

        without_actor = residual - (
            partner_effect[partner_index]
            + occasion_effect[occasion_index]
            + dyad_effect[author_index, partner_index]
        )
        actor_effect = without_actor.reshape(
            authors,
            occasions * events,
            dimensions,
        ).mean(axis=1)
        actor_effect -= actor_effect.mean(axis=0, keepdims=True)

        without_partner = residual - (
            actor_effect[author_index]
            + occasion_effect[occasion_index]
            + dyad_effect[author_index, partner_index]
        )
        for partner_id in range(partners):
            mask = partner_index == partner_id
            partner_effect[partner_id] = (
                without_partner[mask].mean(axis=0) if np.any(mask) else 0.0
            )
        partner_effect -= partner_effect.mean(axis=0, keepdims=True)

        without_occasion = residual - (
            actor_effect[author_index]
            + partner_effect[partner_index]
            + dyad_effect[author_index, partner_index]
        )
        for occasion in range(occasions):
            mask = occasion_index == occasion
            occasion_effect[occasion] = without_occasion[mask].mean(axis=0)
        occasion_effect -= occasion_effect.mean(axis=0, keepdims=True)

        without_dyad = residual - (
            actor_effect[author_index]
            + partner_effect[partner_index]
            + occasion_effect[occasion_index]
        )
        for author in range(authors):
            author_rows = author_index == author
            for partner_id in np.flatnonzero(seen_dyad[author]):
                mask = author_rows & (partner_index == partner_id)
                dyad_effect[author, partner_id] = without_dyad[mask].mean(
                    axis=0
                )
            active = seen_dyad[author]
            dyad_effect[author, active] -= dyad_effect[
                author,
                active,
            ].mean(axis=0, keepdims=True)

    def prediction(
        design: np.ndarray,
        ids: np.ndarray,
        *,
        include_seen_dyad: bool,
    ) -> np.ndarray:
        output = design @ beta
        output += actor_effect[:, None, :]
        output += partner_effect[ids]
        occasion = np.broadcast_to(
            occasion_effect[:, None, :],
            (occasions, events, dimensions),
        ).reshape(occasions * events, dimensions)
        output += occasion[None, :, :]
        if include_seen_dyad:
            author_grid = np.arange(authors)[:, None]
            effects = dyad_effect[author_grid, ids]
            effects *= seen_dyad[author_grid, ids][..., None]
            output += effects
        return output

    train_prediction = prediction(
        train_design,
        train_ids,
        include_seen_dyad=True,
    )
    test_prediction = prediction(
        test_design,
        test_ids,
        include_seen_dyad=True,
    )
    return (
        (train_values - train_prediction).reshape(train.shape),
        (test_values - test_prediction).reshape(test.shape),
    )


def _operator_view(
    *,
    response_residual: np.ndarray,
    condition: np.ndarray,
    partner: np.ndarray,
    condition_kernel: np.ndarray,
    partner_kernel: np.ndarray,
    condition_probe: np.ndarray,
    partner_probe: np.ndarray,
    ridge: float,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    authors = response_residual.shape[0]
    condition_poly = _poly_design(condition[0], degree=3)
    partner_poly = _poly_design(partner[0], degree=3)
    cheap_design = np.column_stack([
        condition_poly[:, 1:],
        partner_poly[:, 1:],
    ])
    condition_width = condition_poly.shape[1] - 1
    cheap_features = {"condition": [], "partner": []}
    rich_features = {"condition": [], "partner": []}
    coefficients: dict[str, list[np.ndarray]] = {
        "full": [],
        "no_condition": [],
        "no_partner": [],
    }
    full_design = np.column_stack([
        cheap_design,
        condition_kernel,
        partner_kernel,
    ])
    no_condition_design = np.column_stack([
        cheap_design,
        partner_kernel,
    ])
    no_partner_design = np.column_stack([
        cheap_design,
        condition_kernel,
    ])
    for author in range(authors):
        target = response_residual[author].reshape(
            -1,
            response_residual.shape[-1],
        )
        cheap_beta = _ridge_coefficients(cheap_design, target, ridge)
        full_beta = _ridge_coefficients(full_design, target, ridge)
        coefficients["full"].append(full_beta)
        coefficients["no_condition"].append(
            _ridge_coefficients(no_condition_design, target, ridge)
        )
        coefficients["no_partner"].append(
            _ridge_coefficients(no_partner_design, target, ridge)
        )
        cheap_features["condition"].append(
            cheap_beta[:condition_width].ravel()
        )
        cheap_features["partner"].append(
            cheap_beta[condition_width:].ravel()
        )
        condition_offset = cheap_design.shape[1]
        partner_offset = condition_offset + condition_kernel.shape[1]
        rich_features["condition"].append(
            (condition_probe @ full_beta[
                condition_offset:partner_offset
            ]).ravel()
        )
        rich_features["partner"].append(
            (partner_probe @ full_beta[partner_offset:]).ravel()
        )
    return (
        {
            "condition_poly3": np.asarray(cheap_features["condition"]),
            "condition_laplace": np.asarray(rich_features["condition"]),
            "partner_poly3": np.asarray(cheap_features["partner"]),
            "partner_laplace": np.asarray(rich_features["partner"]),
        },
        {
            name: np.asarray(values)
            for name, values in coefficients.items()
        },
    )


def _operator_features(
    observed: M3CrossFamilyObserved,
    *,
    seed: int,
    n_components: int,
    ridge: float,
) -> tuple[
    dict[str, tuple[np.ndarray, np.ndarray]],
    dict[str, float],
    dict[str, np.ndarray],
]:
    condition_train_flat = observed.condition_train[0].reshape(
        -1,
        observed.condition_train.shape[-1],
    )
    condition_test_flat = observed.condition_test[0].reshape(
        -1,
        observed.condition_test.shape[-1],
    )
    partner_train_flat = observed.partner_train[0].reshape(
        -1,
        observed.partner_train.shape[-1],
    )
    partner_test_flat = observed.partner_test[0].reshape(
        -1,
        observed.partner_test.shape[-1],
    )
    components = min(n_components, len(condition_train_flat) - 1)
    sklearn_seed = int(seed % (2**32 - 1))
    condition_map = Nystroem(
        kernel="laplacian",
        gamma=0.75,
        n_components=components,
        random_state=sklearn_seed,
    )
    partner_map = Nystroem(
        kernel="laplacian",
        gamma=0.75,
        n_components=components,
        random_state=(sklearn_seed + 1) % (2**32 - 1),
    )
    condition_kernel_train = condition_map.fit_transform(condition_train_flat)
    condition_kernel_test = condition_map.transform(condition_test_flat)
    partner_kernel_train = partner_map.fit_transform(partner_train_flat)
    partner_kernel_test = partner_map.transform(partner_test_flat)

    condition_poly_train = _poly_design(observed.condition_train[0], 3)
    condition_poly_test = _poly_design(observed.condition_test[0], 3)
    partner_poly_train = _poly_design(observed.partner_train[0], 3)
    partner_poly_test = _poly_design(observed.partner_test[0], 3)
    condition_projection = np.linalg.lstsq(
        condition_poly_train,
        condition_kernel_train,
        rcond=None,
    )[0]
    partner_projection = np.linalg.lstsq(
        partner_poly_train,
        partner_kernel_train,
        rcond=None,
    )[0]
    condition_kernel_train -= condition_poly_train @ condition_projection
    condition_kernel_test -= condition_poly_test @ condition_projection
    partner_kernel_train -= partner_poly_train @ partner_projection
    partner_kernel_test -= partner_poly_test @ partner_projection

    rng = np.random.default_rng(seed + 2)
    probe = rng.normal(
        size=(96, observed.condition_train.shape[-1]),
    )
    probe_poly = _poly_design(probe, 3)
    condition_probe = (
        condition_map.transform(probe) - probe_poly @ condition_projection
    )
    partner_probe = (
        partner_map.transform(probe) - probe_poly @ partner_projection
    )

    train_residual, test_residual = _nuisance_residuals(
        observed,
        ridge=ridge,
    )
    train_features, train_coefficients = _operator_view(
        response_residual=train_residual,
        condition=observed.condition_train,
        partner=observed.partner_train,
        condition_kernel=condition_kernel_train,
        partner_kernel=partner_kernel_train,
        condition_probe=condition_probe,
        partner_probe=partner_probe,
        ridge=ridge,
    )
    test_features, _ = _operator_view(
        response_residual=test_residual,
        condition=observed.condition_test,
        partner=observed.partner_test,
        condition_kernel=condition_kernel_test,
        partner_kernel=partner_kernel_test,
        condition_probe=condition_probe,
        partner_probe=partner_probe,
        ridge=ridge,
    )

    condition_gains: list[float] = []
    partner_gains: list[float] = []
    for author in range(observed.response_test.shape[0]):
        y_test = test_residual[author].reshape(
            -1,
            test_residual.shape[-1],
        )
        cheap = np.column_stack([
            condition_poly_test[:, 1:],
            partner_poly_test[:, 1:],
        ])
        condition_design = np.column_stack([
            cheap,
            condition_kernel_test,
        ])
        partner_design = np.column_stack([
            cheap,
            partner_kernel_test,
        ])
        full_design = np.column_stack([
            cheap,
            condition_design[:, cheap.shape[1]:],
            partner_design[:, cheap.shape[1]:],
        ])
        full_prediction = full_design @ train_coefficients["full"][author]
        full_mse = float(np.mean((y_test - full_prediction) ** 2))
        condition_gains.append(
            float(np.mean((
                y_test
                - partner_design
                @ train_coefficients["no_condition"][author]
            ) ** 2))
            - full_mse
        )
        partner_gains.append(
            float(np.mean((
                y_test
                - condition_design
                @ train_coefficients["no_partner"][author]
            ) ** 2))
            - full_mse
        )
    by_author = {
        "condition_laplace_score_gain": np.asarray(condition_gains),
        "partner_laplace_score_gain": np.asarray(partner_gains),
    }
    return (
        {
            family: (train_features[family], test_features[family])
            for family in train_features
        },
        {
            name: float(np.mean(values))
            for name, values in by_author.items()
        },
        by_author,
    )


def _autocov(values: np.ndarray, lags: Iterable[int]) -> np.ndarray:
    output = []
    centered = values - values.mean()
    for lag in lags:
        if lag == 0:
            output.append(float(np.mean(centered * centered)))
        else:
            output.append(float(np.mean(centered[:-lag] * centered[lag:])))
    return np.asarray(output)


def _run_lengths(labels: np.ndarray) -> np.ndarray:
    changes = np.flatnonzero(np.diff(labels) != 0) + 1
    return np.diff(np.concatenate([[0], changes, [len(labels)]]))


def _hazard_profile(values: np.ndarray) -> np.ndarray:
    """Fixed nonparametric dwell-time object from a median state partition."""
    centered = values - np.median(values)
    labels = centered >= 0.0
    lengths = _run_lengths(labels)
    grid = np.asarray([1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])
    survival = np.asarray([np.mean(lengths >= point) for point in grid])
    hazard = np.asarray([
        np.sum(lengths == point) / max(np.sum(lengths >= point), 1)
        for point in grid[:-1]
    ])
    histogram = np.bincount(
        np.minimum(lengths, 32),
        minlength=33,
    )[1:].astype(float)
    histogram /= max(histogram.sum(), 1.0)
    quantiles = np.quantile(lengths, (0.25, 0.50, 0.75, 0.90, 0.95))
    return np.concatenate([survival, hazard, histogram, quantiles])


def _delay_windows(values: np.ndarray, delays: int) -> np.ndarray:
    if len(values) <= delays + 1:
        return np.zeros((1, delays + 1), dtype=float)
    windows = np.column_stack([
        values[delays - lag:len(values) - lag]
        for lag in range(delays + 1)
    ])
    windows -= windows.mean(axis=0, keepdims=True)
    windows /= np.maximum(windows.std(axis=0, keepdims=True), 1e-8)
    return windows


def _time_reversal_profile(
    values: np.ndarray,
    *,
    frequencies: np.ndarray,
) -> np.ndarray:
    """Signed ECF discrepancy between forward and reversed delay states."""
    windows = _delay_windows(values, frequencies.shape[1] - 1)
    reversed_windows = windows[:, ::-1]
    forward = windows @ frequencies.T
    backward = reversed_windows @ frequencies.T
    return np.concatenate([
        np.cos(forward).mean(axis=0) - np.cos(backward).mean(axis=0),
        np.sin(forward).mean(axis=0) - np.sin(backward).mean(axis=0),
    ])


def _rff(values: np.ndarray, omega: np.ndarray, phase: np.ndarray) -> np.ndarray:
    return np.sqrt(2.0 / len(phase)) * np.cos(values @ omega.T + phase)


def _delay_vamp_profile(
    values: np.ndarray,
    *,
    omega: np.ndarray,
    phase: np.ndarray,
    ridge: float = 0.08,
) -> np.ndarray:
    """Fixed RFF delay-state Koopman/VAMP operator coordinates."""
    windows = _delay_windows(values, omega.shape[1] - 1)
    if len(windows) < 3:
        return np.zeros(omega.shape[0] ** 2 + omega.shape[0], dtype=float)
    current = _rff(windows[:-1], omega, phase)
    following = _rff(windows[1:], omega, phase)
    current -= current.mean(axis=0, keepdims=True)
    following -= following.mean(axis=0, keepdims=True)
    covariance = current.T @ current / len(current)
    cross = current.T @ following / len(current)
    operator = np.linalg.solve(
        covariance + ridge * np.eye(len(covariance)),
        cross,
    )
    singular = np.linalg.svd(operator, compute_uv=False)
    return np.concatenate([operator.ravel(), singular])


def _fixed_frequencies(
    rng: np.random.Generator,
    *,
    count: int,
    dimensions: int,
) -> np.ndarray:
    omega = rng.normal(size=(count, dimensions))
    omega /= np.maximum(np.linalg.norm(omega, axis=1, keepdims=True), 1e-12)
    omega *= rng.choice((0.5, 1.0, 2.0, 4.0), size=(count, 1))
    return omega


def _path_features_by_occasion(
    panel: np.ndarray,
    *,
    reversal_frequencies: np.ndarray,
    vamp_frequencies: np.ndarray,
    vamp_phase: np.ndarray,
) -> dict[str, np.ndarray]:
    profiles: dict[str, list[list[np.ndarray]]] = {
        "path_second_order": [],
        "path_hazard": [],
        "path_time_reversal": [],
        "path_delay_vamp": [],
    }
    for author in range(panel.shape[0]):
        author_profiles = {name: [] for name in profiles}
        for occasion in range(panel.shape[1]):
            values = panel[author, occasion]
            second_order: list[float] = []
            hazard: list[float] = []
            reversal: list[float] = []
            vamp: list[float] = []
            for dimension in range(values.shape[1]):
                series = values[:, dimension]
                second_order.extend(_autocov(series, (0, 1, 2)))
                hazard.extend(_hazard_profile(series))
                reversal.extend(_time_reversal_profile(
                    series,
                    frequencies=reversal_frequencies,
                ))
                vamp.extend(_delay_vamp_profile(
                    series,
                    omega=vamp_frequencies,
                    phase=vamp_phase,
                ))
            author_profiles["path_second_order"].append(
                np.asarray(second_order)
            )
            author_profiles["path_hazard"].append(np.asarray(hazard))
            author_profiles["path_time_reversal"].append(
                np.asarray(reversal)
            )
            author_profiles["path_delay_vamp"].append(np.asarray(vamp))
        for name in profiles:
            profiles[name].append(author_profiles[name])
    return {
        name: np.asarray(values)
        for name, values in profiles.items()
    }


def _hazard_log_score_gain(
    train: np.ndarray,
    test: np.ndarray,
    *,
    maximum: int = 64,
) -> np.ndarray:
    """Author-wise held-out dwell log-score gain over leave-author-out pool."""
    authors, occasions, _, dimensions = train.shape

    def lengths(panel: np.ndarray, author: int, dimension: int) -> np.ndarray:
        blocks = []
        for occasion in range(occasions):
            values = panel[author, occasion, :, dimension]
            blocks.append(_run_lengths(values >= np.median(values)))
        return np.concatenate(blocks)

    def fit_hazard(values: np.ndarray) -> np.ndarray:
        clipped = np.minimum(values, maximum)
        return np.asarray([
            (np.sum(clipped == point) + 0.5)
            / (np.sum(clipped >= point) + 1.0)
            for point in range(1, maximum + 1)
        ])

    def score(hazard: np.ndarray, values: np.ndarray) -> float:
        clipped = np.minimum(values, maximum)
        logs = []
        for dwell in clipped:
            survived = np.log(
                np.maximum(1.0 - hazard[: max(dwell - 1, 0)], 1e-12)
            ).sum()
            ended = np.log(max(hazard[dwell - 1], 1e-12))
            logs.append(-(survived + ended))
        return float(np.mean(logs))

    gains = np.empty(authors, dtype=float)
    cache = {
        (split, author, dimension): lengths(
            train if split == "train" else test,
            author,
            dimension,
        )
        for split in ("train", "test")
        for author in range(authors)
        for dimension in range(dimensions)
    }
    for author in range(authors):
        dimension_gains = []
        for dimension in range(dimensions):
            own = fit_hazard(cache[("train", author, dimension)])
            pooled = fit_hazard(np.concatenate([
                cache[("train", other, dimension)]
                for other in range(authors)
                if other != author
            ]))
            target = cache[("test", author, dimension)]
            dimension_gains.append(score(pooled, target) - score(own, target))
        gains[author] = float(np.mean(dimension_gains))
    return gains


def _vamp_prediction_score_gain(
    train: np.ndarray,
    test: np.ndarray,
    *,
    omega: np.ndarray,
    phase: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Held-out RFF delay-state prediction gain over leave-author-out pool."""
    authors, occasions, _, dimensions = train.shape
    components = len(phase)

    def sufficient(
        panel: np.ndarray,
        author: int,
        dimension: int,
        selected_occasions: tuple[int, ...],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
        current_blocks = []
        following_blocks = []
        for occasion in selected_occasions:
            windows = _delay_windows(
                panel[author, occasion, :, dimension],
                omega.shape[1] - 1,
            )
            if len(windows) >= 2:
                current_blocks.append(_rff(windows[:-1], omega, phase))
                following_blocks.append(_rff(windows[1:], omega, phase))
        current = np.concatenate(current_blocks, axis=0)
        following = np.concatenate(following_blocks, axis=0)
        augmented = np.column_stack([current, np.ones(len(current))])
        return (
            augmented.T @ augmented,
            augmented.T @ following,
            np.column_stack([augmented, following]),
            len(current),
        )

    all_occasions = tuple(range(occasions))
    fit_occasions = tuple(range(0, occasions, 2))
    validation_occasions = tuple(range(1, occasions, 2))
    train_stats = {
        (author, dimension): sufficient(
            train,
            author,
            dimension,
            all_occasions,
        )
        for author in range(authors)
        for dimension in range(dimensions)
    }
    fit_stats = {
        (author, dimension): sufficient(
            train,
            author,
            dimension,
            fit_occasions,
        )
        for author in range(authors)
        for dimension in range(dimensions)
    }
    validation_pairs = {
        (author, dimension): sufficient(
            train,
            author,
            dimension,
            validation_occasions,
        )[2]
        for author in range(authors)
        for dimension in range(dimensions)
    }
    test_pairs = {
        (author, dimension): sufficient(
            test,
            author,
            dimension,
            all_occasions,
        )[2]
        for author in range(authors)
        for dimension in range(dimensions)
    }

    def operator(gram: np.ndarray, cross: np.ndarray) -> np.ndarray:
        penalty = np.eye(components + 1)
        penalty[-1, -1] = 0.0
        scale = max(
            1e-7,
            1e-4 * np.trace(gram[:-1, :-1]) / max(components, 1),
        )
        return np.linalg.solve(gram + scale * penalty, cross)

    def pooled_operator(
        stats: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray, int]],
        author: int,
        dimension: int,
    ) -> np.ndarray:
        gram = sum(
            stats[(other, dimension)][0]
            for other in range(authors)
            if other != author
        )
        cross = sum(
            stats[(other, dimension)][1]
            for other in range(authors)
            if other != author
        )
        return operator(gram, cross)

    shrinkage_grid = np.asarray([0.0, 0.10, 0.25, 0.50, 0.75, 1.0])
    validation_loss = np.zeros(len(shrinkage_grid), dtype=float)
    validation_count = 0
    for author in range(authors):
        for dimension in range(dimensions):
            own = operator(
                fit_stats[(author, dimension)][0],
                fit_stats[(author, dimension)][1],
            )
            pooled = pooled_operator(fit_stats, author, dimension)
            pairs = validation_pairs[(author, dimension)]
            current = pairs[:, :components + 1]
            following = pairs[:, components + 1:]
            for index, shrinkage in enumerate(shrinkage_grid):
                blended = pooled + shrinkage * (own - pooled)
                validation_loss[index] += float(np.sum(
                    (following - current @ blended) ** 2
                ))
            validation_count += int(following.size)
    validation_loss /= max(validation_count, 1)
    selected_shrinkage = float(shrinkage_grid[np.argmin(validation_loss)])

    gains = np.empty(authors, dtype=float)
    for author in range(authors):
        dimension_gains = []
        for dimension in range(dimensions):
            own_gram, own_cross, _, _ = train_stats[(author, dimension)]
            own_operator = operator(own_gram, own_cross)
            pooled = pooled_operator(train_stats, author, dimension)
            blended = pooled + selected_shrinkage * (
                own_operator - pooled
            )
            pairs = test_pairs[(author, dimension)]
            current = pairs[:, :components + 1]
            following = pairs[:, components + 1:]
            own_loss = np.mean((following - current @ blended) ** 2)
            pooled_loss = np.mean((following - current @ pooled) ** 2)
            dimension_gains.append(float(pooled_loss - own_loss))
        gains[author] = float(np.mean(dimension_gains))
    return gains, selected_shrinkage


def fit_m3_cross_family(
    observed: M3CrossFamilyObserved,
    *,
    seed: int,
    frequency_directions: int = 512,
    nystroem_components: int = 64,
    ridge: float = 0.35,
) -> M3CrossFamilyEstimate:
    """Fit one frozen estimator suite without generator-family information."""
    validate_cross_family_observed(observed)
    refusals: list[str] = []
    if observed.response_train.shape[1] < 2:
        refusals.append("NO_INDEPENDENT_OCCASION_REPLICATES")
    if not bool(observed.design.get("independent_replicates", False)):
        refusals.append("NO_INDEPENDENT_REPLICATES")
    if not bool(observed.design.get("common_support", False)):
        refusals.append("NO_COMMON_SUPPORT")
    if int(observed.design.get("partners", 0)) < 4:
        refusals.append("INSUFFICIENT_PARTNER_DEGREE")

    whitened_train, whitened_test = _pooled_whiten(
        observed.response_train,
        observed.response_test,
    )
    frequencies = _random_frequency_set(
        dimensions=observed.response_train.shape[-1],
        directions=frequency_directions,
        seed=seed + 101,
    )
    moment_views = _stability_weighted_views(
        _moment_profile_by_occasion(whitened_train),
        _moment_profile_by_occasion(whitened_test),
    )
    ecf_by_occasion_train = _rpecf_by_occasion(
        whitened_train,
        frequencies,
    )
    ecf_by_occasion_test = _rpecf_by_occasion(
        whitened_test,
        frequencies,
    )
    ecf_views = (
        ecf_by_occasion_train.mean(axis=1),
        ecf_by_occasion_test.mean(axis=1),
    )
    raw: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "moments_degree4": moment_views,
        "distribution_ecf": ecf_views,
    }
    heldout_by_author: dict[str, np.ndarray] = {
        "distribution_ecf_score_gain": _ecf_proper_score_gain(
            ecf_by_occasion_train,
            ecf_by_occasion_test,
            samples_per_author=(
                observed.response_train.shape[1]
                * observed.response_train.shape[2]
            ),
        ),
        "moments_degree4_score_gain": _heldout_feature_score(*moment_views),
    }
    operator_features, operator_heldout, operator_by_author = _operator_features(
        observed,
        seed=seed + 211,
        n_components=nystroem_components,
        ridge=ridge,
    )
    raw.update(operator_features)
    heldout_by_author.update(operator_by_author)

    path_rng = np.random.default_rng(seed + 307)
    reversal_frequencies = _fixed_frequencies(
        path_rng,
        count=96,
        dimensions=4,
    )
    vamp_frequencies = _fixed_frequencies(
        path_rng,
        count=20,
        dimensions=5,
    )
    vamp_phase = path_rng.uniform(0.0, 2.0 * np.pi, size=20)
    path_whitened_train, path_whitened_test = _pooled_pca_whiten(
        observed.response_train,
        observed.response_test,
    )
    path_train = _path_features_by_occasion(
        path_whitened_train,
        reversal_frequencies=reversal_frequencies,
        vamp_frequencies=vamp_frequencies,
        vamp_phase=vamp_phase,
    )
    path_test = _path_features_by_occasion(
        path_whitened_test,
        reversal_frequencies=reversal_frequencies,
        vamp_frequencies=vamp_frequencies,
        vamp_phase=vamp_phase,
    )
    for family in (
        "path_second_order",
        "path_hazard",
        "path_time_reversal",
        "path_delay_vamp",
    ):
        views = _stability_weighted_views(
            path_train[family],
            path_test[family],
            minimum_features=3 if family == "path_second_order" else 24,
        )
        raw[family] = views
        heldout_by_author[f"{family}_score_gain"] = _heldout_feature_score(
            *views
        )
    heldout_by_author["path_hazard_score_gain"] = _hazard_log_score_gain(
        path_whitened_train,
        path_whitened_test,
    )
    vamp_gain, vamp_shrinkage = _vamp_prediction_score_gain(
        path_whitened_train,
        path_whitened_test,
        omega=vamp_frequencies,
        phase=vamp_phase,
    )
    heldout_by_author["path_delay_vamp_score_gain"] = vamp_gain

    train_features: dict[str, np.ndarray] = {}
    test_features: dict[str, np.ndarray] = {}
    for family, (train, test) in raw.items():
        train_features[family], test_features[family] = _standardize_pair(
            train,
            test,
        )
    return M3CrossFamilyEstimate(
        train_features=train_features,
        test_features=test_features,
        heldout_metrics={
            **operator_heldout,
            "path_delay_vamp_selected_shrinkage": vamp_shrinkage,
            **{
                name: float(np.mean(values))
                for name, values in heldout_by_author.items()
                if name not in operator_heldout
            },
        },
        heldout_by_author=heldout_by_author,
        refusals=tuple(refusals),
    )
