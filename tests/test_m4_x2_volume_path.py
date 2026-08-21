"""Contract tests for SUICA M4-X2 — the path of expression volume.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X2", commit 550466f) names five objects that are NEW here and therefore have
to be pinned by contract rather than inherited from the X1 arc:

1. the MARGINAL-PRESERVING within-half shuffle — the per-half marginal must be
   invariant BIT FOR BIT, the index array must be a genuine permutation, and
   no index may leave its own cell (U1's exact-bag pattern, carried onto a
   scalar);
2. the MASKED lag-1 correlation — the cross-thread arm's estimator, pinned on
   a hand toy against an explicit by-hand index set;
3. the AR(1) world and the OWNERSHIP MAPPING — the doubling scan must satisfy
   the defining recursion exactly, and the derived phi dispersion must solve
   its own equation and land the planted rho_own on the #76 operating point;
4. the COMMON-PATH null world — the design's decisive honesty check: a world
   with presence but WITHOUT ownership must NOT be called owned;
5. the #87 boundary REGIONS on rho_own, including AT_BOUNDARY as a
   first-class verdict and the straddle report.

Everything the leg inherits (``RunLog``, ``write_json``, ``percentile_ci``,
``anchor_gate``, ``scan_for_cohort_ids`` and the #83 HEAD-baseline helpers) is
X1b's and is covered by that leg's tests; it is re-checked here only where the
binding itself could break.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_x2_volume_path.py"
X1B_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
ARTIFACTS = ROOT / "results" / "m4_x2_volume_path"
REPORT = ROOT / "reports" / "SUICA_M4_X2_VOLUME_PATH_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X1c recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x2_volume_path", SCRIPT)


# ---------------------------------------------------------------------------
# helpers — toy skeletons, no corpus needed
# ---------------------------------------------------------------------------


def toy_arm(cells, links=None, key="toy"):
    """Build an Arm from [(author, half, values), ...] and optional links."""

    values = np.concatenate([np.asarray(c[2], dtype=np.float64)
                             for c in cells])
    lengths = np.array([len(c[2]) for c in cells], dtype=np.int64)
    starts = np.concatenate(([0], np.cumsum(lengths)[:-1])).astype(np.int64)
    authors = np.array([c[0] for c in cells], dtype=np.int64)
    halves = np.array([c[1] for c in cells], dtype=np.int8)
    mask = None
    if links is not None:
        flat = np.concatenate([np.asarray(link) for link in links])
        mask = np.zeros(flat.size, dtype=bool)
        mask[:-1] = flat[:-1] != flat[1:]
    return MOD.Arm(key, key, values, starts, lengths, authors, halves, mask,
                   int(authors.max()) + 1)


def paired_toy(n_authors=400, n_events=200, rho=0.0, seed=7):
    """Two-half skeleton with equal-length cells (stable order preserved)."""

    rng = np.random.default_rng(seed)
    cells = []
    for u in range(n_authors):
        for h in (0, 1):
            cells.append((u, h, rng.normal(size=n_events)))
    return toy_arm(cells)


def reference_lag1(values, mask=None):
    """The registered formula, written out again by hand for the toy tests."""

    values = np.asarray(values, dtype=np.float64)
    idx = np.arange(values.size - 1)
    if mask is not None:
        idx = idx[np.asarray(mask, dtype=bool)[:values.size - 1]]
    if idx.size < 2:
        return float("nan")
    x = values[idx]
    z = values[idx + 1]
    if np.std(x) == 0 or np.std(z) == 0:
        return float("nan")
    return float(np.corrcoef(x, z)[0, 1])


# ---------------------------------------------------------------------------
# 1. the estimator — the pinned lag-1 Pearson, masked and unmasked
# ---------------------------------------------------------------------------


def test_r1_reproduces_the_pearson_correlation_of_the_shifted_pair():
    rng = np.random.default_rng(0)
    seq = rng.normal(size=137)
    arm = toy_arm([(0, 0, seq)])
    assert arm.r1()[0] == pytest.approx(reference_lag1(seq), abs=1e-12)


def test_r1_recovers_a_planted_deterministic_autocorrelation():
    t = np.arange(600, dtype=np.float64)
    seq = np.sin(t / 7.0)
    arm = toy_arm([(0, 0, seq)])
    assert arm.r1()[0] == pytest.approx(math.cos(1.0 / 7.0), abs=2e-3)


def test_adjacency_never_crosses_a_cell_boundary():
    """The last slot of a cell can never open an adjacency (registration)."""

    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    b = np.array([500.0, -500.0, 500.0, -500.0, 500.0, -500.0])
    arm = toy_arm([(0, 0, a), (0, 1, b)])
    got = {int(h): float(v) for h, v in zip(arm.cell_half, arm.r1())}
    assert got[0] == pytest.approx(reference_lag1(a), abs=1e-12)
    assert got[1] == pytest.approx(reference_lag1(b), abs=1e-12)
    # A single joined sequence would give something else entirely.
    assert reference_lag1(np.concatenate([a, b])) != pytest.approx(got[0],
                                                                   abs=1e-6)


def test_masked_cross_thread_r1_on_a_hand_toy():
    """The masked estimator on an index set written out by hand."""

    values = np.array([1.0, 5.0, 2.0, 9.0, 3.0, 7.0, 4.0, 8.0])
    links = ["t1", "t1", "t2", "t2", "t2", "t3", "t3", "t4"]
    # By hand: link differs at j = 1 (t1->t2), j = 4 (t2->t3), j = 6 (t3->t4).
    hand_x = [values[1], values[4], values[6]]
    hand_z = [values[2], values[5], values[7]]
    expected = float(np.corrcoef(hand_x, hand_z)[0, 1])
    arm = toy_arm([(0, 0, values)], links=[links])
    assert arm.r1()[0] == pytest.approx(expected, abs=1e-12)
    assert int(arm._n_pairs[0]) == 3


def test_cross_thread_mask_marks_exactly_the_thread_changes():
    cache = {"ev_link": np.array([10, 10, 11, 12, 12, 12], dtype=np.uint64)}
    mask = MOD.cross_thread_mask(cache)
    assert mask.tolist() == [False, True, True, False, False, False]


def test_masked_and_unmasked_agree_when_every_adjacency_crosses():
    rng = np.random.default_rng(3)
    seq = rng.normal(size=60)
    links = [f"t{i}" for i in range(60)]
    plain = toy_arm([(0, 0, seq)])
    masked = toy_arm([(0, 0, seq)], links=[links])
    assert masked.r1()[0] == pytest.approx(plain.r1()[0], abs=1e-12)


def test_degenerate_cell_returns_nan_and_is_counted():
    arm = toy_arm([(0, 0, np.full(80, 2.5))])
    assert math.isnan(float(arm.r1()[0]))
    assert arm.census()["cells_with_fewer_than_2_pairs"] == 0


def test_cell_with_fewer_than_two_masked_pairs_returns_nan():
    values = np.arange(40, dtype=np.float64)
    links = ["a"] * 39 + ["b"]
    arm = toy_arm([(0, 0, values)], links=[links])
    assert int(arm._n_pairs[0]) == 1
    assert math.isnan(float(arm.r1()[0]))


# ---------------------------------------------------------------------------
# 2. the marginal-preserving shuffle — BIT-EXACT
# ---------------------------------------------------------------------------


def test_shuffle_preserves_every_cell_marginal_bit_for_bit():
    rng = np.random.default_rng(11)
    cells = [(u, h, rng.normal(size=50 + 13 * u))
             for u in range(6) for h in (0, 1)]
    arm = toy_arm(cells)
    for draw in range(5):
        perm = arm.permutation(np.random.default_rng(100 + draw))
        report = MOD.check_marginal_preservation(arm, perm)
        assert report["status"] == "PASS"
        assert report["per_cell_multiset_bit_exact"] is True
        assert report["index_array_is_a_permutation"] is True
        assert report["every_index_stays_inside_its_own_cell"] is True
        # and, spelled out, the raw IEEE-754 bit patterns per cell
        shuffled = arm.y[perm]
        for start, end in zip(arm.offsets[:-1], arm.offsets[1:]):
            assert np.array_equal(
                np.sort(arm.y[start:end].view(np.uint64)),
                np.sort(shuffled[start:end].view(np.uint64)))


def test_the_bit_exact_contract_catches_a_shuffle_that_crosses_cells():
    arm = toy_arm([(0, 0, np.arange(50.0)), (0, 1, np.arange(50.0) + 100.0)])
    perm = np.arange(arm.n_events)
    perm[0], perm[60] = perm[60], perm[0]          # a cross-cell swap
    report = MOD.check_marginal_preservation(arm, perm)
    assert report["status"] == "FAIL"
    assert report["every_index_stays_inside_its_own_cell"] is False
    assert report["per_cell_multiset_bit_exact"] is False


def test_the_bit_exact_contract_catches_a_shuffle_that_duplicates():
    arm = toy_arm([(0, 0, np.arange(50.0))])
    perm = np.arange(arm.n_events)
    perm[3] = perm[4]                              # not a permutation
    report = MOD.check_marginal_preservation(arm, perm)
    assert report["status"] == "FAIL"
    assert report["index_array_is_a_permutation"] is False


def test_shuffle_is_uniform_over_a_small_cell():
    """All 3! orders of a length-3 cell appear with a fixed seed."""

    arm = toy_arm([(0, 0, np.array([1.0, 2.0, 3.0]))])
    rng = np.random.default_rng(5)
    seen = {tuple(arm.y[arm.permutation(rng)]) for _ in range(400)}
    assert len(seen) == 6


def test_shuffle_destroys_the_path_but_not_the_marginal():
    rng = np.random.default_rng(19)
    seq = np.empty(4000)
    seq[0] = rng.normal()
    for t in range(1, seq.size):
        seq[t] = 0.7 * seq[t - 1] + rng.normal()
    arm = toy_arm([(0, 0, seq)])
    assert arm.r1()[0] > 0.6
    draws = [float(arm.r1(arm.y[arm.permutation(rng)])[0]) for _ in range(40)]
    assert abs(float(np.mean(draws))) < 0.05
    assert np.sort(arm.y[arm.permutation(rng)]).tolist() == \
        np.sort(arm.y).tolist()


def test_presence_null_band_brackets_the_shuffled_mean():
    arm = paired_toy(n_authors=40, n_events=120, seed=23)
    null = MOD.presence_null(arm, 99, seed=4)
    assert null["band"][0] < null["null_mean"] < null["band"][1]
    # An iid skeleton's own mean r1 is a draw from that same null.
    observed = float(np.nanmean(arm.r1()))
    assert null["band"][0] <= observed <= null["band"][1]


# ---------------------------------------------------------------------------
# 3. the AR(1) world and the ownership mapping
# ---------------------------------------------------------------------------


def test_ar1_doubling_scan_satisfies_the_defining_recursion_exactly():
    """y_t = phi y_{t-1} + e_t, with e recovered from the phi = 0 world."""

    arm = toy_arm([(0, 0, np.zeros(500)), (0, 1, np.zeros(500))])
    phi = 0.6
    eps = MOD.ar1_values(arm, np.zeros(arm.n_cells),
                         np.random.default_rng(77))
    y = MOD.ar1_values(arm, np.full(arm.n_cells, phi),
                       np.random.default_rng(77))
    for start, end in zip(arm.offsets[:-1], arm.offsets[1:]):
        # the stationary start is the only rescaled draw
        assert y[start] == pytest.approx(eps[start] / math.sqrt(1 - phi ** 2),
                                         rel=1e-12)
        recon = y[start + 1:end] - phi * y[start:end - 1]
        assert np.allclose(recon, eps[start + 1:end], atol=1e-9)


def test_ar1_world_is_stationary_and_carries_the_planted_lag_structure():
    arm = toy_arm([(0, 0, np.zeros(40000))])
    phi = 0.5
    y = MOD.ar1_values(arm, np.full(1, phi), np.random.default_rng(2))
    assert float(np.var(y)) == pytest.approx(1.0 / (1 - phi ** 2), rel=0.05)
    for lag, expected in ((1, phi), (2, phi ** 2), (3, phi ** 3)):
        got = float(np.corrcoef(y[:-lag], y[lag:])[0, 1])
        assert got == pytest.approx(expected, abs=0.02)


def test_iid_world_is_exactly_the_raw_normal_draw():
    arm = toy_arm([(0, 0, np.zeros(300))])
    y = MOD.ar1_values(arm, np.zeros(1), np.random.default_rng(9))
    expect = np.random.default_rng(9).standard_normal((1, 300))[0]
    assert np.array_equal(y, expect)


def test_draw_phi_is_author_owned_in_the_ar_world():
    arm = paired_toy(n_authors=50, n_events=60, seed=31)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    phi = MOD.draw_phi(arm, "ar_owned", mapping, np.random.default_rng(1))
    for u in range(arm.n_authors):
        both = phi[arm.cell_author == u]
        assert both.size == 2
        assert both[0] == both[1]            # one draw per AUTHOR, not cell
    assert float(np.std(phi)) > 0


def test_draw_phi_common_path_and_iid_worlds_are_flat():
    arm = paired_toy(n_authors=20, n_events=60, seed=32)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    common = MOD.draw_phi(arm, "common_path", mapping,
                          np.random.default_rng(1))
    assert np.all(common == MOD.PHI_BAR_COMMON)
    assert float(np.std(common)) == 0.0
    assert np.all(MOD.draw_phi(arm, "iid", mapping,
                               np.random.default_rng(1)) == 0.0)


def test_ownership_mapping_solves_its_own_equation():
    arm = paired_toy(n_authors=300, n_events=80, seed=41)
    mapping = MOD.ownership_variance_target(arm, 0.2, 0.5)
    v = mapping["V_phi_variance"]
    implied = v / math.sqrt((v + mapping["A_early"]) * (v + mapping["A_late"]))
    assert implied == pytest.approx(0.5, abs=1e-9)
    assert mapping["rho_implied_by_the_solution"] == pytest.approx(0.5,
                                                                   abs=1e-9)
    assert mapping["sd_phi"] == pytest.approx(math.sqrt(v), rel=1e-12)


def test_ownership_mapping_reduces_to_V_equals_A_on_balanced_halves():
    """At rho = 1/2 with matched halves the solution is V = A, readably."""

    arm = paired_toy(n_authors=200, n_events=101, seed=42)
    mapping = MOD.ownership_variance_target(arm, 0.2, 0.5)
    assert mapping["A_early"] == pytest.approx(mapping["A_late"], rel=1e-12)
    assert mapping["V_phi_variance"] == pytest.approx(mapping["A_early"],
                                                      rel=1e-9)


def test_ownership_mapping_moves_monotonically_with_the_target():
    arm = paired_toy(n_authors=120, n_events=90, seed=43)
    lo = MOD.ownership_variance_target(arm, 0.2, 0.25)["V_phi_variance"]
    mid = MOD.ownership_variance_target(arm, 0.2, 0.50)["V_phi_variance"]
    hi = MOD.ownership_variance_target(arm, 0.2, 0.75)["V_phi_variance"]
    assert lo < mid < hi


def test_planted_ownership_is_recovered_on_a_toy_skeleton():
    """The ROUTING clause (i) contract, exercised end to end on a toy."""

    arm = paired_toy(n_authors=1500, n_events=120, seed=44)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    rhos = [MOD.synthetic_world(arm, "ar_owned", mapping, 500 + 7 * i,
                                with_presence_null=False, b_perm=0, b_boot=0
                                )["rho_own"] for i in range(4)]
    assert float(np.mean(rhos)) == pytest.approx(0.5, abs=0.05)


def test_planted_mean_r1_prediction_tracks_the_ar_world():
    """The DESCRIPTIVE clause: Marriott-Pope against the realized mean."""

    arm = paired_toy(n_authors=400, n_events=150, seed=45)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    world = MOD.synthetic_world(arm, "ar_owned", mapping, 606,
                                with_presence_null=False, b_perm=0, b_boot=0)
    assert world["mean_r1"] == pytest.approx(world["mean_r1_predicted"],
                                             abs=0.01)
    assert world["mean_r1_predicted"] < MOD.PHI_BAR_AR    # the bias is down


# ---------------------------------------------------------------------------
# 4. the COMMON-PATH null world — presence WITHOUT ownership
# ---------------------------------------------------------------------------


def test_common_path_world_has_presence_but_is_not_called_owned():
    """The design's decisive honesty check, on a toy skeleton."""

    arm = paired_toy(n_authors=800, n_events=120, seed=46)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    world = MOD.synthetic_world(arm, "common_path", mapping, 909,
                                with_presence_null=False, b_perm=199,
                                b_boot=199)
    assert world["mean_r1"] > 0.15                 # PRESENCE is unmistakable
    assert world["ci_covers_zero"] is True         # OWNERSHIP is refused
    assert world["rho_inside_band"] is True
    assert world["ci_covers_own_point"] is True    # #85b
    cell = MOD.point_cell(world["rho_own"], world["ci_covers_zero"])
    assert cell == MOD.CELL_NOT_OWNED


