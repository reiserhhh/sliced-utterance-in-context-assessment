"""Higher-order estimators and cheap-statistic attacks for M3 Atlas V1."""
from __future__ import annotations

import numpy as np

from .m3_mechanism_contracts import M3MechanismEstimate, M3MechanismObserved
from .m3_mechanism_estimator import fit_m3_mechanism_atlas


STRESS_FAMILIES = (
    "covariance_profile",
    "distribution_kme",
    "standardized_distribution_shape",
    "linear_condition",
    "nonlinear_condition",
    "lag1_spectrum",
    "ar2_slow_spectrum",
    "lag2_memory",
    "lag3_memory",
    "lag3_partial_operator",
    "linear_partner",
    "nonlinear_partner",
)


def _flatten(panel: np.ndarray) -> np.ndarray:
    return np.asarray(panel, dtype=float).reshape(panel.shape[0], -1, panel.shape[-1])


def _standardize(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    center = train.mean(axis=0, keepdims=True)
    variance = np.var(train, axis=0, ddof=0)
    keep = variance > 1e-12
    if not np.any(keep):
        zeros = np.zeros((len(train), 1), dtype=float)
        return zeros, zeros.copy()
    # A shared tensor scale preserves the relative energy of coefficients.
    # Per-coordinate z-scoring would inflate null coefficient noise to unit
    # variance and erase the operator's signal hierarchy.
    scale = float(np.sqrt(np.mean(variance[keep])))
    scale = max(scale, 1e-8)
    return (
        (train[:, keep] - center[:, keep]) / scale,
        (test[:, keep] - center[:, keep]) / scale,
    )


def _covariance(panel: np.ndarray) -> np.ndarray:
    return np.asarray([
        np.cov(author, rowvar=False, ddof=0).ravel()
        for author in _flatten(panel)
    ])


def _standardized_ecf(panel: np.ndarray) -> np.ndarray:
    """Multiscale empirical characteristic function after author whitening."""
    values = _flatten(panel)
    center = values.mean(axis=1, keepdims=True)
    scale = values.std(axis=1, ddof=0, keepdims=True)
    standardized = (values - center) / np.maximum(scale, 1e-8)
    frequencies = np.asarray([0.35, 0.70, 1.40, 2.80, 5.60])
    projection = standardized[..., None] * frequencies
    marginal = np.concatenate([
        np.cos(projection).mean(axis=1).reshape(len(values), -1),
        np.sin(projection).mean(axis=1).reshape(len(values), -1),
    ], axis=1)
    # Radial characteristic values capture joint shape without selecting a
    # privileged response coordinate.
    radius = np.linalg.norm(standardized, axis=2)
    radial_projection = radius[..., None] * frequencies
    radial = np.concatenate([
        np.cos(radial_projection).mean(axis=1),
        np.sin(radial_projection).mean(axis=1),
    ], axis=1)
    return np.column_stack([marginal, radial])


def _hermite_design(panel: np.ndarray) -> np.ndarray:
    values = _flatten(panel)
    return np.concatenate([
        values,
        (values ** 2 - 1.0) / np.sqrt(2.0),
        (values ** 3 - 3.0 * values) / np.sqrt(6.0),
    ], axis=2)


def _operator(
    predictor: np.ndarray,
    response: np.ndarray,
    *,
    keep_from: int = 0,
    ridge: float = 0.20,
) -> np.ndarray:
    x_values = _flatten(predictor)
    y_values = _flatten(response)
    output: list[np.ndarray] = []
    for x_author, y_author in zip(x_values, y_values, strict=True):
        x_centered = x_author - x_author.mean(axis=0, keepdims=True)
        y_centered = y_author - y_author.mean(axis=0, keepdims=True)
        coefficients = np.linalg.solve(
            x_centered.T @ x_centered
            + ridge * np.eye(x_centered.shape[1]),
            x_centered.T @ y_centered,
        )
        output.append(coefficients[keep_from:].T.ravel())
    return np.asarray(output)


def _var_operator(panel: np.ndarray, lags: int) -> np.ndarray:
    values = np.asarray(panel, dtype=float)
    values = values - values.mean(axis=(1, 2), keepdims=True)
    authors, occasions, events, dimensions = values.shape
    coefficients = np.empty(
        (authors, lags, dimensions, dimensions),
        dtype=float,
    )
    for author in range(authors):
        predictors: list[np.ndarray] = []
        targets: list[np.ndarray] = []
        for occasion in range(occasions):
            target = values[author, occasion, lags:]
            lagged = np.concatenate([
                values[author, occasion, lags - lag - 1:events - lag - 1]
                for lag in range(lags)
            ], axis=1)
            predictors.append(lagged)
            targets.append(target)
        x_values = np.concatenate(predictors)
        y_values = np.concatenate(targets)
        estimate = np.linalg.solve(
            x_values.T @ x_values
            + 0.30 * np.eye(x_values.shape[1]),
            x_values.T @ y_values,
        )
        coefficients[author] = estimate.reshape(
            lags,
            dimensions,
            dimensions,
        ).transpose(0, 2, 1)
    return coefficients


def _companion_features(coefficients: np.ndarray) -> np.ndarray:
    authors, lags, dimensions, _ = coefficients.shape
    features: list[np.ndarray] = []
    for author in range(authors):
        companion = np.zeros(
            (lags * dimensions, lags * dimensions),
            dtype=float,
        )
        companion[:dimensions] = np.concatenate(
            list(coefficients[author]),
            axis=1,
        )
        if lags > 1:
            companion[dimensions:, :-dimensions] = np.eye(
                (lags - 1) * dimensions
            )
        eigenvalues = np.linalg.eigvals(companion)
        eigenvalues = eigenvalues[np.argsort(-np.abs(eigenvalues))]
        features.append(np.concatenate([
            coefficients[author].ravel(),
            np.abs(eigenvalues),
            np.real(eigenvalues),
        ]))
    return np.asarray(features)


def _partial_lag_features(panel: np.ndarray, lag: int) -> np.ndarray:
    coefficients = _var_operator(panel, lag)
    partial = coefficients[:, lag - 1]
    singular = np.asarray([
        np.linalg.svd(matrix, compute_uv=False)
        for matrix in partial
    ])
    eigenvalue = np.asarray([
        np.sort(np.abs(np.linalg.eigvals(matrix)))[::-1]
        for matrix in partial
    ])
    return np.column_stack([
        partial.reshape(len(partial), -1),
        singular,
        eigenvalue,
    ])


def fit_m3_mechanism_stress(
    observed: M3MechanismObserved,
    *,
    seed: int,
) -> M3MechanismEstimate:
    """Fit cheap and higher-order summaries without access to stress truth."""
    base = fit_m3_mechanism_atlas(observed, seed=seed)
    response = (observed.response_train, observed.response_test)
    condition_hermite = (
        _hermite_design(observed.condition_train),
        _hermite_design(observed.condition_test),
    )
    partner_hermite = (
        _hermite_design(observed.partner_train),
        _hermite_design(observed.partner_test),
    )
    dimensions = observed.condition_train.shape[-1]
    raw = {
        "covariance_profile": (
            _covariance(response[0]),
            _covariance(response[1]),
        ),
        "distribution_kme": (
            base.train_features["distribution_kme"],
            base.test_features["distribution_kme"],
        ),
        "standardized_distribution_shape": (
            _standardized_ecf(response[0]),
            _standardized_ecf(response[1]),
        ),
        "linear_condition": (
            base.train_features["conditional_operator"],
            base.test_features["conditional_operator"],
        ),
        "nonlinear_condition": (
            _operator(
                condition_hermite[0],
                response[0],
                keep_from=dimensions,
            ),
            _operator(
                condition_hermite[1],
                response[1],
                keep_from=dimensions,
            ),
        ),
        "lag1_spectrum": (
            base.train_features["koopman_spectrum"],
            base.test_features["koopman_spectrum"],
        ),
        "ar2_slow_spectrum": (
            _companion_features(_var_operator(response[0], 2)),
            _companion_features(_var_operator(response[1], 2)),
        ),
        "lag2_memory": (
            base.train_features["higher_order_path"],
            base.test_features["higher_order_path"],
        ),
        "lag3_memory": (
            _companion_features(_var_operator(response[0], 3))[
                :, -(3 * observed.response_train.shape[-1]) * 2:
            ],
            _companion_features(_var_operator(response[1], 3))[
                :, -(3 * observed.response_test.shape[-1]) * 2:
            ],
        ),
        "lag3_partial_operator": (
            _partial_lag_features(response[0], 3),
            _partial_lag_features(response[1], 3),
        ),
        "linear_partner": (
            base.train_features["interaction_coupling"],
            base.test_features["interaction_coupling"],
        ),
        "nonlinear_partner": (
            _operator(
                partner_hermite[0],
                response[0],
                keep_from=dimensions,
            ),
            _operator(
                partner_hermite[1],
                response[1],
                keep_from=dimensions,
            ),
        ),
    }
    train: dict[str, np.ndarray] = {}
    test: dict[str, np.ndarray] = {}
    for family, pair in raw.items():
        standardized = _standardize(pair[0], pair[1])
        train[family] = standardized[0]
        test[family] = standardized[1]
    return M3MechanismEstimate(train_features=train, test_features=test)
