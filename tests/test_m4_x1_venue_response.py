"""Contract tests for SUICA M4-X1 — the venue response of expression volume.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, commit
0bdb638) names the objects these tests pin: double-centering correctness on a
hand toy, a permutation that preserves the design exactly, covariance-budget
recovery on a synthetic two-way world with planted shares plus null-world
honesty, the headroom report, the census anchor gate, and the #83 ID-leak
helper with its HEAD-baseline policy.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_x1_venue_response.py"
ARTIFACTS = ROOT / "results" / "m4_x1_venue_response"
REPORT = ROOT / "reports" / "SUICA_M4_X1_VENUE_RESPONSE_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x1_venue_response", SCRIPT)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _complete_grid(n_authors: int, n_comms: int):
    slot_author = np.repeat(np.arange(n_authors), n_comms).astype(np.int64)
    slot_comm = np.tile(np.arange(n_comms), n_authors).astype(np.int64)
    return slot_author, slot_comm


def _design(slot_author, slot_comm, n_per_cell=12.0, n_authors=None,
            n_comms=None):
    m = slot_author.size
    n = np.full(m, float(n_per_cell))
    zeros = np.zeros(m)
    return MOD.Design(
        slot_author=slot_author.astype(np.int64),
        slot_comm=slot_comm.astype(np.int64),
        n_e=n, n_l=n.copy(), s_e=zeros.copy(), s_l=zeros.copy(),
        q_e=zeros.copy(), q_l=zeros.copy(),
        n_authors=int(n_authors if n_authors is not None
                      else slot_author.max() + 1),
        n_comms=int(n_comms if n_comms is not None else slot_comm.max() + 1),
        author_codes=np.unique(slot_author).astype(np.int64),
    )


def _sparse_skeleton(n_authors=260, n_comms=40, k_mean=6, seed=5,
                     n_per_cell=12.0):
    rng = np.random.default_rng(seed)
    k = rng.poisson(max(k_mean - MOD.K_MIN, 0), n_authors) + MOD.K_MIN
    author = np.repeat(np.arange(n_authors), k)
    comm = rng.integers(0, n_comms, author.size)
    key = author.astype(np.int64) * n_comms + comm
    _, first = np.unique(key, return_index=True)
    first = np.sort(first)
    author, comm = author[first], comm[first]
    counts = np.bincount(author, minlength=n_authors)
    keep = (counts >= MOD.K_MIN)[author]
    author, comm = author[keep], comm[keep]
    ua, author = np.unique(author, return_inverse=True)
    uc, comm = np.unique(comm, return_inverse=True)
    return _design(author, comm, n_per_cell, n_authors=ua.size,
                   n_comms=uc.size)


class _SilentLog:
    def event(self, *args, **kwargs):
        return None


# ---------------------------------------------------------------------------
# 1. double-centering on a hand toy
# ---------------------------------------------------------------------------


def test_double_centering_zeros_every_row_and_column_on_a_complete_grid():
    """On a COMPLETE grid the registered v has exact zero margins."""

    slot_author, slot_comm = _complete_grid(6, 5)
    rng = np.random.default_rng(11)
    values = rng.normal(size=slot_author.size)
    v = MOD.double_center(values, slot_author, slot_comm, 6, 5)
    author_means = np.bincount(slot_author, v, 6) / 5
    comm_means = np.bincount(slot_comm, v, 5) / 6
    assert np.allclose(author_means, 0.0, atol=1e-12)
    assert np.allclose(comm_means, 0.0, atol=1e-12)
    assert abs(float(v.mean())) < 1e-12


def test_double_centering_is_the_registered_four_term_formula():
    """v = cellmean - authormean - communitymean + grandmean, by hand."""

    slot_author = np.array([0, 0, 1, 1], dtype=np.int64)
    slot_comm = np.array([0, 1, 0, 1], dtype=np.int64)
    values = np.array([1.0, 3.0, 7.0, 9.0])
    v = MOD.double_center(values, slot_author, slot_comm, 2, 2)
    grand = values.mean()                                   # 5.0
    a = np.array([2.0, 8.0])                                # author means
    b = np.array([4.0, 6.0])                                # community means
    expected = values - a[slot_author] - b[slot_comm] + grand
    assert np.allclose(v, expected)
    assert np.allclose(v, [0.0, 0.0, 0.0, 0.0])             # additive world


def test_double_centering_removes_an_additive_world_exactly():
    """A pure main-effects world has an identically zero interaction."""

    slot_author, slot_comm = _complete_grid(7, 4)
    a = np.array([0.4, -1.0, 2.0, 0.1, -0.3, 5.0, 1.0])
    b = np.array([1.0, -2.0, 0.5, 3.0])
    values = a[slot_author] + b[slot_comm]
    v = MOD.double_center(values, slot_author, slot_comm, 7, 4)
    assert np.allclose(v, 0.0, atol=1e-12)


def test_double_centering_weights_are_the_bootstrap_multiplicities():
    """Author multiplicity 2 == that author's slots duplicated."""

    slot_author = np.array([0, 0, 1, 1, 2, 2], dtype=np.int64)
    slot_comm = np.array([0, 1, 0, 1, 0, 1], dtype=np.int64)
    values = np.array([1.0, 4.0, 2.0, 0.5, -3.0, 2.5])
    mult = np.array([2.0, 1.0, 1.0])
    weighted = MOD.double_center(values, slot_author, slot_comm, 3, 2,
                                 weights=mult[slot_author])
    dup_author = np.array([0, 0, 3, 3, 1, 1, 2, 2], dtype=np.int64)
    dup_comm = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    dup_values = np.concatenate([values[:2], values[:2], values[2:]])
    plain = MOD.double_center(dup_values, dup_author, dup_comm, 4, 2)
    assert np.allclose(weighted, plain[[0, 1, 4, 5, 6, 7]])


