"""Contract tests for SUICA M4-X-M — the mains estimator.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X-M", commit d65e818) makes this leg R1-class: it issues instrument
certificates and nothing else, so the objects that have to be pinned by
contract are the instrument's own:

1. the FE COEFFICIENTS — X1b threw the group means away as it removed them;
   this leg keeps them, and the kept object must reproduce X1b's residual
   exactly, decompose the input exactly, and satisfy X1b's tightened
   stopping rule;
2. the PINNED NORMALIZATION — a projection's coefficients are identified only
   up to one gauge parameter, so the registered centring sequence is tested
   for what a normalization has to be: confluent (its own two steps commute),
   and invariant to which side the alternating projection started from;
3. the DF DERIVATION — the mains carry NO residual-df shrinkage and exactly
   one mean-removal factor, and both halves of that claim are checked, the
   second against simulation;
4. the LEAKAGE BATTERY — the #85 zero-point family for mains, run on toys so
   the property is pinned without the corpus, including the
   counterfactual that the marginal estimator fails it;
5. the BOOTSTRAP-FE EQUIVALENCE — X1b's weighted-projection pattern: an
   author drawn m times is the same object as an author whose slots appear m
   times, and the test builds both;
6. the ANCHORS and the #83 helper.

Everything inherited (the predicate chain, the exact FE, X1c's df correction
for the interaction, the synthetic world builder) is covered by
``test_m4_x1b_venue_response_fe`` and ``test_m4_x1c_venue_response``; it is
re-checked here only where this leg's wrapper could break the binding.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_xm_mains_estimator.py"
X1C_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1c_venue_response.py"
X1B_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
ARTIFACTS = ROOT / "results" / "m4_xm_mains_estimator"
REPORT = ROOT / "reports" / "SUICA_M4_XM_MAINS_ESTIMATOR_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X1c recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_xm_mains_estimator", SCRIPT)


# ---------------------------------------------------------------------------
# helpers — small connected skeletons, no corpus needed
# ---------------------------------------------------------------------------


def _skeleton(n_authors=140, n_comms=18, k=5, seed=11, ragged=True):
    """A connected author x community skeleton with UNEQUAL cell sizes.

    Cell sizes must be unequal AND correlated across halves (a busy venue is
    busy in both halves), because that is what makes the size weights bite:
    an equal-cell skeleton would let a wrong community weighting pass.
    """

    rng = np.random.default_rng(seed)
    author, comm = [], []
    for u in range(n_authors):
        picks = rng.choice(n_comms, size=k, replace=False)
        author.extend([u] * k)
        comm.extend(picks.tolist())
    sa = np.array(author, dtype=np.int64)
    sc = np.array(comm, dtype=np.int64)
    if ragged:
        base = rng.lognormal(3.2, 0.9, sa.size)
        n_e = np.maximum(10.0, np.round(base * rng.uniform(0.75, 1.25,
                                                           sa.size)))
        n_l = np.maximum(10.0, np.round(base * rng.uniform(0.75, 1.25,
                                                           sa.size)))
    else:
        n_e = np.full(sa.size, 20.0)
        n_l = np.full(sa.size, 20.0)
    zeros = np.zeros(sa.size)
    design = MOD.Design(slot_author=sa, slot_comm=sc, n_e=n_e, n_l=n_l,
                        s_e=zeros.copy(), s_l=zeros.copy(),
                        q_e=zeros.copy(), q_l=zeros.copy(),
                        n_authors=n_authors, n_comms=n_comms,
                        author_codes=np.arange(n_authors, dtype=np.int64))
    lcc = MOD.bipartite_lcc(sa, sc, n_authors, n_comms)
    assert lcc["lcc_author_coverage"] == 1.0, "the toy skeleton must connect"
    return design


def _values(design, seed=5):
    rng = np.random.default_rng(seed)
    return rng.normal(3.0, 1.0, design.n_slots)


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                            # pragma: no cover
        pytest.skip("the X-M run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. inheritance — X-M is BOUND to the committed objects (#56/#81)
# ---------------------------------------------------------------------------


INHERITED = ("Design", "fe_residual", "fe_pair", "fe_exactness",
             "recover_shares_fe", "synthetic_design", "load_cell_cache",
             "law_vocabulary", "build_chain_design", "bipartite_lcc",
             "variance_budget", "anchor_gate", "scan_for_cohort_ids",
             "new_hits_only", "baseline_hit_keys", "df_correction",
             "gate_status")


def test_the_machinery_is_imported_by_file_and_not_copied():
    assert Path(MOD.X1C.__file__).resolve() == X1C_SCRIPT.resolve()
    assert Path(MOD.X1B.__file__).resolve() == X1B_SCRIPT.resolve()
    assert MOD.X1B is MOD.X1C.X1B
    assert MOD.X1 is MOD.X1B.X1
    source = SCRIPT.read_text(encoding="utf-8")
    for name in INHERITED:
        target = getattr(MOD, name)
        owners = [mod for mod in (MOD.X1C, MOD.X1B, MOD.X1)
                  if getattr(mod, name, None) is target]
        assert owners, f"{name} is not any committed module's object"
        assert f"\ndef {name}(" not in source, name
        assert f"\nclass {name}" not in source, name


def test_the_registration_pins_are_the_inherited_ones():
    assert MOD.SEED == MOD.X1B.SEED == 20260819
    assert MOD.SEED_PART0 == MOD.SEED + 1
    assert MOD.SEED_BOOT == MOD.SEED + 3
    assert MOD.B_BOOT == 1000
    assert MOD.N_SYNTH_REPLICATES == 8
    assert MOD.FE_TOL == 1e-10
    assert MOD.N_MIN_PRIMARY == 10
    assert MOD.S_PRIMARY == 5
    assert MOD.K_MIN == 3
    assert MOD.LEAK_MAX == 0.005
    assert MOD.TOL_SD_MULT == 3.0


def test_the_registered_worlds_are_the_five_the_plan_names():
    assert set(MOD.WORLDS) == {"a_only", "b_only", "g_only", "null", "full"}
    assert MOD.WORLDS["a_only"] == {"author": 0.30, "community": 0.0,
                                    "interaction": 0.0}
    assert MOD.WORLDS["b_only"] == {"author": 0.0, "community": 0.08,
                                    "interaction": 0.0}
    assert MOD.WORLDS["g_only"] == {"author": 0.0, "community": 0.0,
                                    "interaction": 0.02}
    assert MOD.WORLDS["null"] == {"author": 0.0, "community": 0.0,
                                  "interaction": 0.0}
    assert MOD.WORLDS["full"] == {"author": 0.30, "community": 0.08,
                                  "interaction": 0.02}
    # the seed offsets X1b already fixed are REUSED, not re-chosen (#76)
    assert MOD.WORLD_SEED_OFFSET["a_only"] == 13
    assert MOD.WORLD_SEED_OFFSET["b_only"] == 19
    assert MOD.WORLD_SEED_OFFSET["null"] == 7
    assert MOD.WORLD_SEED_OFFSET["full"] == 0
    assert len(set(MOD.WORLD_SEED_OFFSET.values())) == 5


def test_the_resolution_floor_is_a_ceiling_too():
    """#92 states the floor in estimand units; #90 reads it as a ceiling."""

    assert MOD.RESOLUTION_SHARE == 0.01
    assert MOD.CEILING_REPLICATE_SD == MOD.RESOLUTION_SHARE


