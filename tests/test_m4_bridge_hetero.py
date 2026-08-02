"""Tests for the leg-13 heteroscedastic bridge calibration (additive layer).

Coverage per the leg plan: the default selector path is byte-identical to
leg 2 (no new keys, same numbers), the heteroscedastic generators are
variance-matched to the homoscedastic battery, the replicate variance model
recovers per-author noise structure, the two calibrated floors behave as
designed on homoscedastic / heteroscedastic / C2-machinery fields, and the
group-only refusal survives every selector arm.
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from suica_core.m4_relation_bridge import (
    RelationBridgeConfig,
    c2_machinery_relation_world,
    gram_from_relation,
    heteroscedastic_relation_world,
    permutation_floor,
    planted_relation_world,
    replicate_noise_sd_model,
    rigidity_report,
    spectral_profile,
    squared_distance_field,
    variance_weighted_floor,
)

CONFIG = RelationBridgeConfig()
ARMS = ("negative_spectrum", "variance_weighted", "permutation")


def _arm_report(world, arm, *, seed):
    return rigidity_report(
        world["fields"][0],
        config=CONFIG,
        seed=seed,
        selector=arm,
        replicate_field=world["fields"][1],
        permutation_seed=seed + 10,
    )


def test_default_selector_path_unchanged():
    """The default call must stay byte-identical to leg 2: same key set
    (no selector bookkeeping keys) and same numbers as the explicit
    negative_spectrum selector."""
    world = planted_relation_world("individual", noise=0.1, seed=901)
    default = rigidity_report(world["fields"][0], config=CONFIG, seed=902)
    explicit = rigidity_report(
        world["fields"][0],
        config=CONFIG,
        seed=902,
        selector="negative_spectrum",
        replicate_field=world["fields"][1],
    )
    assert default == explicit
    assert sorted(default.keys()) == [
        "auto_rank",
        "dispersion_ratio",
        "lambda_next",
        "lambda_rank",
        "noise_floor",
        "probe_sigma",
        "refusal_reason",
        "rigidity_index",
        "selected_rank",
        "spectral_margin",
        "stability",
        "status",
    ]


def test_unknown_selector_and_missing_replicate_raise():
    world = planted_relation_world("individual", noise=0.1, seed=903)
    with pytest.raises(ValueError):
        rigidity_report(
            world["fields"][0], config=CONFIG, selector="bogus"
        )
    for arm in ARMS[1:]:
        with pytest.raises(ValueError):
            rigidity_report(
                world["fields"][0], config=CONFIG, selector=arm
            )


def test_homoscedastic_worlds_agree_across_arms():
    """On a clean homoscedastic individual world all three floors select
    the planted rank, so margin/stability/index coincide exactly."""
    world = planted_relation_world("individual", noise=0.1, seed=901)
    reports = [_arm_report(world, arm, seed=902) for arm in ARMS]
    assert [r["selected_rank"] for r in reports] == [3, 3, 3]
    assert all(r["status"] == "R_TO_V_LICENSED" for r in reports)
    for report in reports[1:]:
        assert report["rigidity_index"] == pytest.approx(
            reports[0]["rigidity_index"], abs=1e-12
        )


def test_hetero_generators_variance_matched():
    """Both mechanisms are variance-matched in expectation to the
    homoscedastic battery at the same noise level."""
    world = heteroscedastic_relation_world(
        "individual", mechanism="pair_magnitude", noise=0.2, seed=904
    )
    exact = squared_distance_field(world["truth"])
    mask = ~np.eye(len(exact), dtype=bool)

    def offdiag_rms(matrix):
        return float(np.sqrt(np.mean(matrix[mask] ** 2)))

    realized = offdiag_rms(world["fields"][0] - exact)
    nominal = 0.2 * offdiag_rms(exact)
    assert 0.85 < realized / nominal < 1.15
    world = heteroscedastic_relation_world(
        "individual",
        mechanism="author_lognormal",
        noise=0.2,
        author_sigma=1.0,
        seed=905,
    )
    exact = squared_distance_field(world["truth"])
    realized = offdiag_rms(world["fields"][0] - exact)
    nominal = 0.2 * offdiag_rms(exact)
    assert 0.4 < realized / nominal < 2.5  # heavy-tailed factors
    assert world["family"] == "h2_individual"
    assert np.isfinite(world["author_factor_max"])


def test_replicate_variance_model_recovers_row_structure():
    """The rank-one row/col model must track the realized per-row noise
    power under strong per-author heterogeneity (H2, sigma 1.5)."""
    world = heteroscedastic_relation_world(
        "individual",
        mechanism="author_lognormal",
        noise=0.2,
        author_sigma=1.5,
        seed=903,
    )
    exact = squared_distance_field(world["truth"])
    sd_model = replicate_noise_sd_model(
        world["fields"][0], world["fields"][1]
    )
    model_power = (sd_model**2).sum(axis=1)
    realized_power = ((world["fields"][0] - exact) ** 2).sum(axis=1)
    correlation = spearmanr(model_power, realized_power).statistic
    assert correlation > 0.8  # observed .975 at this seed


def test_variance_weighted_floor_matches_homoscedastic_scale():
    """In the homoscedastic case the analytic weighted edge reduces to
    sigma * sqrt(n-1), i.e. the negative-spectrum floor's scale."""
    world = planted_relation_world("individual", noise=0.1, seed=901)
    gram = gram_from_relation(world["fields"][0])
    profile = spectral_profile(gram)
    floor = variance_weighted_floor(
        replicate_noise_sd_model(world["fields"][0], world["fields"][1])
    )
    assert 0.6 < floor / profile["noise_floor"] < 1.6


