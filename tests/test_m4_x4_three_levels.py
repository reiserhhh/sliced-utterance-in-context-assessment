"""Contract tests for SUICA M4-X4 — the three-level decomposition.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X4", commit 42f0625) names six objects that are NEW here and therefore have
to be pinned by contract rather than inherited from the X line:

1. WITHIN-CENTERING EXACTNESS — level 2 must be blind to any per-(author,
   half) shift of y, and a cell with no x spread must contribute EXACTLY zero
   to the pooled sums (not "approximately zero");
2. THE ERGODIC WORLD'S DELTA HONESTY — a world with one slope for everybody
   and person intercepts unrelated to their own mean x must read Delta = 0;
3. THE NON-ERGODIC WORLD'S DERIVED DELTA — the identity Delta = gamma is
   analytic, so with the noise switched off it must hold to machine precision
   and not merely on average;
4. THE SLOPE-OWNERSHIP MAPPING — the #76 operating point must solve its own
   equation, reduce to V = A on balanced halves, move monotonically with its
   target, and actually plant the ownership it claims on a toy skeleton;
5. THE #88a PRICING ORDER — the boundary regions must be pinned to disk
   BEFORE the first real-arm number, asserted from the artifacts' own
   timestamps and not from prose; and the priced ladder's own coherence must
   be reported when the regions overlap;
6. THE CELLS — the registered Delta ladder including the sign-flip clause's
   "both slopes detected" requirement, and X2's ownership ladder re-priced.

Everything the leg inherits (``RunLog``, ``write_json``, ``percentile_ci``,
``anchor_gate``, ``ownership_null``, ``cluster_bootstrap_pairs``,
``implied_phi_variance``, ``order_and_halve``, ``scan_for_cohort_ids`` and the
#83 HEAD-baseline helpers) is X2's and is covered by that leg's tests; it is
re-checked here only where the binding itself could break.
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
SCRIPT = ROOT / "scripts" / "run_suica_m4_x4_three_levels.py"
X2_SCRIPT = ROOT / "scripts" / "run_suica_m4_x2_volume_path.py"
ARTIFACTS = ROOT / "results" / "m4_x4_three_levels"
REPORT = ROOT / "reports" / "SUICA_M4_X4_THREE_LEVELS_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X2 recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x4_three_levels", SCRIPT)


# ---------------------------------------------------------------------------
# helpers — toy skeletons, no corpus needed
# ---------------------------------------------------------------------------


def toy_cache(halves):
    """A minimal cache from [(x_early, x_late), ...], one entry per author."""

    n_early = np.array([len(e) for e, _ in halves], dtype=np.int64)
    n_total = np.array([len(e) + len(l) for e, l in halves], dtype=np.int64)
    ev_x = np.concatenate([np.concatenate([np.asarray(e, dtype=np.float64),
                                           np.asarray(l, dtype=np.float64)])
                           for e, l in halves])
    return {
        "n_early": n_early,
        "n_total": n_total,
        "offsets": np.concatenate(([0], np.cumsum(n_total))).astype(np.int64),
        "ev_x": ev_x,
    }


def toy_skeleton(halves, key="toy", sel=None):
    cache = toy_cache(halves)
    stats = MOD.x_only_stats(cache)
    if sel is None:
        sel = np.ones(len(halves), dtype=bool)
    return MOD.Skeleton(key, key, cache, sel, stats, with_events=True)


def balanced_skeleton(n_authors=400, n_events=40, seed=3):
    """Equal-length halves whose x values are iid normal (well-conditioned)."""

    rng = np.random.default_rng(seed)
    halves = [(rng.normal(size=n_events), rng.normal(size=n_events))
              for _ in range(n_authors)]
    return toy_skeleton(halves)


def reference_slope(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    return float(np.polyfit(x, y, 1)[0])


def measure(sk, y):
    return MOD.three_levels(MOD.cell_moments(sk, y))


# ---------------------------------------------------------------------------
# 1. within-centering exactness (the level-2 contract)
# ---------------------------------------------------------------------------


def test_cell_slope_reproduces_the_ordinary_least_squares_slope():
    x_e = np.array([1.0, 2.0, 3.0, 5.0, 8.0])
    x_l = np.array([-1.0, 0.5, 2.0, 2.5])
    sk = toy_skeleton([(x_e, x_l)])
    y = np.concatenate([3.0 - 0.25 * x_e + np.array([.1, -.2, .05, 0., -.1]),
                        1.0 + 0.5 * x_l])
    mom = MOD.cell_moments(sk, y)
    beta_e, beta_l, ok = MOD.per_cell_slopes(sk, mom)
    assert bool(ok[0])
    assert beta_e[0] == pytest.approx(reference_slope(x_e, y[:5]), abs=1e-12)
    assert beta_l[0] == pytest.approx(reference_slope(x_l, y[5:]), abs=1e-12)


def test_level_2_is_blind_to_any_per_cell_shift_of_y():
    """Adding a constant inside a cell must not move num, den or level 2."""

    sk = balanced_skeleton(n_authors=60, n_events=25, seed=11)
    rng = np.random.default_rng(5)
    y = rng.normal(size=sk.events["n_events"])
    base = MOD.cell_moments(sk, y)
    shift = rng.normal(size=2 * sk.n_authors) * 10.0
    y_shifted = y + shift[sk.events["key"]]
    moved = MOD.cell_moments(sk, y_shifted)
    for name in ("num_e", "num_l", "den_e", "den_l"):
        assert np.allclose(base[name], moved[name], atol=1e-9, rtol=1e-10)
    assert MOD.three_levels(base)["beta_within"] == pytest.approx(
        MOD.three_levels(moved)["beta_within"], abs=1e-12)


def test_level_2_is_the_den_weighted_mean_of_the_per_cell_slopes():
    sk = balanced_skeleton(n_authors=50, n_events=20, seed=13)
    rng = np.random.default_rng(7)
    y = rng.normal(size=sk.events["n_events"])
    mom = MOD.cell_moments(sk, y)
    beta_e, beta_l, _ = MOD.per_cell_slopes(sk, mom)
    early = float(np.sum(beta_e * mom["den_e"]) / np.sum(mom["den_e"]))
    late = float(np.sum(beta_l * mom["den_l"]) / np.sum(mom["den_l"]))
    got = MOD.three_levels(mom)
    assert got["beta_within_early"] == pytest.approx(early, abs=1e-12)
    assert got["beta_within_late"] == pytest.approx(late, abs=1e-12)
    assert got["beta_within"] == pytest.approx(0.5 * (early + late), abs=1e-15)


def test_a_cell_with_no_x_spread_contributes_exactly_zero_and_is_counted():
    flat = np.full(6, -2.0)
    varied = np.array([-3.0, -1.0, -2.0, -4.0, -1.5, -2.5])
    sk = toy_skeleton([(flat, varied), (varied, varied)])
    assert bool(sk.degenerate_e[0]) and not bool(sk.degenerate_l[0])
    y = np.arange(sk.events["n_events"], dtype=np.float64)
    mom = MOD.cell_moments(sk, y)
    assert mom["num_e"][0] == 0.0
    assert mom["den_e"][0] == 0.0
    beta_e, beta_l, ok = MOD.per_cell_slopes(sk, mom)
    assert math.isnan(beta_e[0])
    assert not bool(ok[0]) and bool(ok[1])
    assert sk.census()["authors_with_a_constant_half"] == 1


def test_level_1_is_the_slope_of_the_person_means():
    sk = balanced_skeleton(n_authors=80, n_events=15, seed=17)
    rng = np.random.default_rng(19)
    y = rng.normal(size=sk.events["n_events"])
    mom = MOD.cell_moments(sk, y)
    got = MOD.three_levels(mom)
    assert got["beta_between"] == pytest.approx(
        reference_slope(mom["xbar"], mom["ybar"]), abs=1e-10)
    assert got["r_between"] == pytest.approx(
        float(np.corrcoef(mom["xbar"], mom["ybar"])[0, 1]), abs=1e-12)
    assert got["delta_erg"] == pytest.approx(
        got["beta_between"] - got["beta_within"], abs=1e-15)


# ---------------------------------------------------------------------------
# 2/3. the two planted-world identities
# ---------------------------------------------------------------------------


def test_the_nonergodic_delta_identity_is_exact_without_noise():
    """Delta = gamma is ANALYTIC, so noise-free it must hold to machine eps."""

    sk = balanced_skeleton(n_authors=120, n_events=30, seed=23)
    beta, gamma = -0.10, 0.25
    x = sk.events["x"]
    y = (gamma * sk.xbar[sk.events["who"]] + beta * x)
    got = measure(sk, y)
    assert got["beta_within"] == pytest.approx(beta, abs=1e-10)
    assert got["beta_between"] == pytest.approx(beta + gamma, abs=1e-10)
    assert got["delta_erg"] == pytest.approx(gamma, abs=1e-10)


def test_the_ergodic_delta_identity_is_exact_without_noise():
    """One slope for all, intercepts unrelated to xbar: Delta is exactly 0."""

    sk = balanced_skeleton(n_authors=120, n_events=30, seed=29)
    rng = np.random.default_rng(31)
    a = rng.normal(size=sk.n_authors)
    a -= np.polyfit(sk.xbar, a, 1)[0] * (sk.xbar - sk.xbar.mean())
    y = a[sk.events["who"]] - 0.10 * sk.events["x"]
    got = measure(sk, y)
    assert got["beta_within"] == pytest.approx(-0.10, abs=1e-10)
    assert got["beta_between"] == pytest.approx(-0.10, abs=1e-8)
    assert got["delta_erg"] == pytest.approx(0.0, abs=1e-8)


def test_the_ergodic_world_reads_zero_delta_with_noise_on():
    """The planted ERGODIC world, run through the runner's own plumbing."""

    sk = balanced_skeleton(n_authors=500, n_events=30, seed=37)
    mapping = MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET)
    deltas = []
    for i in range(12):
        rng = np.random.default_rng(1000 + i)
        y, _ = MOD.plant_world(sk, MOD.WORLD_ERGODIC, mapping, rng)
        deltas.append(measure(sk, y)["delta_erg"])
    deltas = np.array(deltas)
    sem = float(np.std(deltas, ddof=1) / math.sqrt(deltas.size))
    assert abs(float(deltas.mean())) < 4.0 * sem