def test_the_ar_world_separates_from_the_common_path_world():
    """Same skeleton, same presence level, opposite ownership verdict."""

    arm = paired_toy(n_authors=800, n_events=120, seed=47)
    mapping = MOD.ownership_variance_target(arm, MOD.PHI_BAR_AR, 0.5)
    owned = MOD.synthetic_world(arm, "ar_owned", mapping, 111,
                                with_presence_null=False, b_perm=199,
                                b_boot=199)
    flat = MOD.synthetic_world(arm, "common_path", mapping, 222,
                               with_presence_null=False, b_perm=199,
                               b_boot=199)
    assert abs(owned["mean_r1"] - flat["mean_r1"]) < 0.03
    assert owned["rho_own"] > 0.35
    assert owned["ci_covers_zero"] is False
    assert flat["ci_covers_zero"] is True


# ---------------------------------------------------------------------------
# 5. ownership: the pairing permutation and the cluster bootstrap
# ---------------------------------------------------------------------------


def test_rho_own_is_the_pearson_correlation_of_the_two_halves():
    rng = np.random.default_rng(51)
    early = rng.normal(size=500)
    late = 0.4 * early + rng.normal(size=500)
    ok = np.ones(500, dtype=bool)
    got = float(MOD.rowwise_pearson(early[ok], late[ok])[0])
    assert got == pytest.approx(float(np.corrcoef(early, late)[0, 1]),
                                abs=1e-12)


