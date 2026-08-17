"""M4-T3 -- the identity budget.

These defend the three claims the budget rests on: that the depth-weighted
path code really is a depth-weighted prefix, that the excess-bits currency
behaves (log2(K) for a perfect ranking, zero for a random one after the
permutation correction), and that V-T3c's convex combination really is the
cosine of the weighted concatenation it stands in for.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_t3_identity_budget.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_t3_identity_budget",
                                                  SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["m4_t3_identity_budget"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def t3():
    return _load()


class _FakeTree:
    """A frozen two-level tree stand-in with explicit routes."""

    def __init__(self, routes):
        self.routes = routes

    def route_many(self, rows):
        return [self.routes[int(r[0])] for r in np.asarray(rows)]


def test_path_code_dot_product_is_the_depth_weighted_prefix(t3):
    routes = {0: [0, 1, 3, 7], 1: [0, 1, 3, 8], 2: [0, 2, 5, 9]}
    tree = _FakeTree(routes)
    rows = np.array([[0.0], [1.0], [2.0]])
    early, late, leaves = t3.path_codes(tree, rows, rows)
    assert leaves.tolist() == [7, 8, 9]
    # users 0 and 1 share the prefix (1, 3) -> depths 1 and 2 -> 1 + 2 = 3
    assert early[0] @ late[1] == pytest.approx(3.0)
    # a user with itself shares depths 1, 2, 3 -> 1 + 2 + 3 = 6
    assert early[0] @ late[0] == pytest.approx(6.0)
    # users 0 and 2 diverge immediately -> nothing shared
    assert early[0] @ late[2] == pytest.approx(0.0)


def test_within_block_ranks_match_brute_force(t3):
    rng = np.random.default_rng(4)
    negs = [rng.integers(0, 5, size=int(k)).astype(float)
            for k in rng.integers(2, 12, size=15)]
    rd = t3.Reading([0.0] * 15, negs, [(0, 0)] * 15)
    got = rd._within_block_ranks()
    for t in range(15):
        a = rd.neg_off[t]
        block = negs[t]
        for i, v in enumerate(block):
            want = float((block > v).sum()) + 0.5 * float((block == v).sum())
            assert got[a + i] == pytest.approx(want)


def test_excess_bits_is_log2K_for_a_perfect_ranking(t3):
    # every true match outscores every stranger: rank 1, K = 11 -> log2(11)
    negs = [np.zeros(10) for _ in range(50)]
    rd = t3.Reading([1.0] * 50, negs, [(0, 0)] * 50)
    bits = rd._bits_observed()
    assert bits.mean() == pytest.approx(math.log2(11.0))


def test_excess_bits_vanishes_for_a_random_ranking(t3):
    rng = np.random.default_rng(21)
    negs = [rng.normal(size=25) for _ in range(400)]
    rd = t3.Reading([float(x) for x in rng.normal(size=400)], negs,
                    [(0, 0)] * 400)
    res = rd.evaluate(np.random.default_rng(1), b_boot=50, b_perm=200)
    assert abs(res["auc"] - 0.5) < 0.05
    assert abs(res["excess_bits"]) < 0.15
    assert res["bits_null_mean"] > 1.0          # ~1.44 bits before correction
    assert res["auc_check_ok"]


def test_excess_bits_is_large_when_identity_is_strong(t3):
    rng = np.random.default_rng(8)
    negs = [rng.normal(size=25) for _ in range(300)]
    rd = t3.Reading([4.0] * 300, negs, [(0, 0)] * 300)
    res = rd.evaluate(np.random.default_rng(2), b_boot=50, b_perm=200)
    assert res["auc"] > 0.99
    assert res["excess_bits"] > 3.0


def test_convex_combination_equals_cosine_of_weighted_concatenation(t3):
    """RN-T3-9's load-bearing identity."""
    rng = np.random.default_rng(13)
    tree_e, tree_l = rng.normal(size=(6, 9)), rng.normal(size=(6, 9))
    emb_e, emb_l = rng.normal(size=(6, 4)), rng.normal(size=(6, 4))
    cos_tree = t3.cosine_scores(tree_e, tree_l)
    cos_emb = t3.cosine_scores(emb_e, emb_l)
    for w in (0.0, 0.25, 0.5, 0.75, 1.0):
        left = np.hstack([math.sqrt(1 - w) * t3._unit(tree_e),
                          math.sqrt(w) * t3._unit(emb_e)])
        right = np.hstack([math.sqrt(1 - w) * t3._unit(tree_l),
                           math.sqrt(w) * t3._unit(emb_l)])
        concat = left @ right.T
        assert np.allclose(concat, (1 - w) * cos_tree + w * cos_emb, atol=1e-12)