def test_the_nonergodic_world_recovers_gamma_with_noise_on():
    sk = balanced_skeleton(n_authors=500, n_events=30, seed=41)
    mapping = MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET)
    deltas = []
    for i in range(12):
        rng = np.random.default_rng(2000 + i)
        y, _ = MOD.plant_world(sk, MOD.WORLD_NONERGODIC, mapping, rng)
        deltas.append(measure(sk, y)["delta_erg"])
    deltas = np.array(deltas)
    sem = float(np.std(deltas, ddof=1) / math.sqrt(deltas.size))
    assert abs(float(deltas.mean()) - MOD.GAMMA_PLANT) < 4.0 * sem


def test_the_null_world_plants_no_slope_at_all():
    sk = balanced_skeleton(n_authors=300, n_events=25, seed=43)
    mapping = MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET)
    rng = np.random.default_rng(3000)
    y, truth = MOD.plant_world(sk, MOD.WORLD_NULL, mapping, rng)
    assert truth["planted_beta_mean"] == 0.0
    assert truth["planted_beta_sd"] == 0.0
    got = measure(sk, y)
    assert abs(got["beta_within"]) < 0.05
    assert abs(got["delta_erg"]) < 0.15


def test_the_owned_world_gives_every_author_their_own_slope():
    sk = balanced_skeleton(n_authors=200, n_events=20, seed=47)
    mapping = MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET)
    rng = np.random.default_rng(4000)
    _, truth = MOD.plant_world(sk, MOD.WORLD_OWNED, mapping, rng)
    assert truth["planted_beta_sd"] == pytest.approx(mapping["sd_beta"],
                                                     rel=0.25)


