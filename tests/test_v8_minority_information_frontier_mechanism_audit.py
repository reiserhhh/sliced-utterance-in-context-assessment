"""Tests for the H4D-R2 mechanism audit."""
from __future__ import annotations

import numpy as np

from scripts.analyze_suica_v8_minority_information_frontier_v37h4d_r2 import (
    fit_information_logistic,
    hypergeometric_moments,
    paired_bootstrap_difference,
    predict_information_logistic,
)


def test_information_logistic_recovers_increasing_power() -> None:
    rng = np.random.default_rng(603_001)
    information = np.exp(np.linspace(2.0, 9.0, 1000))
    truth = 1.0 / (
        1.0 + np.exp(-(np.log(information) - 5.5))
    )
    detected = rng.random(len(information)) < truth
    model = fit_information_logistic(information, detected)
    predicted = predict_information_logistic(model, information)
    assert model["slope"] > 0
    assert predicted[-1] > predicted[0]


def test_hypergeometric_moments_match_nominal_support() -> None:
    mean, variance = hypergeometric_moments(
        population=256,
        active=32,
        test=64,
    )
    assert np.isclose(mean, 8.0)
    assert variance > 0


def test_paired_bootstrap_detects_small_calibration_gap() -> None:
    rng = np.random.default_rng(603_002)
    predicted = rng.uniform(0.1, 0.9, size=2000)
    observed = rng.random(len(predicted)) < predicted
    difference, lower, upper = paired_bootstrap_difference(
        observed,
        predicted,
        seed=603_003,
        draws=1000,
    )
    assert abs(difference) < 0.05
    assert lower < difference < upper
