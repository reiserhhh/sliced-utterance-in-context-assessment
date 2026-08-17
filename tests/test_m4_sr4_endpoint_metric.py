"""M4-SR4 -- the endpoint and the metric.

The leg turns on one algebraic claim (RN-SR4-1): at full rank the PPMI
embedding is a rotation of the unfactorised PPMI space, so the d=1043 row
and the ppmi-full row are the same estimand by two numerical routes. If
that were false, the registration's three-way pattern table would be
comparing two different things and the METRIC_BORNE cell would be
unreachable. The rest pins the pattern table itself.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_sr4_endpoint_metric.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_sr4_endpoint_metric",
                                                  SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["m4_sr4_endpoint_metric"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sr4():
    return _load()


def test_ppmi_matrix_and_sr3_factorisation_are_the_same_object(sr4):
    rng = np.random.default_rng(5)
    counts = rng.poisson(1.7, size=(80, 60)).astype(float)
    pm = sr4.ppmi_matrix(counts)
    sv, vt = sr4.sr3().ppmi_factorisation(counts)
    _u, sv2, vt2 = np.linalg.svd(pm, full_matrices=False)
    assert np.array_equal(sv, sv2)
    assert np.array_equal(vt, vt2)
    assert pm.shape == counts.shape
    assert np.all(pm >= 0.0), "PPMI must be non-negative by construction"


def test_full_rank_embedding_is_a_rotation_of_the_ppmi_space(sr4):
    """RN-SR4-1 -- the claim the whole three-way disambiguation rests on."""
    rng = np.random.default_rng(12)
    counts = rng.poisson(2.0, size=(70, 55)).astype(float)
    freq = sr4.t2().row_normalise(rng.poisson(1.0, size=(40, 55)).astype(float))
    pm = sr4.ppmi_matrix(counts)
    sv, vt = sr4.sr3().ppmi_factorisation(counts)
    full = sr4.sr3().emb_at(sv, vt, vt.shape[0])
    cos_emb = sr4.t3().cosine_scores(freq @ full, freq @ full)
    cos_ppmi = sr4.t3().cosine_scores(freq @ pm.T, freq @ pm.T)
    assert np.abs(cos_emb - cos_ppmi).max() < 1e-10


def test_truncation_below_full_rank_is_not_a_rotation(sr4):
    """The contrast that makes the sweep informative at all."""
    rng = np.random.default_rng(13)
    counts = rng.poisson(2.0, size=(70, 55)).astype(float)
    freq = sr4.t2().row_normalise(rng.poisson(1.0, size=(40, 55)).astype(float))
    pm = sr4.ppmi_matrix(counts)
    sv, vt = sr4.sr3().ppmi_factorisation(counts)
    small = sr4.sr3().emb_at(sv, vt, 4)
    cos_small = sr4.t3().cosine_scores(freq @ small, freq @ small)
    cos_ppmi = sr4.t3().cosine_scores(freq @ pm.T, freq @ pm.T)
    assert np.abs(cos_small - cos_ppmi).max() > 1e-6


def _curve(det: dict[str, bool], r: float = 0.03):
    out = {}
    for row in sr4_rows():
        out[f"{row}|stratified"] = {"DETECTED": det.get(row, False), "r": r,
                                    "degenerate": False}
        out[f"{row}|marginal"] = {"DETECTED": det.get(row, False), "r": r,
                                  "degenerate": False}
    return out


_ROWS_CACHE: list[str] = []


def sr4_rows():
    return _ROWS_CACHE


def test_pattern_table_metric_borne(sr4):
    _ROWS_CACHE[:] = sr4.ROWS
    got = sr4.verdict(_curve({"flat": True}))
    assert got["verdict"] == "METRIC_BORNE"
    assert got["flat_detected"] and not got["any_truncation_detected"]
    assert not got["ppmi_full_detected"]


def test_pattern_table_continuous_high_rank(sr4):
    _ROWS_CACHE[:] = sr4.ROWS
    big = sr4.HALF_FLAT + 0.01
    got = sr4.verdict(_curve({"d=1043": True, "flat": True}, r=big))
    assert got["verdict"] == "CONTINUOUS_CARRIER_HIGH_RANK"
    assert got["first_high_rank_hit"] == "d=1043"
    got768 = sr4.verdict(_curve({"d=768": True, "d=1043": True, "flat": True},
                                r=big))
    assert got768["first_high_rank_hit"] == "d=768"


def test_pattern_table_rank_anomaly(sr4):
    _ROWS_CACHE[:] = sr4.ROWS
    got = sr4.verdict(_curve({"ppmi_full": True, "flat": True}))
    assert got["verdict"] == "RANK_ANOMALY_NAMED"


def test_pattern_table_underresolved_when_nothing_detects(sr4):
    _ROWS_CACHE[:] = sr4.ROWS
    assert sr4.verdict(_curve({}))["verdict"] == "UNDERRESOLVED"
    degen = _curve({"flat": True})
    degen["d=768|stratified"]["degenerate"] = True
    assert sr4.verdict(degen)["verdict"] == "UNDERRESOLVED"


def test_high_rank_detection_below_half_flat_is_still_flagged(sr4):
    _ROWS_CACHE[:] = sr4.ROWS
    got = sr4.verdict(_curve({"d=768": True, "flat": True},
                             r=sr4.HALF_FLAT - 0.005))
    assert got["verdict"] == "CONTINUOUS_CARRIER_HIGH_RANK"
    assert "magnitude caveat" in got["reason"]


def test_rows_and_constants_are_the_registered_ones(sr4):
    assert sr4.DIMS_SR3 == (64, 128, 256, 512)
    assert sr4.DIMS_NEW == (768, 1043)
    assert sr4.ROWS == ["d=64", "d=128", "d=256", "d=512", "d=768", "d=1043",
                        "ppmi_full", "flat"]
    assert sr4.A_SR2_FLAT_WITHIN == 0.04768658177503308
    assert sr4.HALF_FLAT == pytest.approx(0.02384329088751654, abs=1e-15)
    assert sr4.SEED == 20260817
    assert (sr4.A_N_FULL, sr4.A_N_CLEAN, sr4.A_REMOVED) == (1304, 1269, 23)
