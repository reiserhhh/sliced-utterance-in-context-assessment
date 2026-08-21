"""Contract tests for SUICA M4-X5 — the ergodicity atlas.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X5", commit de09409) bakes in the three defects X4 purchased, and those are
what has to be pinned by contract here — the three-level estimators
themselves are X4's and are covered by that leg's tests, re-checked here only
where the binding could break:

1. #89 THE ESTIMABILITY FLOOR AND ITS PINNED PATH — ``den`` must be the
   two-pass float64 accumulation (mean first, then squared deviations), which
   is not the same number as the one-pass form on the cells the floor judges;
   the floor must be stated in the estimand's own denominator units; and a
   cell with no x spread must be unable to pass it;
2. THE FLOORED SLOPE — the level-3 estimator is the per-cell OLS slope, every
   pool author is scored, and none is silently dropped;
3. #90 THE PRECISION CEILINGS, BOTH DIRECTIONS — a recovery clause whose
   replicate spread is inside its tolerance floor is INFORMATIVE and the gate
   can pass; one whose spread exceeds it is UNINFORMATIVE and, being routing,
   STOPS the leg;
4. #91 LADDER COHERENCE AND THE EXPLICIT COLLAPSE — priced regions that are
   not a ladder must collapse the ownership classification to the stated
   binary rather than leave an empty interior cell;
5. THE R1 IMPORT — X4's committed Delta is imported and not recomputed, and
   the floored ownership recomputed on this leg's fresh cache must reproduce
   X4's committed value bit for bit;
6. THE ATLAS ROUTES, the plateau PREDICTION, the per-relation gate helpers,
   the transforms (including ``slog`` on negative scores), the blocking
   anchors and the #83 helper.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_x5_ergodicity_atlas.py"
X4_SCRIPT = ROOT / "scripts" / "run_suica_m4_x4_three_levels.py"
ARTIFACTS = ROOT / "results" / "m4_x5_ergodicity_atlas"
X4_ARTIFACTS = ROOT / "results" / "m4_x4_three_levels"
REPORT = ROOT / "reports" / "SUICA_M4_X5_ERGODICITY_ATLAS_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X4 recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x5_ergodicity_atlas", SCRIPT)

needs_artifacts = pytest.mark.skipif(
    not (ARTIFACTS / "verdict.json").exists(),
    reason="results/ is gitignored; the run's artifacts are local")
needs_x4_artifacts = pytest.mark.skipif(
    not (X4_ARTIFACTS / "cells.json").exists(),
    reason="X4's results/ is gitignored; the import check is local")


# ---------------------------------------------------------------------------
# helpers — toy caches and skeletons, no corpus needed
# ---------------------------------------------------------------------------


def toy_cache(authors):
    """A minimal cache from [(x_early, x_late, y_early, y_late), ...].

    x lands in the ``common`` channel and y in the ``volume`` channel, so the
    R1 relation spec reads them; ``score`` mirrors y with holes punched in it
    and ``gap`` is left undefined unless a test fills it.
    """

    n_early = np.array([len(a[0]) for a in authors], dtype=np.int64)
    n_total = np.array([len(a[0]) + len(a[1]) for a in authors],
                       dtype=np.int64)
    ev_common = np.concatenate([np.concatenate([np.asarray(a[0], float),
                                                np.asarray(a[1], float)])
                                for a in authors])
    ev_volume = np.concatenate([np.concatenate([np.asarray(a[2], float),
                                                np.asarray(a[3], float)])
                                for a in authors])
    return {
        "n_early": n_early,
        "n_total": n_total,
        "offsets": np.concatenate(([0], np.cumsum(n_total))).astype(np.int64),
        "ev_common": ev_common,
        "ev_volume": ev_volume,
        "ev_score": ev_volume.copy(),
        "ev_gap": np.full(ev_common.size, np.nan),
    }


R1 = MOD.RELATION_BY_KEY["R1"]


def toy_skeleton(authors, sel=None, relation=R1, with_events=True):
    cache = toy_cache(authors)
    who, half = MOD.event_author_and_half(cache)
    stats = MOD.relation_stats(cache, relation, who, half)
    if sel is None:
        sel = np.ones(len(authors), dtype=bool)
    sk = MOD.RelationSkeleton("toy", "toy", relation, cache, sel, stats, who,
                              half, with_events=with_events)
    return sk, cache, stats


def random_authors(n_authors=600, n_events=40, seed=5, slope=0.0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_authors):
        xe = rng.normal(size=n_events)
        xl = rng.normal(size=n_events)
        out.append((xe, xl, slope * xe + rng.normal(size=n_events),
                    slope * xl + rng.normal(size=n_events)))
    return out


def reference_slope(x, y):
    return float(np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)[0])


# ---------------------------------------------------------------------------
# 1. #89 — the estimability floor and its PINNED two-pass path
# ---------------------------------------------------------------------------


def test_two_pass_den_is_the_sum_of_squared_deviations_from_the_cell_mean():
    x = np.array([1.0, 2.0, 4.0, 8.0, 3.0, 3.5])
    key = np.array([0, 0, 0, 1, 1, 1])
    cnt, mean, den = MOD.two_pass_den(x, key, 2)
    for cell in (0, 1):
        values = x[key == cell]
        assert cnt[cell] == values.size
        assert mean[cell] == pytest.approx(values.mean())
        assert den[cell] == pytest.approx(
            float(np.sum((values - values.mean()) ** 2)), rel=0, abs=1e-12)


def test_the_two_pass_path_is_pinned_because_the_one_pass_form_disagrees():
    """#89's second half: the predicate must PIN its computation path.

    On a cell whose spread is tiny against its offset — exactly the cell the
    floor is there to judge — the one-pass ``E[x^2] - E[x]^2`` form cancels
    catastrophically and can even go NEGATIVE, while the two-pass form is
    accurate.  The floor would admit or reject different authors under the
    two paths, which is why the registration names one.
    """

    x = 1e8 + np.array([0.0, 1.0, 2.0, 3.0])
    key = np.zeros(4, dtype=np.int64)
    _, _, den = MOD.two_pass_den(x, key, 1)
    exact = float(np.sum((x - x.mean()) ** 2))          # == 5.0
    assert exact == pytest.approx(5.0, abs=1e-9)
    assert den[0] == pytest.approx(exact, abs=1e-9)
    n = float(x.size)
    one_pass = float((x * x).sum() - x.sum() ** 2 / n)
    assert abs(one_pass - exact) > 1.0                  # the path matters


def test_the_floor_is_stated_in_the_estimands_own_denominator_units():
    assert MOD.ESTIMABILITY_FLOOR_DEN == 1.0
    config_text = SCRIPT.read_text(encoding="utf-8")
    assert "estimability_floor_path" in config_text
    assert "den >= 1" in config_text


def test_a_cell_with_no_x_spread_has_den_exactly_zero_and_cannot_pass():
    authors = [(np.full(60, 2.0), np.linspace(0, 1, 60),
                np.arange(60.0), np.arange(60.0)),
               (np.linspace(0, 3, 60), np.linspace(0, 3, 60),
                np.arange(60.0), np.arange(60.0))]
    _, cache, stats = toy_skeleton(authors, with_events=False)
    assert stats["den_e"][0] == 0.0
    assert not stats["den_floor"][0]
    assert not stats["pool"][0]
    assert stats["pool"][1]
    assert stats["dropped_by_the_den_floor"] == 1


def test_the_pool_needs_fifty_usable_events_in_each_half_and_the_floor():
    small = (np.linspace(0, 1, 49), np.linspace(0, 1, 60),
             np.arange(49.0), np.arange(60.0))
    tiny_spread = (np.linspace(0, 0.01, 60), np.linspace(0, 1, 60),
                   np.arange(60.0), np.arange(60.0))
    good = (np.linspace(0, 3, 60), np.linspace(0, 3, 60),
            np.arange(60.0), np.arange(60.0))
    _, _, stats = toy_skeleton([small, tiny_spread, good], with_events=False)
    assert list(stats["count_floor"]) == [False, True, True]
    assert stats["den_e"][1] < MOD.ESTIMABILITY_FLOOR_DEN
    assert list(stats["pool"]) == [False, False, True]
    assert stats["dropped_by_the_count_floor"] == 1
    assert stats["dropped_by_the_den_floor"] == 1


def test_usable_events_are_the_intersection_of_the_two_channels():
    authors = [(np.linspace(0, 3, 60), np.linspace(0, 3, 60),
                np.arange(60.0), np.arange(60.0))]
    cache = toy_cache(authors)
    cache["ev_score"][:10] = np.nan          # the score channel loses 10
    who, half = MOD.event_author_and_half(cache)
    volume = MOD.relation_stats(cache, R1, who, half)
    score_rel = MOD.RELATION_BY_KEY["R4"]    # common x score
    scored = MOD.relation_stats(cache, score_rel, who, half)
    assert volume["usable_events"] == 120
    assert scored["usable_events"] == 110
    assert scored["n_e"][0] == 50 and volume["n_e"][0] == 60
    assert scored["den_e"][0] < volume["den_e"][0]


# ---------------------------------------------------------------------------
# 2. the FLOORED level-3 slope
# ---------------------------------------------------------------------------


def test_the_floored_slope_is_the_per_cell_ordinary_least_squares_slope():
    x_e = np.array([1.0, 2.0, 3.0, 5.0, 8.0] * 12)
    y_e = np.array([2.0, 1.0, 4.0, 3.0, 9.0] * 12)
    x_l = np.array([0.0, 1.0, 1.0, 4.0, 6.0] * 12)
    y_l = np.array([1.0, 0.0, 2.0, 5.0, 4.0] * 12)
    sk, cache, stats = toy_skeleton([(x_e, x_l, y_e, y_l)])
    mom = MOD.cell_moments(sk, np.concatenate([y_e, y_l]))
    beta_e, beta_l, ok = MOD.per_cell_slopes(sk, mom)
    assert bool(ok.all())
    assert beta_e[0] == pytest.approx(reference_slope(x_e, y_e))
    assert beta_l[0] == pytest.approx(reference_slope(x_l, y_l))


def test_every_pool_author_is_scored_at_level_three():
    authors = random_authors(40, 60, seed=11)
    sk, cache, stats = toy_skeleton(authors)
    y = cache["ev_volume"][sk.events["sel_event"]]
    mom = MOD.cell_moments(sk, y)
    _, _, ok = MOD.per_cell_slopes(sk, mom)
    assert int(ok.sum()) == sk.n_authors
    assert bool(sk.ok.all()) and bool(sk.precise.all())


def test_level_one_is_the_slope_of_the_person_means_over_usable_events():
    authors = random_authors(50, 30, seed=13, slope=0.4)
    sk, cache, stats = toy_skeleton(authors)
    y = cache["ev_volume"][sk.events["sel_event"]]
    mom = MOD.cell_moments(sk, y)
    levels = MOD.three_levels(mom)
    assert levels["beta_between"] == pytest.approx(
        reference_slope(mom["xbar"], mom["ybar"]))
    assert levels["delta_erg"] == pytest.approx(
        levels["beta_between"] - levels["beta_within"])


def test_level_two_is_the_den_weighted_mean_of_the_per_cell_slopes():
    authors = random_authors(30, 40, seed=17, slope=-0.3)
    sk, cache, stats = toy_skeleton(authors)
    y = cache["ev_volume"][sk.events["sel_event"]]
    mom = MOD.cell_moments(sk, y)
    beta_e, beta_l, _ = MOD.per_cell_slopes(sk, mom)
    early = float(np.sum(beta_e * mom["den_e"]) / np.sum(mom["den_e"]))
    late = float(np.sum(beta_l * mom["den_l"]) / np.sum(mom["den_l"]))
    assert MOD.three_levels(mom)["beta_within"] == pytest.approx(
        0.5 * (early + late))


def test_the_analyse_helper_refuses_a_nan_slope_that_survived_the_pool():
    authors = random_authors(20, 60, seed=19)
    sk, cache, stats = toy_skeleton(authors)
    y = cache["ev_volume"][sk.events["sel_event"]]
    mom = MOD.cell_moments(sk, y)
    sk.degenerate_e = sk.degenerate_e.copy()
    sk.degenerate_e[0] = True                  # simulate a floor failure
    with pytest.raises(RuntimeError):
        MOD.analyse_relation_arm(sk, mom, b_perm=10, b_boot=10, seed_perm=1,
                                 seed_boot=2)


# ---------------------------------------------------------------------------
# 3. the transforms (#70 pinned) and the channels
# ---------------------------------------------------------------------------


def test_slog_is_signed_and_symmetric_including_negative_scores():
    assert MOD.slog(np.array([0.0]))[0] == 0.0
    assert MOD.slog(np.array([4.0]))[0] == pytest.approx(math.log1p(4.0))
    assert MOD.slog(np.array([-4.0]))[0] == pytest.approx(-math.log1p(4.0))
    values = np.array([-1000.0, -7.0, -1.0, 0.0, 1.0, 7.0, 1000.0])
    out = MOD.slog(values)
    assert np.all(np.diff(out) > 0)                       # strictly monotone
    assert out == pytest.approx(-MOD.slog(-values))       # odd


def test_slog_keeps_a_missing_score_missing():
    assert not np.isfinite(MOD.slog(np.array([np.nan]))[0])


def test_the_gap_channel_drops_the_first_event_and_nonpositive_gaps():
    scaffold = {
        "author_code": np.array([0, 0, 0, 0, 1, 1], dtype=np.int32),
        "subreddit_code": np.array([0, 1, 0, 1, 0, 1], dtype=np.int32),
        "created_utc": np.array([100.0, 110.0, 110.0, 1110.0, 5.0, 15.0]),
        "wcq": np.array([3, 4, 5, 6, 7, 8], dtype=np.int32),
        "score": np.array([1.0, -2.0, np.nan, 4.0, 5.0, 6.0]),
        "authors": ["a", "b"],
        "subreddits": ["s0", "s1"],
        "stream_stats": {},
    }
    log = MOD.RunLog(Path("/tmp") / "x5_toy_gap.jsonl")
    old_floor = MOD.POOL_FLOOR_EVENTS
    MOD.POOL_FLOOR_EVENTS = 1
    try:
        cache = MOD.build_event_cache(
            scaffold, np.array([False, False]), log)
    finally:
        MOD.POOL_FLOOR_EVENTS = old_floor
    gap = cache["ev_gap"]
    assert not np.isfinite(gap[0])                    # first event of author a
    assert gap[1] == pytest.approx(math.log10(10.0))
    assert not np.isfinite(gap[2])                    # tie -> nonpositive
    assert gap[3] == pytest.approx(math.log10(1000.0))
    assert not np.isfinite(gap[4])                    # first event of author b
    assert gap[5] == pytest.approx(math.log10(10.0))
    assert not np.isfinite(cache["ev_score"][2])      # the missing score
    assert cache["ev_score"][1] == pytest.approx(-math.log1p(2.0))
    assert cache["ev_volume"][0] == pytest.approx(math.log1p(3.0))


def test_the_five_relations_are_the_registered_ones():
    assert [r.key for r in MOD.RELATIONS] == ["R1", "R2", "R3", "R4", "R5"]
    assert [(r.x, r.y) for r in MOD.RELATIONS] == [
        ("common", "volume"), ("gap", "volume"), ("volume", "score"),
        ("common", "score"), ("common", "gap")]
    assert MOD.RELATIONS[0].imported and not any(
        r.imported for r in MOD.RELATIONS[1:])
    assert MOD.NEW_RELATIONS == ("R2", "R3", "R4", "R5")


# ---------------------------------------------------------------------------
# 4. #90 — the precision ceilings, BOTH directions
# ---------------------------------------------------------------------------


def test_ceiling_clause_is_informative_when_the_spread_is_inside_the_floor():
    clause = MOD.ceiling_clause("toy", 0.004, 0.02)
    assert clause["informative"] and clause["status"] == "INFORMATIVE"


def test_ceiling_clause_is_uninformative_when_the_spread_exceeds_the_floor():
    clause = MOD.ceiling_clause("toy", 0.165, 0.02)
    assert not clause["informative"]
    assert clause["status"] == "UNINFORMATIVE"
    assert "stops" in clause["note"]
    assert not MOD.ceiling_clause("toy", float("nan"), 0.02)["informative"]


def _toy_gate(tmp_path, seed, routes_ownership=True):
    sk, _, _ = toy_skeleton(random_authors(500, 30, seed=seed))
    log = MOD.RunLog(tmp_path / "gate.jsonl")
    return MOD.relation_gate(sk, b_perm=99, b_boot=200,
                             seed=MOD.SEED_PART0, log=log,
                             routes_ownership=routes_ownership)


def test_an_uninformative_ceiling_stops_the_leg(tmp_path):
    """#90, the stopping direction: a small skeleton cannot resolve the
    planted Delta at the registered floor, so the clause is UNINFORMATIVE and
    the ROUTING gate FAILS — the leg would A1-stop."""

    gate = _toy_gate(tmp_path, seed=23)
    assert gate["ceilings"]["delta"]["replicate_sd"] > MOD.TOL_FLOOR_DELTA
    assert gate["ceilings"]["delta"]["status"] == "UNINFORMATIVE"
    uninformative = [c for c in gate["routing"]
                     if c["status"] == "UNINFORMATIVE"]
    assert uninformative and gate["status"] == "FAIL"
    verdict = MOD.build_verdict({"R2": gate}, {"route": "unused"}, {})
    assert verdict["cell"] == MOD.ATLAS_A1_STOP
    assert verdict["failed_relations"] == ["R2"]


def test_an_informative_ceiling_lets_the_gate_pass(tmp_path, monkeypatch):
    """#90, the passing direction: with the ceilings set where the design can
    meet them, every routing clause reads PASS and the gate certifies."""

    monkeypatch.setattr(MOD, "TOL_FLOOR_DELTA", 1.0)
    monkeypatch.setattr(MOD, "TOL_FLOOR_RHO", 1.0)
    gate = _toy_gate(tmp_path, seed=23)
    assert all(c["informative"] for c in gate["ceilings"].values())
    assert not [c for c in gate["routing"] if c["status"] == "UNINFORMATIVE"]
    assert gate["status"] == "PASS"
    assert [c["id"] for c in gate["routing"]] == [
        "i", "ii", "ii-ceiling", "iii-owned", "iii-owned-ceiling", "iii",
        "iv", "v", "vi"]
    assert all(c["status"] == "ANNOTATED" for c in gate["descriptive"])


def test_the_ownership_recovery_clause_routes_only_where_registered(tmp_path):
    gate = _toy_gate(tmp_path, seed=29, routes_ownership=False)
    ids = [c["id"] for c in gate["routing"]]
    assert "iii-owned" not in ids and "iii-owned-ceiling" not in ids
    assert gate["routes_ownership"] is False
    # the owned worlds still ran, because #88a prices from them
    assert MOD.WORLD_OWNED in gate["worlds"]
    assert MOD.WORLD_OWNED_LOW in gate["worlds"]
    assert gate["regions"]["rho_high"]["half_width"] > 0


def test_every_gate_world_runs_the_registered_number_of_replicates(tmp_path):
    gate = _toy_gate(tmp_path, seed=31, routes_ownership=False)
    for world in (MOD.WORLD_ERGODIC, MOD.WORLD_NONERGODIC, MOD.WORLD_NULL,
                  MOD.WORLD_OWNED, MOD.WORLD_OWNED_LOW):
        assert gate["worlds"][world]["replicates"] == MOD.N_SYNTH_REPLICATES


def test_the_nonergodic_world_plants_the_derived_delta(tmp_path):
    """The identity Delta = gamma is analytic, so the planted world's mean
    must sit on it — this is the recovery the ceiling then judges."""

    gate = _toy_gate(tmp_path, seed=37, routes_ownership=False)
    world = gate["worlds"][MOD.WORLD_NONERGODIC]
    assert abs(world["delta_erg_mean"] - MOD.GAMMA_PLANT) <= \
        MOD.TOL_SD_MULT * world["delta_erg_sd"]
    ergodic = gate["worlds"][MOD.WORLD_ERGODIC]
    assert abs(ergodic["delta_erg_mean"]) <= \
        MOD.TOL_SD_MULT * ergodic["delta_erg_sd"]
    assert abs(world["delta_erg_mean"] - MOD.GAMMA_PLANT) < \
        abs(world["delta_erg_mean"])


# ---------------------------------------------------------------------------
# 5. #88a pricing and #91 ladder coherence with the EXPLICIT collapse
# ---------------------------------------------------------------------------


def priced(low_w, high_w, delta_w=0.02):
    return {"relation": "toy", "priced_utc": "2026-01-01T00:00:00Z",
            "delta": {"centre": 0.0, "half_width": delta_w},
            "rho_low": {"centre": 0.15, "half_width": low_w},
            "rho_high": {"centre": 0.50, "half_width": high_w}}


def test_region_pricing_takes_the_matched_worlds_half_widths():
    regions = MOD.price_regions(
        "R2",
        {"delta_half_width_mean": 0.019},
        {"rho_half_width_mean": 0.028, "rho_own_mean": 0.147},
        {"rho_half_width_mean": 0.021, "rho_own_mean": 0.504})
    assert regions["delta"]["half_width"] == 0.019
    assert regions["rho_low"]["half_width"] == 0.028
    assert regions["rho_high"]["half_width"] == 0.021
    assert regions["rho_low"]["matched_world"] == MOD.WORLD_OWNED_LOW
    assert regions["rho_high"]["matched_world"] == MOD.WORLD_OWNED
    assert regions["delta"]["matched_world"] == MOD.WORLD_NULL
    assert regions["priced_utc"].endswith("Z")


def test_ladder_is_coherent_when_the_priced_regions_are_a_ladder():
    ladder = MOD.ladder_coherence(priced(0.03, 0.025))
    assert ladder["coherent"] and ladder["status"] == "COHERENT"
    assert ladder["classification"] == "LADDER"
    assert ladder["failed_conditions"] == []
    assert ladder["edges"] == pytest.approx([0.12, 0.18, 0.475, 0.525])


def test_ladder_collapses_when_the_regions_overlap():
    ladder = MOD.ladder_coherence(priced(0.38, 0.18))   # X4's own pricing
    assert not ladder["coherent"]
    assert ladder["status"] == "COLLAPSED_TO_BINARY"
    assert "regions_disjoint" in ladder["failed_conditions"]
    assert "weakly_owned_nonempty" in ladder["failed_conditions"]
    assert "COLLAPSES EXPLICITLY" in ladder["note"]


def test_ladder_collapses_when_the_low_region_reaches_through_zero():
    ladder = MOD.ladder_coherence(priced(0.16, 0.02))
    assert not ladder["coherent"]
    assert ladder["failed_conditions"] == ["not_owned_side_nonempty"]


def test_ladder_collapses_on_a_degenerate_half_width():
    ladder = MOD.ladder_coherence(priced(0.0, 0.02))
    assert not ladder["coherent"]
    assert "half_widths_positive" in ladder["failed_conditions"]


@pytest.mark.parametrize("rho,expected", [
    (0.05, MOD.CELL_NOT_OWNED),
    (0.15, MOD.CELL_AT_LOW),
    (0.30, MOD.CELL_WEAK),
    (0.50, MOD.CELL_AT_HIGH),
    (0.80, MOD.CELL_STRONG),
])
def test_the_priced_ladder_cells_when_coherent(rho, expected):
    regions = priced(0.03, 0.025)
    ladder = MOD.ladder_coherence(regions)
    assert MOD.rho_cell(rho, [rho - 0.01, rho + 0.01], regions,
                        ladder) == expected


@pytest.mark.parametrize("rho,ci,expected", [
    (0.30, [0.20, 0.40], MOD.CELL_OWNED_BINARY),
    (0.80, [0.70, 0.90], MOD.CELL_OWNED_BINARY),
    (0.05, [-0.02, 0.12], MOD.CELL_NOT_OWNED_BINARY),
    (-0.20, [-0.30, -0.10], MOD.CELL_NOT_OWNED_BINARY),
])
def test_the_collapse_is_the_stated_binary_and_nothing_else(rho, ci, expected):
    regions = priced(0.38, 0.18)
    ladder = MOD.ladder_coherence(regions)
    assert not ladder["coherent"]
    assert MOD.rho_cell(rho, ci, regions, ladder) == expected


def test_null_first_holds_in_both_classification_modes():
    for regions in (priced(0.03, 0.025), priced(0.38, 0.18)):
        ladder = MOD.ladder_coherence(regions)
        cell = MOD.rho_cell(0.30, [-0.05, 0.65], regions, ladder)
        assert cell in (MOD.CELL_NOT_OWNED, MOD.CELL_NOT_OWNED_BINARY)


def test_classify_records_which_classification_was_used():
    result = {
        "relation": "R2", "cohort": "disjoint", "label": "toy",
        "beta_between": 0.08, "beta_within": 0.06, "delta_erg": 0.02,
        "boot": {"delta_ci": [0.01, 0.03]}, "delta_ci_covers_zero": False,
        "beta_between_detected": True, "beta_within_detected": True,
        "rho_own": 0.30, "rho_ci": [0.28, 0.32], "rho_ci_covers_zero": False,
        "ownership_null": {"band": [-0.02, 0.02]},
        "census": {"authors": 10, "usable_events": 100},
    }
    coherent = MOD.classify(result, {"regions": priced(0.03, 0.025),
                                     "ladder": MOD.ladder_coherence(
                                         priced(0.03, 0.025))})
    assert coherent["ownership_classification"] == "LADDER"
    assert coherent["rho_cell"] == MOD.CELL_WEAK
    assert coherent["delta_cell"] == MOD.CELL_SAME_SIGN
    collapsed = MOD.classify(result, {"regions": priced(0.38, 0.18),
                                      "ladder": MOD.ladder_coherence(
                                          priced(0.38, 0.18))})
    assert collapsed["ownership_classification"] == "BINARY"
    assert collapsed["rho_cell"] == MOD.CELL_OWNED_BINARY
    assert collapsed["rho_region_edges_straddled"] == []


def test_the_delta_ladder_still_needs_both_slopes_detected_for_a_flip():
    base = {"delta_ci_covers_zero": False, "beta_between": 0.07,
            "beta_within": -0.01}
    assert MOD.delta_cell({**base, "beta_between_detected": True,
                           "beta_within_detected": True}) == MOD.CELL_SIGN_FLIP
    assert MOD.delta_cell({**base, "beta_between_detected": True,
                           "beta_within_detected": False}) == \
        MOD.CELL_SIGN_UNRESOLVED
    assert MOD.delta_cell({**base, "delta_ci_covers_zero": True,
                           "beta_between_detected": True,
                           "beta_within_detected": True}) == MOD.CELL_INDIST


# ---------------------------------------------------------------------------
# 6. the R1 import
# ---------------------------------------------------------------------------


def test_the_import_check_is_a_bit_check_not_an_approximation():
    imported = {"x4_floored_rho_own": 0.276816343318229,
                "x4_floored_authors": 7986}
    exact = {"rho_own": 0.276816343318229, "census": {"authors": 7986}}
    assert MOD.r1_import_check(exact, imported)["status"] == "PASS"
    off = {"rho_own": 0.276816343318229 + 1e-9, "census": {"authors": 7986}}
    assert MOD.r1_import_check(off, imported)["status"] == "FAIL"
    wrong_n = {"rho_own": 0.276816343318229, "census": {"authors": 7985}}
    assert MOD.r1_import_check(wrong_n, imported)["status"] == "FAIL"
    assert MOD.X4_IMPORT_TOL == 1e-12


@needs_x4_artifacts
def test_r1_levels_are_x4s_committed_numbers_unchanged():
    cells = json.loads((X4_ARTIFACTS / "cells.json").read_text())
    for cohort, arm in (("disjoint", "primary"), ("big5", "big5")):
        imported = MOD.import_r1_levels(cohort)
        assert imported["delta_erg"] == cells[arm]["delta_erg"]
        assert imported["beta_between"] == cells[arm]["beta_between"]
        assert imported["beta_within"] == cells[arm]["beta_within"]
        assert imported["boot"]["delta_ci"] == cells[arm]["delta_ci"]
        assert imported["delta_cell_x4"] == cells[arm]["delta_cell"]
        assert imported["imported"] is True


@needs_x4_artifacts
def test_r1_inherits_x4s_gate_and_x4s_FLOORED_pricing():
    gate = MOD.imported_r1_gate()
    x4 = json.loads((X4_ARTIFACTS / "part0_gate.json").read_text())
    ann = x4["regions"]["annotation_precision_floored"]
    assert gate["status"] == x4["status"] == "PASS"
    assert gate["regions"]["rho_low"]["half_width"] == ann["rho_low_half_width"]
    assert gate["regions"]["rho_high"]["half_width"] == \
        ann["rho_high_half_width"]
    assert gate["regions"]["delta"]["half_width"] == \
        x4["regions"]["delta"]["half_width"]
    assert gate["regions"]["priced_utc"] == x4["regions"]["priced_utc"]
    # the floored worlds are the ones matched to X5's estimator, and they
    # price a ladder the unfloored ones could not
    assert MOD.ladder_coherence(gate["regions"])["coherent"]
    assert not MOD.ladder_coherence({
        "rho_low": x4["regions"]["rho_low"],
        "rho_high": x4["regions"]["rho_high"]})["coherent"]


def test_the_runner_does_not_recompute_the_imported_levels():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "with_levels=not spec.imported" in src
    assert "levels = three_levels(mom) if with_levels else {}" in src


# ---------------------------------------------------------------------------
# 7. the atlas routes, the plateau PREDICTION, the leans
# ---------------------------------------------------------------------------


def atlas_cells(cell_by_relation, rho=0.3):
    cells = {}
    for key, cell in cell_by_relation.items():
        cells[f"{key}:disjoint"] = {"delta_cell": cell, "rho_own": rho,
                                    "rho_ci": [rho - 0.02, rho + 0.02]}
    return cells


def test_atlas_route_one_is_the_uniform_ergodic_null():
    cells = atlas_cells({k: MOD.CELL_INDIST for k in
                         ("R1", "R2", "R3", "R4", "R5")})
    summary = MOD.atlas_summary(cells, "disjoint")
    assert summary["route"] == MOD.ATLAS_UNIFORM_ERGODIC
    assert summary["all_levels_indistinguishable"]


def test_atlas_route_two_needs_one_shared_nonergodic_cell():
    cells = atlas_cells({k: MOD.CELL_SAME_SIGN for k in
                         ("R1", "R2", "R3", "R4", "R5")})
    summary = MOD.atlas_summary(cells, "disjoint")
    assert summary["route"] == MOD.ATLAS_UNIFORM_NONERGODIC
    assert summary["all_in_one_nonergodic_cell"]


def test_all_nonergodic_but_in_different_cells_is_heterogeneous():
    """The recorded refinement: five relations spread over two nonergodic
    cells is a map WITH structure, and the literal predicate is kept."""

    cells = atlas_cells({"R1": MOD.CELL_SIGN_FLIP, "R2": MOD.CELL_SAME_SIGN,
                         "R3": MOD.CELL_SAME_SIGN, "R4": MOD.CELL_SAME_SIGN,
                         "R5": MOD.CELL_SAME_SIGN})
    summary = MOD.atlas_summary(cells, "disjoint")
    assert summary["route"] == MOD.ATLAS_HETEROGENEOUS
    assert summary["all_nonergodic_literal"]
    assert not summary["all_in_one_nonergodic_cell"]


def test_atlas_route_three_on_a_mixed_map():
    cells = atlas_cells({"R1": MOD.CELL_SIGN_FLIP, "R2": MOD.CELL_INDIST,
                         "R3": MOD.CELL_INDIST, "R4": MOD.CELL_SIGN_UNRESOLVED,
                         "R5": MOD.CELL_SAME_SIGN})
    summary = MOD.atlas_summary(cells, "disjoint")
    assert summary["route"] == MOD.ATLAS_HETEROGENEOUS
    assert summary["n_distinct_cells"] == 4
    assert not summary["all_nonergodic_literal"]


def test_the_plateau_prediction_is_scored_on_the_registered_band():
    cells = {}
    for key, rho in (("R2", 0.26), ("R3", 0.29), ("R4", 0.41), ("R5", 0.10)):
        cells[f"{key}:disjoint"] = {"rho_own": rho,
                                    "rho_ci": [rho - 0.02, rho + 0.02],
                                    "delta_cell": MOD.CELL_INDIST}
    plateau = MOD.plateau_prediction(cells)
    assert plateau["band"] == [0.25, 0.30]
    assert plateau["n_relations_in_band"] == 2
    assert plateau["held"] and plateau["status"] == "HELD"
    cells["R3:disjoint"]["rho_own"] = 0.45
    cells["R3:disjoint"]["rho_ci"] = [0.43, 0.47]
    broken = MOD.plateau_prediction(cells)
    assert broken["n_relations_in_band"] == 1
    assert broken["status"] == "BROKEN"


def test_the_plateau_band_is_the_one_the_bridge_named():
    assert MOD.PLATEAU_BAND == (0.25, 0.30)
    assert MOD.PLATEAU_MIN_RELATIONS == 2
    for value in (0.279, 0.259, 0.277):
        assert MOD.PLATEAU_BAND[0] <= value <= MOD.PLATEAU_BAND[1]


def test_leans_score_every_registered_lean_and_keep_r5_unleaned():
    cells = {}
    for key in ("R1", "R2", "R3", "R4", "R5"):
        cells[f"{key}:disjoint"] = {
            "delta_cell": MOD.CELL_SAME_SIGN, "beta_between": 0.05,
            "beta_within": 0.02, "rho_own": 0.27,
            "rho_ci": [0.25, 0.29]}
    summary = MOD.atlas_summary(cells, "disjoint")
    plateau = MOD.plateau_prediction(cells)
    rows = MOD.evaluate_leans(cells, summary, plateau)
    assert len(rows) == 9
    statuses = [row["status"] for row in rows]
    assert statuses.count("N/A — REGISTERED UNLEANED") == 1
    assert rows[0]["status"] == "HELD"       # R2 beta_within > 0
    assert rows[1]["status"] == "HELD"       # R2 SAME_SIGN
    assert rows[-1]["status"] == "HELD"      # the plateau, 4 of 4 in band
    assert any("ATLAS_HETEROGENEOUS" in row["lean"] for row in rows)


def test_flags_73_fires_on_a_cohort_divergence():
    cells = {}
    for key in ("R1", "R2", "R3", "R4", "R5"):
        for cohort, cell in (("disjoint", MOD.CELL_SAME_SIGN),
                             ("big5", MOD.CELL_SAME_SIGN)):
            cells[f"{key}:{cohort}"] = {
                "relation": key, "cohort": cohort, "delta_cell": cell,
                "delta_erg": 0.05, "delta_ci": [0.01, 0.09],
                "delta_is_straddle": False, "rho_cell": MOD.CELL_WEAK,
                "rho_own": 0.3, "rho_ci": [0.2, 0.4],
                "rho_is_straddle": False}
    assert MOD.flags_73(cells) == []
    cells["R3:big5"]["delta_cell"] = MOD.CELL_INDIST
    flags = MOD.flags_73(cells)
    assert len(flags) == 1 and flags[0]["relation"] == "R3"
    assert "the disjoint cohort routes" in flags[0]["note"]


def test_build_verdict_routes_on_the_disjoint_atlas():
    gates = {key: {"status": "PASS"} for key in
             ("R1", "R2", "R3", "R4", "R5")}
    cells = atlas_cells({"R1": MOD.CELL_SIGN_FLIP, "R2": MOD.CELL_INDIST,
                         "R3": MOD.CELL_INDIST, "R4": MOD.CELL_INDIST,
                         "R5": MOD.CELL_SAME_SIGN})
    for cell in cells.values():
        cell["rho_cell"] = MOD.CELL_WEAK
    summary = MOD.atlas_summary(cells, "disjoint")
    verdict = MOD.build_verdict(gates, summary, cells)
    assert verdict["cell"] == MOD.ATLAS_HETEROGENEOUS
    assert verdict["ownership_by_relation"]["R5"] == MOD.CELL_WEAK
    gates["R4"]["status"] = "FAIL"
    assert MOD.build_verdict(gates, summary, cells)["cell"] == MOD.ATLAS_A1_STOP


# ---------------------------------------------------------------------------
# 8. registration pins, blocking anchors, governance, #83
# ---------------------------------------------------------------------------


def test_registration_pins():
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499
    assert MOD.B_BOOT == 1000
    assert MOD.POOL_FLOOR_EVENTS == 50
    assert MOD.ESTIMABILITY_FLOOR_DEN == 1.0
    assert MOD.N_SYNTH_REPLICATES == 8
    assert MOD.ERGODIC_COVER_FLOOR == 6
    assert MOD.TOL_SD_MULT == 3.0
    assert MOD.TOL_FLOOR_RHO == 0.02
    assert MOD.BOUNDARY_RHO_LOW == 0.15
    assert MOD.BOUNDARY_RHO_HIGH == 0.50
    assert MOD.BOUNDARY_DELTA_CENTRE == 0.0
    assert MOD.RHO_TRUE_TARGET == 0.50


def test_blocking_anchors_match_the_registration_text():
    text = PLAN.read_text(encoding="utf-8")
    section = text[text.index("## X5 — the ergodicity atlas"):]
    for token in ("7,989", "1,100", "8,008", "1,116", "7,986", "1,096",
                  "7,966", "1,081", "1.138", "1.031", "0.966", "147",
                  "17,640,062", "8,004", "1,112"):
        assert token in section, token
    assert MOD.ANCHOR_POOL == {"R1": (8_004, 1_112), "R2": (7_989, 1_100),
                               "R3": (8_008, 1_116), "R4": (7_986, 1_096),
                               "R5": (7_966, 1_081)}
    assert MOD.ANCHOR_SDX_MEDIAN_DISJOINT == {"R2": 1.138, "R3": 1.031,
                                              "R4": 0.966, "R5": 0.966}
    assert MOD.ANCHOR_SCORE_MISSING == 147
    assert MOD.ANCHOR_ROWS_PARSEABLE == 17_640_062
    assert MOD.ANCHOR_AUTHORS == (MOD.ANCHOR_BIG5_AUTHORS
                                  + MOD.ANCHOR_DISJOINT_AUTHORS) == 10_296
    assert MOD.ANCHOR_COMMUNITIES == 46_214
    assert (MOD.ANCHOR_X_MIN, MOD.ANCHOR_X_MAX) == (-7.25, -1.14)


def test_anchor_gate_is_blocking_and_exact():
    assert MOD.anchor_gate({"a": 1}, {"a": 1})["status"] == "PASS"
    assert MOD.anchor_gate({"a": 1.0001}, {"a": 1.0})["status"] == "FAIL"
    assert MOD.anchor_gate({}, {"a": 1})["status"] == "FAIL"


def test_inherited_machinery_is_the_x4_object_not_a_copy():
    """#56/#81: the names are BOUND to the committed X4 module, not copied."""

    assert Path(MOD.X4.__file__).resolve() == X4_SCRIPT.resolve()
    for name in ("three_levels", "cell_moments", "per_cell_slopes",
                 "paired_level_bootstrap", "dispersion",
                 "ownership_slope_target", "run_world", "delta_cell",
                 "edges_straddled", "community_x", "ownership_null",
                 "cluster_bootstrap_pairs", "rowwise_pearson",
                 "order_and_halve", "anchor_gate", "percentile_ci",
                 "scan_for_cohort_ids", "baseline_hit_keys", "new_hits_only",
                 "write_json", "utc_now", "fmt", "fmt_ci"):
        assert getattr(MOD, name) is getattr(MOD.X4, name), name
    assert MOD.RunLog is MOD.X4.RunLog
    assert MOD.X4.percentile_ci is MOD.X4.X2.percentile_ci
    src = SCRIPT.read_text(encoding="utf-8")
    for name in ("def three_levels", "def cell_moments", "def write_json",
                 "def percentile_ci", "def anchor_gate", "class RunLog",
                 "def ownership_null", "def cluster_bootstrap_pairs",
                 "def order_and_halve", "def per_cell_slopes",
                 "def paired_level_bootstrap", "def run_world",
                 "def scan_for_cohort_ids"):
        assert name not in src, f"X5 must not redefine {name}"