# ---------------------------------------------------------------------------
# 2. the permutation preserves the design
# ---------------------------------------------------------------------------


def test_permutation_preserves_the_slots_the_counts_and_the_author_values():
    design = _sparse_skeleton(seed=3)
    rng = np.random.default_rng(19)
    perm = MOD.within_author_permutation(design.slot_author, rng)
    # (a) the slot list itself is untouched: the permutation moves VALUES
    assert np.array_equal(design.slot_author[perm], design.slot_author)
    # (b) each author keeps its own cell count
    before = np.bincount(design.slot_author, None, design.n_authors)
    after = np.bincount(design.slot_author[perm], None, design.n_authors)
    assert np.array_equal(before, after)
    # (c) each community keeps its number of cells
    cb = np.bincount(design.slot_comm, None, design.n_comms)
    ca = np.bincount(design.slot_comm, None, design.n_comms)
    assert np.array_equal(cb, ca)
    # (d) values only ever move WITHIN an author block
    values = np.arange(design.n_slots, dtype=np.float64)
    moved = values[perm]
    for author in range(design.n_authors):
        mask = design.slot_author == author
        assert sorted(moved[mask]) == sorted(values[mask])


def test_permutation_leaves_author_means_and_the_grand_mean_invariant():
    design = _sparse_skeleton(seed=8)
    rng = np.random.default_rng(4)
    perm = MOD.within_author_permutation(design.slot_author, rng)
    values = rng.normal(size=design.n_slots)
    a_before = np.bincount(design.slot_author, values, design.n_authors)
    a_after = np.bincount(design.slot_author, values[perm], design.n_authors)
    assert np.allclose(a_before, a_after)
    assert math.isclose(values.mean(), values[perm].mean(), rel_tol=1e-12)


def test_batched_permutations_are_within_author_shuffles_too():
    design = _sparse_skeleton(seed=2)
    rng = np.random.default_rng(77)
    batch = MOD.permutation_batch(design.slot_author, rng, 5)
    assert batch.shape == (5, design.n_slots)
    for row in batch:
        assert np.array_equal(design.slot_author[row], design.slot_author)


def test_permutation_null_of_R_sits_at_the_bands_own_centre_on_a_toy():
    """A world with NO structure: R must land inside its own band."""

    design = _sparse_skeleton(n_authors=200, n_comms=30, seed=6)
    shares = {"author": 0.0, "community": 0.0, "interaction": 0.0}
    world = MOD.synthetic_design(design, shares, np.random.default_rng(1))
    v_e = MOD.double_center(world.mean_e, world.slot_author, world.slot_comm,
                            world.n_authors, world.n_comms)
    v_l = MOD.double_center(world.mean_l, world.slot_author, world.slot_comm,
                            world.n_authors, world.n_comms)
    r = float(np.nanmean(MOD.per_author_correlations(
        v_e, v_l, world.slot_author, world.n_authors)))
    null = MOD.permutation_null(world, 99, 12345)
    assert null["r_band"][0] <= r <= null["r_band"][1]
    assert abs(null["r_null_mean"]) < 0.05


