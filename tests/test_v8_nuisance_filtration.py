"""Tests for the V8 M nuisance-sensitivity filtration."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_nuisance_filtration import (
    bootstrap_link_interval,
    cross_trace_decomposition,
    fit_nuisance_residualizer,
    signed_link,
    text_opportunity_vector,
    within_context_decomposition_null,
    within_context_link_null,
)
from suica_core.v8_marginal_background_quotient import quotient_statistics


def test_text_opportunity_vector_is_finite_and_schema_aligned() -> None:
    values, columns = text_opportunity_vector(
        "I THINK 42!\\n- see https://example.com #test @you"
    )
    assert values.shape == (len(columns),)
    assert np.isfinite(values).all()
    assert values[0] > 0


def test_d0_frozen_residualizer_removes_planted_opportunity_relation() -> None:
    rng = np.random.default_rng(11)
    authors = 180
    nuisance = rng.normal(size=(authors, 2, 3))
    nuisance[:, 1] = nuisance[:, 0] + rng.normal(
        scale=0.05,
        size=(authors, 3),
    )
    coefficients = rng.normal(size=(3, 5))
    values = nuisance @ coefficients + rng.normal(
        scale=0.15,
        size=(authors, 2, 5),
    )
    calibration = np.zeros(authors, dtype=bool)
    calibration[:100] = True
    model = fit_nuisance_residualizer(
        values,
        nuisance,
        calibration,
        columns=range(3),
    )
    residual = model.transform(values, nuisance)
    before = np.corrcoef(values[100:, 0, 0], values[100:, 1, 0])[0, 1]
    after = np.corrcoef(residual[100:, 0, 0], residual[100:, 1, 0])[0, 1]
    assert before > 0.8
    assert abs(after) < 0.25


def test_within_context_null_contains_fixed_points_in_support() -> None:
    rng = np.random.default_rng(7)
    values = rng.normal(size=(60, 2, 8))
    contexts = np.repeat(["a", "b", "c"], 20)
    observed, null = within_context_link_null(
        values,
        contexts,
        draws=99,
        rng=rng,
    )
    assert np.isfinite(observed)
    assert null.shape == (99,)
    assert np.isfinite(null).all()


def test_linear_time_signed_link_matches_reference_implementation() -> None:
    rng = np.random.default_rng(13)
    values = rng.normal(size=(70, 2, 11))
    expected = quotient_statistics(values, compute_auc=False)["link"]
    assert abs(signed_link(values) - expected) < 1e-12


def test_context_stratified_bootstrap_interval_is_ordered() -> None:
    rng = np.random.default_rng(19)
    identity = rng.normal(size=(80, 6))
    values = np.stack(
        [
            identity + rng.normal(scale=0.4, size=identity.shape),
            identity + rng.normal(scale=0.4, size=identity.shape),
        ],
        axis=1,
    )
    lower, upper = bootstrap_link_interval(
        values,
        np.repeat(["a", "b"], 40),
        draws=99,
        rng=rng,
    )
    assert lower < upper
    assert lower > 0


def test_cross_trace_decomposition_closes_with_directional_coupling() -> None:
    rng = np.random.default_rng(29)
    profile = rng.normal(size=(120, 2, 7))
    residual = rng.normal(size=(120, 2, 7))
    residual[:, 1] += 0.35 * residual[:, 0]
    raw = profile + residual
    result = cross_trace_decomposition(raw, residual)
    assert abs(result["closure_error"]) < 1e-12
    assert abs(
        result["sum"] - result["observed_link"]
    ) < 1e-12


def test_decomposition_excess_closes_under_context_null() -> None:
    rng = np.random.default_rng(37)
    profile = rng.normal(size=(90, 2, 6))
    residual = rng.normal(size=(90, 2, 6))
    raw = profile + residual
    observed, null = within_context_decomposition_null(
        raw,
        residual,
        np.repeat(["a", "b", "c"], 30),
        draws=99,
        rng=rng,
    )
    parts = (
        "profile_predictable",
        "residual",
        "profile_to_residual",
        "residual_to_profile",
    )
    component_excess = sum(
        observed[name] - null[name].mean()
        for name in parts
    )
    total_excess = observed["observed_link"] - null["observed_link"].mean()
    assert abs(component_excess - total_excess) < 1e-12