def test_id_scan_helper_finds_a_planted_name(tmp_path):
    target = tmp_path / "leak.md"
    target.write_text("the author zqxjkvbnm posted twice\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([target], ["zqxjkvbnm", "other"])[
        "n_hits"] == 1


def test_id_scan_helper_ignores_short_names_and_substrings(tmp_path):
    target = tmp_path / "clean.md"
    target.write_text("abc defghij\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([target], ["abc"])["n_hits"] == 0
    assert MOD.scan_for_cohort_ids([target], ["defg"])["n_hits"] == 0


def test_governance_five_metadata_columns_no_bodies_no_labels():
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"score"' in src and '"word_count_quoteless"' in src
    assert '"body"' not in src
    columns = ["author", "subreddit", "created_utc", "word_count_quoteless",
               "score"]
    assert all(f'"{column}"' in src for column in columns)
    # every mention of the label file is a statement that it is not opened
    for line in src.splitlines():
        if "author_profiles" in line:
            assert "NEVER" in line or "never" in line, line
    # the only file the runner reads with pandas is the comments stream and
    # the cohort NAME LIST
    reads = [line for line in src.splitlines() if "read_csv" in line]
    assert len(reads) == 2
    assert any("args.cohort" in line for line in reads)
    assert 'usecols=["author"]' in src          # the cohort NAME LIST only
    assert "usecols=columns" in src             # the five metadata columns


def test_committed_files_are_exactly_the_scanned_set():
    names = {path.name for path in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_X5_ERGODICITY_ATLAS_REPORT.md",
                     "run_suica_m4_x5_ergodicity_atlas.py",
                     "test_m4_x5_ergodicity_atlas.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_boundaries_carry_the_registered_cautions():
    text = " ".join(MOD.BOUNDARIES)
    for token in ("VOLUME, TIMING and PLATFORM FEEDBACK", "never content",
                  "platform feedback, not quality", "projection caution",
                  "No psychological naming", "EXPLORATORY, corpus-level",
                  "cohort-selection caveat", "Pool selection",
                  "Saegusa & Geshi (2025)", "author_profiles.csv"):
        assert token in text, token


# ---------------------------------------------------------------------------
# 9. the artifacts of the run (skipped in a fresh clone: results/ is ignored)
# ---------------------------------------------------------------------------


@needs_artifacts
def test_census_artifact_passed_every_blocking_anchor():
    census = json.loads((ARTIFACTS / "census.json").read_text())
    assert census["status"] == "PASS"
    for pin in census["pins"].values():
        assert pin["status"] == "PASS"
    for key, (disjoint, big5) in MOD.ANCHOR_POOL.items():
        if key == "R1":
            assert census["pins"]["R1 pool, X4's sd(x) > 0 path, disjoint"][
                "observed"] == disjoint
            continue
        assert census["relations"][key]["pool_disjoint"] == disjoint
        assert census["relations"][key]["pool_big5"] == big5


@needs_artifacts
def test_every_relation_gate_passed_with_informative_ceilings():
    gates = json.loads((ARTIFACTS / "part0_gate.json").read_text())
    assert set(gates) == {"R1", "R2", "R3", "R4", "R5"}
    for key, gate in gates.items():
        assert gate["status"] == "PASS", key
        assert all(c["status"] == "PASS" for c in gate["routing"]), key
        for ceiling in gate.get("ceilings", {}).values():
            assert ceiling["status"] == "INFORMATIVE", key
            assert ceiling["replicate_sd"] <= ceiling["ceiling"]
    assert gates["R2"]["routes_ownership"] is True
    assert all(not gates[k]["routes_ownership"] for k in
               ("R1", "R3", "R4", "R5"))


@needs_artifacts
def test_every_relation_priced_its_own_regions_before_the_first_number():
    pricing = json.loads((ARTIFACTS / "region_pricing.json").read_text())
    ordering = json.loads((ARTIFACTS / "ordering.json").read_text())
    assert ordering["status"] == "PASS"
    for key, block in pricing.items():
        assert block["regions"]["priced_utc"] < \
            ordering["first_real_number_utc"], key
        for edge in ("delta", "rho_low", "rho_high"):
            assert block["regions"][edge]["half_width"] > 0
        assert block["ladder"]["status"] in ("COHERENT",
                                             "COLLAPSED_TO_BINARY")
    assert (ARTIFACTS / "region_pricing.json").stat().st_mtime <= \
        (ARTIFACTS / "arms.json").stat().st_mtime


@needs_artifacts
def test_the_atlas_artifact_and_the_verdict_agree():
    atlas = json.loads((ARTIFACTS / "atlas.json").read_text())
    verdict = json.loads((ARTIFACTS / "verdict.json").read_text())
    assert verdict["cell"] == atlas["disjoint"]["route"]
    assert verdict["cell"] in (MOD.ATLAS_UNIFORM_ERGODIC,
                               MOD.ATLAS_UNIFORM_NONERGODIC,
                               MOD.ATLAS_HETEROGENEOUS)
    cells = json.loads((ARTIFACTS / "cells.json").read_text())
    for key, cell in atlas["disjoint"]["cells_by_relation"].items():
        assert cells[f"{key}:disjoint"]["delta_cell"] == cell


@needs_artifacts
def test_every_arm_carries_the_three_levels_and_its_own_nulls():
    arms = json.loads((ARTIFACTS / "arms.json").read_text())
    assert len(arms) == 10
    for key, arm in arms.items():
        assert arm["ownership_null"]["b"] == MOD.B_PERM, key
        assert arm["ownership_boot"]["b"] == MOD.B_BOOT, key
        assert arm["boot"]["b"] == MOD.B_BOOT, key
        for field in ("beta_between", "beta_within", "delta_erg", "rho_own"):
            assert math.isfinite(arm[field]), (key, field)
    for cohort in ("disjoint", "big5"):
        assert arms[f"R1:{cohort}"]["imported"] is True


@needs_artifacts
def test_the_r1_import_bit_check_passed_on_the_fresh_cache():
    payload = json.loads((ARTIFACTS / "report_payload.json").read_text())
    check = payload["r1_import_check"]
    assert check["status"] == "PASS"
    assert check["abs_difference"] == 0.0
    assert check["authors_x5"] == check["authors_x4"] == 7986


@needs_artifacts
def test_the_report_carries_the_atlas_the_plateau_and_the_bridge_citation():
    text = REPORT.read_text(encoding="utf-8")
    verdict = json.loads((ARTIFACTS / "verdict.json").read_text())
    plateau = json.loads((ARTIFACTS / "plateau.json").read_text())
    assert f"**Verdict: `{verdict['cell']}`**" in text
    assert "## THE ATLAS" in text
    for key in ("R1", "R2", "R3", "R4", "R5"):
        assert f"**{key}**" in text
    assert "Saegusa & Geshi 2025" in text
    assert "三枝高大・下司忠大 (2025)" in text
    assert f"**Outcome: `{plateau['status']}`**" in text
    assert "build-out" in text
    assert "## Honest anomalies" in text
    assert "## Boundaries" in text


@needs_artifacts
def test_the_id_leak_scan_passed_with_only_the_head_collisions():
    scan = json.loads((ARTIFACTS / "id_leak_scan.json").read_text())
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS


@needs_artifacts
def test_the_floor_effect_artifact_quotes_both_legs():
    effect = json.loads((ARTIFACTS / "floor_effect.json").read_text())
    assert effect["var_beta_R1_disjoint"]["x4_unfloored"] < 0
    assert effect["var_beta_R1_disjoint"]["x5_floored"] > 0
    assert effect["owned_world_rho_replicate_sd"]["x4_unfloored"] > \
        MOD.TOL_FLOOR_RHO
    assert effect["owned_world_rho_replicate_sd"]["x5_floored_max"] <= \
        MOD.TOL_FLOOR_RHO
    assert effect["ladders_coherent"] == effect["ladders_total"] == 5
