"""M4-SR2 -- the trait-coupling budget.

These defend the three things this leg could silently get wrong: that the
masked Mantel is the same statistic SR1 computes when the mask is the whole
triangle, that the stratified permutation really does keep every user inside
its own observability stratum (otherwise the conditional null is not
conditional at all), and that the within-fold mask contains only pairs the
fold-local representations can actually define.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_sr2_coupling_budget.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_sr2_coupling_budget",
                                                  SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["m4_sr2_coupling_budget"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sr2():
    return _load()


def test_masked_mantel_equals_sr1_mantel_on_the_whole_triangle(sr2):
    rng = np.random.default_rng(3)
    n = 40
    x, y = rng.normal(size=(n, 6)), rng.normal(size=(n, 5))
    A = sr2.sr1().hellinger_cos(np.abs(x))
    B = sr2.sr1().neg_euclid(y, squared=True)
    iu = np.triu_indices(n, k=1)
    got = sr2.mantel_masked(A, B, (iu[0], iu[1]), b_perm=10, seed=1)
    assert got["r"] == pytest.approx(sr2.sr1().mantel_r(A, B), abs=1e-12)
    assert got["n_pairs"] == n * (n - 1) // 2


def test_stratified_permutation_never_leaves_its_stratum(sr2):
    rng = np.random.default_rng(7)
    strata = np.repeat(np.arange(6), 20)
    for _ in range(30):
        p = sr2._permute(len(strata), rng, strata)
        assert sorted(p.tolist()) == list(range(len(strata)))
        assert np.array_equal(strata[p], strata), "a user changed stratum"
    free = sr2._permute(len(strata), rng, None)
    assert sorted(free.tolist()) == list(range(len(strata)))


def test_masked_mantel_detects_a_planted_coupling_and_not_noise(sr2):
    rng = np.random.default_rng(11)
    n = 60
    z = rng.normal(size=(n, 5))
    B = sr2.sr1().neg_euclid(z, squared=True)
    iu = np.triu_indices(n, k=1)
    planted = sr2.mantel_masked(B + 0.05 * rng.normal(size=(n, n)), B,
                                (iu[0], iu[1]), b_perm=199, seed=2)
    assert planted["DETECTED"]
    assert planted["p_one_sided_positive"] < 0.05
    noise = sr2.sr1().hellinger_cos(np.abs(rng.normal(size=(n, 8))))
    got = sr2.mantel_masked(noise, B, (iu[0], iu[1]), b_perm=199, seed=3)
    assert abs(got["null_mean"]) < 0.05
    assert got["null_sd"] > 0


def test_masked_mantel_reports_degeneracy_instead_of_inventing_a_number(sr2):
    n = 20
    A = np.ones((n, n))
    B = sr2.sr1().neg_euclid(np.random.default_rng(1).normal(size=(n, 5)))
    iu = np.triu_indices(n, k=1)
    got = sr2.mantel_masked(A, B, (iu[0], iu[1]), b_perm=10, seed=1)
    assert got["degenerate"] and got["r"] == 0.0


def test_within_fold_mask_contains_only_same_fold_defined_pairs(sr2):
    fold_of = np.array([0, 0, 1, 1, -1, 2, 2, 0])
    sel = {"n": len(fold_of), "fold_of": fold_of}
    m = sr2.pair_masks(sel)
    i, j = m["within_fold"]
    assert len(i) == m["n_within"]
    assert np.all(fold_of[i] == fold_of[j])
    assert np.all(fold_of[i] >= 0), "an unrouted user entered the mask"
    assert np.all(i < j), "the mask must be an upper triangle"
    assert m["n_full"] == len(fold_of) * (len(fold_of) - 1) // 2


def test_observability_strata_are_balanced_and_meet_the_pool_target(sr2):
    rng = np.random.default_rng(5)
    obs = rng.normal(size=(1000, 4))
    obs[:, 0] += np.linspace(0, 6, 1000)          # a real leading axis
    st = sr2.observability_strata(obs)
    assert st["n_strata"] == sr2.N_STRATA
    assert sum(st["sizes"]) == 1000
    assert st["min_stratum"] - 1 >= sr2.POOL_TARGET
    assert st["meets_pool_target"]
    assert 0.0 < st["explained_variance"] <= 1.0


def test_verdicts_are_null_first(sr2):
    hit = {"DETECTED": True, "degenerate": False}
    miss = {"DETECTED": False, "degenerate": False}
    assert sr2.verdict_a(hit)["verdict"] == "DETECTED"
    assert sr2.verdict_a(miss)["verdict"] == "NULL"
    assert sr2.verdict_a({"degenerate": True})["verdict"] == "UNDERRESOLVED"
    assert sr2.verdict_b(hit, hit)["verdict"] == "detected-and-SURVIVES"
    assert sr2.verdict_b(hit, miss)["verdict"] == "detected-but-DIES"
    assert sr2.verdict_b(miss, hit)["verdict"] == "NULL_MARGINAL"
    assert sr2.verdict_c(hit)["verdict"] == "SURVIVES"
    assert sr2.verdict_c(miss)["verdict"] == "DIES"


def test_routing_is_arm_level_and_covering(sr2):
    assert sr2.route("DETECTED", "detected-but-DIES", "DIES")["outcome"] == \
        "SR1_RETYPED_SUPPORT_CONFOUND"
    assert sr2.route("NULL", "detected-and-SURVIVES", "SURVIVES")["outcome"] == \
        "TASTE_CARRIES_THE_COUPLING"
    for vb in ("detected-but-DIES", "NULL_MARGINAL"):
        assert sr2.route("NULL", vb, "SURVIVES")["outcome"] == \
            "COUPLING_BEYOND_TASTE"
    und = sr2.route("UNDERRESOLVED", "NULL_MARGINAL", "UNDERRESOLVED")
    assert und["outcome"] == "UNDERRESOLVED"
    assert any(m.startswith("UNDERRESOLVED:") for m in und["modifiers"])
    # V-SR2a never gates the others -- it only ever contributes a modifier
    a_hit = sr2.route("DETECTED", "NULL_MARGINAL", "SURVIVES")
    a_miss = sr2.route("NULL", "NULL_MARGINAL", "SURVIVES")
    assert a_hit["outcome"] == a_miss["outcome"] == "COUPLING_BEYOND_TASTE"
    assert "SUPPORT_TRAIT_COUPLING_DETECTED" in a_hit["modifiers"]
    assert "SUPPORT_TRAIT_COUPLING_NULL" in a_miss["modifiers"]


def test_anchors_are_the_adjudicated_constants(sr2):
    assert sr2.A_SR1_R == 0.048987613136188025
    assert sr2.A_SR1_PAIRS == 852165
    assert sr2.A_SR1_USERS == 1306
    assert sr2.A_SR1_NULL_SD == 0.009064019613144935
    assert sr2.A_T3_OBS == 0.7293990670964055
    assert sr2.A_T3_EMB_STRAT == 0.9311359256886822
    assert (sr2.A_N_FULL, sr2.A_N_CLEAN, sr2.A_REMOVED) == (1304, 1269, 23)
    assert (sr2.SEED, sr2.SR1_SEED) == (20260817, 20260816)
    assert sr2.POOL_TARGET == 20 and sr2.N_STRATA == 10
