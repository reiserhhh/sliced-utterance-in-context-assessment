"""Tests for the V8 event-to-M3-to-HJIC seam."""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from suica_core.v8_m3_hjic_seam import (
    M3HJICSeamSpec,
    frozen_random_features,
    m3_block_features,
    run_m3_hjic_seam_repetition,
)


@lru_cache(maxsize=1)
def _result():
    spec = M3HJICSeamSpec(
        permutations=99,
        bootstrap_draws=99,
        mesoscopic_reliability_floor=0.25,
    )
    return run_m3_hjic_seam_repetition(
        0,
        seed=20260802,
        spec=spec,
    )


def _world(table: str, name: str):
    return [row for row in _result()[table] if row["world"] == name]


def test_m3_feature_map_is_deterministic_and_block_local() -> None:
    spec = M3HJICSeamSpec(permutations=19, bootstrap_draws=19)
    event_frequencies, transition_frequencies = frozen_random_features(
        seed=3,
        spec=spec,
    )
    events = np.arange(
        2 * spec.events * spec.event_dimensions,
        dtype=float,
    ).reshape(2, spec.events, spec.event_dimensions)
    first, names = m3_block_features(
        events,
        event_frequencies=event_frequencies,
        transition_frequencies=transition_frequencies,
        block_size=spec.block_size,
    )
    second, second_names = m3_block_features(
        events.copy(),
        event_frequencies=event_frequencies,
        transition_frequencies=transition_frequencies,
        block_size=spec.block_size,
    )
    assert first.shape[:2] == (2, spec.blocks)
    assert first.shape[2] == len(names)
    assert names == second_names
    assert np.array_equal(first, second)


def test_clean_event_path_reaches_relation_license_without_truth() -> None:
    license_row = _world("licenses", "GLOBAL_INVARIANT")[0]
    truth_row = _world("truth_audit", "GLOBAL_INVARIANT")[0]
    assert license_row["final_seam_license"] == 1
    assert license_row["truth_used_by_license"] is False
    assert truth_row["relation_fidelity"] > 0.8
    assert truth_row["relative_frobenius_error"] < 0.25


def test_gauge_alias_preserves_output_but_not_mechanism_identity() -> None:
    alias = _world("alias_invariance", "MICRO_GAUGE_ALIAS")[0]
    license_row = _world("licenses", "MICRO_GAUGE_ALIAS")[0]
    assert alias["relative_output_difference"] < 1e-10
    assert alias["mechanism_identity_license"] == 0
    assert license_row["final_seam_license"] == 1


def test_cross_replicate_estimator_repairs_same_view_attenuation() -> None:
    attenuation = _world(
        "attenuation_diagnostics",
        "ESTIMATION_ATTENUATION",
    )[0]
    assert attenuation["corrected_better"] == 1
    assert attenuation["relative_error_reduction"] > 0.25


def test_cancellation_and_ecological_relation_are_not_globalized() -> None:
    cancellation = _world(
        "licenses",
        "BALANCED_CONTEXT_CANCELLATION",
    )[0]
    ecological = _world("licenses", "ECOLOGICAL_ONLY")[0]
    assert cancellation["cancellation_detected"] == 1
    assert cancellation["global_invariant_license"] == 0
    assert ecological["ecological_between_detected"] == 1
    assert ecological["relation_license"] == 0


def test_out_of_family_signal_is_detected_and_refused() -> None:
    mismatch = _world(
        "m3_adequacy_diagnostics",
        "MECHANISM_FAMILY_MISMATCH",
    )[0]
    license_row = _world(
        "licenses",
        "MECHANISM_FAMILY_MISMATCH",
    )[0]
    assert mismatch["periodic_out_of_model_reliability"] > 0.75
    assert mismatch["mesoscopic_reliability"] < 0.25
    assert mismatch["mismatch_detected"] == 1
    assert license_row["final_seam_license"] == 0


def test_primary_coverage_targets_population_not_sample_truth() -> None:
    coverage = _world("uncertainty_coverage", "GLOBAL_INVARIANT")[0]
    assert coverage["total"] == 16
    assert 0 <= coverage["covered"] <= coverage["total"]
    assert coverage["mean_width"] > 0
    assert coverage["nested_mean_width"] > 0


def test_between_operator_uses_its_own_null_when_enabled() -> None:
    spec = M3HJICSeamSpec(
        permutations=99,
        bootstrap_draws=19,
        mesoscopic_reliability_floor=0.25,
        calibrate_between_null=True,
    )
    result = run_m3_hjic_seam_repetition(
        0,
        seed=20260803,
        spec=spec,
    )
    ecological = [
        row
        for row in result["licenses"]
        if row["world"] == "ECOLOGICAL_ONLY"
    ][0]
    heldout = [
        row
        for row in result["licenses"]
        if row["world"] == "HELDOUT_D0_NULL"
    ][0]
    assert ecological["between_threshold"] < ecological["relation_threshold"]
    assert ecological["ecological_between_detected"] == 1
    assert heldout["ecological_between_detected"] == 0


@lru_cache(maxsize=1)
def _support_result():
    spec = M3HJICSeamSpec(
        permutations=99,
        bootstrap_draws=19,
        mesoscopic_reliability_floor=0.25,
        shared_generator_mechanism=True,
        calibrate_between_null=True,
        support_invariance_audit=True,
    )
    return run_m3_hjic_seam_repetition(
        0,
        seed=20260804,
        spec=spec,
    )


def _support_world(name: str):
    return [
        row
        for row in _support_result()["licenses"]
        if row["world"] == name
    ][0]


def test_support_gauge_is_accepted_but_operator_drift_is_refused() -> None:
    clean = _support_world("GLOBAL_INVARIANT")
    gauge = _support_world("WITHIN_SUPPORT_GAUGE")
    drift = _support_world("MEASUREMENT_SUPPORT_DRIFT_GLOBAL")
    assert clean["support_adequate"] == 1
    assert gauge["support_adequate"] == 1
    assert gauge["support_noninvariant"] == 0
    assert drift["support_noninvariant"] == 1
    assert drift["final_seam_license"] == 0


def test_absent_replicated_support_is_underresolved_not_drift() -> None:
    underresolved = _support_world("SUPPORT_UNDERRESOLVED")
    assert underresolved["support_underresolved"] == 1
    assert underresolved["support_noninvariant"] == 0
    assert underresolved["final_seam_license"] == 0