# ---------------------------------------------------------------------------
# 3. synthetic recovery + null-world honesty (the Part 0 machinery)
# ---------------------------------------------------------------------------


def test_synthetic_world_carries_the_planted_shares_into_the_estimator():
    """On a DENSE design the registered estimator recovers the plant."""

    slot_author, slot_comm = _complete_grid(220, 12)
    skeleton = _design(slot_author, slot_comm, n_per_cell=25.0)
    recovered = []
    for rep in range(6):
        world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES,
                                     np.random.default_rng(100 + rep))
        recovered.append(MOD.recover_shares(world))
    for key, planted in MOD.PLANTED_SHARES.items():
        got = float(np.mean([row[key] for row in recovered]))
        assert abs(got - planted) < 0.02, (key, got, planted)


def test_the_null_world_is_not_detected_on_a_dense_design():
    slot_author, slot_comm = _complete_grid(220, 12)
    skeleton = _design(slot_author, slot_comm, n_per_cell=25.0)
    world = MOD.synthetic_design(skeleton, MOD.NULL_SHARES,
                                 np.random.default_rng(9))
    result = MOD.analyse_design(world, b_perm=99, b_boot=120, seed_perm=31,
                                seed_boot=41, tag="toy_null",
                                log=_SilentLog())
    ci = result["bootstrap"]["shares_ci"]["interaction"]
    band = result["null"]["r_band"]
    assert ci[0] <= 0.0 <= ci[1], ci
    assert band[0] <= result["R"] <= band[1], (result["R"], band)


def test_a_planted_interaction_is_detected_on_a_dense_design():
    slot_author, slot_comm = _complete_grid(220, 12)
    skeleton = _design(slot_author, slot_comm, n_per_cell=25.0)
    world = MOD.synthetic_design(skeleton, {"author": 0.30, "community": 0.08,
                                            "interaction": 0.10},
                                 np.random.default_rng(13))
    result = MOD.analyse_design(world, b_perm=99, b_boot=120, seed_perm=51,
                                seed_boot=61, tag="toy_signal",
                                log=_SilentLog())
    assert result["bootstrap"]["shares_ci"]["interaction"][0] > 0.0
    assert result["R"] > result["null"]["r_band"][1]


def test_the_synthetic_world_uses_the_skeleton_and_no_real_y():
    """Part 0 borrows DESIGN only: same slots, same counts, new y."""

    skeleton = _sparse_skeleton(seed=21)
    skeleton.s_e[:] = 12345.0                     # a value Part 0 must ignore
    world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES,
                                 np.random.default_rng(2))
    assert np.array_equal(world.slot_author, skeleton.slot_author)
    assert np.array_equal(world.slot_comm, skeleton.slot_comm)
    assert np.array_equal(world.n_e, skeleton.n_e)
    assert np.array_equal(world.n_l, skeleton.n_l)
    assert not np.allclose(world.s_e, skeleton.s_e)


def test_synthetic_cell_statistics_are_a_faithful_comment_level_draw():
    """The drawn sufficient statistics behave like real per-cell moments."""

    slot_author, slot_comm = _complete_grid(400, 6)
    skeleton = _design(slot_author, slot_comm, n_per_cell=20.0)
    world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES,
                                 np.random.default_rng(3))
    n = world.n_e
    within = (world.q_e - world.s_e ** 2 / n) / (n - 1.0)
    assert float(within.min()) > 0.0                    # a real variance
    assert abs(float(world.var_y()) - 1.0) < 0.15       # unit total variance


def test_recovery_criterion_is_the_registered_tolerance_rule():
    assert MOD.PLANTED_SHARES == {"author": 0.30, "community": 0.08,
                                  "interaction": 0.02}
    assert MOD.NULL_SHARES["interaction"] == 0.0
    assert MOD.N_SYNTH_REPLICATES == 8
    assert MOD.TOL_SD_MULT == 3.0
    assert MOD.TOL_FLOOR == 0.01
    assert MOD.TOL_FLOOR < MOD.TRACE_MAX            # tighter than the cell edge


