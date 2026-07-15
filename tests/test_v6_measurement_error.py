from __future__ import annotations

import numpy as np

from suica_sim.measurement_error import (dialogue_response_world,
    fixed_reference_shift, occasion_error_curve, response_excitation_world,
    window_perturbation_curve)


def test_fixed_reference_is_composition_invariant():
    result = fixed_reference_shift(np.random.default_rng(1), 200)
    assert result["fixed_reference_mean_abs_shift"] == 0
    assert result["batch_norm_mean_abs_shift"] > .5


def test_single_context_response_is_refused():
    result = response_excitation_world(np.random.default_rng(2), 100)
    assert result["response_rmse"] < .1
    assert result["single_context_refusal_rate"] == 1


def test_dialogue_partner_input_is_required():
    result = dialogue_response_world(np.random.default_rng(3), 100, 5, 20)
    assert result["observed_partner_input_error"] < result["unobserved_partner_input_bias"]


def test_window_guard_requires_four_windows():
    rows = window_perturbation_curve(np.random.default_rng(4), 30)
    assert any(row["guard"] != "ok" for row in rows)


def test_fixed_reference_calibration_improves_error_and_coverage():
    rows = occasion_error_curve(np.random.default_rng(5), 20, 160, 48)
    assert rows[-1]["rmse"] < rows[1]["rmse"]
    assert .90 <= rows[-1]["coverage"] <= .99
    assert rows[0]["guard"].startswith("single-occasion")
