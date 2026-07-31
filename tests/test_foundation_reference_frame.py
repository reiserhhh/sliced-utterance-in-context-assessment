"""Adversarial tests for the synthetic SUICA L4-to-L5 frontier."""
from __future__ import annotations

import copy

import numpy as np
import pytest

from suica_core.foundation_reference_frame import (
    L45ReferenceSpec,
    aggregate_to_common_facet,
    fit_l45_pipeline,
    fit_reference_frame,
    mdd_metrics,
    normalized_score_error,
    observable_nested_region,
    operator_transport_audit,
    oracle_score_target,
    resample_observed_panel,
    score_correlation,
    score_panel,
    simulate_l45_world,
)


@pytest.fixture()
def small_spec() -> L45ReferenceSpec:
    return L45ReferenceSpec(
        reference_authors=72,
        fit_authors=48,
        test_authors=32,
        facets=8,
        occasions=4,
        dimensions=4,
        response_rank=2,
        events_per_facet=6,
    )


def _fit(world: dict, seed: int = 41_502) -> dict:
    return fit_l45_pipeline(
        world,
        candidates=[0, 2, 4],
        folds=4,
        seed=seed,
        soft_noninferiority_margin=0.01,
    )


def test_clean_world_produces_accurate_reference_relative_score(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_501,
        world="clean",
        noise_mode="gaussian",
        spec=small_spec,
    )
    pipeline = _fit(world)
    scored = score_panel(world["test"], world, pipeline)
    target = oracle_score_target(world["test"], world, pipeline)

    assert pipeline["status"] == "L45_PIPELINE_READY"
    assert scored["status"] == "L5_CANDIDATE_SCORE_READY"
    assert score_correlation(scored["point"], target) > 0.95
    assert normalized_score_error(scored["point"], target) < 0.25
    assert pipeline["estimator"] in {"hard_selected", "soft_conserving"}


def test_scoring_and_fitting_do_not_require_generator_truth(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_503,
        world="clean",
        noise_mode="gaussian",
        spec=small_spec,
    )
    complete = _fit(world, seed=41_504)
    observed = copy.deepcopy(world)
    for role in ("reference", "fit", "test"):
        observed[role].pop("stable_field")
    observed_fit = _fit(observed, seed=41_504)
    complete_score = score_panel(world["test"], world, complete)
    observed_score = score_panel(observed["test"], observed, observed_fit)

    assert observed_fit["status"] == "L45_PIPELINE_READY"
    assert np.allclose(
        complete["reference_frame"]["center"],
        observed_fit["reference_frame"]["center"],
    )
    assert np.allclose(complete_score["point"], observed_score["point"])
    with pytest.raises(ValueError, match="unavailable"):
        oracle_score_target(observed["test"], observed, observed_fit)


def test_facet_standardization_corrects_composition_shift(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_505,
        world="composition_shift",
        noise_mode="gaussian",
        spec=small_spec,
    )
    aggregate = aggregate_to_common_facet(
        world["test"],
        world["lambda_facet"],
    )
    target = np.einsum(
        "f,afd->ad",
        world["lambda_facet"],
        world["test"]["stable_field"],
    )
    standardized_error = np.sqrt(np.mean(
        (aggregate["standardized"].mean(axis=1) - target) ** 2
    ))
    naive_error = np.sqrt(np.mean(
        (aggregate["naive"].mean(axis=1) - target) ** 2
    ))

    assert aggregate["status"] == "COMMON_FACET_READY"
    assert standardized_error < naive_error
    assert aggregate["minimum_ess_ratio"] < 1.0


def test_target_weighting_corrects_reference_mixture(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_506,
        world="reference_mixture",
        noise_mode="gaussian",
        spec=small_spec,
    )
    weighted = fit_reference_frame(
        world["reference"],
        lambda_facet=world["lambda_facet"],
        target_group_weights=world["target_group_weights"],
        ridge=small_spec.covariance_ridge,
        weighted=True,
    )
    unweighted = fit_reference_frame(
        world["reference"],
        lambda_facet=world["lambda_facet"],
        target_group_weights=world["target_group_weights"],
        ridge=small_spec.covariance_ridge,
        weighted=False,
    )
    truth = world["true_reference_center"]

    assert np.linalg.norm(weighted["center"] - truth) < np.linalg.norm(
        unweighted["center"] - truth
    )