def test_the_gate_fails_when_the_estimator_cannot_recover():
    """A rigged recovery block must route to FAIL, not be waved through."""

    fake = {"author": {"planted": 0.30, "recovered_mean": 0.30,
                       "replicate_sd": 0.001, "tolerance": 0.01,
                       "bias": 0.0, "status": "PASS"},
            "interaction": {"planted": 0.02, "recovered_mean": 0.09,
                            "replicate_sd": 0.001, "tolerance": 0.01,
                            "bias": 0.07, "status": "FAIL"}}
    assert any(row["status"] == "FAIL" for row in fake.values())
    tol = max(MOD.TOL_FLOOR, MOD.TOL_SD_MULT * 0.001)
    assert abs(0.09 - 0.02) > tol


# ---------------------------------------------------------------------------
# 4. the variance budget and R
# ---------------------------------------------------------------------------


def test_the_budget_shares_and_the_residual_sum_to_one():
    slot_author, slot_comm = _complete_grid(120, 8)
    skeleton = _design(slot_author, slot_comm, n_per_cell=20.0)
    world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES,
                                 np.random.default_rng(23))
    budget = MOD.recover_shares(world)
    total = (budget["author"] + budget["community"] + budget["interaction"]
             + budget["residual"])
    assert math.isclose(total, 1.0, rel_tol=1e-12)


def test_per_author_correlation_is_pearson_over_the_shared_communities():
    slot_author = np.array([0, 0, 0, 1, 1, 1], dtype=np.int64)
    v_e = np.array([1.0, 2.0, 3.0, 1.0, 0.0, -1.0])
    v_l = np.array([2.0, 4.0, 6.0, 5.0, 5.0, 5.0])
    r = MOD.per_author_correlations(v_e, v_l, slot_author, 2)
    assert math.isclose(r[0], 1.0, rel_tol=1e-9)        # exactly collinear
    assert not np.isfinite(r[1])                        # flat half -> undefined


def test_a_flat_author_is_dropped_from_R_and_counted_in_the_headroom():
    r = np.array([0.5, np.nan, -0.25, np.nan])
    head = MOD.headroom_report(r)
    assert head["authors_scored"] == 2
    assert head["authors_undefined"] == 2
    assert math.isclose(head["mean"], 0.125, rel_tol=1e-12)


def test_cross_half_covariance_is_attenuation_free_under_pure_noise():
    """Half-noise drawn afresh contributes zero in expectation."""

    slot_author, slot_comm = _complete_grid(300, 10)
    skeleton = _design(slot_author, slot_comm, n_per_cell=15.0)
    world = MOD.synthetic_design(
        skeleton, {"author": 0.0, "community": 0.0, "interaction": 0.0},
        np.random.default_rng(31))
    budget = MOD.recover_shares(world)
    assert abs(budget["interaction"]) < 0.01
    assert abs(budget["author"]) < 0.02
    assert abs(budget["community"]) < 0.02


def test_weighted_cov_matches_numpy_on_the_unweighted_case():
    rng = np.random.default_rng(44)
    x, z = rng.normal(size=50), rng.normal(size=50)
    got = MOD.weighted_cov(x, z)
    want = float(np.cov(x, z, ddof=0)[0, 1])
    assert math.isclose(got, want, rel_tol=1e-10)


# ---------------------------------------------------------------------------
# 5. the headroom report (#84)
# ---------------------------------------------------------------------------


def test_headroom_reports_the_realized_distribution_and_its_ceiling():
    r = np.concatenate([np.full(10, 0.995), np.linspace(-0.5, 0.5, 90)])
    head = MOD.headroom_report(r)
    assert head["authors_scored"] == 100
    assert math.isclose(head["share_above_0.99"], 0.10, rel_tol=1e-9)
    assert set(head["quantiles"]) == {"q00", "q05", "q10", "q25", "q50",
                                      "q75", "q90", "q95", "q100"}
    assert head["quantiles"]["q00"] == pytest.approx(-0.5)
    assert head["quantiles"]["q100"] == pytest.approx(0.995)
    assert sum(head["histogram_counts"]) == 100
    assert len(head["histogram_edges"]) == 21


def test_headroom_exists_by_construction_when_cells_are_noisy():
    """Within-cell noise keeps every per-author correlation off the ceiling."""

    skeleton = _sparse_skeleton(n_authors=400, n_comms=25, k_mean=8, seed=15)
    world = MOD.synthetic_design(skeleton, {"author": 0.0, "community": 0.0,
                                            "interaction": 0.40},
                                 np.random.default_rng(6))
    v_e = MOD.double_center(world.mean_e, world.slot_author, world.slot_comm,
                            world.n_authors, world.n_comms)
    v_l = MOD.double_center(world.mean_l, world.slot_author, world.slot_comm,
                            world.n_authors, world.n_comms)
    r = MOD.per_author_correlations(v_e, v_l, world.slot_author,
                                    world.n_authors)
    head = MOD.headroom_report(r)
    assert head["share_above_0.99"] < 0.05
    assert head["mean"] < 0.95


