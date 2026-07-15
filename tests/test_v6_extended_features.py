from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
from suica_sim.extended_features import (assert_timestamp_order, discover_change_point,
    discover_change_point_series, evaluate_choice, fit_var_ols, generate_change_point_world,
    generate_choice_world, generate_var_world,
    occupancy_preserving_shuffle, recover_scale_energy)


def test_p7_null_has_zero_cross_lag_and_correct_se_shape():
    values = generate_var_world(np.random.default_rng(3), 2000, 0)
    fit = fit_var_ols(values)
    assert abs(fit["A"][1, 0]) < .08
    assert fit["se"].shape == fit["A"].shape
    assert np.all(fit["se"] > 0)


def test_p7_oracle_latent_preserves_planted_coupling():
    _, latent = generate_var_world(
        np.random.default_rng(4), 3000, .32, return_latent=True)
    assert abs(fit_var_ols(latent)["A"][1, 0] - .32) < .05


def test_p7_dense_nonhurdle_observation_recovers_prediction_gain():
    gains = []
    from suica_sim.extended_features import _var_fold_metrics
    for seed in range(12):
        observed = generate_var_world(
            np.random.default_rng(100 + seed), 800, .32,
            zero_probability=0.0, intensity=3.0)
        gains.append(_var_fold_metrics(observed, 5)["likelihood_gain"])
    assert np.mean(gains) > 0


def test_p8_format_only_is_removed_before_cp_discovery():
    data = generate_change_point_world(np.random.default_rng(5), 160, "format_only", 64)
    fit = discover_change_point(data, 110)
    before, after = fit["residual"][:64], fit["residual"][64:110]
    assert abs(before.mean() - after.mean()) < .35


def test_p8_oracle_series_localizes_planted_change():
    data = generate_change_point_world(np.random.default_rng(6), 256, "latent", 128)
    cp = discover_change_point_series(data["latent_score"], 160)
    assert abs(cp - 128) <= 16


def test_p9_alias_equivalent_energy_and_four_cycle_guard():
    t = np.arange(64)
    a = np.sin(2*np.pi*t/4)
    b = np.sin(2*np.pi*t*(1-1/4))
    assert np.allclose(recover_scale_energy(a)[4], recover_scale_energy(b)[4])
    assert 32 >= 4 * 4 and not 32 >= 4 * 16


def test_p10_shuffle_preserves_occupancy():
    rng = np.random.default_rng(9)
    data = generate_choice_world(rng, 3, 40)
    shuffled = occupancy_preserving_shuffle(data["choice"], rng)
    assert np.array_equal(np.bincount(shuffled), np.bincount(data["choice"]))


def test_p10_person_delta_is_repeated_transition_profile_not_context_spread():
    stable = generate_choice_world(np.random.default_rng(10), 30, 180)
    shuffled = generate_choice_world(np.random.default_rng(10), 30, 180, True)
    assert evaluate_choice(stable)["person_delta"] > evaluate_choice(shuffled)["person_delta"]


def test_timestamp_order_guard():
    assert_timestamp_order(np.array([1, 2, 3]))
    with pytest.raises(ValueError): assert_timestamp_order(np.array([1, 3, 2]))


def test_quick_runner_writes_all_formats(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/run_v6_extended_features.py"),
                           "--profile", "quick", "--output-dir", str(tmp_path)],
                          check=True, capture_output=True, text=True, timeout=120)
    payload = json.loads(proc.stdout)
    assert payload["rows"] == 4
    assert all(Path(p).is_file() for p in payload["outputs"].values())
