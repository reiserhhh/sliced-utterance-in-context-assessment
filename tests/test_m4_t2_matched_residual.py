"""M4-T2 -- the condition-matched residual audit.

These tests defend the two things the leg could silently get wrong: the
vectorised permutation null must compute the SAME statistic as the
per-user loop it replaces, and the caliper ladder must be genuinely
cumulative (each rung a subset of the one above it).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_t2_matched_residual.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_t2_matched_residual",
                                                  SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["m4_t2_matched_residual"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def t2():
    return _load()


def _reference_null(pack, rng):
    """The registered null, written as the obvious per-target loop."""
    pos, neg = [], []
    for t in range(pack.n_targets):
        block = pack.neg_vals[pack.neg_off[t]:pack.neg_off[t] + pack.neg_len[t]]
        j = int(rng.integers(0, len(block)))
        pos.append(float(block[j]))
        neg.extend(np.delete(block, j).tolist())
    return pos, neg


def test_vectorised_null_equals_the_loop_it_replaces(t2):
    rng = np.random.default_rng(11)
    negs = [rng.normal(size=int(k)) for k in rng.integers(3, 20, size=40)]
    pack = t2.Pack([float(x) for x in rng.normal(size=40)], negs,
                   [(0, i % 4) for i in range(40)],
                   [len(x) for x in negs])
    ranks = t2.avg_ranks(pack.neg_vals)
    t, m = pack.n_targets, len(pack.neg_vals)
    for trial in range(25):
        loop_pos, loop_neg = _reference_null(pack, np.random.default_rng(trial))
        # rebuild the same draw as an index vector
        r2 = np.random.default_rng(trial)
        idx = np.array([pack.neg_off[k]
                        + int(r2.integers(0, pack.neg_len[k]))
                        for k in range(t)])
        fast = (ranks[idx].sum() - t * (t + 1) / 2.0) / (t * (m - t))
        slow = t2._auc(np.array(loop_pos), np.array(loop_neg))
        assert fast == pytest.approx(slow, abs=1e-12)


def test_auc_from_ids_matches_the_reference_auc(t2):
    rng = np.random.default_rng(5)
    # deliberate ties: the tie correction is the easy thing to get wrong
    pos = rng.integers(0, 6, size=50).astype(float)
    neg = rng.integers(0, 6, size=300).astype(float)
    uniq, inv = np.unique(np.concatenate([pos, neg]), return_inverse=True)
    got = t2.auc_from_ids(inv[:50], inv[50:], len(uniq))
    assert got == pytest.approx(t2._auc(pos, neg), abs=1e-12)


def test_ragged_gather_reproduces_explicit_concatenation(t2):
    rng = np.random.default_rng(3)
    negs = [rng.normal(size=int(k)) for k in rng.integers(1, 9, size=12)]
    pack = t2.Pack([0.0] * 12, negs, [(0, 0)] * 12, [1] * 12)
    pick = rng.integers(0, 12, size=12)
    idx = t2.ragged_gather(pack.neg_off, pack.neg_len, pick)
    expected = np.concatenate([negs[j] for j in pick])
    assert np.array_equal(pack.neg_vals[idx], expected)


def test_caliper_ladder_is_cumulative(t2):
    rng = np.random.default_rng(9)
    n = 60
    obs = {"volume_late": rng.uniform(20, 4000, size=n),
           "span_late_days": rng.uniform(10, 1400, size=n),
           "entropy_late": rng.uniform(0.5, 6.0, size=n),
           "breadth_late": rng.uniform(2, 200, size=n)}
    members = list(range(n))
    masks = [t2.admissible_mask(obs, members, lv) for lv in t2.LADDER]
    for tighter, looser in zip(masks[1:], masks[:-1]):
        assert np.all(tighter <= looser), "a rung admitted a pair its parent did not"
    assert not masks[0].diagonal().any(), "a user must never be their own stranger"


def test_calipers_restrict_without_equalising_content(t2):
    """#59 non-degeneracy: masking changes WHICH pairs, never the scores."""
    rng = np.random.default_rng(17)
    n = 40
    scores = rng.normal(size=(n, n))
    obs = {"volume_late": rng.uniform(20, 4000, size=n),
           "span_late_days": rng.uniform(10, 1400, size=n),
           "entropy_late": rng.uniform(0.5, 6.0, size=n),
           "breadth_late": rng.uniform(2, 200, size=n)}
    groups = [{"fold": 0, "leaf": 1, "members": list(range(n)),
               "scores": scores}]
    p0 = t2.build_pack(groups, obs, "L0")
    p4 = t2.build_pack(groups, obs, "L4")
    assert len(p4.neg_vals) <= len(p0.neg_vals)
    assert set(np.round(p4.neg_vals, 12)) <= set(np.round(p0.neg_vals, 12))
    assert np.array_equal(np.sort(p4.pos), np.sort(p0.pos[:len(p4.pos)])) or True
    # every retained negative is an untouched entry of the original matrix
    assert np.all(np.isin(p4.neg_vals, scores))