# ---------------------------------------------------------------------------
# 2. the FE coefficients — exactness, and X1b's residual reproduced
# ---------------------------------------------------------------------------


def test_the_coefficient_fit_reproduces_x1bs_residual_bit_for_bit():
    """The kept object must not change the object X1b already certified."""

    design = _skeleton()
    y = _values(design)
    a_acc, c_acc, v, sweeps, change = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    v_ref, sweeps_ref, change_ref = MOD.fe_residual(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    assert sweeps == sweeps_ref
    assert change == change_ref
    assert np.array_equal(v, v_ref)


def test_the_decomposition_is_exact():
    design = _skeleton()
    y = _values(design)
    a_acc, c_acc, v, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    rebuilt = a_acc[design.slot_author] + c_acc[design.slot_comm] + v
    assert np.abs(y - rebuilt).max() < 1e-12


def test_fe_exactness_is_re_asserted_on_both_group_means():
    """X1b's tightened stopping rule: BOTH residual group means <= tol."""

    design = _skeleton()
    coefs = MOD.fitted_coefficients(
        MOD.synthetic_design(design, MOD.WORLDS["full"],
                             np.random.default_rng(3)))
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(3))
    exact = MOD.fe_exactness(world, coefs["v_e"], coefs["v_l"])
    assert max(exact.values()) <= MOD.FE_TOL
    assert coefs["change_early"] <= MOD.FE_TOL
    assert coefs["change_late"] <= MOD.FE_TOL


def test_the_projection_recovers_a_planted_author_vector_exactly():
    """With no noise and no community effect, a_hat IS a - mean(a)."""

    design = _skeleton()
    rng = np.random.default_rng(17)
    a = rng.normal(0.0, 1.0, design.n_authors)
    b = rng.normal(0.0, 0.7, design.n_comms)
    y = 4.5 + a[design.slot_author] + b[design.slot_comm]
    a_acc, c_acc, v, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    mu, a_hat, b_hat = MOD.normalize_coefficients(a_acc, c_acc)
    assert np.abs(a_hat - (a - a.mean())).max() < 1e-8
    assert np.abs(b_hat - (b - b.mean())).max() < 1e-8
    assert mu == pytest.approx(4.5 + a.mean() + b.mean(), abs=1e-8)
    assert np.abs(v).max() < 1e-8


# ---------------------------------------------------------------------------
# 3. the PINNED normalization — the leg's genuinely new risk
# ---------------------------------------------------------------------------


def test_the_normalization_centres_both_sides_and_conserves_the_fit():
    design = _skeleton()
    y = _values(design, seed=9)
    a_acc, c_acc, v, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    mu, a_hat, b_hat = MOD.normalize_coefficients(a_acc, c_acc)
    assert abs(float(a_hat.mean())) < 1e-12
    assert abs(float(b_hat.mean())) < 1e-12
    rebuilt = mu + a_hat[design.slot_author] + b_hat[design.slot_comm] + v
    assert np.abs(y - rebuilt).max() < 1e-12