# ---------------------------------------------------------------------------
# 4. the slope-ownership mapping (#76 operating point)
# ---------------------------------------------------------------------------


def test_ownership_mapping_solves_its_own_equation():
    sk = balanced_skeleton(n_authors=200, n_events=30, seed=53)
    for target in (0.15, 0.30, 0.50, 0.75):
        m = MOD.ownership_slope_target(sk, target)
        v, a_e, a_l = m["V_slope_variance"], m["A_early"], m["A_late"]
        assert v / math.sqrt((v + a_e) * (v + a_l)) == pytest.approx(
            target, abs=1e-10)
        assert m["rho_implied_by_the_solution"] == pytest.approx(target,
                                                                 abs=1e-10)


def test_ownership_mapping_reduces_to_V_equals_A_on_balanced_halves():
    """At rho = 1/2 with A_e = A_l the equation collapses to V = A."""

    x = np.array([-1.0, 0.0, 1.0, 2.0])
    sk = toy_skeleton([(x, x) for _ in range(30)])
    m = MOD.ownership_slope_target(sk, 0.5)
    assert m["A_early"] == pytest.approx(m["A_late"], abs=1e-12)
    assert m["V_slope_variance"] == pytest.approx(m["A_early"], rel=1e-9)


def test_ownership_mapping_moves_monotonically_with_the_target():
    sk = balanced_skeleton(n_authors=100, n_events=25, seed=59)
    values = [MOD.ownership_slope_target(sk, t)["V_slope_variance"]
              for t in (0.10, 0.25, 0.50, 0.80)]
    assert all(b > a for a, b in zip(values, values[1:]))


def test_ownership_mapping_uses_only_the_authors_it_is_masked_to():
    sk = balanced_skeleton(n_authors=40, n_events=20, seed=61)
    mask = np.zeros(sk.n_authors, dtype=bool)
    mask[:10] = True
    m = MOD.ownership_slope_target(sk, 0.5, mask=mask)
    assert m["authors_in_the_mapping"] == 10
    assert m["A_early"] == pytest.approx(
        float(np.mean(1.0 / sk.den_e[mask])), abs=1e-12)


