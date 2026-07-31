"""Tests for M4-C.3.3 nested opportunity excitation."""
from __future__ import annotations

import numpy as np

from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_opportunity_excitation import (
    balanced_response_probe,
    build_excited_observed,
    subset_opportunity_budget,
)


def _world(seed: int = 1501):
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=24,
        reference_selection_points=16,
        calibration_occasions=4,
        selection_occasions=4,
        evaluation_occasions=2,
        events=32,
    )
    observed, truth = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=spec,
        seed=seed,
    )
    return spec, observed, truth


def test_balanced_probe_is_zero_mean_and_orthogonal() -> None:
    probes = np.stack(
        [balanced_response_probe(index, np.ones(2)) for index in range(4)]
    )
    assert np.allclose(np.mean(probes, axis=0), 0.0)
    assert np.allclose(probes.T @ probes, 2.0 * np.eye(2))


def test_excitation_preserves_evaluation_and_changes_training_paths() -> None:
    spec, observed, truth = _world()
    excited = build_excited_observed(
        observed,
        truth,
        spec,
        seed=1501,
    )
    assert np.array_equal(
        excited.ecology.train_evaluation.response,
        observed.ecology.train_evaluation.response,
    )
    assert not np.array_equal(
        excited.ecology.train_calibration.response,
        observed.ecology.train_calibration.response,
    )
    assert not np.array_equal(
        excited.ecology.train_calibration.generated_menu,
        observed.ecology.train_calibration.generated_menu,
    )


def test_budget_subsets_are_strict_prefixes() -> None:
    _, observed, _ = _world(seed=1502)
    small = subset_opportunity_budget(
        observed,
        calibration_occasions=2,
        selection_occasions=2,
    )
    assert np.array_equal(
        small.ecology.test_calibration.menu,
        observed.ecology.test_calibration.menu[:, :2],
    )
    assert np.array_equal(
        small.ecology.test_selection.response,
        observed.ecology.test_selection.response[:, :2],
    )
    assert np.array_equal(
        small.ecology.test_evaluation.menu,
        observed.ecology.test_evaluation.menu,
    )