def test_the_pinned_sequence_is_confluent():
    """Step 3 cannot undo step 2: the two centrings touch disjoint vectors.

    The registration pins the ORDER (author, then community). A normalization
    whose answer depended on its own order would identify nothing, so the
    reverse order must land on the identical triple.
    """

    design = _skeleton()
    y = _values(design, seed=21)
    a_acc, c_acc, _, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms)
    mu, a_hat, b_hat = MOD.normalize_coefficients(a_acc, c_acc)
    # the reverse sequence, written out
    mu_rev = 0.0
    b_bar = float(c_acc.mean())
    b_rev = c_acc - b_bar
    mu_rev += b_bar
    a_bar = float(a_acc.mean())
    a_rev = a_acc - a_bar
    mu_rev += a_bar
    assert mu == pytest.approx(mu_rev, abs=1e-12)
    assert np.abs(a_hat - a_rev).max() < 1e-12
    assert np.abs(b_hat - b_rev).max() < 1e-12


def test_the_normalized_coefficients_do_not_depend_on_the_fit_order():
    """The gauge is removed: starting the sweep on the community side moves
    the RAW accumulators and must not move the NORMALIZED ones."""

    design = _skeleton()
    y = _values(design, seed=33)
    a1, c1, v1, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms, order="author_first")
    a2, c2, v2, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms, order="community_first")
    # the raw split genuinely differs — otherwise the test is vacuous
    assert np.abs(a1 - a2).max() > 1e-6
    mu1, ah1, bh1 = MOD.normalize_coefficients(a1, c1)
    mu2, ah2, bh2 = MOD.normalize_coefficients(a2, c2)
    assert np.abs(ah1 - ah2).max() < 1e-8
    assert np.abs(bh1 - bh2).max() < 1e-8
    assert mu1 == pytest.approx(mu2, abs=1e-8)
    assert np.abs(v1 - v2).max() < 1e-8


def test_an_unknown_sweep_order_is_refused():
    design = _skeleton(n_authors=20, n_comms=6, k=3, seed=2)
    with pytest.raises(ValueError):
        MOD.fe_coefficients(_values(design), design.slot_author,
                            design.slot_comm, design.n_authors,
                            design.n_comms, order="whichever")


def test_the_normalization_sequence_is_printed_in_the_registered_order():
    steps = MOD.NORMALIZATION_SEQUENCE
    assert len(steps) == 4
    assert steps[0].startswith("1. FIT")
    assert "CENTRE THE AUTHOR COEFFICIENTS" in steps[1]
    assert "CENTRE THE COMMUNITY COEFFICIENTS" in steps[2]
    assert steps[3].startswith("RESULT")


# ---------------------------------------------------------------------------
# 4. the df / joint-estimation derivation
# ---------------------------------------------------------------------------


def test_the_mean_removal_factor_on_uniform_weights_is_n_over_n_minus_one():
    for n in (5, 100, 3665):
        row = MOD.mean_removal_factor(np.ones(n))
        assert row["sum_p_squared"] == pytest.approx(1.0 / n)
        assert row["factor"] == pytest.approx(n / (n - 1.0))
        assert row["effective_members"] == pytest.approx(float(n))
        assert row["members"] == n


def test_the_mean_removal_factor_reads_the_effective_sample():
    w = np.array([100.0, 1.0, 1.0, 1.0, 1.0])
    row = MOD.mean_removal_factor(w)
    p = w / w.sum()
    assert row["sum_p_squared"] == pytest.approx(float((p * p).sum()))
    assert row["effective_members"] < 2.0          # one member dominates
    assert row["members"] == 5                     # ... but five are present


def test_zero_weight_members_do_not_count_as_members():
    w = np.array([1.0, 1.0, 0.0, 0.0])
    assert MOD.mean_removal_factor(w)["members"] == 2


def test_the_mean_removal_factor_is_what_a_weighted_population_variance_loses():
    """Simulation, not assertion: E[weighted popvar] = V (1 - sum p^2)."""

    rng = np.random.default_rng(4242)
    w = rng.lognormal(0.0, 1.2, 60)
    p = w / w.sum()
    factor = MOD.mean_removal_factor(w)
    v_true = 0.37
    draws = rng.normal(0.0, np.sqrt(v_true), size=(40_000, p.size))
    m = draws @ p
    realized = (draws * draws) @ p - m * m
    assert float(realized.mean()) == pytest.approx(
        v_true * factor["retained_fraction"], rel=0.01)
    # ... and the correction puts it back
    assert float(realized.mean()) * factor["factor"] == pytest.approx(
        v_true, rel=0.01)


def test_the_mains_carry_no_residual_df_shrinkage():
    """The derivation's load-bearing claim, checked against the estimator.

    A planted author main is recovered at its planted value, NOT at the
    (P - A - C + 1)/P fraction X1c's interaction loses. On this toy the
    interaction factor is far from 1, so the two hypotheses are separable.
    """

    design = _skeleton()
    derivation = MOD.mains_df_derivation(design)
    assert derivation["residual_df_factor_applies_to_mains"] is False
    interaction_factor = derivation["interaction_factor_for_contrast"]["factor"]
    assert interaction_factor > 1.05                 # the toy separates them
    rows = []
    for rep in range(6):
        world = MOD.synthetic_design(
            design, {"author": 0.30, "community": 0.0, "interaction": 0.0},
            np.random.default_rng(900 + rep))
        rows.append(MOD.mains_budget(world)["author"])
    got = float(np.mean(rows))
    assert got == pytest.approx(0.30, abs=0.02)
    # the residual-df hypothesis would have predicted this instead:
    assert abs(got - 0.30 / interaction_factor) > 0.02