def test_planted_ownership_is_recovered_on_a_toy_skeleton():
    """The whole point of the mapping: plant 0.50, read back about 0.50."""

    sk = balanced_skeleton(n_authors=1200, n_events=30, seed=67)
    mapping = MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET)
    rhos = []
    for i in range(8):
        rng = np.random.default_rng(5000 + i)
        y, _ = MOD.plant_world(sk, MOD.WORLD_OWNED, mapping, rng)
        beta_e, beta_l, ok = MOD.per_cell_slopes(sk, MOD.cell_moments(sk, y))
        rhos.append(float(MOD.rowwise_pearson(beta_e[ok], beta_l[ok])[0]))
    rhos = np.array(rhos)
    tol = max(MOD.TOL_FLOOR_RHO, MOD.TOL_SD_MULT * float(np.std(rhos, ddof=1)))
    assert abs(float(rhos.mean()) - MOD.RHO_TRUE_TARGET) <= tol


def test_the_mapping_binds_x2s_quadratic_rather_than_restating_it():
    """The mapping is X2's quadratic, solved for a SLOPE variance."""

    assert MOD.implied_phi_variance is MOD.X2.implied_phi_variance
    sk = balanced_skeleton(n_authors=60, n_events=20, seed=71)
    m = MOD.ownership_slope_target(sk, 0.4)
    assert m["V_slope_variance"] == MOD.X2.implied_phi_variance(
        0.4, m["A_early"], m["A_late"])


# ---------------------------------------------------------------------------
# 5. the cross-half dispersion and the headroom annotation
# ---------------------------------------------------------------------------


def test_var_beta_is_the_cross_half_covariance():
    rng = np.random.default_rng(73)
    e = rng.normal(size=500)
    l = 0.6 * e + rng.normal(size=500)
    ok = np.ones(500, dtype=bool)
    got = MOD.dispersion(e, l, ok)
    assert got["var_true_cross_half"] == pytest.approx(
        float(np.cov(e, l, ddof=1)[0, 1]), abs=1e-12)
    assert got["mean_beta"] == pytest.approx(float(np.mean(0.5 * (e + l))),
                                             abs=1e-12)
    assert got["sd_true"] == pytest.approx(
        math.sqrt(got["var_true_cross_half"]), abs=1e-12)
    assert got["headroom_hi"] - got["headroom_lo"] == pytest.approx(
        2 * 1.96 * got["sd_true"], abs=1e-10)


def test_var_beta_reports_n_a_when_the_covariance_is_negative():
    rng = np.random.default_rng(79)
    e = rng.normal(size=200)
    l = -e + 0.01 * rng.normal(size=200)
    got = MOD.dispersion(e, l, np.ones(200, dtype=bool))
    assert got["var_true_cross_half"] < 0
    assert math.isnan(got["sd_true"])
    assert math.isnan(got["headroom_lo"])


# ---------------------------------------------------------------------------
# 6. the paired bootstrap (one author draw, both slopes redone)
# ---------------------------------------------------------------------------


def test_paired_bootstrap_recomputes_both_slopes_from_the_same_draw():
    """Delta's bootstrap sd must be the sd of the DIFFERENCE, not a sum."""

    sk = balanced_skeleton(n_authors=300, n_events=20, seed=83)
    rng = np.random.default_rng(89)
    y, _ = MOD.plant_world(
        sk, MOD.WORLD_NONERGODIC,
        MOD.ownership_slope_target(sk, MOD.RHO_TRUE_TARGET), rng)
    mom = MOD.cell_moments(sk, y)
    boot = MOD.paired_level_bootstrap(mom, 400, 97)
    assert boot["b"] == 400
    point = MOD.three_levels(mom)["delta_erg"]
    assert boot["delta_ci"][0] < point < boot["delta_ci"][1]
    assert boot["delta_boot_sd"] < (boot["beta_between_boot_sd"]
                                    + boot["beta_within_boot_sd"])


def test_paired_bootstrap_is_deterministic_under_its_seed():
    sk = balanced_skeleton(n_authors=100, n_events=15, seed=101)
    rng = np.random.default_rng(103)
    mom = MOD.cell_moments(sk, rng.normal(size=sk.events["n_events"]))
    a = MOD.paired_level_bootstrap(mom, 200, 11)
    b = MOD.paired_level_bootstrap(mom, 200, 11)
    assert a == b


# ---------------------------------------------------------------------------
# 7. the cells, the priced regions and the ladder's own coherence
# ---------------------------------------------------------------------------


def fake_regions(delta_w=0.02, low_w=0.03, high_w=0.04):
    return {"delta": {"centre": 0.0, "half_width": delta_w},
            "rho_low": {"centre": 0.15, "half_width": low_w},
            "rho_high": {"centre": 0.50, "half_width": high_w}}