def test_pairing_permutation_null_destroys_a_planted_ownership():
    rng = np.random.default_rng(52)
    early = rng.normal(size=900)
    late = early + 0.3 * rng.normal(size=900)
    ok = np.ones(900, dtype=bool)
    null = MOD.ownership_null(early, late, ok, 299, seed=3)
    point = float(MOD.rowwise_pearson(early, late)[0])
    assert point > 0.9
    assert abs(null["null_mean"]) < 0.02
    assert null["band"][0] < 0.0 < null["band"][1]
    assert point > null["band"][1]


def test_pairing_permutation_leaves_the_two_marginals_alone():
    """Permuting the PAIRING cannot change either half's own distribution."""

    rng = np.random.default_rng(53)
    early = rng.normal(size=200)
    late = rng.normal(size=200)
    ok = np.ones(200, dtype=bool)
    a = MOD.ownership_null(early, late, ok, 99, seed=8)
    b = MOD.ownership_null(early, np.sort(late)[np.argsort(np.argsort(late))],
                           ok, 99, seed=8)
    assert a["band"] == b["band"]


def test_cluster_bootstrap_ci_brackets_a_planted_correlation():
    rng = np.random.default_rng(54)
    early = rng.normal(size=1200)
    late = 0.5 * early + math.sqrt(1 - 0.25) * rng.normal(size=1200)
    ok = np.ones(1200, dtype=bool)
    boot = MOD.cluster_bootstrap_pairs(early, late, ok, 400, seed=6)
    point = float(MOD.rowwise_pearson(early, late)[0])
    assert boot["ci"][0] < point < boot["ci"][1]
    assert boot["ci"][0] > 0.0


