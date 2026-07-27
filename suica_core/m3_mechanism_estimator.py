"""Competing out-of-generator summaries for the M3 mechanism atlas."""
from __future__ import annotations

import numpy as np

from .m3_mechanism_contracts import (
    M3MechanismEstimate,
    M3MechanismObserved,
    validate_mechanism_observed,
)


MECHANISM_FAMILIES = (
    "mean_position",
    "distribution_kme",
    "conditional_operator",
    "koopman_spectrum",
    "interaction_coupling",
    "higher_order_path",
    "opportunity_profile",
)


def _flatten_panel(values: np.ndarray) -> np.ndarray:
    return np.asarray(values, dtype=float).reshape(values.shape[0], -1, values.shape[-1])


def _ridge_operator(
    predictor: np.ndarray,
    response: np.ndarray,
    *,
    ridge: float = 0.10,
    intercept: bool = True,
) -> np.ndarray:
    """Fit one response-by-predictor slope operator per author.

    Intercepts are fitted when requested but never returned as part of the
    operator. This prevents stable position or opportunity exposure from
    masquerading as conditional response or partner coupling.
    """
    x_values = _flatten_panel(predictor)
    y_values = _flatten_panel(response)
    authors = x_values.shape[0]
    outputs: list[np.ndarray] = []
    for author in range(authors):
        x_author = x_values[author]
        y_author = y_values[author]
        if intercept:
            x_author = np.column_stack([
                np.ones(len(x_author)),
                x_author,
            ])
        gram = x_author.T @ x_author
        penalty = ridge * np.eye(gram.shape[0])
        if intercept:
            penalty[0, 0] = 0.0
        coefficients = np.linalg.solve(
            gram + penalty,
            x_author.T @ y_author,
        )
        if intercept:
            coefficients = coefficients[1:]
        outputs.append(coefficients.T.ravel())
    return np.asarray(outputs)