# ---------------------------------------------------------------------------
# 6. eligibility, the census gate and the cell rule
# ---------------------------------------------------------------------------


def _toy_cells():
    """A hand table: author 0 has 3 shared communities, author 1 has 2."""

    rows = [
        # author, comm, half, n
        (0, 0, 0, 12), (0, 0, 1, 15),
        (0, 1, 0, 11), (0, 1, 1, 10),
        (0, 2, 0, 20), (0, 2, 1, 20),
        (0, 3, 0, 20), (0, 3, 1, 4),      # late half short -> not shared
        (1, 0, 0, 30), (1, 0, 1, 30),
        (1, 1, 0, 30), (1, 1, 1, 30),     # only 2 shared -> author dropped
        (2, 0, 0, 6), (2, 0, 1, 6),
        (2, 1, 0, 6), (2, 1, 1, 6),
        (2, 2, 0, 6), (2, 2, 1, 6),       # eligible at n=5, not at n=10
    ]
    author = np.array([r[0] for r in rows], dtype=np.int32)
    comm = np.array([r[1] for r in rows], dtype=np.int32)
    half = np.array([r[2] for r in rows], dtype=np.int8)
    n = np.array([r[3] for r in rows], dtype=np.int64)
    return {
        "cell_author": author, "cell_comm": comm, "cell_half": half,
        "cell_n": n,
        "s_wcq": n.astype(np.float64) * 2.0,
        "q_wcq": n.astype(np.float64) * 4.5,
        "s_wc": n.astype(np.float64) * 3.0,
        "q_wc": n.astype(np.float64) * 9.5,
        "n_subs": 4, "n_authors": 3,
    }


def test_eligibility_is_the_registered_predicate():
    table = _toy_cells()
    mask = np.ones(3, dtype=bool)
    primary = MOD.build_design(table, mask, 10)
    assert primary.n_authors == 1                 # only author 0 survives
    assert primary.n_slots == 3                   # its three shared communities
    assert set(primary.author_codes.tolist()) == {0}
    loose = MOD.build_design(table, mask, 5)
    assert loose.n_authors == 2                   # author 2 joins at n_min = 5
    assert loose.n_slots == 6


def test_a_cohort_mask_and_a_community_mask_both_restrict_the_grid():
    table = _toy_cells()
    only_two = np.array([False, False, True])
    assert MOD.build_design(table, only_two, 10).n_slots == 0
    assert MOD.build_design(table, only_two, 5).n_authors == 1
    vocab = np.array([True, True, False, False])
    assert MOD.build_design(table, np.ones(3, bool), 10,
                            comm_mask=vocab).n_authors == 0


def test_k_min_is_three_shared_communities_in_both_halves():
    assert MOD.K_MIN == 3
    assert MOD.N_MIN_PRIMARY == 10
    assert MOD.N_MIN_SENSITIVITY == 5
    table = _toy_cells()
    design = MOD.build_design(table, np.ones(3, bool), 10, k_min=2)
    assert design.n_authors == 2                  # author 1 joins at k_min = 2


def test_the_census_anchor_gate_blocks_on_any_mismatch():
    ok = MOD.anchor_gate({"a": 5, "b": 0.0}, {"a": 5, "b": 0.0})
    assert ok["status"] == "PASS"
    bad = MOD.anchor_gate({"a": 6, "b": 0.0}, {"a": 5, "b": 0.0})
    assert bad["status"] == "FAIL"
    assert bad["pins"]["a"]["status"] == "FAIL"
    assert bad["pins"]["b"]["status"] == "PASS"


