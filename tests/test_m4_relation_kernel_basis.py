"""Tests for calibration-only M4 relation-kernel transport."""
from __future__ import annotations

import numpy as np

from suica_core.m4_relation_kernel_basis import (
    build_relation_kernel_bases,
)


def _basis(seed: int = 1201) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    return {
        role: np.column_stack(
            [np.ones(16), rng.normal(size=(16, 7))]
        )
        for role in ("calibration", "selection", "evaluation")
    }


def test_kernel_basis_preserves_mass_and_declared_shapes() -> None:
    _, values = build_relation_kernel_bases(_basis(), rank=4)
    for basis in values.values():
        assert basis.shape == (16, 5)
        assert np.array_equal(basis[:, 0], np.ones(16))
        assert np.isfinite(basis).all()


def test_kernel_basis_is_invariant_to_shared_orthogonal_gauge() -> None:
    basis = _basis(seed=1202)
    rng = np.random.default_rng(2202)
    q, _ = np.linalg.qr(rng.normal(size=(7, 7)))
    rotated = {
        role: np.column_stack([values[:, 0], values[:, 1:] @ q])
        for role, values in basis.items()
    }
    first, first_values = build_relation_kernel_bases(basis, rank=5)
    second, second_values = build_relation_kernel_bases(
        rotated,
        rank=5,
    )
    assert abs(first.bandwidth - second.bandwidth) < 1e-12
    for role in basis:
        first_gram = (
            first_values[role][:, 1:]
            @ first_values[role][:, 1:].T
        )
        second_gram = (
            second_values[role][:, 1:]
            @ second_values[role][:, 1:].T
        )
        assert np.allclose(
            first_gram,
            second_gram,
            atol=1e-10,
            rtol=1e-10,
        )