def test_rho_region_edges_are_the_priced_half_widths():
    edges = MOD.rho_region_edges(fake_regions())
    assert edges == pytest.approx((0.12, 0.18, 0.46, 0.54))


@pytest.mark.parametrize("rho,expected", [
    (-0.20, MOD.CELL_NOT_OWNED),
    (0.05, MOD.CELL_NOT_OWNED),
    (0.12, MOD.CELL_AT_LOW),
    (0.15, MOD.CELL_AT_LOW),
    (0.18, MOD.CELL_AT_LOW),
    (0.30, MOD.CELL_WEAK),
    (0.46, MOD.CELL_AT_HIGH),
    (0.54, MOD.CELL_AT_HIGH),
    (0.90, MOD.CELL_STRONG),
])
def test_rho_ladder(rho, expected):
    assert MOD.rho_cell(rho, False, fake_regions()) == expected


def test_the_null_cell_is_checked_first_on_both_objects():
    assert MOD.rho_cell(0.9, True, fake_regions()) == MOD.CELL_NOT_OWNED
    result = {"delta_ci_covers_zero": True, "beta_between": 1.0,
              "beta_within": -1.0, "beta_between_detected": True,
              "beta_within_detected": True}
    assert MOD.delta_cell(result) == MOD.CELL_INDIST


def test_delta_ladder_needs_both_slopes_detected_for_a_sign_flip():
    base = {"delta_ci_covers_zero": False, "beta_between": 0.07,
            "beta_within": -0.01, "beta_between_detected": True,
            "beta_within_detected": True}
    assert MOD.delta_cell(base) == MOD.CELL_SIGN_FLIP
    undetected = dict(base, beta_within_detected=False)
    assert MOD.delta_cell(undetected) == MOD.CELL_SIGN_UNRESOLVED
    same = dict(base, beta_within=0.01)
    assert MOD.delta_cell(same) == MOD.CELL_SAME_SIGN


def test_ladder_status_flags_an_empty_weakly_owned_interval():
    coherent = MOD.ladder_status(fake_regions())
    assert coherent["status"] == "COHERENT"
    assert coherent["weakly_owned_interval_is_empty"] is False
    collapsed = MOD.ladder_status(fake_regions(low_w=0.40, high_w=0.20))
    assert collapsed["status"] == "DEGENERATE_OVERLAP"
    assert collapsed["weakly_owned_interval_is_empty"] is True


def test_straddles_report_every_priced_edge_the_interval_crosses():
    assert MOD.edges_straddled([0.10, 0.50], MOD.rho_region_edges(
        fake_regions())) == ["0.1200", "0.1800", "0.4600"]
    assert MOD.edges_straddled([0.20, 0.30],
                               MOD.rho_region_edges(fake_regions())) == []


def test_classify_reports_both_objects_and_both_straddles():
    result = {
        "arm": "toy", "label": "toy", "delta_erg": 0.05,
        "delta_ci_covers_zero": False, "beta_between": 0.07,
        "beta_within": -0.01, "beta_between_detected": True,
        "beta_within_detected": True, "rho_own": 0.30,
        "rho_ci": [0.10, 0.50], "rho_ci_covers_zero": False,
        "boot": {"delta_ci": [0.01, 0.09]},
        "ownership_null": {"band": [-0.02, 0.02]},
    }
    cell = MOD.classify(result, fake_regions())
    assert cell["delta_cell"] == MOD.CELL_SIGN_FLIP
    assert cell["rho_cell"] == MOD.CELL_WEAK
    assert cell["delta_is_straddle"] is True     # crosses +0.02
    assert cell["rho_is_straddle"] is True
    assert cell["delta_inside_priced_region"] is False


def test_flags_73_fires_on_divergence_and_the_primary_routes():
    def cell(delta_c, rho_c):
        return {"delta_cell": delta_c, "rho_cell": rho_c, "delta_erg": 0.05,
                "delta_ci": [0.03, 0.07], "rho_own": 0.3,
                "rho_ci": [0.2, 0.4], "delta_is_straddle": False,
                "rho_is_straddle": False,
                "delta_region_edges_straddled": [],
                "rho_region_edges_straddled": []}
    cells = {"primary": cell(MOD.CELL_SIGN_FLIP, MOD.CELL_WEAK),
             "big5": cell(MOD.CELL_SAME_SIGN, MOD.CELL_WEAK)}
    flags = MOD.flags_73(cells)
    assert len(flags) == 1
    assert flags[0]["arm"] == "big5" and flags[0]["object"] == "Delta_erg"
    assert flags[0]["primary_cell"] == MOD.CELL_SIGN_FLIP
    assert MOD.flags_73({"primary": cells["primary"]}) == []