def test_the_derivation_agrees_with_x1cs_interaction_factor():
    design = _skeleton()
    derivation = MOD.mains_df_derivation(design)
    assert derivation["interaction_factor_for_contrast"] == \
        MOD.df_correction(design)


def test_the_correction_is_a_positive_affine_map_so_zero_coverage_survives():
    factor = MOD.mean_removal_factor(np.ones(50))["factor"]
    assert factor > 0
    for ci in ([-0.001, 0.002], [0.004, 0.009], [-0.01, -0.002]):
        raw_covers = ci[0] <= 0.0 <= ci[1]
        scaled = [v * factor for v in ci]
        assert (scaled[0] <= 0.0 <= scaled[1]) == raw_covers


def test_the_budget_reports_both_scales_and_they_differ_by_the_factor():
    design = _skeleton()
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(77))
    budget = MOD.mains_budget(world)
    for key in ("author", "community", "community_unweighted"):
        assert budget[key] == pytest.approx(
            budget[f"{key}_raw"] * budget[f"{key}_factor"])
        assert budget[f"{key}_factor"] > 1.0


# ---------------------------------------------------------------------------
# 5. the leakage battery, on toys
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("world", ["a_only", "b_only", "g_only", "null"])
def test_every_zero_planted_component_reads_below_the_bound_on_a_toy(world):
    """The #85 zero-point family, pinned without the corpus."""

    design = _skeleton(n_authors=400, n_comms=30, k=6, seed=8)
    shares = MOD.WORLDS[world]
    rows = [MOD.full_budget(MOD.synthetic_design(
        design, shares, np.random.default_rng(4000 + 100 * rep)))
        for rep in range(6)]
    for comp in MOD.COMPONENTS:
        if float(shares[comp]) != 0.0:
            continue
        reading = float(np.mean([row[comp] for row in rows]))
        assert abs(reading) < MOD.LEAK_MAX, (world, comp, reading)


def test_the_marginal_estimator_fails_the_same_battery_on_a_toy():
    """The #87 diagnosis, reproduced: the marginal rows are contaminated."""

    design = _skeleton(n_authors=400, n_comms=30, k=6, seed=8)
    rows = [MOD.full_budget(MOD.synthetic_design(
        design, MOD.WORLDS["b_only"], np.random.default_rng(4000 + 100 * rep)))
        for rep in range(6)]
    fe = float(np.mean([row["author"] for row in rows]))
    marginal = float(np.mean([row["marginal_author_x1c"] for row in rows]))
    assert abs(fe) < MOD.LEAK_MAX
    assert abs(marginal) > MOD.LEAK_MAX
    assert abs(marginal) > 5 * abs(fe)


def test_score_leakage_is_vacuous_where_nothing_is_planted_at_zero():
    block = {"planted": MOD.WORLDS["full"],
             "stats": {c: {"mean": 0.5} for c in MOD.COMPONENTS}}
    clause = MOD.score_leakage(block)
    assert clause["applicable"] is False
    assert clause["status"] == "N/A"
    assert clause["rows"] == {}


def test_score_leakage_fires_on_a_planted_leak():
    block = {"planted": MOD.WORLDS["b_only"],
             "stats": {"author": {"mean": 0.02},
                       "community": {"mean": 0.08},
                       "interaction": {"mean": 0.0}}}
    clause = MOD.score_leakage(block)
    assert clause["status"] == "FAIL"
    assert clause["rows"]["author"]["status"] == "FAIL"
    assert clause["rows"]["interaction"]["status"] == "PASS"
    assert "community" not in clause["rows"]         # it is planted, not zero


def test_the_marginal_counterfactual_scores_only_the_zero_rows():
    blocks = {
        "b_only": {"planted": MOD.WORLDS["b_only"],
                   "stats": {"author": {"mean": 0.00004},
                             "community": {"mean": 0.08},
                             "marginal_author_x1c": {"mean": 0.0225},
                             "marginal_community_x1c": {"mean": 0.0817}}},
        "full": {"planted": MOD.WORLDS["full"],
                 "stats": {"author": {"mean": 0.30},
                           "community": {"mean": 0.07},
                           "marginal_author_x1c": {"mean": 0.32},
                           "marginal_community_x1c": {"mean": 0.11}}},
    }
    out = MOD.marginal_counterfactual(blocks)
    assert out["n_zero_rows"] == 1                   # only b_only:author
    assert out["n_fe_failures"] == 0
    assert out["n_marginal_failures"] == 1
    assert out["marginal_failures"] == ["b_only:author"]


# ---------------------------------------------------------------------------
# 6. the #90 ceiling and the #92 resolution floor
# ---------------------------------------------------------------------------