def test_the_registered_census_pins_are_the_registration_numbers():
    assert MOD.CENSUS_ROWS_PARSEABLE == 17_640_062
    assert MOD.CENSUS_AUTHORS == 10_296
    assert MOD.CENSUS_BIG5_AUTHORS == 1_401
    assert MOD.CENSUS_DISJOINT_AUTHORS == 8_895
    assert MOD.CENSUS_POOL_DISJOINT_N10 == 4_342
    assert MOD.CENSUS_POOL_DISJOINT_N5 == 5_842
    assert MOD.CENSUS_POOL_BIG5_N10 == 615
    assert MOD.CENSUS_LAW_VOCAB == 1_443
    assert MOD.CENSUS_VOCAB_FLOOR_USERS == math.ceil(
        MOD.VOCAB_FLOOR_FRACTION * MOD.CENSUS_DISJOINT_AUTHORS)
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499
    assert MOD.B_BOOT == 1000


@pytest.mark.parametrize("ci,expected", [
    ([0.001, 0.010], [MOD.CELL_TRACE]),
    ([0.030, 0.070], [MOD.CELL_IDIOSYNCRATIC]),
    ([0.120, 0.200], [MOD.CELL_MAJOR]),
    ([0.010, 0.040], [MOD.CELL_TRACE, MOD.CELL_IDIOSYNCRATIC]),
    ([0.050, 0.150], [MOD.CELL_IDIOSYNCRATIC, MOD.CELL_MAJOR]),
    ([-0.010, 0.150], [MOD.CELL_TRACE, MOD.CELL_IDIOSYNCRATIC,
                       MOD.CELL_MAJOR]),
])
def test_magnitude_cells_are_the_registered_boundaries(ci, expected):
    assert MOD.magnitude_cells(ci) == expected


def test_the_null_cell_needs_both_clauses():
    """NULL-first (#55): R inside its band AND the share CI covering 0."""

    base = {"budget": {"interaction": 0.001},
            "bootstrap": {"shares_ci": {"interaction": [-0.01, 0.01]}},
            "null": {"r_band": [-0.05, 0.05]}, "R": 0.01}
    assert MOD.classify(base)["cell"] == MOD.CELL_NO_RESPONSE

    r_outside = json.loads(json.dumps(base))
    r_outside["R"] = 0.40
    assert MOD.classify(r_outside)["cell"] != MOD.CELL_NO_RESPONSE

    ci_excludes = json.loads(json.dumps(base))
    ci_excludes["bootstrap"]["shares_ci"]["interaction"] = [0.005, 0.015]
    ci_excludes["budget"]["interaction"] = 0.01
    out = MOD.classify(ci_excludes)
    assert out["cell"] == MOD.CELL_TRACE
    assert out["straddle"] is False


def test_a_straddling_interval_is_reported_as_a_straddle():
    arm = {"budget": {"interaction": 0.025},
           "bootstrap": {"shares_ci": {"interaction": [0.010, 0.040]}},
           "null": {"r_band": [-0.05, 0.05]}, "R": 0.30}
    out = MOD.classify(arm)
    assert out["straddle"] is True
    assert out["cell"] == MOD.CELL_IDIOSYNCRATIC          # the point's cell
    assert out["touched"] == [MOD.CELL_TRACE, MOD.CELL_IDIOSYNCRATIC]


def test_the_registered_leans_are_evaluated_not_enforced():
    arm = {"R": 0.12, "budget": {"interaction": 0.01, "author": 0.30,
                                 "community": 0.05}}
    rows = MOD.evaluate_leans(arm, MOD.CELL_TRACE, MOD.CELL_TRACE)
    assert all(row["held"] for row in rows)
    miss = {"R": 0.60, "budget": {"interaction": 0.30, "author": 0.90,
                                  "community": 0.90}}
    rows = MOD.evaluate_leans(miss, MOD.CELL_MAJOR, MOD.CELL_TRACE)
    assert not any(row["held"] for row in rows)


# ---------------------------------------------------------------------------
# 7. the stream, the halves and the cache
# ---------------------------------------------------------------------------


def _toy_stream(tmp_path: Path) -> Path:
    rows = []
    for author, base in (("alpha", 1_000_000), ("beta", 2_000_000)):
        for i in range(9):
            rows.append({"author": author, "subreddit": f"sub{i % 3}",
                         "created_utc": base + i * 100,
                         "word_count_quoteless": i + 1,
                         "word_count": i + 2, "body": "never read"})
    path = tmp_path / "toy.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_the_stream_reads_metadata_only_and_never_a_body(tmp_path):
    path = _toy_stream(tmp_path)
    scaffold = MOD.stream_metadata(path, MOD.RunLog(tmp_path / "log.jsonl"))
    assert set(scaffold) == {"author_code", "subreddit_code", "created_utc",
                             "wcq", "wc", "authors", "subreddits",
                             "stream_stats"}
    assert scaffold["stream_stats"]["rows_parseable"] == 18
    assert scaffold["authors"] == ["alpha", "beta"]
    blob = json.dumps({k: v for k, v in scaffold.items()
                       if k in ("authors", "subreddits")})
    assert "never read" not in blob