def _pooled_condition_residual(
    train_condition: np.ndarray,
    train_response: np.ndarray,
    target_condition: np.ndarray,
    target_response: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Remove only the pooled opportunity-response law fit on train events."""
    x_train = _flatten_panel(train_condition).reshape(-1, train_condition.shape[-1])
    y_train = _flatten_panel(train_response).reshape(-1, train_response.shape[-1])
    x_train_augmented = np.column_stack([np.ones(len(x_train)), x_train])
    coefficients = np.linalg.solve(
        x_train_augmented.T @ x_train_augmented
        + 0.10 * np.diag([0.0] + [1.0] * x_train.shape[1]),
        x_train_augmented.T @ y_train,
    )

    def residual(condition: np.ndarray, response: np.ndarray) -> np.ndarray:
        shape = response.shape
        x_values = _flatten_panel(condition).reshape(-1, condition.shape[-1])
        prediction = np.column_stack([
            np.ones(len(x_values)),
            x_values,
        ]) @ coefficients
        return (
            _flatten_panel(response).reshape(-1, response.shape[-1])
            - prediction
        ).reshape(shape)

    return (
        residual(train_condition, train_response),
        residual(target_condition, target_response),
    )


def _kme_features(
    train: np.ndarray,
    test: np.ndarray,
    *,
    seed: int,
    frequencies: int = 48,
) -> tuple[np.ndarray, np.ndarray]:
    pooled = _flatten_panel(train).reshape(-1, train.shape[-1])
    rng = np.random.default_rng(seed)
    sample_size = min(len(pooled), 1_200)
    sample = pooled[rng.choice(len(pooled), size=sample_size, replace=False)]
    paired = sample[rng.permutation(len(sample))]
    distances = np.linalg.norm(sample - paired, axis=1)
    bandwidth = float(np.median(distances[distances > 1e-8]))
    if not np.isfinite(bandwidth) or bandwidth <= 1e-8:
        bandwidth = 1.0
    omega = rng.normal(
        scale=1.0 / bandwidth,
        size=(train.shape[-1], frequencies),
    )
    phase = rng.uniform(0.0, 2.0 * np.pi, size=frequencies)

    def transform(panel: np.ndarray) -> np.ndarray:
        values = _flatten_panel(panel)
        projection = np.einsum("und,df->unf", values, omega) + phase
        return np.sqrt(2.0 / frequencies) * np.concatenate([
            np.cos(projection).mean(axis=1),
            np.sin(projection).mean(axis=1),
        ], axis=1)

    return transform(train), transform(test)


def _centered_paths(panel: np.ndarray) -> np.ndarray:
    values = np.asarray(panel, dtype=float)
    return values - values.mean(axis=(1, 2), keepdims=True)


def _lag_operator(panel: np.ndarray, lag: int, *, ridge: float = 0.20) -> np.ndarray:
    values = _centered_paths(panel)
    authors, occasions, _, dimensions = values.shape
    operators = np.empty((authors, dimensions, dimensions), dtype=float)
    for author in range(authors):
        previous = values[author, :, :-lag].reshape(-1, dimensions)
        current = values[author, :, lag:].reshape(-1, dimensions)
        gram = previous.T @ previous + ridge * np.eye(dimensions)
        operators[author] = np.linalg.solve(
            gram,
            previous.T @ current,
        ).T
    return operators


def _koopman_features(panel: np.ndarray) -> np.ndarray:
    operator = _lag_operator(panel, 1)
    spectral: list[np.ndarray] = []
    for matrix in operator:
        values = np.linalg.eigvals(matrix)
        order = np.argsort(-np.abs(values))
        values = values[order]
        spectral.append(np.concatenate([
            np.abs(values),
            np.real(values),
            np.imag(values),
        ]))
    return np.column_stack([
        operator.reshape(len(operator), -1),
        np.asarray(spectral),
    ])


def _higher_order_features(panel: np.ndarray) -> np.ndarray:
    lag_one = _lag_operator(panel, 1)
    lag_two = _lag_operator(panel, 2)
    memory = lag_two - np.einsum("uij,ujk->uik", lag_one, lag_one)
    singular = np.asarray([
        np.linalg.svd(matrix, compute_uv=False)
        for matrix in memory
    ])
    eigenvalue = np.asarray([
        np.sort(np.abs(np.linalg.eigvals(matrix)))[::-1]
        for matrix in memory
    ])
    # The spectrum is invariant to a common rotation and avoids treating every
    # noisy matrix entry as a separate author signal.
    return np.column_stack([
        singular,
        eigenvalue,
        np.trace(memory, axis1=1, axis2=2),
        np.linalg.norm(memory, axis=(1, 2)),
    ])


def _opportunity_features(panel: np.ndarray) -> np.ndarray:
    values = _flatten_panel(panel)
    # Opportunity location is the estimand in the current confound world.
    # Covariance belongs to a separate opportunity-shape mechanism and would
    # dilute location with finite-sample noise.
    return values.mean(axis=1)


def _standardize_cross_view(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    center = train.mean(axis=0, keepdims=True)
    scale = train.std(axis=0, ddof=0, keepdims=True)
    keep = scale.ravel() > 1e-8
    if not np.any(keep):
        return (
            np.zeros((len(train), 1), dtype=float),
            np.zeros((len(test), 1), dtype=float),
        )
    return (
        (train[:, keep] - center[:, keep]) / scale[:, keep],
        (test[:, keep] - center[:, keep]) / scale[:, keep],
    )


def fit_m3_mechanism_atlas(
    observed: M3MechanismObserved,
    *,
    seed: int,
) -> M3MechanismEstimate:
    """Extract mutually competing mesoscopic summaries from event panels."""
    validate_mechanism_observed(observed)
    residual_train, residual_test = _pooled_condition_residual(
        observed.condition_train,
        observed.response_train,
        observed.condition_test,
        observed.response_test,
    )
    distribution_train, distribution_test = _kme_features(
        residual_train,
        residual_test,
        seed=seed,
    )
    raw: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "mean_position": (
            _flatten_panel(observed.response_train).mean(axis=1),
            _flatten_panel(observed.response_test).mean(axis=1),
        ),
        "distribution_kme": (distribution_train, distribution_test),
        "conditional_operator": (
            _ridge_operator(observed.condition_train, observed.response_train),
            _ridge_operator(observed.condition_test, observed.response_test),
        ),
        "koopman_spectrum": (
            _koopman_features(residual_train),
            _koopman_features(residual_test),
        ),
        "interaction_coupling": (
            _ridge_operator(observed.partner_train, observed.response_train),
            _ridge_operator(observed.partner_test, observed.response_test),
        ),
        "higher_order_path": (
            _higher_order_features(residual_train),
            _higher_order_features(residual_test),
        ),
        "opportunity_profile": (
            _opportunity_features(observed.condition_train),
            _opportunity_features(observed.condition_test),
        ),
    }
    train_features: dict[str, np.ndarray] = {}
    test_features: dict[str, np.ndarray] = {}
    for family, (train, test) in raw.items():
        standardized = _standardize_cross_view(train, test)
        train_features[family] = standardized[0]
        test_features[family] = standardized[1]
    train_features["union"] = np.concatenate([
        train_features[family] / np.sqrt(train_features[family].shape[1])
        for family in MECHANISM_FAMILIES
        if family != "mean_position"
    ], axis=1)
    test_features["union"] = np.concatenate([
        test_features[family] / np.sqrt(test_features[family].shape[1])
        for family in MECHANISM_FAMILIES
        if family != "mean_position"
    ], axis=1)
    return M3MechanismEstimate(
        train_features=train_features,
        test_features=test_features,
    )