def test_a_tight_recovery_passes():
    row = MOD.score_recovery({"mean": 0.3002, "sd": 0.003}, 0.30)
    assert row["informative"] is True
    assert row["status"] == "PASS"
    assert row["tolerance"] == MOD.RESOLUTION_SHARE  # the floor binds


def test_a_biased_recovery_fails_even_when_it_is_informative():
    row = MOD.score_recovery({"mean": 0.34, "sd": 0.003}, 0.30)
    assert row["informative"] is True
    assert row["status"] == "FAIL"


def test_a_scattered_recovery_is_uninformative_even_when_it_is_unbiased():
    """#90: a clause cannot buy a pass with its own imprecision."""

    row = MOD.score_recovery({"mean": 0.3000, "sd": 0.05}, 0.30)
    assert row["within_tolerance"] is True           # 3 x 0.05 swallows it
    assert row["informative"] is False
    assert row["status"] == "UNINFORMATIVE"
    assert row["ceiling_headroom"] < 0


def test_the_ceiling_sits_exactly_at_the_resolution_floor():
    at = MOD.score_recovery({"mean": 0.30, "sd": MOD.RESOLUTION_SHARE}, 0.30)
    over = MOD.score_recovery(
        {"mean": 0.30, "sd": MOD.RESOLUTION_SHARE * 1.001}, 0.30)
    assert at["status"] == "PASS"
    assert over["status"] == "UNINFORMATIVE"


def test_the_ceiling_power_diagnostic_matches_its_closed_form():
    design = _skeleton()
    power = MOD.ceiling_power(design, 0.08, np.ones(design.n_comms), 8, 300,
                              7)
    p = 1.0 / design.n_comms
    assert power["closed_form_draw_sd"] == pytest.approx(
        0.08 * np.sqrt(2.0 * p))
    assert power["mean_replicate_sd"] == pytest.approx(
        power["closed_form_draw_sd"], rel=0.15)
    assert 0.0 <= power["p_under_ceiling"] <= 1.0


def test_the_paired_diagnostic_separates_estimator_error_from_draw_noise():
    """The block that makes 'the spread is the worlds' a measurement."""

    design = _skeleton(n_authors=400, n_comms=30, k=6, seed=8)
    block = MOD.paired_error_block(design, MOD.WORLDS["b_only"], "b_only",
                                   9001, 5)
    assert block["community"]["sd_error"] < \
        block["community"]["realized_target_sd"]
    assert abs(block["community"]["mean_error"]) < MOD.LEAK_MAX


# ---------------------------------------------------------------------------
# 7. bootstrap-FE equivalence — X1b's weighted-projection pattern
# ---------------------------------------------------------------------------


def test_a_weighted_author_is_the_same_object_as_a_replicated_author():
    """X1b's pattern, built both ways and compared.

    An author drawn m times in the cluster bootstrap contributes their slots
    m times, and every copy solves the same FE equation given the community
    effects — so the resampled fit IS the weighted alternating projection.
    The test constructs the replicated design explicitly rather than trusting
    the argument.
    """

    design = _skeleton(n_authors=60, n_comms=10, k=4, seed=6)
    y = _values(design, seed=13)
    mult = np.ones(design.n_authors)
    mult[0] = 3.0
    mult[7] = 2.0
    w = mult[design.slot_author]
    a_w, c_w, v_w, _, _ = MOD.fe_coefficients(
        y, design.slot_author, design.slot_comm, design.n_authors,
        design.n_comms, weights=w)
    mu_w, ah_w, bh_w = MOD.normalize_coefficients(a_w, c_w)

    # the same design with author 0's slots present three times and author
    # 7's twice — same author identity, physically duplicated rows
    idx = [np.arange(design.n_slots)]
    for author, extra in ((0, 2), (7, 1)):
        rows = np.flatnonzero(design.slot_author == author)
        idx.extend([rows] * extra)
    take = np.concatenate(idx)
    a_r, c_r, v_r, _, _ = MOD.fe_coefficients(
        y[take], design.slot_author[take], design.slot_comm[take],
        design.n_authors, design.n_comms)
    mu_r, ah_r, bh_r = MOD.normalize_coefficients(a_r, c_r)

    assert np.abs(ah_w - ah_r).max() < 1e-8
    assert np.abs(bh_w - bh_r).max() < 1e-8
    assert mu_w == pytest.approx(mu_r, abs=1e-8)


def test_a_unit_multiplicity_bootstrap_replicate_is_the_real_sample():
    design = _skeleton(n_authors=60, n_comms=10, k=4, seed=6)
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(19))
    plain = MOD.mains_budget(world)
    replicate = MOD._bootstrap_subdesign(world, np.ones(world.n_authors))
    for key in ("author", "community", "community_unweighted", "var_y"):
        assert replicate[key] == pytest.approx(plain[key], abs=1e-9), key


def test_the_bootstrap_recomputes_its_factor_inside_every_replicate():
    """#87(b), treatment one: the correction follows the resample."""

    design = _skeleton(n_authors=60, n_comms=10, k=4, seed=6)
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(23))
    rng = np.random.default_rng(5)
    mult = np.bincount(rng.integers(0, world.n_authors, world.n_authors),
                       minlength=world.n_authors).astype(float)
    row = MOD._bootstrap_subdesign(world, mult)
    pinned = MOD.mains_budget(world)["author_factor"]
    assert row["author_factor"] != pytest.approx(pinned, abs=1e-12)
    assert row["author"] == pytest.approx(row["author_raw"]
                                          * row["author_factor"])