@pytest.mark.parametrize(
    ("world_name", "fit_status", "score_status"),
    [
        ("support_hole", "L45_PIPELINE_READY", "REFUSE_NONOVERLAP"),
        (
            "choice_response_alias",
            "REFUSE_CHOICE_RESPONSE_ALIAS_NO_FACET_PROVENANCE",
            "REFUSE_CHOICE_RESPONSE_ALIAS_NO_FACET_PROVENANCE",
        ),
        (
            "person_occasion_alias",
            "REFUSE_PERSON_OCCASION_ALIAS",
            "REFUSE_PERSON_OCCASION_ALIAS",
        ),
        (
            "correlated_replicate_shock",
            "REFUSE_CORRELATED_OR_UNDECLARED_OCCASIONS",
            "REFUSE_CORRELATED_OR_UNDECLARED_OCCASIONS",
        ),
    ],
)
def test_nonidentified_worlds_are_refused(
    small_spec: L45ReferenceSpec,
    world_name: str,
    fit_status: str,
    score_status: str,
) -> None:
    world = simulate_l45_world(
        seed=41_507,
        world=world_name,
        noise_mode="gaussian",
        spec=small_spec,
    )
    pipeline = _fit(world)
    scored = score_panel(world["test"], world, pipeline)

    assert pipeline["status"] == fit_status
    assert scored["status"] == score_status


def test_operator_transport_accepts_chart_change_and_rejects_kernel(
    small_spec: L45ReferenceSpec,
) -> None:
    clean = simulate_l45_world(
        seed=41_508,
        world="clean",
        noise_mode="gaussian",
        spec=small_spec,
    )
    kernel = simulate_l45_world(
        seed=41_509,
        world="operator_kernel",
        noise_mode="gaussian",
        spec=small_spec,
    )

    valid = operator_transport_audit(clean)
    invalid = operator_transport_audit(kernel)
    assert valid["status"] == "OPERATOR_TRANSPORT_READY"
    assert valid["commutation_defect"] < 1e-10
    assert invalid["status"] == "REFUSE_OPERATOR_KERNEL_NONINVERTIBLE"


def test_aq_alias_preserves_observable_but_forbids_cause_attribution(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_510,
        world="aq_gauge_alias",
        noise_mode="gaussian",
        spec=small_spec,
    )
    pipeline = _fit(world)
    scored = score_panel(world["test"], world, pipeline)

    assert world["alias_identity_error"] < 1e-12
    assert world["cause_attribution_allowed"] is False
    assert scored["cause_attribution_allowed"] is False


def test_observable_nested_region_is_finite(
    small_spec: L45ReferenceSpec,
) -> None:
    world = simulate_l45_world(
        seed=41_511,
        world="informative_precision",
        noise_mode="heteroskedastic_t5",
        spec=small_spec,
    )
    pipeline = _fit(world, seed=41_512)
    region = observable_nested_region(
        world,
        pipeline,
        draws=16,
        tracked_authors=4,
        candidates=[0, 2, 4],
        folds=4,
        seed=41_513,
        soft_noninferiority_margin=0.01,
    )

    assert 0.0 <= region["coverage"] <= 1.0
    assert np.isfinite(region["median_radius"])
    assert region["successful_draw_rate"] >= 0.75


def test_occasion_resampling_recovers_non_event_variation() -> None:
    spec = L45ReferenceSpec(
        reference_authors=24,
        fit_authors=16,
        test_authors=12,
        facets=6,
        occasions=4,
        dimensions=3,
        response_rank=2,
        events_per_facet=4,
        event_scale=0.0,
        occasion_scale=0.3,
    )
    world = simulate_l45_world(
        seed=41_515,
        world="clean",
        noise_mode="gaussian",
        spec=spec,
    )
    event_only = resample_observed_panel(
        world["test"],
        np.random.default_rng(41_516),
        lambda_facet=world["lambda_facet"],
        resample_occasions=False,
    )
    full = resample_observed_panel(
        world["test"],
        np.random.default_rng(41_516),
        lambda_facet=world["lambda_facet"],
        resample_occasions=True,
    )

    assert np.allclose(event_only["means"], world["test"]["means"])
    assert not np.allclose(full["means"], world["test"]["means"])


def test_mdd_calibration_reports_valid_rates() -> None:
    rng = np.random.default_rng(41_514)
    stable = rng.normal(size=(80, 4))
    left = stable + rng.normal(scale=0.15, size=stable.shape)
    right = stable + rng.normal(scale=0.15, size=stable.shape)
    result = mdd_metrics(left, right)

    assert result["mdd95"] > 0.0
    assert 0.0 <= result["null_false_positive"] <= 1.0
    assert 0.0 <= result["two_mdd_power"] <= 1.0