def test_cluster_bootstrap_ci_covers_zero_when_there_is_no_ownership():
    rng = np.random.default_rng(55)
    early = rng.normal(size=1500)
    late = rng.normal(size=1500)
    ok = np.ones(1500, dtype=bool)
    boot = MOD.cluster_bootstrap_pairs(early, late, ok, 400, seed=6)
    assert boot["ci"][0] <= 0.0 <= boot["ci"][1]


def test_paired_puts_each_half_in_its_own_column():
    arm = toy_arm([(0, 0, np.arange(60.0)), (0, 1, np.arange(60.0)[::-1]),
                   (1, 0, np.arange(60.0)), (1, 1, np.arange(60.0))])
    r1 = arm.r1()
    early, late, ok = arm.paired(r1)
    assert ok.all()
    by_cell = {(int(a), int(h)): float(v)
               for a, h, v in zip(arm.cell_author, arm.cell_half, r1)}
    assert early[0] == pytest.approx(by_cell[(0, 0)])
    assert late[0] == pytest.approx(by_cell[(0, 1)])
    assert early[1] == pytest.approx(by_cell[(1, 0)])


# ---------------------------------------------------------------------------
# 6. cells, the #87 boundary REGIONS, straddles, leans, verdict
# ---------------------------------------------------------------------------


def test_region_edges_are_the_registered_numbers():
    assert MOD.LOW_LO == pytest.approx(0.139)
    assert MOD.LOW_HI == pytest.approx(0.161)
    assert MOD.HIGH_LO == pytest.approx(0.489)
    assert MOD.HIGH_HI == pytest.approx(0.511)


@pytest.mark.parametrize("rho,expected", [
    (-0.20, MOD.CELL_NOT_OWNED),
    (0.000, MOD.CELL_NOT_OWNED),
    (0.138, MOD.CELL_NOT_OWNED),
    (0.139, MOD.CELL_AT_LOW),
    (0.150, MOD.CELL_AT_LOW),
    (0.161, MOD.CELL_AT_LOW),
    (0.162, MOD.CELL_WEAK),
    (0.300, MOD.CELL_WEAK),
    (0.488, MOD.CELL_WEAK),
    (0.489, MOD.CELL_AT_HIGH),
    (0.500, MOD.CELL_AT_HIGH),
    (0.511, MOD.CELL_AT_HIGH),
    (0.512, MOD.CELL_STRONG),
    (0.900, MOD.CELL_STRONG),
])
def test_point_cell_ladder(rho, expected):
    assert MOD.point_cell(rho, False) == expected