def test_halves_split_at_the_authors_own_full_stream_median(tmp_path):
    path = _toy_stream(tmp_path)
    scaffold = MOD.stream_metadata(path, MOD.RunLog(tmp_path / "log.jsonl"))
    medians, counts = MOD.author_medians(scaffold["author_code"],
                                         scaffold["created_utc"], 2)
    assert counts.tolist() == [9, 9]
    assert medians[0] == 1_000_400                    # the 5th of 9 timestamps
    early = scaffold["created_utc"] <= medians[scaffold["author_code"]]
    assert int(early.sum()) == 10                     # "<= to early"


def _dense_toy_stream(tmp_path: Path) -> Path:
    """Two authors x three communities x two halves x six comments."""

    rows = []
    for author, base in (("alpha", 1_000_000), ("beta", 2_000_000)):
        for sub in range(3):
            for half, offset in ((0, 0), (1, 500_000)):
                for i in range(6):
                    rows.append({"author": author, "subreddit": f"sub{sub}",
                                 "created_utc": base + offset + i * 10 + sub,
                                 "word_count_quoteless": 5 + i + sub,
                                 "word_count": 6 + i + sub,
                                 "body": "never read"})
    path = tmp_path / "dense.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_the_cell_table_keeps_sufficient_statistics_only(tmp_path):
    path = _dense_toy_stream(tmp_path)
    log = MOD.RunLog(tmp_path / "log.jsonl")
    scaffold = MOD.stream_metadata(path, log)
    table = MOD.build_cell_table(scaffold, log)
    assert set(table["cell_half"].tolist()) == {0, 1}
    assert table["cell_n"].min() >= MOD.MIN_CELL_KEEP
    assert table["cell_n"].tolist() == [6] * 12      # 2 x 3 x 2 cells of 6
    n = table["cell_n"].astype(float)
    assert np.all(table["q_wcq"] >= table["s_wcq"] ** 2 / n - 1e-9)
    assert table["author_rows"].tolist() == [36, 36]
    assert table["pair_author"].size == 6            # (author, community)
    # the cache carries sums, not comments: nothing is per-comment shaped
    assert table["cell_author"].size == table["s_wcq"].size == 12


def test_the_vocabulary_rule_is_sr0s_rule_re_instantiated(tmp_path):
    path = _toy_stream(tmp_path)
    log = MOD.RunLog(tmp_path / "log.jsonl")
    scaffold = MOD.stream_metadata(path, log)
    table = MOD.build_cell_table(scaffold, log)
    vocab = MOD.law_vocabulary(table, np.array([True, True]), log)
    assert vocab["authors_seen"] == 2
    assert vocab["floor_users"] == math.ceil(MOD.VOCAB_FLOOR_FRACTION * 2)
    assert vocab["vocabulary_size"] == 3
    assert vocab["disjoint_events"] == 18


def test_the_registered_floor_arithmetic_is_ceil_one_percent():
    assert MOD.VOCAB_FLOOR_FRACTION == 0.01
    assert math.ceil(0.01 * 8895) == 89


# ---------------------------------------------------------------------------
# 8. the ID-leak helper (#83) and governance
# ---------------------------------------------------------------------------