def test_build_verdict_a1_stops_when_a_routing_clause_fails():
    verdict = MOD.build_verdict({"status": "FAIL"}, {}, {})
    assert verdict["cell"] == MOD.CELL_A1_STOP
    assert "A1 stop" in verdict["note"]


# ---------------------------------------------------------------------------
# 8. the skeleton: order, halves, pool and the census descriptors
# ---------------------------------------------------------------------------


def test_order_is_stable_so_ties_keep_stream_order():
    author = np.array([0, 0, 0, 0], dtype=np.int32)
    created = np.array([5.0, 5.0, 5.0, 9.0])
    order, half, medians, counts = MOD.order_and_halve(author, created, 1)
    assert list(order) == [0, 1, 2, 3]
    assert medians[0] == pytest.approx(5.0)
    assert list(half) == [0, 0, 0, 1]


def test_community_x_is_the_log10_share_of_the_whole_stream():
    codes = np.array([0, 0, 0, 1], dtype=np.int32)
    x, counts = MOD.community_x(codes, 2)
    assert list(counts) == [3, 1]
    assert x[0] == pytest.approx(math.log10(0.75))
    assert x[1] == pytest.approx(math.log10(0.25))


def test_x_only_stats_never_touch_y():
    sk = balanced_skeleton(n_authors=20, n_events=12, seed=107)
    assert set(MOD.x_only_stats(toy_cache([(np.arange(3.0),
                                            np.arange(3.0))]))) == {
        "n_e", "n_l", "den_e", "den_l", "degenerate_e", "degenerate_l",
        "xbar", "n_u"}
    assert sk.den_e.min() > 0


def test_precision_floor_is_x_only_and_pinned_in_the_config():
    sk = toy_skeleton([(np.array([0.0, 0.0, 0.1]), np.array([0.0, 1.0, 2.0])),
                       (np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]))])
    assert sk.den_e[0] < MOD.PRECISION_FLOOR_DEN
    assert not bool(sk.precise[0]) and bool(sk.precise[1])
    assert bool(sk.ok[0]) and bool(sk.ok[1])


def test_within_author_sd_x_is_the_mean_of_the_two_half_sds():
    early = np.array([0.0, 2.0])
    late = np.array([1.0, 1.0, 1.0, 7.0])
    cache = toy_cache([(early, late)])
    got = MOD.within_author_sd_x(cache)[0]
    want = 0.5 * (float(np.std(early)) + float(np.std(late)))
    assert got == pytest.approx(want, abs=1e-12)


def test_community_profile_counts_distinct_venues_and_the_top_share():
    cache = toy_cache([(np.zeros(3), np.zeros(2))])
    cache["ev_comm"] = np.array([1, 1, 2, 3, 1], dtype=np.int32)
    cache["n_subs"] = 4
    distinct, share = MOD.community_profile(cache)
    assert int(distinct[0]) == 3
    assert share[0] == pytest.approx(3 / 5)


# ---------------------------------------------------------------------------
# 9. registration pins, anchors and governance
# ---------------------------------------------------------------------------


def test_registration_pins():
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499
    assert MOD.B_BOOT == 1000
    assert MOD.POOL_FLOOR_PRIMARY == 50
    assert MOD.POOL_FLOOR_SENSITIVITY == 100
    assert MOD.N_SYNTH_REPLICATES == 8
    assert MOD.TOL_SD_MULT == 3.0
    assert MOD.TOL_FLOOR_RHO == 0.02
    assert MOD.TOL_DELTA_SCALE_FRAC == 0.02
    assert MOD.RHO_TRUE_TARGET == 0.50
    assert MOD.BOUNDARY_RHO_LOW == 0.15
    assert MOD.BOUNDARY_RHO_HIGH == 0.50
    assert MOD.BOUNDARY_DELTA_CENTRE == 0.0


def test_blocking_anchors_match_the_registration_text():
    text = PLAN.read_text(encoding="utf-8")
    section = text[text.index("## X4 — the three-level decomposition"):]
    for token in ("17,640,062", "46,214", "8,004", "1,112", "0.805", "0.965",
                  "1.111", "0.660", "0.856", "1.013", "0.259", "0.577",
                  "0.329", "0.743"):
        assert token in section, token
    assert "−7.25" in section and "−1.14" in section
    assert MOD.ANCHOR_ROWS_PARSEABLE == 17_640_062
    assert MOD.ANCHOR_AUTHORS == 10_296
    assert MOD.ANCHOR_BIG5_AUTHORS == 1_401
    assert MOD.ANCHOR_DISJOINT_AUTHORS == 8_895
    assert MOD.ANCHOR_AUTHORS == (MOD.ANCHOR_BIG5_AUTHORS
                                  + MOD.ANCHOR_DISJOINT_AUTHORS)
    assert MOD.ANCHOR_COMMUNITIES == 46_214
    assert MOD.ANCHOR_POOL_DISJOINT == 8_004
    assert MOD.ANCHOR_POOL_BIG5 == 1_112
    assert MOD.ANCHOR_SDX_DISJOINT == (0.805, 0.965, 1.111)
    assert MOD.ANCHOR_SDX_BIG5 == (0.660, 0.856, 1.013)
    assert MOD.ANCHOR_TOP1_DISJOINT == (0.259, 0.577)
    assert MOD.ANCHOR_TOP1_BIG5 == (0.329, 0.743)
    assert (MOD.ANCHOR_X_MIN, MOD.ANCHOR_X_MAX) == (-7.25, -1.14)


