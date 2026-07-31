"""Tests for V8 capacity-conditioned replicated-support coverage."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_support_containment import (
    SupportContainmentSpec,
    _coverage,
    _filter_bank,
    classify_pair,
    effective_rank,
    impose_spectrum,
    positive_density,
    soft_capacity_filter,
)


def _diagonal_density(values: list[float]) -> np.ndarray:
    probabilities = np.asarray(values, dtype=float)
    probabilities /= probabilities.sum()
    return np.diag(probabilities)


def test_soft_filter_has_registered_trace_and_bounds() -> None:
    density = _diagonal_density([8, 6, 4, 3, 2, 1, 1, 1])
    support_filter = soft_capacity_filter(density, 3, tau=0.05)
    eigenvalues = np.linalg.eigvalsh(support_filter)
    assert np.isclose(np.trace(support_filter), 3.0, atol=1e-8)
    assert eigenvalues.min() >= -1e-10
    assert eigenvalues.max() <= 1.0 + 1e-10


def test_regularization_interpolates_toward_isotropic_filter() -> None:
    density = _diagonal_density([12, 8, 4, 2, 1, 1, 1, 1])
    low_tau = soft_capacity_filter(density, 3, tau=0.01)
    high_tau = soft_capacity_filter(density, 3, tau=100.0)
    isotropic = np.eye(8) * (3 / 8)
    assert np.linalg.norm(high_tau - isotropic) < np.linalg.norm(
        low_tau - isotropic
    )


def test_identical_support_has_unit_target_normalized_coverage() -> None:
    density = _diagonal_density([12, 8, 5, 3, 2, 1, 1, 1])
    bank = _filter_bank(
        density,
        density,
        capacities=(2, 4),
        tau_multipliers=(0.5, 1.0),
    )
    forward, reverse, _ = _coverage(
        bank,
        density,
        density,
        denominator_floor=1e-8,
        minimum_grid_fraction=1.0,
    )
    assert np.isclose(forward, 1.0)
    assert np.isclose(reverse, 1.0)


def test_isotropic_support_is_refused_by_zero_native_excess() -> None:
    density = np.eye(12) / 12
    bank = _filter_bank(
        density,
        density,
        capacities=(2, 4),
        tau_multipliers=(1.0,),
    )
    forward, reverse, _ = _coverage(
        bank,
        density,
        density,
        denominator_floor=1e-8,
        minimum_grid_fraction=1.0,
    )
    assert np.isnan(forward)
    assert np.isnan(reverse)


def test_full_spectrum_replacement_preserves_axes_and_hits_template() -> None:
    density = _diagonal_density([12, 7, 4, 2, 1, 1, 1, 1])
    template = np.asarray([8, 7, 6, 5, 4, 3, 2, 1], dtype=float)
    template /= template.sum()
    matched = impose_spectrum(density, template)
    assert np.allclose(matched, np.diag(np.diag(matched)), atol=1e-12)
    assert np.allclose(
        np.linalg.eigvalsh(matched)[::-1],
        np.sort(template)[::-1],
    )


def test_positive_density_discards_negative_cross_replicate_modes() -> None:
    density, rank, positive_rank = positive_density(
        np.diag([3.0, 1.0, -2.0, -4.0])
    )
    assert np.isclose(np.trace(density), 1.0)
    assert positive_rank == 2
    assert np.isclose(rank, 1.6)
    assert np.all(np.linalg.eigvalsh(density) >= -1e-12)
    assert np.isclose(effective_rank(density), 1.6)


def test_underresolved_classification_keeps_output_schema() -> None:
    result = classify_pair(pd.DataFrame(), spec=SupportContainmentSpec())
    assert result == {
        "decision": "COVERAGE_UNDERRESOLVED",
        "direction": "",
    }