def test_null_cell_is_checked_first():
    """#55: a CI covering 0 routes to PATH_NOT_OWNED at ANY point value."""

    for rho in (0.15, 0.30, 0.55, 0.95):
        assert MOD.point_cell(rho, True) == MOD.CELL_NOT_OWNED


def test_straddles_reports_every_region_edge_the_interval_crosses():
    assert MOD.straddles([0.10, 0.20]) == ["0.139", "0.161"]
    assert MOD.straddles([0.20, 0.30]) == []
    assert MOD.straddles([0.48, 0.52]) == ["0.489", "0.511"]
    assert MOD.straddles([0.13, 0.60]) == ["0.139", "0.161", "0.489", "0.511"]


def _fake_arm_result(key, rho, ci, band=(-0.02, 0.02), presence=0.11):
    return {"arm": key, "label": key, "rho_own": rho,
            "ownership_boot": {"ci": list(ci)},
            "ownership_null": {"band": list(band)},
            "ci_covers_zero": bool(ci[0] <= 0.0 <= ci[1]),
            "presence_mean_r1": presence,
            "presence_null": {"band": [-0.001, 0.001]},
            "presence_detected": True}


def test_classify_reports_the_cell_and_the_straddle_together():
    got = MOD.classify(_fake_arm_result("primary", 0.155, (0.14, 0.17)))
    assert got["cell"] == MOD.CELL_AT_LOW
    assert got["is_straddle"] is True
    assert got["region_edges_straddled"] == ["0.161"]


def test_flags_73_fires_on_a_divergent_arm_and_the_primary_routes():
    cells = {
        "primary": MOD.classify(_fake_arm_result("primary", 0.30,
                                                 (0.28, 0.32))),
        "big5": MOD.classify(_fake_arm_result("big5", 0.64, (0.60, 0.68))),
    }
    flags = MOD.flags_73(cells)
    assert [f["arm"] for f in flags] == ["big5"]
    assert flags[0]["primary_cell"] == MOD.CELL_WEAK
    assert flags[0]["arm_cell"] == MOD.CELL_STRONG
    assert "the primary routes" in flags[0]["note"]


def test_flags_73_is_empty_when_every_arm_agrees_and_no_edge_is_crossed():
    cells = {k: MOD.classify(_fake_arm_result(k, 0.30, (0.28, 0.32)))
             for k in ("primary", "big5", "cross_thread")}
    assert MOD.flags_73(cells) == []


def test_evaluate_leans_scores_all_five_registered_leans():
    arms = {"primary": _fake_arm_result("primary", 0.42, (0.39, 0.45)),
            "big5": _fake_arm_result("big5", 0.44, (0.40, 0.48))}
    cells = {k: MOD.classify(v) for k, v in arms.items()}
    retention = {"cross_thread": {"label": "ct", "rho_own": 0.34,
                                  "ratio": 0.81},
                 "venue_resid": {"label": "vr", "rho_own": 0.16,
                                 "ratio": 0.38}}
    leans = MOD.evaluate_leans(cells, arms, retention)
    assert len(leans) == 5
    status = [row["status"] for row in leans]
    assert status == ["HELD", "HELD", "HELD", "BROKEN", "HELD"]


def test_build_verdict_a1_stops_when_a_routing_clause_fails():
    verdict = MOD.build_verdict({"status": "FAIL"}, {}, {})
    assert verdict["cell"] == MOD.CELL_A1_STOP
    assert "no corpus estimand" in verdict["note"].lower() \
        or "NO corpus estimand" in verdict["note"]


def test_build_verdict_routes_on_the_primary_arm():
    arms = {"primary": _fake_arm_result("primary", 0.26, (0.23, 0.29))}
    arms["primary"]["authors_paired"] = 8008
    cells = {"primary": MOD.classify(arms["primary"])}
    verdict = MOD.build_verdict({"status": "PASS"}, cells, arms)
    assert verdict["cell"] == MOD.CELL_WEAK
    assert verdict["routes_on"].startswith("rho_own, PRIMARY")
    assert verdict["authors"] == 8008


# ---------------------------------------------------------------------------
# 7. the skeleton rules — order, halves, pool, venue residual, census
# ---------------------------------------------------------------------------


def test_order_is_stable_so_ties_keep_stream_order():
    author = np.array([0, 0, 0, 0], dtype=np.int32)
    created = np.array([5.0, 5.0, 5.0, 5.0])
    order, half, medians, counts = MOD.order_and_halve(author, created, 1)
    assert order.tolist() == [0, 1, 2, 3]
    assert medians[0] == 5.0
    assert half.tolist() == [0, 0, 0, 0]          # <= median is EARLY


def test_half_split_uses_the_full_stream_median_with_early_inclusive():
    author = np.zeros(5, dtype=np.int32)
    created = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    order, half, medians, counts = MOD.order_and_halve(author, created, 1)
    assert medians[0] == 3.0
    assert half.tolist() == [0, 0, 0, 1, 1]
    author2 = np.zeros(4, dtype=np.int32)
    created2 = np.array([1.0, 2.0, 4.0, 8.0])
    _, half2, medians2, _ = MOD.order_and_halve(author2, created2, 1)
    assert medians2[0] == 3.0
    assert half2.tolist() == [0, 0, 1, 1]


def test_order_and_halve_sorts_each_author_separately():
    author = np.array([1, 0, 1, 0], dtype=np.int32)
    created = np.array([20.0, 30.0, 10.0, 5.0])
    order, half, medians, counts = MOD.order_and_halve(author, created, 2)
    assert order.tolist() == [3, 1, 2, 0]
    assert counts.tolist() == [2, 2]


