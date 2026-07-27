"""Tests for the V3.7H.2 repeated-opportunity frontier."""
from __future__ import annotations

import numpy as np

from suica_core.v8_common_shock_frontier import (
    CommonShockSpec,
    legacy_stream_excess,
    prepare_response_geometry,
    repeated_opportunity_excess,
    score_common_shock_panel,
    score_stable_energy,
    simulate_common_shock_panel,
)
from suica_core.v8_resolution_filtration import (
    fit_joint_resolution_family,
    resolution_candidates,
)
from suica_core.v8_resolution_filtration_h1 import (
    PairedScheduleSpec,
    simulate_schedule_calibration_context,
)


def _fixture() -> tuple[dict, dict, dict, CommonShockSpec]:
    schedule_spec = PairedScheduleSpec(
        dimension=8,
        budgets=(8, 16, 32),
        reference_authors=320,
        calibration_authors=360,
        panel_authors=1800,
        opportunity_start=8,
    )
    context = simulate_schedule_calibration_context(
        seed=39_210,
        spec=schedule_spec,
    )
    zero = context["reference"][:, :, -1].mean(axis=(0, 1))
    fitted, _, _ = fit_joint_resolution_family(
        context["calibration"],
        budgets=schedule_spec.budgets,
        external_zero=zero,
        candidates=resolution_candidates(),
        folds=3,
        seed=39_211,
        noise_shrinkage=0.25,
    )
    endpoint = fitted[32]
    response = prepare_response_geometry(
        context,
        endpoint,
        geometry="random_rotation",
        seed=39_212,
    )
    common_spec = CommonShockSpec(
        dimension=8,
        endpoint_budget=32,
        panel_authors=1800,
        event_rms_at_64=0.40,
    )
    return context, endpoint, response, common_spec


def test_k1_repeated_opportunity_is_unidentifiable() -> None:
    context, fitted, response, spec = _fixture()
    panel = simulate_common_shock_panel(
        context,
        fitted,
        response,
        seed=39_220,
        spec=spec,
        opportunity_repeats=1,
        stream_correlation=0.3,
        common_shock_score_energy=0.05,
        noise_mode="gaussian",
        response_score_eta=0.0,
    )
    scores = score_common_shock_panel(panel["values"], fitted)
    estimate = repeated_opportunity_excess(scores, fitted)
    assert score_stable_energy(fitted) > 0.0
    assert estimate["identified"] == 0.0
    assert np.isnan(estimate["q_total"])
    assert np.isnan(estimate["q_author"])


def test_repeated_opportunities_remove_correlated_common_shock() -> None:
    context, fitted, response, spec = _fixture()
    panel = simulate_common_shock_panel(
        context,
        fitted,
        response,
        seed=39_230,
        spec=spec,
        opportunity_repeats=8,
        stream_correlation=0.6,
        common_shock_score_energy=0.05,
        noise_mode="gaussian",
        response_score_eta=0.0,
    )
    scores = score_common_shock_panel(panel["values"], fitted)
    legacy = legacy_stream_excess(scores, fitted)
    repeated = repeated_opportunity_excess(scores, fitted)
    assert legacy["q_total"] > 0.02
    assert abs(repeated["q_total"]) < 0.015


def test_repeated_opportunities_recover_response_energy() -> None:
    context, fitted, response, spec = _fixture()
    panel = simulate_common_shock_panel(
        context,
        fitted,
        response,
        seed=39_240,
        spec=spec,
        opportunity_repeats=8,
        stream_correlation=0.6,
        common_shock_score_energy=0.05,
        noise_mode="gaussian",
        response_score_eta=0.10,
    )
    scores = score_common_shock_panel(panel["values"], fitted)
    repeated = repeated_opportunity_excess(scores, fitted)
    target = panel["achieved_response_score_eta"]
    assert abs(target - 0.10) < 0.02
    assert abs(repeated["q_total"] - target) < 0.02


def test_global_shift_is_total_not_author_relative_sensitivity() -> None:
    context, fitted, response, spec = _fixture()
    panel = simulate_common_shock_panel(
        context,
        fitted,
        response,
        seed=39_250,
        spec=spec,
        opportunity_repeats=8,
        stream_correlation=0.3,
        common_shock_score_energy=0.01,
        noise_mode="gaussian",
        response_score_eta=0.0,
        global_shift_score_eta=0.10,
    )
    scores = score_common_shock_panel(panel["values"], fitted)
    repeated = repeated_opportunity_excess(scores, fitted)
    assert repeated["q_total"] > 0.07
    assert abs(repeated["q_author"]) < 0.02


def test_persistent_confound_is_observationally_identical() -> None:
    context, fitted, response, spec = _fixture()
    common = {
        "context": context,
        "fitted": fitted,
        "response_geometry": response,
        "seed": 39_260,
        "spec": spec,
        "opportunity_repeats": 4,
        "stream_correlation": 0.3,
        "common_shock_score_energy": 0.01,
        "noise_mode": "gaussian",
        "response_score_eta": 0.10,
    }
    response_world = simulate_common_shock_panel(
        **common,
        effect_source="author_response",
    )
    confound_world = simulate_common_shock_panel(
        **common,
        effect_source="persistent_schedule_confound",
    )
    assert np.array_equal(
        response_world["values"],
        confound_world["values"],
    )
    assert response_world["effect_source"] != confound_world["effect_source"]
