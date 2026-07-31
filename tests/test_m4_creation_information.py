"""Tests for M4-C.3.3 empirical creation information."""
from __future__ import annotations

import numpy as np

from suica_core.m4_creation_information import (
    fisher_spectrum_from_design,
)


def test_information_doubles_under_exact_design_replication() -> None:
    rng = np.random.default_rng(1601)
    design = rng.normal(size=(200, 9))
    coefficient = rng.normal(scale=0.1, size=9)
    columns = np.arange(3, 9)
    first = fisher_spectrum_from_design(
        design,
        coefficient,
        columns,
    )
    repeated = fisher_spectrum_from_design(
        np.vstack([design, design]),
        coefficient,
        columns,
    )
    assert np.isclose(repeated[0], 2.0 * first[0])
    assert np.isclose(repeated[1], 2.0 * first[1])
    assert np.isclose(repeated[2], first[2])
    assert np.isclose(repeated[3], first[3])


def test_orthogonal_design_has_better_minimum_information() -> None:
    rng = np.random.default_rng(1602)
    common = rng.normal(size=(400, 1))
    collinear = np.column_stack(
        [common[:, 0], common[:, 0] + 0.01 * rng.normal(size=400)]
    )
    orthogonal = rng.normal(size=(400, 2))
    prefix = np.ones((400, 1))
    coefficient = np.zeros(3)
    weak = fisher_spectrum_from_design(
        np.column_stack([prefix, collinear]),
        coefficient,
        np.asarray([1, 2]),
    )
    strong = fisher_spectrum_from_design(
        np.column_stack([prefix, orthogonal]),
        coefficient,
        np.asarray([1, 2]),
    )
    assert strong[0] > weak[0]