def test_median_adjacencies_uses_the_per_author_mean_of_the_two_halves():
    """The .75 in the Big5 anchor is only reachable this way."""

    cache = {"n_early": np.array([51, 61, 71, 81], dtype=np.int64),
             "n_total": np.array([102, 123, 143, 165], dtype=np.int64)}
    sel = np.ones(4, dtype=bool)
    # per-author mean adjacencies: 50.0, 60.5, 70.5, 81.5 -> median 65.5
    assert MOD.median_adjacencies(cache, sel) == pytest.approx(65.5)
    cache2 = {"n_early": np.array([51, 61], dtype=np.int64),
              "n_total": np.array([102, 124], dtype=np.int64)}
    # 50.0 and 61.0 -> median 55.5, and a .25/.75 arises on other pairings
    assert MOD.median_adjacencies(cache2, np.ones(2, bool)) == \
        pytest.approx(55.5)


def test_venue_residual_removes_the_community_half_mean():
    cache = {
        "ev_wcq": np.array([0, 3, 7, 3], dtype=np.int32),
        "ev_comm": np.array([0, 0, 1, 1], dtype=np.int32),
        "ev_half": np.array([0, 0, 1, 1], dtype=np.int8),
        "ch_count": np.array([2, 0, 0, 2], dtype=np.int64),
        "ch_sum": np.array([math.log(1) + math.log(4), 0.0, 0.0,
                            math.log(8) + math.log(4)]),
    }
    resid, info = MOD.venue_residual(cache)
    y = np.log1p(cache["ev_wcq"].astype(float))
    assert resid[0] == pytest.approx(y[0] - y[:2].mean())
    assert resid[1] == pytest.approx(y[1] - y[:2].mean())
    assert resid[2] == pytest.approx(y[2] - y[2:].mean())
    assert info["events_residualized"] == 4


def test_arm_layout_gives_one_early_and_one_late_cell_per_author():
    cache = {"offsets": np.array([0, 10, 30, 60], dtype=np.int64),
             "n_early": np.array([4, 9, 15], dtype=np.int64),
             "n_total": np.array([10, 20, 30], dtype=np.int64)}
    sel = np.array([True, False, True])
    start, length, author, half = MOD.arm_layout(cache, sel)
    assert start.tolist() == [0, 30, 4, 45]
    assert length.tolist() == [4, 15, 6, 15]
    assert author.tolist() == [0, 1, 0, 1]
    assert half.tolist() == [0, 0, 1, 1]


def test_degenerate_halves_counts_by_sd_alone():
    cache = {"ev_wcq": np.array([5, 5, 5, 5, 1, 9, 2, 8], dtype=np.int32),
             "ev_half": np.array([0, 0, 1, 1, 0, 0, 1, 1], dtype=np.int8),
             "n_total": np.array([4, 4], dtype=np.int64)}
    assert MOD.degenerate_halves(cache, np.array([True, False])) == 2
    assert MOD.degenerate_halves(cache, np.array([False, True])) == 0


def test_cross_share_helper_is_the_pooled_within_half_share():
    cache = {
        "n_total": np.array([4, 4], dtype=np.int64),
        "n_early": np.array([2, 2], dtype=np.int64),
        "offsets": np.array([0, 4, 8], dtype=np.int64),
        "ev_half": np.array([0, 0, 1, 1, 0, 0, 1, 1], dtype=np.int8),
        "ev_link": np.array([1, 2, 3, 3, 5, 5, 7, 8], dtype=np.uint64),
    }
    ct = MOD.cross_thread_mask(cache)
    # within-half adjacencies: author 0 -> (0,1) cross, (2,3) same;
    #                          author 1 -> (4,5) same, (6,7) cross
    assert MOD._cross_share(cache, np.array([True, True]), ct) == \
        pytest.approx(0.5)
    assert MOD._cross_share(cache, np.array([True, False]), ct) == \
        pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 8. registration pins, anchors, provenance, governance
# ---------------------------------------------------------------------------


def test_registration_pins():
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499
    assert MOD.B_BOOT == 1000
    assert MOD.POOL_FLOOR_PRIMARY == 50
    assert MOD.POOL_FLOOR_SENSITIVITY == 100
    assert MOD.BOUNDARY_LOW == 0.15
    assert MOD.BOUNDARY_HIGH == 0.50
    assert MOD.BOUNDARY_HALFWIDTH == 0.011
    assert MOD.N_SYNTH_REPLICATES == 8
    assert MOD.TOL_FLOOR == 0.02
    assert MOD.TOL_SD_MULT == 3.0
    assert MOD.RHO_TRUE_TARGET == 0.50
    assert MOD.LEAN_RHO_OWN == (0.30, 0.60)
    # seeds DERIVED from the registration pin, never re-chosen (#76)
    assert (MOD.SEED_PART0, MOD.SEED_PERM, MOD.SEED_BOOT) == \
        (MOD.SEED + 1, MOD.SEED + 2, MOD.SEED + 3)


