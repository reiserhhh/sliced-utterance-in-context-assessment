"""Tests for vector-valued M4 applicability signatures."""
from __future__ import annotations

import numpy as np

from suica_core.m4_applicability_signature import (
    m4_applicability_signature,
)
from suica_core.m4_boundary_ecology import intervene_evaluation_support
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_rcca_chart import (
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def test_signature_is_finite_and_detects_support_intervention() -> None:
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=24,
        reference_selection_points=16,
        categories=16,
        events=24,
    )
    observed = generate_m4_pre_response_condition(
        world="endogenous_creation_expansion",
        spec=spec,
        seed=812_031,
    )
    chart = fit_response_safe_rcca_chart(
        observed,
        support_permutation_repetitions=19,
        support_bootstrap_repetitions=19,
        canonical_permutation_repetitions=19,
        canonical_bootstrap_repetitions=19,
        null_trials=5,
        minimum_support_stability_lcb=0.0,
        minimum_consensus_eigenvalue=0.0,
        minimum_native_consensus_affinity=0.0,
        minimum_projector_affinity=0.0,
        minimum_heldout_cka=0.0,
        minimum_coverage=0.0,
        seed=812_031,
    )
    r_basis = build_response_safe_rcca_basis(chart, observed)
    bases = {"R": r_basis, "B0": r_basis}
    native = m4_applicability_signature(observed, chart, bases)
    native_count = int(
        round(native["support_minimum_coverage"] * spec.categories)
    )
    target = max(min(native_count - 2, 12), 0)
    changed = intervene_evaluation_support(
        observed,
        chart,
        target_count=target,
    ).observed
    changed_basis = build_response_safe_rcca_basis(chart, changed)
    shifted = m4_applicability_signature(
        changed,
        chart,
        {"R": changed_basis, "B0": changed_basis},
    )
    assert all(np.isfinite(list(native.values())))
    assert all(np.isfinite(list(shifted.values())))
    assert (
        shifted["support_minimum_coverage"]
        < native["support_minimum_coverage"]
    )
    assert shifted["tail_fraction"] > native["tail_fraction"]