def test_permutation_floor_deterministic_and_scaled():
    world = heteroscedastic_relation_world(
        "individual", mechanism="pair_magnitude", noise=0.2, seed=904
    )
    one = permutation_floor(
        world["fields"][0], world["fields"][1], seed=7
    )
    two = permutation_floor(
        world["fields"][0], world["fields"][1], seed=7
    )
    assert one == two
    gram = gram_from_relation(world["fields"][0])
    profile = spectral_profile(gram)
    assert 0.5 < one / profile["noise_floor"] < 2.0


def test_noise_floor_override_changes_only_the_floor():
    world = planted_relation_world("individual", noise=0.1, seed=906)
    gram = gram_from_relation(world["fields"][0])
    base = spectral_profile(gram)
    overridden = spectral_profile(gram, noise_floor_override=1e9)
    assert overridden["selected_rank"] == 0
    assert np.allclose(
        overridden["eigenvalues"], base["eigenvalues"]
    )


def test_c2_baseline_floor_collapse_is_the_cap_mechanism():
    """The C2 empirical-logit field is an exact squared-distance matrix of
    noisy profile vectors, so its Gram is PSD up to float error: the
    negative-spectrum floor collapses to ~0 and the auto-rank caps."""
    world = c2_machinery_relation_world("joint", epsilon=1.5, seed=905)
    profile = spectral_profile(gram_from_relation(world["fields"][0]))
    assert profile["noise_floor"] < 1e-6
    assert profile["selected_rank"] == CONFIG.rank_cap


def test_c2_variance_weighted_uncaps_with_positive_margin():
    world = c2_machinery_relation_world("joint", epsilon=1.5, seed=905)
    report = _arm_report(world, "variance_weighted", seed=906)
    assert report["selected_rank"] < CONFIG.rank_cap
    assert report["selected_rank"] >= 1
    assert report["spectral_margin"] > 0.0
    assert report["status"] == "R_TO_V_REFUSED"  # license stays shut


def test_group_only_refused_under_every_arm():
    """The vanishing-individuality trap must be refused by all selector
    arms, both for the planted analogue and the C2 machinery."""
    planted = planted_relation_world("group_only", noise=0.1, seed=902)
    machinery = c2_machinery_relation_world("group_only", seed=11)
    for world in (planted, machinery):
        for arm in ARMS:
            report = _arm_report(world, arm, seed=907)
            assert report["status"] == "R_TO_V_REFUSED"
    # the permutation floor un-caps the machinery null to near the oracle
    # rank while still refusing (observed rank 3 at this seed)
    report = _arm_report(machinery, "permutation", seed=907)
    assert report["selected_rank"] < CONFIG.rank_cap