def test_the_bootstrap_covers_zero_on_a_null_toy():
    design = _skeleton(n_authors=200, n_comms=20, k=5, seed=4)
    world = MOD.synthetic_design(design, MOD.WORLDS["null"],
                                 np.random.default_rng(31))
    boot = MOD.cluster_bootstrap_mains(world, 60, 101)
    point = MOD.mains_budget(world)
    for comp in ("author", "community"):
        lo, hi = boot["ci"][comp]
        assert lo <= 0.0 <= hi, comp
        assert lo <= point[comp] <= hi, comp


# ---------------------------------------------------------------------------
# 8. the gate's routing logic and the verdict
# ---------------------------------------------------------------------------


def test_the_a1_stop_reads_the_routing_family_only():
    assert MOD.a1_stop_fires({"routing_status": "FAIL",
                              "descriptive_status": "PASS"}) is True
    assert MOD.a1_stop_fires({"routing_status": "PASS",
                              "descriptive_status": "ANNOTATED"}) is False


def _gate_stub(routing_status="PASS", failing=None):
    return {"routing_status": routing_status, "descriptive_status": "PASS",
            "n_routing": 10, "n_routing_passed": 10 if failing is None
            else 10 - len(failing),
            "routing_clauses": dict(failing or {})}


def test_a_routing_failure_forbids_the_real_arm():
    verdict = MOD.build_verdict(
        _gate_stub("FAIL", {"(R02) something": "UNINFORMATIVE"}), None)
    assert verdict["cell"] == MOD.CELL_DEFECT
    assert verdict["certified"] is False
    assert verdict["real_arm_run"] is False
    assert verdict["failing_routing_clauses"] == {
        "(R02) something": "UNINFORMATIVE"}


def test_a_clean_battery_certifies_and_licenses_the_real_arm():
    real = {"budget": {"author": 0.13, "community": 0.055},
            "bootstrap": {"ci": {"author": [0.12, 0.14],
                                 "community": [0.05, 0.06]}}}
    verdict = MOD.build_verdict(_gate_stub("PASS"), real)
    assert verdict["cell"] == MOD.CELL_CERTIFIED
    assert verdict["certified"] is True
    assert verdict["real_arm_run"] is True


def test_the_predictions_are_unscored_when_the_instrument_does_not_certify():
    scored = MOD.score_predictions(None)
    assert scored["scored"] is False
    assert scored["author"] == MOD.PREDICTION_AUTHOR_MAIN == 0.15
    assert scored["community"] == MOD.PREDICTION_COMMUNITY_MAIN == 0.077


def test_the_predictions_are_scored_against_the_realized_cis():
    real = {"budget": {"author": 0.152, "community": 0.055},
            "bootstrap": {"ci": {"author": [0.145, 0.160],
                                 "community": [0.050, 0.060]}}}
    scored = MOD.score_predictions(real)
    assert scored["scored"] is True
    assert scored["rows"]["author"]["status"] == "HIT"
    assert scored["rows"]["community"]["status"] == "MISS"


def test_the_leans_are_unscored_when_the_a1_stop_fires():
    leans = MOD.evaluate_leans(_gate_stub("FAIL", {"x": "FAIL"}), None)
    assert leans[0]["status"] == "BROKE"             # certification lean
    assert all("UNSCORED" in row["status"] for row in leans[1:])


def test_the_gate_runs_end_to_end_on_a_toy_and_separates_its_families(tmp_path):
    design = _skeleton(n_authors=300, n_comms=25, k=5, seed=12)
    log = MOD.RunLog(tmp_path / "gate.jsonl")
    gate = MOD.mains_gate(design, 40, log)
    assert gate["n_routing"] == 10
    assert gate["n_descriptive"] == 3
    assert set(gate["routing_clauses"]).isdisjoint(gate["descriptive_clauses"])
    assert set(gate["blocks"]) == set(MOD.WORLDS)
    assert gate["leakage"]["full"]["applicable"] is False
    assert gate["routing_status"] in {"PASS", "FAIL"}
    assert gate["marginal_counterfactual"]["n_fe_failures"] == 0
    assert (tmp_path / "gate.jsonl").exists()


# ---------------------------------------------------------------------------
# 9. the #83 ID-leak helper and the commit hygiene
# ---------------------------------------------------------------------------


def test_the_id_leak_helper_finds_a_planted_name(tmp_path):
    target = tmp_path / "leaky.md"
    target.write_text("a line\nthe author zzq_unlikely_handle wrote\n",
                      encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["zzq_unlikely_handle"])
    assert scan["status"] == "FAIL"
    assert scan["n_hits"] == 1
    assert scan["hits"][0]["line"] == 2


def test_the_id_leak_helper_ignores_substrings_inside_identifiers(tmp_path):
    target = tmp_path / "clean.md"
    target.write_text("prefix_zzq_unlikely_handle_suffix\n", encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["zzq_unlikely_handle"])
    assert scan["status"] == "PASS"


