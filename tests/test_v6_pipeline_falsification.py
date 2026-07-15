from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from suica_sim.pipeline import (_discover_axis, _fold_matched_strangers, _pvalue, _statistic,
                                _within_occasion_center, fit_crossfit,
                                load_pipeline_config, null_refits, person_delta,
                                run_pipeline)
from suica_sim.pipeline_worlds import generate_pipeline_world, matched_strangers


def _cfg():
    cfg, digest = load_pipeline_config(ROOT / "configs/sim_v6/pipeline_quick.json")
    return cfg, digest


def test_outer_test_users_never_participate_in_fit():
    cfg, _ = _cfg(); data = generate_pipeline_world(1, "P5_alt", persons=30)
    fits = fit_crossfit(data, folds=3, inner_folds=2, seed=2)
    for fit in fits:
        assert set(fit.train_users).isdisjoint(fit.test_users)
        assert set(fit.train_users) | set(fit.test_users) == set(np.unique(data.person))


def test_null_draws_reselect_axis_after_fresh_dgp():
    cfg, _ = _cfg(); refs = null_refits(cfg, "P0_null", 3, 9)
    assert len({r["dgp_seed"] for r in refs}) == 3
    assert len({tuple(r["axis_hashes"]) for r in refs}) == 3


def test_matched_stranger_has_support_and_no_self_match():
    data = generate_pipeline_world(3, "P5_alt", persons=24)
    strangers = matched_strangers(data, np.random.default_rng(4))
    assert len(strangers) == 24
    assert np.all(strangers != np.arange(24))


def test_matched_strangers_are_within_outer_test_fold():
    data = generate_pipeline_world(31, "P5_alt", persons=30)
    fits = fit_crossfit(data, folds=3, inner_folds=2, seed=32)
    for fit in fits:
        assert set(fit.scores) == set(fit.test_users)
        assert set(fit.occasion_susceptibility) == set(fit.test_users)
        assert all(v.shape[0] == 4 for v in fit.occasion_susceptibility.values())
        matches = _fold_matched_strangers(data, fit)
        assert all(u in fit.test_users and v in fit.test_users and u != v
                   for u, v in matches.items())


def test_add_one_p_value_is_never_zero():
    assert _pvalue(100.0, [0.0] * 9) == .1


def test_segmentation_jitter_artifact_can_trigger():
    clean = generate_pipeline_world(5, "P2_artifact", persons=60, jitter=0.0)
    artifact = generate_pipeline_world(5, "P2_artifact", persons=60, jitter=2.0)
    clean_var = np.var(clean.counts / clean.opportunity[:, None])
    artifact_var = np.var(artifact.counts / artifact.opportunity[:, None])
    assert artifact_var > clean_var


def test_null_world_cannot_emit_person_claim():
    data = generate_pipeline_world(7, "P5_null", persons=20)
    assert data.metadata["person_amplitude"] == 0.0
    assert data.world.endswith("null")


def test_person_alt_delta_exceeds_person_null():
    null = generate_pipeline_world(41, "P5_null", persons=72, occasions=5, windows=8)
    alt = generate_pipeline_world(41, "P5_alt", persons=72, occasions=5, windows=8,
                                  signal_scale=1.8)
    null_fits = fit_crossfit(null, folds=3, inner_folds=2, seed=42)
    alt_fits = fit_crossfit(alt, folds=3, inner_folds=2, seed=42)
    assert person_delta(alt, alt_fits, 43, 99)[0] > person_delta(null, null_fits, 43, 99)[0]


def test_congruence_recovers_strong_low_rank_signal():
    cfg, _ = _cfg(); cfg = {**cfg, "persons": 90, "occasions": 5, "windows": 8}
    data = generate_pipeline_world(51, "P3_lowrank", persons=90, occasions=5,
                                   windows=8, signal_scale=2.5)
    assert _statistic(data, cfg, 52)["congruence"] > .5


def test_congruence_is_invariant_to_rotation_within_truth_subspace():
    rng = np.random.default_rng(53)
    truth, _ = np.linalg.qr(rng.normal(size=(6, 2)))
    rotated_axis = truth @ np.array([[1.0], [1.0]]) / np.sqrt(2)
    from suica_sim.pipeline import principal_congruence
    assert principal_congruence(rotated_axis, truth)["congruence"] > .999


def test_static_shift_does_not_change_dynamic_eigen_materially():
    data = generate_pipeline_world(61, "P3_lowrank", persons=40, occasions=5, windows=8)
    rng = np.random.default_rng(62)
    residual = rng.normal(size=(len(data.person), data.counts.shape[1]))
    shifted = residual + rng.normal(scale=10, size=(40, data.counts.shape[1]))[data.person]
    mask = np.ones(len(data.person), dtype=bool)
    centered = _within_occasion_center(residual, data, mask)
    shifted_centered = _within_occasion_center(shifted, data, mask)
    _, _, eigen = _discover_axis(centered, data, mask, 2)
    _, _, shifted_eigen = _discover_axis(shifted_centered, data, mask, 2)
    assert np.allclose(centered, shifted_centered)
    assert np.allclose(eigen, shifted_eigen)


def test_full_config_has_required_null_draws():
    full = json.loads((ROOT / "configs/sim_v6/pipeline_full.json").read_text())
    assert full["null_draws"] >= 1999


def test_quick_schema_and_saved_audit_material():
    cfg, digest = _cfg(); result = run_pipeline(cfg, digest)
    assert len(result["rows"]) == 7 and result["diagnostic_only"] is True
    assert {"config_hash", "code_hash", "data_hash", "null_distribution",
            "max_t_null", "fold_assignments", "fpr_wilson_ci", "gates"} <= result.keys()
    assert all(r["p_raw"] > 0 and r["p_fwer"] > 0 for r in result["rows"])
    assert next(r for r in result["rows"] if r["world"] == "SIM-P1")["hidden_opportunity_refusal"]
    p2 = next(r for r in result["rows"] if r["world"] == "SIM-P2")
    assert len(p2["segmentation_projector_distance"]) == 3
    assert result["gates"]["scenario_detection"] is None
    assert result["gates"]["power"] is None
    assert result["power_status"].startswith("not estimated")