def test_anchor_gate_is_blocking_and_exact():
    assert MOD.anchor_gate({"a": 1}, {"a": 1})["status"] == "PASS"
    assert MOD.anchor_gate({"a": 1.0001}, {"a": 1.0})["status"] == "FAIL"
    assert MOD.anchor_gate({}, {"a": 1})["status"] == "FAIL"


def test_inherited_machinery_is_the_x2_object_not_a_copy():
    """#56/#81: the names are BOUND to the committed X2 module, not copied."""

    assert Path(MOD.X2.__file__).resolve() == X2_SCRIPT.resolve()
    for name in ("ownership_null", "cluster_bootstrap_pairs",
                 "rowwise_pearson", "implied_phi_variance",
                 "order_and_halve", "anchor_gate", "percentile_ci",
                 "scan_for_cohort_ids", "baseline_hit_keys", "new_hits_only",
                 "write_json", "utc_now", "fmt", "fmt_ci"):
        assert getattr(MOD, name) is getattr(MOD.X2, name), name
    assert MOD.RunLog is MOD.X2.RunLog
    # ... and X2 itself is bound to X1b, which is bound to X1 -> U2/U2b.
    assert MOD.X2.percentile_ci is MOD.X2.X1B.percentile_ci
    src = SCRIPT.read_text(encoding="utf-8")
    for name in ("def write_json", "def percentile_ci", "def anchor_gate",
                 "def scan_for_cohort_ids", "class RunLog",
                 "def ownership_null", "def cluster_bootstrap_pairs",
                 "def order_and_halve", "def implied_phi_variance"):
        assert name not in src, f"X4 must not redefine {name}"


def test_id_scan_helper_finds_a_planted_name(tmp_path):
    target = tmp_path / "leak.md"
    target.write_text("the author zqxjkvbnm posted twice\n", encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["zqxjkvbnm", "otherperson"])
    assert scan["n_hits"] == 1


