"""Tests for independent pairwise mechanism superposition."""
from __future__ import annotations

import numpy as np

from suica_core.m3_mechanism_decomposition import (
    MECHANISM_TO_FAMILY,
    M3MechanismMixtureSpec,
    generate_m3_mechanism_pair_world,
)
from suica_core.m3_mechanism_stress_estimator import fit_m3_mechanism_stress


def test_pair_parameters_are_independent_and_reproducible() -> None:
    pair = ("condition", "interaction")
    observed, truth = generate_m3_mechanism_pair_world(
        pair=pair,
        spec=M3MechanismMixtureSpec(authors=24, occasions=4, events=64),
        seed=501,
    )
    repeated, repeated_truth = generate_m3_mechanism_pair_world(
        pair=pair,
        spec=M3MechanismMixtureSpec(authors=24, occasions=4, events=64),
        seed=501,
    )
    assert np.allclose(observed.response_train, repeated.response_train)
    assert np.allclose(
        truth.author_parameters["condition"],
        repeated_truth.author_parameters["condition"],
    )
    assert abs(np.corrcoef(
        truth.author_parameters["condition"].ravel(),
        truth.author_parameters["interaction"].ravel(),
    )[0, 1]) < 0.45


def test_knockout_removes_target_component_but_preserves_other() -> None:
    pair = ("condition", "interaction")
    spec = M3MechanismMixtureSpec(
        authors=24,
        occasions=5,
        events=96,
        noise=0.10,
    )
    full, _ = generate_m3_mechanism_pair_world(
        pair=pair,
        spec=spec,
        seed=502,
    )
    knockout, _ = generate_m3_mechanism_pair_world(
        pair=pair,
        spec=spec,
        seed=502,
        disabled=frozenset({"condition"}),
    )
    full_estimate = fit_m3_mechanism_stress(full, seed=503)
    knockout_estimate = fit_m3_mechanism_stress(knockout, seed=503)
    condition_family = MECHANISM_TO_FAMILY["condition"]
    interaction_family = MECHANISM_TO_FAMILY["interaction"]
    condition_change = np.mean(np.linalg.norm(
        full_estimate.train_features[condition_family]
        - knockout_estimate.train_features[condition_family],
        axis=1,
    ))
    interaction_change = np.mean(np.linalg.norm(
        full_estimate.train_features[interaction_family]
        - knockout_estimate.train_features[interaction_family],
        axis=1,
    ))
    assert condition_change > interaction_change
