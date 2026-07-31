"""Estimator for SUICA M4 mechanism-composition signatures.

The estimator separates two games:

* an observational held-out game, which preserves dependence among drivers;
* a product-reference game, which breaks driver dependence while preserving
  each marginal and the fitted response law.

Their difference distinguishes structural interaction from contribution
created by redundant or suppressive dependence.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np

from .m4_composition_contracts import (
    M4CompositionEstimate,
    M4CompositionObserved,
    validate_composition_estimate,
    validate_composition_observed,
)


Subset = tuple[int, ...]


def subset_lattice(mechanisms: int, max_order: int) -> tuple[Subset, ...]:
    """Return the non-empty subset lattice in deterministic order."""
    if mechanisms < 1:
        raise ValueError("mechanisms must be positive")
    if not 1 <= max_order <= mechanisms:
        raise ValueError("max_order must be within the mechanism dimension")
    return tuple(
        subset
        for order in range(1, max_order + 1)
        for subset in combinations(range(mechanisms), order)
    )


def mobius_dividends(
    values: dict[Subset, float],
    *,
    subsets: tuple[Subset, ...],
) -> dict[Subset, float]:
    """Apply exact subset-lattice Möbius inversion."""
    dividends: dict[Subset, float] = {}
    for subset in subsets:
        subtotal = sum(
            value
            for lower, value in dividends.items()
            if len(lower) < len(subset) and set(lower).issubset(subset)
        )
        dividends[subset] = float(values.get(subset, 0.0) - subtotal)
    return dividends


def shapley_from_dividends(
    dividends: dict[Subset, float],
    mechanisms: int,
) -> np.ndarray:
    """Compress a truncated Harsanyi lattice into Shapley allocations."""
    output = np.zeros(mechanisms, dtype=float)
    for subset, value in dividends.items():
        share = value / len(subset)
        for mechanism in subset:
            output[mechanism] += share
    return output


def _standardize(
    fit: np.ndarray,
    target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    center = fit.mean(axis=0, keepdims=True)
    scale = fit.std(axis=0, ddof=0, keepdims=True)
    scale = np.where(scale > 1e-8, scale, 1.0)
    return (fit - center) / scale, (target - center) / scale


def _monomial_design(
    drivers: np.ndarray,
    terms: tuple[Subset, ...],
) -> np.ndarray:
    if not terms:
        return np.empty((len(drivers), 0), dtype=float)
    return np.column_stack([
        np.prod(drivers[:, term], axis=1)
        for term in terms
    ])


def _ridge_coefficients(
    design: np.ndarray,
    response: np.ndarray,
    *,
    ridge: float,
) -> tuple[float, np.ndarray]:
    augmented = np.column_stack([np.ones(len(design)), design])
    gram = augmented.T @ augmented
    penalty = ridge * np.eye(gram.shape[0])
    penalty[0, 0] = 0.0
    coefficient = np.linalg.solve(
        gram + penalty,
        augmented.T @ response,
    )
    return float(coefficient[0]), coefficient[1:]


def _predict(
    design: np.ndarray,
    intercept: float,
    coefficient: np.ndarray,
) -> np.ndarray:
    return intercept + design @ coefficient


def _proper_value(
    response: np.ndarray,
    prediction: np.ndarray,
    baseline: float,
) -> float:
    baseline_error = float(np.mean((response - baseline) ** 2))
    if baseline_error <= 1e-12:
        return 0.0
    model_error = float(np.mean((response - prediction) ** 2))
    return float(1.0 - model_error / baseline_error)


def _coalition_terms(
    coalition: Subset,
    lattice: tuple[Subset, ...],
) -> tuple[Subset, ...]:
    selected = set(coalition)
    return tuple(term for term in lattice if set(term).issubset(selected))


def _observational_game(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    *,
    lattice: tuple[Subset, ...],
    ridge: float,
) -> dict[Subset, float]:
    values: dict[Subset, float] = {}
    baseline = float(np.mean(y_fit))
    for coalition in lattice:
        terms = _coalition_terms(coalition, lattice)
        fit_design = _monomial_design(x_fit, terms)
        eval_design = _monomial_design(x_eval, terms)
        intercept, coefficient = _ridge_coefficients(
            fit_design,
            y_fit,
            ridge=ridge,
        )
        values[coalition] = _proper_value(
            y_eval,
            _predict(eval_design, intercept, coefficient),
            baseline,
        )
    return values


def _product_reference_game(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    *,
    lattice: tuple[Subset, ...],
    ridge: float,
    rng: np.random.Generator,
) -> tuple[dict[Subset, float], dict[Subset, float], float, float]:
    """Estimate structural coalition energy after breaking driver dependence."""
    fit_design = _monomial_design(x_fit, lattice)
    intercept, coefficient = _ridge_coefficients(
        fit_design,
        y_fit,
        ridge=ridge,
    )
    heldout = _proper_value(
        y_eval,
        _predict(
            _monomial_design(x_eval, lattice),
            intercept,
            coefficient,
        ),
        float(np.mean(y_fit)),
    )
    product = np.empty_like(x_eval)
    for column in range(x_eval.shape[1]):
        product[:, column] = x_eval[rng.permutation(len(x_eval)), column]
    product_design = _monomial_design(product, lattice)
    full = _predict(product_design, intercept, coefficient)
    denominator = float(np.var(full, ddof=0))
    if denominator <= 1e-12:
        return (
            {subset: 0.0 for subset in lattice},
            {subset: 0.0 for subset in lattice},
            0.0,
            heldout,
        )

    values: dict[Subset, float] = {}
    for coalition in lattice:
        positions = [
            index
            for index, term in enumerate(lattice)
            if set(term).issubset(coalition)
        ]
        prediction = np.full(len(product), intercept, dtype=float)
        if positions:
            prediction += (
                product_design[:, positions] @ coefficient[positions]
            )
        values[coalition] = float(np.var(prediction, ddof=0) / denominator)
    signs = {
        term: float(np.sign(coefficient[index]))
        for index, term in enumerate(lattice)
    }
    return values, signs, denominator, heldout


def _project(values: np.ndarray, predictor: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(predictor)), predictor])
    coefficient = np.linalg.solve(
        design.T @ design + 1e-6 * np.eye(design.shape[1]),
        design.T @ values,
    )
    return design @ coefficient


def _projection_commutator(
    response: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    left = _project(_project(response, second), first)
    right = _project(_project(response, first), second)
    denominator = float(np.linalg.norm(response - np.mean(response)))
    if denominator <= 1e-12:
        return 0.0
    return float(np.linalg.norm(left - right) / denominator)


def _slope(response: np.ndarray, predictor: np.ndarray) -> float:
    centered = predictor - np.mean(predictor)
    denominator = float(np.dot(centered, centered))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(centered, response - np.mean(response)) / denominator)


def _gate_direction(
    response: np.ndarray,
    target: np.ndarray,
    gate: np.ndarray,
) -> float:
    threshold = float(np.median(gate))
    high = gate > threshold
    low = ~high
    if np.sum(high) < 8 or np.sum(low) < 8:
        return 0.0
    high_slope = _slope(response[high], target[high])
    low_slope = _slope(response[low], target[low])
    # A symmetric product changes slope sign across the split; a gate keeps
    # the response orientation but changes its magnitude or turns it off.
    if high_slope * low_slope < 0.0:
        return 0.0
    return float(max(
        0.0,
        (abs(high_slope) - abs(low_slope))
        / (abs(high_slope) + abs(low_slope) + 1e-12),
    ))


def _alias_score(drivers: np.ndarray) -> tuple[float, bool]:
    correlation = np.corrcoef(drivers, rowvar=False)
    off_diagonal = correlation - np.eye(correlation.shape[0])
    maximum = float(np.max(np.abs(off_diagonal)))
    singular = np.linalg.svd(
        np.cov(drivers, rowvar=False),
        compute_uv=False,
    )
    condition = float(singular[0] / max(singular[-1], 1e-15))
    refusal = bool(maximum >= 0.9995 or condition >= 1e8)
    return maximum, refusal


def _average_games(
    games: list[dict[Subset, float]],
    lattice: tuple[Subset, ...],
) -> dict[Subset, float]:
    return {
        subset: float(np.mean([game[subset] for game in games]))
        for subset in lattice
    }


def _estimate_author(
    drivers: np.ndarray,
    response: np.ndarray,
    *,
    lattice: tuple[Subset, ...],
    ridge: float,
    seed: int,
) -> dict[str, float]:
    occasions = drivers.shape[0]
    folds = [
        (
            np.arange(occasions) % 2 == parity,
            np.arange(occasions) % 2 != parity,
        )
        for parity in (0, 1)
    ]
    observational: list[dict[Subset, float]] = []
    product: list[dict[Subset, float]] = []
    signs: list[dict[Subset, float]] = []
    full_energies: list[float] = []
    heldout_full_values: list[float] = []
    for fold_index, (fit_mask, eval_mask) in enumerate(folds):
        x_fit_raw = drivers[fit_mask].reshape(-1, drivers.shape[-1])
        x_eval_raw = drivers[eval_mask].reshape(-1, drivers.shape[-1])
        y_fit = response[fit_mask].reshape(-1)
        y_eval = response[eval_mask].reshape(-1)
        x_fit, x_eval = _standardize(x_fit_raw, x_eval_raw)
        observational.append(
            _observational_game(
                x_fit,
                y_fit,
                x_eval,
                y_eval,
                lattice=lattice,
                ridge=ridge,
            )
        )
        (
            product_game,
            coefficient_sign,
            energy,
            heldout_full,
        ) = _product_reference_game(
            x_fit,
            y_fit,
            x_eval,
            y_eval,
            lattice=lattice,
            ridge=ridge,
            rng=np.random.default_rng(seed + 10_003 * (fold_index + 1)),
        )
        product.append(product_game)
        signs.append(coefficient_sign)
        full_energies.append(energy)
        heldout_full_values.append(heldout_full)

    observational_values = _average_games(observational, lattice)
    product_values = _average_games(product, lattice)
    observational_dividends = mobius_dividends(
        observational_values,
        subsets=lattice,
    )
    product_dividends = mobius_dividends(
        product_values,
        subsets=lattice,
    )
    coefficient_signs = {
        subset: float(np.sign(np.mean([item[subset] for item in signs])))
        for subset in lattice
    }

    x_all_raw = drivers.reshape(-1, drivers.shape[-1])
    y_all = response.reshape(-1)
    x_all, _ = _standardize(x_all_raw, x_all_raw)
    alias, refusal = _alias_score(x_all)
    metrics: dict[str, float] = {
        "alias_score": alias,
        "refusal": float(refusal),
        "product_signal_energy": float(np.mean(full_energies)),
        "heldout_full_value": float(np.mean(heldout_full_values)),
    }
    for subset in lattice:
        key = "&".join(str(value) for value in subset)
        metrics[f"obs_value|{key}"] = observational_values[subset]
        metrics[f"obs_div|{key}"] = observational_dividends[subset]
        metrics[f"product_value|{key}"] = product_values[subset]
        metrics[f"product_div|{key}"] = product_dividends[subset]
        metrics[f"dependence_gap|{key}"] = (
            observational_dividends[subset] - product_dividends[subset]
        )
        metrics[f"coefficient_sign|{key}"] = coefficient_signs[subset]

    mechanisms = drivers.shape[-1]
    for first, second in combinations(range(mechanisms), 2):
        key = f"{first}&{second}"
        metrics[f"commutator|{key}"] = _projection_commutator(
            y_all,
            x_all[:, first],
            x_all[:, second],
        )
        metrics[f"gate|{first}->{second}"] = _gate_direction(
            y_all,
            x_all[:, second],
            x_all[:, first],
        )
        metrics[f"gate|{second}->{first}"] = _gate_direction(
            y_all,
            x_all[:, first],
            x_all[:, second],
        )

    observational_shapley = shapley_from_dividends(
        observational_dividends,
        mechanisms,
    )
    product_shapley = shapley_from_dividends(
        product_dividends,
        mechanisms,
    )
    for mechanism in range(mechanisms):
        metrics[f"obs_shapley|{mechanism}"] = float(
            observational_shapley[mechanism]
        )
        metrics[f"product_shapley|{mechanism}"] = float(
            product_shapley[mechanism]
        )
    return metrics


def _panel_metrics(
    drivers: np.ndarray,
    response: np.ndarray,
    *,
    lattice: tuple[Subset, ...],
    ridge: float,
    seed: int,
) -> dict[str, np.ndarray]:
    rows = [
        _estimate_author(
            drivers[author],
            response[author],
            lattice=lattice,
            ridge=ridge,
            seed=seed + 100_003 * author,
        )
        for author in range(len(drivers))
    ]
    names = tuple(sorted(rows[0]))
    return {
        name: np.asarray([row[name] for row in rows], dtype=float)
        for name in names
    }


def _signature(
    metrics: dict[str, np.ndarray],
) -> tuple[np.ndarray, tuple[str, ...]]:
    names = tuple(
        name
        for name in sorted(metrics)
        if name != "refusal"
    )
    return np.column_stack([metrics[name] for name in names]), names


def fit_m4_composition(
    observed: M4CompositionObserved,
    *,
    max_order: int = 3,
    ridge: float = 0.05,
    seed: int = 1_618_033,
) -> M4CompositionEstimate:
    """Recover a two-view author mechanism-composition signature."""
    validate_composition_observed(observed)
    lattice = subset_lattice(len(observed.mechanism_names), max_order)
    train_metrics = _panel_metrics(
        observed.drivers_train,
        observed.response_train,
        lattice=lattice,
        ridge=ridge,
        seed=seed,
    )
    test_metrics = _panel_metrics(
        observed.drivers_test,
        observed.response_test,
        lattice=lattice,
        ridge=ridge,
        seed=seed + 70_000_031,
    )
    train_raw, names = _signature(train_metrics)
    test_raw, test_names = _signature(test_metrics)
    if names != test_names:
        raise RuntimeError("train/test signature features do not match")
    center = train_raw.mean(axis=0, keepdims=True)
    scale = train_raw.std(axis=0, ddof=0, keepdims=True)
    scale = np.where(scale > 1e-8, scale, 1.0)
    estimate = M4CompositionEstimate(
        train_signature=(train_raw - center) / scale,
        test_signature=(test_raw - center) / scale,
        feature_names=names,
        train_metrics=train_metrics,
        test_metrics=test_metrics,
        train_refusal=train_metrics["refusal"].astype(bool),
        test_refusal=test_metrics["refusal"].astype(bool),
    )
    validate_composition_estimate(
        estimate,
        authors=observed.drivers_train.shape[0],
    )
    return estimate