def test_id_scan_helper_ignores_short_names(tmp_path):
    target = tmp_path / "clean.md"
    target.write_text("abc def\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([target], ["abc"])["n_hits"] == 0


def test_governance_no_body_column_and_no_labels():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "author_profiles" not in source.replace(
        "``author_profiles.csv`` is NEVER opened", "").replace(
        "author_profiles_csv", "").replace(
        "`author_profiles.csv` was never opened", "")
    assert '"body"' not in source
    columns = re.search(r'columns = \[(.*?)\]', source, re.S).group(1)
    assert "body" not in columns
    assert "author" in columns and "subreddit" in columns
    assert "word_count_quoteless" in columns


def test_committed_files_are_exactly_the_scanned_set():
    names = {p.name for p in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_X4_THREE_LEVELS_REPORT.md",
                     "run_suica_m4_x4_three_levels.py",
                     "test_m4_x4_three_levels.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_boundaries_carry_the_registered_cautions():
    joined = " ".join(MOD.BOUNDARIES).lower()
    for token in ("metadata only", "volume", "projection", "psychological",
                  "exploratory", "selection", "owner"):
        assert token in joined, token
    assert "author_profiles.csv" in " ".join(MOD.BOUNDARIES)


# ---------------------------------------------------------------------------
# 10. the artifacts of the actual run
# ---------------------------------------------------------------------------


needs_artifacts = pytest.mark.skipif(
    not (ARTIFACTS / "verdict.json").exists(),
    reason="results/ is gitignored; the run's artifacts are local")


@needs_artifacts
def test_census_artifact_passed_every_blocking_anchor():
    census = json.loads((ARTIFACTS / "census.json").read_text())
    assert census["status"] == "PASS"
    pins = census["pins"]
    key_disjoint = ("pool (>= 50 each half AND sd(x) > 0 each half), "
                    "disjoint")
    assert pins[key_disjoint]["observed"] == MOD.ANCHOR_POOL_DISJOINT
    assert pins[key_disjoint.replace("disjoint", "Big5")]["observed"] == \
        MOD.ANCHOR_POOL_BIG5
    assert pins["communities"]["observed"] == MOD.ANCHOR_COMMUNITIES
    for pin in pins.values():
        assert pin["status"] == "PASS"


@needs_artifacts
def test_part0_routing_clauses_all_passed():
    part0 = json.loads((ARTIFACTS / "part0_gate.json").read_text())
    assert part0["status"] == "PASS"
    assert [c["id"] for c in part0["routing"]] == ["i", "ii", "iii", "iv", "v",
                                                   "vi"]
    assert all(c["status"] == "PASS" for c in part0["routing"])
    assert all(c["status"] == "ANNOTATED" for c in part0["descriptive"])
    assert part0["derived_delta_nonergodic"] == MOD.GAMMA_PLANT
    for world in (MOD.WORLD_ERGODIC, MOD.WORLD_NONERGODIC, MOD.WORLD_OWNED,
                  MOD.WORLD_OWNED_LOW, MOD.WORLD_NULL):
        assert part0["worlds"][world]["replicates"] == MOD.N_SYNTH_REPLICATES


@needs_artifacts
def test_the_regions_were_priced_before_the_first_real_number():
    """#88a, asserted from the artifacts' own timestamps."""

    pricing = json.loads((ARTIFACTS / "region_pricing.json").read_text())
    ordering = json.loads((ARTIFACTS / "ordering.json").read_text())
    assert ordering["status"] == "PASS"
    assert pricing["priced_utc"] == ordering["priced_utc"]
    assert pricing["priced_utc"] < ordering["first_real_number_utc"]
    for key in ("delta", "rho_low", "rho_high"):
        assert pricing[key]["half_width"] > 0
    assert pricing["delta"]["matched_world"] == MOD.WORLD_NULL
    assert pricing["rho_high"]["matched_world"] == MOD.WORLD_OWNED
    assert pricing["rho_low"]["matched_world"] == MOD.WORLD_OWNED_LOW
    # the pricing must PRE-date every real-arm artifact on disk as well
    assert (ARTIFACTS / "region_pricing.json").stat().st_mtime <= \
        (ARTIFACTS / "arms.json").stat().st_mtime


@needs_artifacts
def test_the_priced_ladder_status_is_reported_not_hidden():
    pricing = json.loads((ARTIFACTS / "region_pricing.json").read_text())
    ladder = pricing["ladder"]
    assert ladder["status"] in ("COHERENT", "DEGENERATE_OVERLAP")
    text = REPORT.read_text(encoding="utf-8")
    if ladder["status"] == "DEGENERATE_OVERLAP":
        assert "DEGENERATE_OVERLAP" in text
        assert "EMPTY interval" in text


@needs_artifacts
def test_every_arm_carries_all_three_levels():
    arms = json.loads((ARTIFACTS / "arms.json").read_text())
    assert set(arms) == {"primary", "big5", "floor100"}
    for arm in arms.values():
        assert arm["ownership_null"]["b"] == MOD.B_PERM
        assert arm["ownership_boot"]["b"] == MOD.B_BOOT
        assert arm["boot"]["b"] == MOD.B_BOOT
        for key in ("beta_between", "beta_within", "delta_erg", "rho_own"):
            assert math.isfinite(arm[key])
        assert arm["delta_erg"] == pytest.approx(
            arm["beta_between"] - arm["beta_within"], abs=1e-12)
        assert "precision_floor" in arm


@needs_artifacts
def test_report_headline_is_generated_from_the_artifacts():
    verdict = json.loads((ARTIFACTS / "verdict.json").read_text())
    text = REPORT.read_text(encoding="utf-8")
    assert f"`{verdict['cell']}`" in text
    assert f"{verdict['delta_erg']:.6f}" in text
    assert f"{verdict['beta_between']:.6f}" in text
    assert f"{verdict['beta_within']:.6f}" in text


@needs_artifacts
def test_id_leak_scan_passed_with_the_recorded_baseline():
    scan = json.loads((ARTIFACTS / "id_leak_scan.json").read_text())
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS


@needs_artifacts
def test_ledger_carries_exactly_one_x4_row():
    rows = [line for line in LEDGER.read_text(encoding="utf-8").splitlines()
            if line.startswith("| M4-X4 ")]
    assert len(rows) == 1
    assert "EXPLORATORY" in rows[0]
    assert "metadata-only" in rows[0]
    assert "label-free" in rows[0]
    assert "OWNER" in rows[0]


@needs_artifacts
def test_plan_carries_the_appended_outcome():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X4 outcome (executor, 2026-08-19)" in text
    assert text.index("## X4 — the three-level decomposition") < \
        text.index("## X4 outcome (executor, 2026-08-19)")


@needs_artifacts
def test_no_generated_table_cell_carries_a_bare_pipe():
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            assert "||" not in line.replace("| |", "")