def test_neg_euclid_scores_are_negative_distances(t3):
    a = np.array([[0.0, 0.0], [3.0, 4.0]])
    b = np.array([[0.0, 0.0], [0.0, 1.0]])
    got = t3.neg_euclid_scores(a, b)
    assert got[0, 0] == pytest.approx(0.0)
    assert got[1, 0] == pytest.approx(-5.0)
    assert got[0, 1] == pytest.approx(-1.0)


def test_obs_matrix_is_z_scored_and_four_dimensional(t3):
    rng = np.random.default_rng(6)
    counts = rng.poisson(3.0, size=(40, 12)).astype(float)
    freq = t3.t2().row_normalise(counts)
    span = rng.uniform(10, 900, size=40)
    for log_scale in (False, True):
        z = t3.obs_matrix(counts, freq, span, log_scale=log_scale)
        assert z.shape == (40, 4)
        assert np.allclose(z.mean(axis=0), 0.0, atol=1e-9)
        assert np.allclose(z.std(axis=0), 1.0, atol=1e-9)


def test_verdicts_are_null_first_and_banded(t3):
    major = {"auc": 0.80, "ci95": [0.77, 0.83], "median_pool": 25.0,
             "UNDERRESOLVED": False}
    assert t3.verdict_a(major)["verdict"] == "MAJOR"
    minor = {**major, "auc": 0.55, "ci95": [0.52, 0.58]}
    assert t3.verdict_a(minor)["verdict"] == "MINOR"
    mod = {**major, "auc": 0.70, "ci95": [0.66, 0.74]}
    assert t3.verdict_a(mod)["verdict"] == "MODERATE"
    thin = {**major, "median_pool": 3.0, "UNDERRESOLVED": True}
    assert t3.verdict_a(thin)["verdict"] == "UNDERRESOLVED"
    lives = {"auc": 0.62, "ci95": [0.60, 0.64], "null_band": [0.48, 0.52],
             "median_pool": 25.0, "UNDERRESOLVED": False}
    assert t3.verdict_b(lives)["verdict"] == "SURVIVES"
    dead = {**lives, "auc": 0.51, "ci95": [0.49, 0.53]}
    assert t3.verdict_b(dead)["verdict"] == "DIES"
    assert t3.verdict_c({"ADEQUATE": True})["verdict"] == "ADEQUATE"
    assert t3.verdict_c({"ADEQUATE": False})["verdict"] == "GAP_REMAINS"


def test_routing_is_arm_level_not_conjunctive(t3):
    """The T2 lesson: an undecided arm must not void a decided one."""
    r = t3.route("UNDERRESOLVED", "SURVIVES", "GAP_REMAINS")
    assert "BUDGET_WITH_RESIDUAL" in r["outcomes"]
    assert "TASTE_BEYOND_SUPPORT" in r["modifiers"]
    assert any(m.startswith("UNDERRESOLVED:") for m in r["modifiers"])
    r2 = t3.route("MAJOR", "DIES", "ADEQUATE")
    assert r2["outcomes"] == ["SUPPORT_CHANNEL_MAJOR",
                              "JOINT_REPRESENTATION_ADEQUATE"]
    assert "TRANSPORT_WAS_SUPPORT" in r2["modifiers"]
    r3 = t3.route("UNDERRESOLVED", "UNDERRESOLVED", "UNDERRESOLVED")
    assert r3["outcomes"] == ["UNDERRESOLVED"]


def test_anchors_are_the_adjudicated_constants(t3):
    assert t3.A_FLAT_FULL == 0.9836592822513264
    assert t3.A_FLAT_CLEAN == 0.9660999136733576
    assert t3.A_RESID_FULL == 0.9552295265671575
    assert t3.A_T2_ARMB_AUC == 0.6031409031779736
    assert t3.A_T2_ARMB_NULL == [0.4869631462640095, 0.5149378939035671]
    assert (t3.A_N_FULL, t3.A_N_CLEAN) == (1304, 1269)
    assert t3.POOL_TARGET == 20
    assert t3.EPS_GAP == 0.03
    assert t3.SEED == 20260817