def test_blocking_anchors_match_the_registration_text():
    section = PLAN.read_text(encoding="utf-8").split(
        "## X2 — the path of expression volume")[1]
    for token in ("8,008", "1,116", "0.73159", "0.62054", "348.0", "491.75",
                  "17,640,062", "10,296", "1,401", "8,895"):
        assert token in section, token
    assert MOD.ANCHOR_POOL_DISJOINT == 8_008
    assert MOD.ANCHOR_POOL_BIG5 == 1_116
    assert MOD.ANCHOR_CROSS_SHARE_DISJOINT == 0.73159
    assert MOD.ANCHOR_CROSS_SHARE_BIG5 == 0.62054
    assert MOD.ANCHOR_MEDIAN_ADJ_DISJOINT == 348.0
    assert MOD.ANCHOR_MEDIAN_ADJ_BIG5 == 491.75
    assert MOD.ANCHOR_DEGENERATE_DISJOINT == 0
    assert MOD.ANCHOR_DEGENERATE_BIG5 == 0
    assert MOD.ANCHOR_ROWS_PARSEABLE == 17_640_062
    assert MOD.ANCHOR_AUTHORS == 10_296
    assert MOD.ANCHOR_BIG5_AUTHORS + MOD.ANCHOR_DISJOINT_AUTHORS == \
        MOD.ANCHOR_AUTHORS


def test_anchor_gate_is_blocking_and_exact():
    ok = MOD.anchor_gate({"a": 8_008}, {"a": 8_008})
    bad = MOD.anchor_gate({"a": 8_007}, {"a": 8_008})
    assert ok["status"] == "PASS"
    assert bad["status"] == "FAIL"


def test_inherited_machinery_is_the_x1b_object_not_a_copy():
    """#56/#81: the names are BOUND to the committed X1b module, not copied."""

    assert Path(MOD.X1B.__file__).resolve() == X1B_SCRIPT.resolve()
    for name in ("write_json", "utc_now", "fmt", "fmt_ci", "percentile_ci",
                 "scan_for_cohort_ids", "baseline_hit_keys", "new_hits_only",
                 "anchor_gate"):
        assert getattr(MOD, name) is getattr(MOD.X1B, name), name
    assert MOD.RunLog is MOD.X1B.RunLog
    # ... and X1b itself is bound to X1, which is bound to U2/U2b.
    assert MOD.X1B.percentile_ci is MOD.X1B.X1.percentile_ci
    src = SCRIPT.read_text(encoding="utf-8")
    for name in ("def write_json", "def percentile_ci", "def anchor_gate",
                 "def scan_for_cohort_ids", "class RunLog"):
        assert name not in src, f"X2 must not redefine {name}"


def test_id_scan_helper_finds_a_planted_name(tmp_path):
    target = tmp_path / "prose.md"
    target.write_text("the author name_of_interest wrote a lot\n")
    scan = MOD.scan_for_cohort_ids([target], ["name_of_interest"])
    assert scan["status"] == "FAIL"
    assert scan["n_hits"] == 1
    clean = MOD.scan_for_cohort_ids([target], ["someone_else_entirely"])
    assert clean["status"] == "PASS"


def test_id_scan_helper_ignores_substring_matches():
    """A name inside a longer identifier is not a leak (the #83 rule)."""

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.md"
        p.write_text("prefixed_name_suffixed\n")
        assert MOD.scan_for_cohort_ids([p], ["name"])["status"] == "PASS"


def test_governance_no_body_column_and_no_labels():
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"body"' not in src
    assert "usecols=columns" in src
    assert re.search(r'columns = \["author", "subreddit", "created_utc",\s*'
                     r'"link_id",\s*"word_count_quoteless"\]', src)
    # author_profiles.csv appears ONLY inside a governance statement
    assert "author_profiles" in src
    for match in re.finditer("author_profiles", src):
        window = src[max(0, match.start() - 220):match.end() + 220].lower()
        assert "never" in window, window
    # ... and it is never opened: no read of it exists anywhere in the source
    assert not re.search(r"(read_csv|open)\([^)]*author_profiles", src)


