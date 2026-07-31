"""Tests for the SUICA M4 mechanism-composition algebra."""
from __future__ import annotations

import numpy as np

from suica_core.m4_composition_audit import audit_m4_composition
from suica_core.m4_composition_estimator import (
    fit_m4_composition,
    mobius_dividends,
    subset_lattice,
)
from suica_core.m4_composition_generator import (
    MECHANISM_NAMES,
    M4CompositionSpec,
    generate_m4_composition_world,
)


THRESHOLDS = {
    "support_threshold": 0.045,
    "observational_threshold": 0.10,
    "gate_threshold": 0.35,
    "commutator_threshold": 0.15,
    "null_value_threshold": 0.08,
}


def _audit(world: str, seed: int = 800) -> dict[str, object]:
    observed, truth = generate_m4_composition_world(
        world=world,
        spec=M4CompositionSpec(
            authors=16,
            occasions=4,
            events=96,
            noise=0.25,
        ),
        seed=seed,
    )
    estimate = fit_m4_composition(observed, seed=seed + 1)
    return audit_m4_composition(
        estimate,
        truth,
        MECHANISM_NAMES,
        **THRESHOLDS,
    )


def test_subset_lattice_and_mobius_reconstruct_values() -> None:
    lattice = subset_lattice(6, 3)
    assert len(lattice) == 41
    values = {
        subset: float(sum(index + 1 for index in subset) + len(subset) ** 2)
        for subset in lattice
    }
    dividends = mobius_dividends(values, subsets=lattice)
    for subset in lattice:
        reconstructed = sum(
            value
            for lower, value in dividends.items()
            if set(lower).issubset(subset)
        )
        assert np.isclose(reconstructed, values[subset])


def test_generator_is_reproducible_and_knockout_changes_target() -> None:
    spec = M4CompositionSpec(authors=12, occasions=3, events=64, noise=0.20)
    full, truth = generate_m4_composition_world(
        world="synergy",
        spec=spec,
        seed=811,
    )
    repeated, repeated_truth = generate_m4_composition_world(
        world="synergy",
        spec=spec,
        seed=811,
    )
    knockout, _ = generate_m4_composition_world(
        world="synergy",
        spec=spec,
        seed=811,
        disabled=frozenset({"condition"}),
    )
    assert np.allclose(full.response_train, repeated.response_train)
    assert np.allclose(
        truth.author_parameters["strength"],
        repeated_truth.author_parameters["strength"],
    )
    assert not np.allclose(full.response_train, knockout.response_train)


def test_structural_synergy_and_alias_are_distinguished() -> None:
    synergy = _audit("synergy", seed=821)
    alias = _audit("alias", seed=822)
    assert synergy["support_recall"] >= 0.90
    assert synergy["sign_accuracy"] == 1.0
    assert alias["alias_refused"] is True
    assert alias["refusal_rate"] >= 0.80


def test_redundancy_and_suppression_have_opposite_observational_dividends() -> None:
    redundancy = _audit("redundancy", seed=831)
    suppression = _audit("suppression", seed=832)
    assert redundancy["diagnosed_kind"] == "redundancy"
    assert suppression["diagnosed_kind"] == "suppression"


def test_gate_direction_is_not_reduced_to_generic_synergy() -> None:
    gate = _audit("gate", seed=841)
    synergy = _audit("synergy", seed=842)
    assert gate["diagnosed_kind"] == "gate"
    assert synergy["diagnosed_kind"] == "synergy"