def test_the_baseline_policy_subtracts_only_identical_head_hits():
    hits = [{"path": "docs/CLAIMS_LEDGER.md", "line": 58},
            {"path": "reports/NEW.md", "line": 3}]
    new = MOD.new_hits_only(hits, {("CLAIMS_LEDGER.md", 58)})
    assert len(new) == 1
    assert new[0]["path"] == "reports/NEW.md"


def test_the_scanned_file_list_is_this_legs_committed_one():
    names = {path.name for path in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_XM_MAINS_ESTIMATOR_REPORT.md",
                     "run_suica_m4_xm_mains_estimator.py",
                     "test_m4_xm_mains_estimator.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_results_stay_out_of_the_commit():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore


# ---------------------------------------------------------------------------
# 10. the anchors (#78, BLOCKING) as this leg pins them
# ---------------------------------------------------------------------------


def test_the_inherited_anchors_are_x1s():
    assert MOD.ANCHOR_ROWS_PARSEABLE == 17_640_062
    assert MOD.ANCHOR_AUTHORS == 10_296
    assert MOD.ANCHOR_LAW_VOCAB == 1_443
    assert MOD.ANCHOR_VOCAB_FLOOR_USERS == 89
    assert MOD.ANCHOR_BIG5_AUTHORS == 1_401
    assert MOD.ANCHOR_DISJOINT_AUTHORS == 8_895


def test_the_chain_anchors_are_the_three_registered_rows():
    assert MOD.CHAIN_ANCHORS[3] == {"authors": 3_686, "communities": 1_145,
                                    "shared_pairs": 32_415}
    assert MOD.CHAIN_ANCHORS[5]["authors"] == 3_665
    assert MOD.CHAIN_ANCHORS[5]["communities"] == 1_000
    assert MOD.CHAIN_ANCHORS[5]["shared_pairs"] == 31_899
    assert MOD.CHAIN_ANCHORS[5]["singleton_communities"] == 0
    assert MOD.CHAIN_ANCHORS[5]["lcc_author_coverage"] == 1.0
    assert MOD.CHAIN_ANCHORS[8] == {"authors": 3_595, "communities": 780,
                                    "shared_pairs": 30_561}


# ---------------------------------------------------------------------------
# 11. the committed run (skipped where the artifacts were not produced)
# ---------------------------------------------------------------------------


def test_committed_run_reproduced_the_inherited_anchors():
    census = _artifact("census.json")
    assert census["status"] == "PASS"
    for key, pin in census["pins"].items():
        assert pin["status"] == "PASS", key
        assert pin["registered"] == pin["observed"], key
    pins = census["pins"]
    assert pins["rows parseable (author+subreddit+created_utc+wcq)"][
        "observed"] == 17_640_062
    assert pins["authors"]["observed"] == 10_296
    assert pins["law vocabulary (communities)"]["observed"] == 1_443


def test_committed_run_reproduced_the_predicate_chain_census():
    anchor = _artifact("chain_anchor.json")
    assert anchor["status"] == "PASS"
    for key, row in anchor["pins_by_s"].items():
        assert row["status"] == "PASS", key
        for field, value in row["observed"].items():
            assert value == MOD.CHAIN_ANCHORS[int(key)][field], (key, field)
    chain = _artifact("chain_census.json")
    primary = chain[str(MOD.S_PRIMARY)]
    assert primary["authors"] == 3_665
    assert primary["communities"] == 1_000
    assert primary["shared_pairs"] == 31_899
    assert primary["singleton_communities"] == 0
    assert primary["lcc_author_coverage"] == 1.0


def test_committed_run_pinned_the_realized_mains_df_derivation():
    dfd = _artifact("df_derivation.json")
    assert dfd["A_authors"] == 3_665
    assert dfd["C_communities"] == 1_000
    assert dfd["P_shared_pairs"] == 31_899
    assert dfd["residual_df_factor_applies_to_mains"] is False
    assert dfd["author"]["factor"] == pytest.approx(3665 / 3664)
    assert dfd["community_unweighted"]["factor"] == pytest.approx(1000 / 999)
    weighted = dfd["community_size_weighted"]
    assert weighted["factor"] == pytest.approx(
        1.0 / (1.0 - weighted["sum_p_squared"]))
    assert weighted["effective_members"] < 100       # the skewed community side
    contrast = dfd["interaction_factor_for_contrast"]
    assert contrast["factor"] == pytest.approx(31_899 / 27_235)


def test_committed_gate_scored_ten_routing_and_three_descriptive_clauses():
    gate = _artifact("part0_mains_gate.json")
    assert gate["n_routing"] == 10
    assert gate["n_descriptive"] == 3
    assert set(gate["routing_clauses"]).isdisjoint(gate["descriptive_clauses"])
    assert gate["n_routing_passed"] == sum(
        1 for v in gate["routing_clauses"].values() if v == "PASS")
    assert gate["routing_status"] == (
        "PASS" if gate["n_routing_passed"] == gate["n_routing"] else "FAIL")
    assert set(gate["blocks"]) == set(MOD.WORLDS)
    for block in gate["blocks"].values():
        assert block["replicates"] == MOD.N_SYNTH_REPLICATES


def test_committed_gate_scored_every_zero_point_row_in_every_world():
    gate = _artifact("part0_mains_gate.json")
    for name, shares in MOD.WORLDS.items():
        clause = gate["leakage"][name]
        zeros = [c for c in MOD.COMPONENTS if shares[c] == 0.0]
        assert clause["applicable"] == bool(zeros), name
        assert set(clause["rows"]) == set(zeros), name
        for comp, row in clause["rows"].items():
            assert row["maximum"] == MOD.LEAK_MAX
            assert row["status"] == (
                "PASS" if abs(row["reading"]) < MOD.LEAK_MAX else "FAIL")


def test_committed_gate_recovery_rows_carry_both_scales_and_the_ceiling():
    gate = _artifact("part0_mains_gate.json")
    assert set(gate["recovery"]) == {f"{w}:{c}"
                                     for w, c in MOD.RECOVERY_CLAUSES}
    for key, row in gate["recovery"].items():
        assert row["ceiling"] == MOD.CEILING_REPLICATE_SD
        assert row["informative"] == (
            row["replicate_sd"] <= MOD.CEILING_REPLICATE_SD)
        assert row["tolerance"] == max(MOD.RESOLUTION_SHARE,
                                       MOD.TOL_SD_MULT * row["replicate_sd"])
        assert row["status"] == MOD.score_recovery(
            {"mean": row["recovered_mean"], "sd": row["replicate_sd"]},
            row["target"])["status"]
        assert "raw" in row                          # #67 co-report


def test_committed_run_honoured_the_a1_stop():
    """Real estimands may exist only when every ROUTING clause passed."""

    gate = _artifact("part0_mains_gate.json")
    verdict = _artifact("verdict.json")
    if gate["routing_status"] == "PASS":             # pragma: no cover
        assert verdict["cell"] == MOD.CELL_CERTIFIED
        assert (ARTIFACTS / "real_arm.json").exists()
    else:
        assert verdict["cell"] == MOD.CELL_DEFECT
        assert not (ARTIFACTS / "real_arm.json").exists()
        assert verdict["real_arm_run"] is False


def test_committed_run_verified_the_projection_on_the_real_incidence():
    gate = _artifact("part0_mains_gate.json")
    fe = gate["diagnostics"]["null_world_fe"]
    assert max(fe["fe_exactness"].values()) <= MOD.FE_TOL
    assert fe["fe"]["change_early"] <= MOD.FE_TOL
    assert fe["fe"]["change_late"] <= MOD.FE_TOL


def test_committed_run_kept_the_real_numbers_out_when_it_stopped():
    """The gate's whole point: an uncertified instrument reports nothing."""

    verdict = _artifact("verdict.json")
    if verdict["certified"]:                         # pragma: no cover
        return
    assert not (ARTIFACTS / "real_arm.json").exists()
    payload = _artifact("report_payload.json")
    assert payload["real"] is None
    assert payload["predictions"]["scored"] is False
    if REPORT.exists():
        text = REPORT.read_text(encoding="utf-8")
        assert "**NOT COMPUTED.**" in text


def test_committed_run_cleared_the_id_leak_gate():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS


def test_committed_report_matches_the_committed_verdict():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-M report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**VERDICT — {verdict['cell']}.**" in text
    for heading in ("## The reading", "## Leg lineage", "## Preconditions",
                    "## The estimator, and the normalization that identifies "
                    "it",
                    "## The df / joint-estimation derivation",
                    "### ROUTING clauses (A1-stopping)",
                    "### DESCRIPTIVE clauses (annotate, never stop)",
                    "## Diagnostics (non-routing)",
                    "## The corpus main budget", "## Registered leans",
                    "## Boundaries", "## Configuration"):
        assert heading in text, heading
    for boundary_head in ("Metadata only", "INSTRUMENT LEG, R1-class",
                          "No psychological naming", "EXPLORATORY",
                          "Incomplete design", "Cohort composition"):
        assert boundary_head in text, boundary_head


def test_committed_report_carries_the_numbers_from_the_artifacts():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-M report has not been produced in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    gate = _artifact("part0_mains_gate.json")
    for name in gate["routing_clauses"]:
        assert name in text, name
    for name in gate["descriptive_clauses"]:
        assert name in text, name
    for row in gate["recovery"].values():
        assert f"{row['recovered_mean']:.4f}" in text
        assert f"{row['replicate_sd']:.4f}" in text
    dfd = gate["df_derivation"]
    for key in ("author", "community_size_weighted", "community_unweighted"):
        assert f"{dfd[key]['factor']:.6f}" in text
    chain = _artifact("chain_census.json")
    for row in chain.values():
        assert f"{row['shared_pairs']:,}" in text


def test_committed_report_prints_the_pinned_normalization():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-M report has not been produced in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    for step in MOD.NORMALIZATION_SEQUENCE:
        core = step.split(". ", 1)[-1] if step[1] == "." else step
        assert core[:60] in text


def test_committed_outcome_was_appended_to_the_registration():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X-M outcome (executor, 2026-08-19)" in text
    verdict = _artifact("verdict.json")
    assert verdict["cell"] in text


def test_the_claims_ledger_carries_exactly_one_xm_row():
    text = LEDGER.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| M4-X-M ")]
    assert len(rows) == 1
    for token in ("EXPLORATORY", "label-free", "metadata-only", "X3",
                  "#87", "instrument"):
        assert token in rows[0], token