def test_committed_files_are_exactly_the_scanned_set():
    names = {p.name for p in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_X2_VOLUME_PATH_REPORT.md",
                     "run_suica_m4_x2_volume_path.py",
                     "test_m4_x2_volume_path.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_boundaries_carry_the_registered_cautions():
    text = " ".join(MOD.BOUNDARIES).lower()
    for phrase in ("metadata only", "projection caution", "psychological",
                   "exploratory", "typology-enriched", "attenuat"):
        assert phrase in text, phrase


# ---------------------------------------------------------------------------
# 9. artifacts and rule 24 (skipped when the leg has not been run here)
# ---------------------------------------------------------------------------


needs_artifacts = pytest.mark.skipif(
    not (ARTIFACTS / "verdict.json").exists(),
    reason="results/ is gitignored; the run's artifacts are local")


@needs_artifacts
def test_census_artifact_passed_every_blocking_anchor():
    census = json.loads((ARTIFACTS / "census.json").read_text())
    assert census["status"] == "PASS"
    pins = census["pins"]
    assert pins["pool: >= 50 events in EACH half, disjoint"]["observed"] == 8008
    assert pins["pool: >= 50 events in EACH half, Big5"]["observed"] == 1116
    assert pins["median adjacencies per half, Big5"]["observed"] == 491.75
    for pin in pins.values():
        assert pin["status"] == "PASS"


@needs_artifacts
def test_part0_routing_clauses_all_passed():
    part0 = json.loads((ARTIFACTS / "part0_gate.json").read_text())
    assert part0["status"] == "PASS"
    assert [c["id"] for c in part0["routing"]] == ["i", "ii", "iii", "iv", "v"]
    assert all(c["status"] == "PASS" for c in part0["routing"])
    assert all(c["status"] == "ANNOTATED" for c in part0["descriptive"])
    assert part0["marginal_contract"]["per_cell_multiset_bit_exact"] is True


@needs_artifacts
def test_report_headline_is_generated_from_the_artifacts():
    verdict = json.loads((ARTIFACTS / "verdict.json").read_text())
    text = REPORT.read_text(encoding="utf-8")
    assert f"`{verdict['cell']}`" in text
    assert f"{verdict['rho_own']:.4f}" in text
    assert f"{verdict['presence_mean_r1']:.4f}" in text


@needs_artifacts
def test_every_arm_is_reported_with_both_estimands():
    arms = json.loads((ARTIFACTS / "arms.json").read_text())
    assert set(arms) == {"primary", "cross_thread", "venue_resid", "big5",
                         "floor100"}
    for arm in arms.values():
        assert arm["presence_null"]["b"] == MOD.B_PERM
        assert arm["ownership_null"]["b"] == MOD.B_PERM
        assert arm["ownership_boot"]["b"] == MOD.B_BOOT
        assert math.isfinite(arm["rho_own"])


@needs_artifacts
def test_id_leak_scan_passed_with_the_recorded_baseline():
    scan = json.loads((ARTIFACTS / "id_leak_scan.json").read_text())
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS


@needs_artifacts
def test_ledger_carries_exactly_one_x2_row():
    rows = [line for line in LEDGER.read_text(encoding="utf-8").splitlines()
            if line.startswith("| M4-X2 ")]
    assert len(rows) == 1
    assert "EXPLORATORY" in rows[0]
    assert "metadata-only" in rows[0]
    assert "label-free" in rows[0]


@needs_artifacts
def test_plan_carries_the_appended_outcome():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X2 outcome (executor, 2026-08-19)" in text
    assert text.index("## X2 — the path of expression volume") < \
        text.index("## X2 outcome (executor, 2026-08-19)")


# ---------------------------------------------------------------------------
# 10. the attenuation arithmetic (annotation; it must still be right)
# ---------------------------------------------------------------------------


def test_implied_phi_variance_inverts_the_part0_mapping():
    """The annotation and the gate's mapping are the SAME model, inverted."""

    for a_e, a_l, v_true in ((0.004, 0.004, 0.004), (0.01, 0.02, 0.006),
                             (0.002, 0.009, 0.03)):
        rho = v_true / math.sqrt((v_true + a_e) * (v_true + a_l))
        assert MOD.implied_phi_variance(rho, a_e, a_l) == \
            pytest.approx(v_true, rel=1e-9)


def test_implied_phi_variance_is_undefined_outside_the_unit_interval():
    assert math.isnan(MOD.implied_phi_variance(0.0, 0.01, 0.01))
    assert math.isnan(MOD.implied_phi_variance(-0.2, 0.01, 0.01))
    assert math.isnan(MOD.implied_phi_variance(1.0, 0.01, 0.01))


def test_attenuation_arithmetic_reads_two_arms_of_the_same_world_alike():
    """Longer halves attenuate less: the same planted Var(phi), two rho."""

    a_short = 0.02
    a_long = 0.005
    v = 0.01
    rho_short = v / (v + a_short)
    rho_long = v / (v + a_long)
    assert rho_long > rho_short
    assert MOD.implied_phi_variance(rho_short, a_short, a_short) == \
        pytest.approx(MOD.implied_phi_variance(rho_long, a_long, a_long),
                      rel=1e-9)


@needs_artifacts
def test_attenuation_artifact_covers_every_arm():
    att = json.loads((ARTIFACTS / "attenuation.json").read_text())
    arms = json.loads((ARTIFACTS / "arms.json").read_text())
    assert set(att) == set(arms)
    for key, row in att.items():
        assert row["rho_own"] == pytest.approx(arms[key]["rho_own"])
        assert "NOT an estimator" in row["note"]


def test_honest_anomalies_names_every_divergence_it_should():
    arms = {"primary": toy_arm([(0, 0, np.arange(60.0)),
                                (0, 1, np.arange(60.0))])}
    results = {
        "primary": _fake_arm_result("primary", 0.26, (0.23, 0.29)),
        "big5": _fake_arm_result("big5", 0.64, (0.59, 0.68), presence=0.18),
        "floor100": _fake_arm_result("floor100", 0.33, (0.30, 0.37)),
        "cross_thread": _fake_arm_result("cross_thread", 0.11,
                                         (0.07, 0.14), presence=0.05),
    }
    for res in results.values():
        res["presence_null"] = {"band": [-0.006, -0.004],
                                "null_mean": -0.005}
    attenuation = {k: {"implied_phi_variance": v, "A_early": 0.0046}
                   for k, v in (("primary", 0.0016), ("big5", 0.0073),
                                ("floor100", 0.0015),
                                ("cross_thread", 0.0007))}
    part0 = {"common_path": {"rho_own": 0.008,
                             "ownership_boot": {"ci": [-0.02, 0.038]}}}
    rows = MOD.honest_anomalies(arms, results, {}, part0, attenuation)
    text = " ".join(r["anomaly"] + r["detail"] for r in rows).lower()
    assert len(rows) == 5
    for phrase in ("below zero", "strongly_owned", "floor-100", "straddle",
                   "asymmetric"):
        assert phrase in text, phrase


def test_exact_prints_anchors_at_their_registered_precision():
    assert MOD._exact(17_640_062) == "17,640,062"
    assert MOD._exact(0.73159) == "0.73159"
    assert MOD._exact(0.62054) == "0.62054"
    assert MOD._exact(348.0) == "348"
    assert MOD._exact(491.75) == "491.75"
    assert MOD._exact(0) == "0"


def test_no_generated_table_cell_carries_a_bare_pipe():
    """A literal '|' inside a cell silently splits the markdown table."""

    import io
    lines: list[str] = []
    MOD._table(lines.append, ["a", "b"], [["x", "y"]])
    assert lines[0].count("|") == 3
    if REPORT.exists():
        for line in REPORT.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and line.endswith("|"):
                cells = line.strip("|").split("|")
                assert all(cell.strip() != "" for cell in cells), line