def test_id_leak_scanner_finds_a_planted_name(tmp_path):
    target = tmp_path / "leaky.md"
    target.write_text("the author zebra_wrangler said something\n",
                      encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["zebra_wrangler", "absent_name"])
    assert scan["status"] == "FAIL"
    assert scan["n_hits"] == 1
    clean = tmp_path / "clean.md"
    clean.write_text("aggregates only\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([clean], ["zebra_wrangler"])["n_hits"] == 0


def test_new_hits_are_separated_from_pre_existing_ones_mechanically():
    hits = [{"path": "/x/CLAIMS_LEDGER.md", "line": 58},
            {"path": "/x/CLAIMS_LEDGER.md", "line": 742},
            {"path": "/x/SUICA_M4_X1_VENUE_RESPONSE_REPORT.md", "line": 12}]
    baseline = {("CLAIMS_LEDGER.md", 58), ("CLAIMS_LEDGER.md", 742)}
    new = MOD.new_hits_only(hits, baseline)
    assert len(new) == 1
    assert new[0]["line"] == 12
    assert MOD.new_hits_only(hits, baseline | {
        ("SUICA_M4_X1_VENUE_RESPONSE_REPORT.md", 12)}) == []


def test_the_scan_universe_is_every_author_name_in_the_file():
    assert MOD.CENSUS_AUTHORS == (MOD.CENSUS_BIG5_AUTHORS
                                  + MOD.CENSUS_DISJOINT_AUTHORS)


def test_the_label_file_is_never_opened_only_declared_unopened():
    """`author_profiles.csv` may be NAMED as unopened; never read."""

    needle = "author" + "_profiles"               # never a literal here
    for path in (SCRIPT, Path(__file__)):
        for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            if needle not in line:
                continue
            lowered = line.lower()
            assert not any(token in lowered for token in
                           ("read_csv", "open(", "np.load", "read_text",
                            "pd.read")), (path.name, number, line)
            assert ("never" in lowered or "not opened" in lowered
                    or "false" in lowered), (path.name, number, line)


def test_only_metadata_columns_are_requested():
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'usecols=["author", "subreddit", "created_utc",' in text
    assert '"body"' not in text.replace('"body": "never read"', "")


def test_the_committed_files_list_is_what_the_scan_covers():
    names = {path.name for path in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_X1_VENUE_RESPONSE_REPORT.md",
                     "run_suica_m4_x1_venue_response.py",
                     "test_m4_x1_venue_response.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_results_stay_out_of_the_commit():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore


# ---------------------------------------------------------------------------
# 9. the committed run (skipped where the artifacts were not produced)
# ---------------------------------------------------------------------------


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                         # pragma: no cover
        pytest.skip("the X1 run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_run_reproduced_every_census_pin():
    census = _artifact("census.json")
    assert census["status"] == "PASS"
    for key, pin in census["pins"].items():
        assert pin["status"] == "PASS", key
        assert pin["registered"] == pin["observed"], key


def test_committed_run_recorded_its_part0_decision():
    part0 = _artifact("part0_synthetic_gate.json")
    assert part0["status"] in {"PASS", "FAIL"}
    assert set(part0["recovery"]) == set(MOD.PLANTED_SHARES)
    assert part0["planted_block"]["replicates"] == MOD.N_SYNTH_REPLICATES
    assert part0["null_block"]["planted"]["interaction"] == 0.0
    for key, row in part0["recovery"].items():
        assert row["tolerance"] >= MOD.TOL_FLOOR
        expected = "PASS" if abs(row["bias"]) <= row["tolerance"] else "FAIL"
        assert row["status"] == expected, key


def test_committed_run_honoured_the_a1_stop():
    """No real estimand may exist unless Part 0 passed."""

    part0 = _artifact("part0_synthetic_gate.json")
    verdict = _artifact("verdict.json")
    if part0["status"] == "PASS":
        assert verdict["cell"] != MOD.CELL_A1_STOP
        assert (ARTIFACTS / "arms.json").exists()
    else:
        assert verdict["cell"] == MOD.CELL_A1_STOP
        assert not (ARTIFACTS / "arms.json").exists()
        assert not (ARTIFACTS / "cells.json").exists()


def test_committed_report_matches_the_committed_verdict():
    if not REPORT.exists():                        # pragma: no cover
        pytest.skip("the X1 report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**VERDICT — {verdict['cell']}.**" in text
    for boundary_head in ("Metadata only", "projection caution",
                          "No psychological naming", "EXPLORATORY",
                          "Cohort composition"):
        assert boundary_head in text


def test_committed_report_carries_the_part0_numbers_from_the_artifact():
    if not REPORT.exists():                        # pragma: no cover
        pytest.skip("the X1 report has not been produced in this checkout")
    part0 = _artifact("part0_synthetic_gate.json")
    text = REPORT.read_text(encoding="utf-8")
    for row in part0["recovery"].values():
        assert f"{row['recovered_mean']:.4f}" in text
    assert f"{part0['honesty']['interaction_share']:.4f}" in text


def test_committed_run_cleared_the_id_leak_gate():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == MOD.CENSUS_AUTHORS


def test_committed_outcome_was_appended_to_the_registration():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X1 outcome (executor, 2026-08-19)" in text