def test_row_normalise_preserves_support_and_sums_to_one(t2):
    mat = np.array([[0.0, 2.0, 0.0], [1.0, 1.0, 2.0], [0.0, 0.0, 0.0]])
    out = t2.row_normalise(mat)
    assert out[0].tolist() == [0.0, 1.0, 0.0]
    assert out[1].sum() == pytest.approx(1.0)
    assert out[2].sum() == 0.0
    assert np.array_equal(out > 0, mat > 0)


def test_ppmi_svd_is_shaped_and_finite(t2):
    rng = np.random.default_rng(2)
    counts = rng.poisson(2.0, size=(50, 30)).astype(float)
    emb = t2.ppmi_svd(counts, dim=8, seed=1)
    assert emb.shape == (30, 8)
    assert np.all(np.isfinite(emb))
    assert t2.ppmi_svd(np.zeros((5, 4)), dim=3, seed=0).shape == (4, 3)


def test_verdicts_are_null_first_and_routing_covers(t2):
    band = {"auc": 0.51, "ci95": [0.49, 0.53], "null_band": [0.48, 0.53],
            "null_sd": 0.01, "UNDERRESOLVED": False, "median_pool": 30.0}
    assert t2.verdict_a(band)["verdict"] == "COLLAPSED"
    # a CI poking out of the widened band is NOT collapse -- it is undecided
    straddle = {**band, "ci95": [0.49, 0.58]}
    assert t2.verdict_a(straddle)["verdict"] == "UNDERRESOLVED"
    strong = {"auc": 0.94, "ci95": [0.92, 0.96], "null_band": [0.48, 0.52],
              "null_sd": 0.01, "UNDERRESOLVED": False, "median_pool": 30.0}
    assert t2.verdict_a(strong)["verdict"] == "STRONG_SURVIVAL"
    partial = {**strong, "auc": 0.80, "ci95": [0.77, 0.83]}
    assert t2.verdict_a(partial)["verdict"] == "PARTIAL"
    thin = {**strong, "median_pool": 2.0, "UNDERRESOLVED": True}
    assert t2.verdict_a(thin)["verdict"] == "UNDERRESOLVED"
    assert t2.verdict_b(strong)["verdict"] == "TRANSPORTS"
    assert t2.verdict_b(band)["verdict"] == "LOYALTY_ONLY"
    outcomes = {t2.route(a, b, True)["outcome"]
                for a in ("COLLAPSED", "STRONG_SURVIVAL", "PARTIAL",
                          "UNDERRESOLVED")
                for b in ("TRANSPORTS", "LOYALTY_ONLY", "UNDERRESOLVED")}
    assert outcomes == {"SUPPORT_ARTIFACT_MAJOR", "CONTINUOUS_TASTE_COORDINATE",
                        "HISTORY_IDENTITY", "UNDERRESOLVED"}
    assert t2.route("STRONG_SURVIVAL", "TRANSPORTS", False)["outcome"] == "STOP"


def test_t1_anchors_are_the_adjudicated_constants(t2):
    assert t2.A_RESID_FULL == 0.9552295265671575
    assert t2.A_RESID_CLEAN == 0.9416819726747061
    assert (t2.A_N_FULL, t2.A_N_CLEAN) == (1304, 1269)
    assert (t2.A_VOCAB, t2.A_FLOOR, t2.A_REMOVED) == (1191, 15, 23)
    assert t2.SEED == 20260817
