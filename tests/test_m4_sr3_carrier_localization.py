"""M4-SR3 -- carrier localization.

The load-bearing claim of this leg's implementation is RN-SR3-1: that
slicing one PPMI factorisation to different widths IS T2/T3's frozen
recipe at each d, not an approximation of it. If that were false the whole
sweep would be measuring a different object at every point. The rest
defends the curve classification, which has to distinguish "no carrier
found" from "carrier found but small".
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_sr3_carrier_localization.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_sr3_carrier_localization",
                                                  SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["m4_sr3_carrier_localization"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sr3():
    return _load()


def test_sliced_embedding_is_bit_identical_to_the_frozen_recipe(sr3):
    """RN-SR3-1 -- the claim the whole sweep rests on."""
    rng = np.random.default_rng(4)
    counts = rng.poisson(1.5, size=(120, 90)).astype(float)
    sv, vt = sr3.ppmi_factorisation(counts)
    for d in (8, 16, 32, 64, 89):
        assert np.array_equal(sr3.emb_at(sv, vt, d),
                              sr3.t2().ppmi_svd(counts, d, 0)), \
            f"slice at d={d} differs from the recipe"


def test_slices_are_prefixes_of_one_another(sr3):
    rng = np.random.default_rng(9)
    counts = rng.poisson(2.0, size=(60, 50)).astype(float)
    sv, vt = sr3.ppmi_factorisation(counts)
    small, large = sr3.emb_at(sv, vt, 8), sr3.emb_at(sv, vt, 32)
    assert np.array_equal(small, large[:, :8])


def test_requested_dimension_is_capped_by_available_rank(sr3):
    rng = np.random.default_rng(2)
    counts = rng.poisson(1.0, size=(10, 40)).astype(float)
    sv, vt = sr3.ppmi_factorisation(counts)
    emb = sr3.emb_at(sv, vt, 512)
    assert emb.shape == (40, vt.shape[0])
    assert emb.shape[1] <= 10
    assert sr3.ppmi_factorisation(np.zeros((5, 4)))[0].size == 0


def test_identity_reading_builds_one_positive_per_target(sr3):
    rng = np.random.default_rng(6)
    blocks = []
    for fold in range(3):
        m = 7
        blocks.append((fold, list(range(m)), rng.normal(size=(m, m))))
    rd = sr3.identity_reading(blocks)
    assert rd.n == 21
    assert np.all(rd.neg_len == 6)
    assert len(rd.neg_vals) == 21 * 6
    assert {k[0] for k in rd.keys} == {0, 1, 2}


def test_verdict_a_separates_no_carrier_from_small_carrier(sr3):
    half = 0.5 * sr3.A_SR2_FLAT_WITHIN

    def curve(det_at=None, r=0.03):
        out = {}
        for d in sr3.DIMS:
            hit = det_at is not None and d >= det_at
            out[f"d={d}|stratified"] = {"DETECTED": hit, "r": r,
                                        "degenerate": False}
            out[f"d={d}|marginal"] = {"r": r, "DETECTED": hit,
                                      "degenerate": False}
        out["flat|stratified"] = {"DETECTED": True, "r": 0.048,
                                  "degenerate": False}
        out["flat|marginal"] = {"DETECTED": True, "r": 0.048,
                                "degenerate": False}
        return out

    assert sr3.verdict_a(curve(), half)["verdict"] == "INDICATOR_CARRIER"
    big = sr3.verdict_a(curve(det_at=256, r=half + 0.01), half)
    assert big["verdict"] == "CONTINUOUS_CARRIER"
    assert big["first_detected_d"] == 256
    small = sr3.verdict_a(curve(det_at=128, r=half - 0.01), half)
    assert small["verdict"] == "MIXED"
    assert small["first_detected_d"] == 128
    dead = curve()
    dead["flat|stratified"]["DETECTED"] = False
    assert sr3.verdict_a(dead, half)["verdict"] == "UNDERRESOLVED"
    degen = curve()
    degen["d=64|stratified"]["degenerate"] = True
    assert sr3.verdict_a(degen, half)["verdict"] == "UNDERRESOLVED"


def test_verdict_a_reports_monotonicity_of_the_marginal_curve(sr3):
    half = 0.5 * sr3.A_SR2_FLAT_WITHIN
    rising, falling = {}, {}
    for i, d in enumerate(sr3.DIMS):
        for tgt, seq in ((rising, [0.01, 0.02, 0.03, 0.04]),
                         (falling, [0.04, 0.03, 0.02, 0.01])):
            tgt[f"d={d}|marginal"] = {"r": seq[i], "DETECTED": False,
                                      "degenerate": False}
            tgt[f"d={d}|stratified"] = {"r": seq[i], "DETECTED": False,
                                        "degenerate": False}
    for tgt in (rising, falling):
        tgt["flat|stratified"] = {"DETECTED": True, "r": 0.048,
                                  "degenerate": False}
        tgt["flat|marginal"] = {"DETECTED": True, "r": 0.048,
                                "degenerate": False}
    assert sr3.verdict_a(rising, half)["marginal_monotone_nondecreasing"]
    assert not sr3.verdict_a(falling, half)["marginal_monotone_nondecreasing"]


def test_verdict_b_measures_how_much_of_the_identity_gap_closes(sr3):
    ident = {"flat": {"auc": 0.98, "ci95": [0.975, 0.985]}}
    for d, auc in zip(sr3.DIMS, (0.94, 0.95, 0.96, 0.97)):
        ident[f"d={d}"] = {"auc": auc, "ci95": [auc - 0.005, auc + 0.004]}
    got = sr3.verdict_b(ident)
    assert got["gap_at_d64"] == pytest.approx(0.04)
    assert got["gap_at_d512"] == pytest.approx(0.01)
    assert got["fraction_of_gap_closed"] == pytest.approx(0.75)
    assert not got["ci_overlaps_flat_at_512"]
    ident[f"d={max(sr3.DIMS)}"] = {"auc": 0.978, "ci95": [0.974, 0.982]}
    assert sr3.verdict_b(ident)["ci_overlaps_flat_at_512"]


def test_route_carries_the_classification_into_the_slug(sr3):
    assert sr3.route("CONTINUOUS_CARRIER")["slug"] == "continuous-carrier"
    assert sr3.route("INDICATOR_CARRIER")["slug"] == "indicator-carrier"
    assert sr3.route("MIXED")["slug"] == "mixed"
    assert sr3.route("UNDERRESOLVED")["outcome"] == "UNDERRESOLVED"


def test_anchors_are_the_adjudicated_constants(sr3):
    assert sr3.A_SR2_EMB64_MARGINAL == 0.023884547516782918
    assert sr3.A_SR2_FLAT_WITHIN == 0.04768658177503308
    assert sr3.A_SR1_FULL == 0.048987613136188025
    assert sr3.A_T3_EMB64_AUC == 0.9449125076918007
    assert sr3.A_T3_FLAT_AUC == 0.9836592913058296
    assert sr3.A_T3_JOINT_AUC == 0.9449583347971448
    assert sr3.DIMS == (64, 128, 256, 512)
    assert (sr3.SEED, sr3.SR1_SEED) == (20260817, 20260816)
    assert sr3.POOL_TARGET == 20
