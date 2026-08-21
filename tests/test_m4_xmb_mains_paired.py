"""Contract tests for SUICA M4-X-Mb — the mains estimator, paired-scored.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X-Mb", commit e421072) makes this leg a GATE-ARITHMETIC leg: the estimator,
the skeleton, the normalization, the worlds and the seeds are X-M's committed
ones, and what changes is how four clauses are scored.  The objects that have
to be pinned by contract are therefore:

1. the INHERITANCE — X-Mb must be bound to X-M's committed objects rather than
   holding copies of them, and its worlds, seeds and ceilings must be the same
   numbers X-M registered;
2. the REALIZED COMPONENT — the reconstruction of a replicate's drawn a/b/g
   has to be the vectors X1's builder actually used, which is checked against
   a noiseless world where the cell means ARE those vectors;
3. PAIRED-vs-NOMINAL SCORING, in both directions — a world-limited clause that
   fails nominally must be able to pass paired, and an estimator that is
   genuinely wrong must fail paired even when the nominal reading forgives it;
4. the EFFECTIVE-SAMPLE formula and its published rows (#93c);
5. the REPLICATE BUDGET arithmetic (#93b), including the sign of the nominal
   clause's response to a larger budget;
6. the CERTIFICATION ORDER (#93 note) — the real arm must be unreachable
   without a stamp, and the stamp must precede it in the artifacts;
7. the ANCHORS, the #83 helper and the commit hygiene.

Everything inherited (the exact FE, the pinned normalization, the df
derivation, the leakage battery, the bootstrap-FE equivalence) is covered by
``test_m4_xm_mains_estimator`` and below it; it is re-checked here only where
this leg's wrapper could break the binding.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_xmb_mains_paired.py"
XM_SCRIPT = ROOT / "scripts" / "run_suica_m4_xm_mains_estimator.py"
X1C_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1c_venue_response.py"
X1B_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
ARTIFACTS = ROOT / "results" / "m4_xmb_mains_paired"
REPORT = ROOT / "reports" / "SUICA_M4_XMB_MAINS_PAIRED_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X-M recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_xmb_mains_paired", SCRIPT)


# ---------------------------------------------------------------------------
# helpers — small connected skeletons, no corpus needed
# ---------------------------------------------------------------------------


def _skeleton(n_authors=140, n_comms=18, k=5, seed=11, ragged=True):
    """A connected author x community skeleton with UNEQUAL cell sizes."""

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
    lcc = MOD.XM.bipartite_lcc(sa, sc, n_authors, n_comms)
    assert lcc["lcc_author_coverage"] == 1.0, "the toy skeleton must connect"
    return design


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                            # pragma: no cover
        pytest.skip("the X-Mb run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. inheritance — X-Mb is BOUND to X-M's committed objects (#56/#81)
# ---------------------------------------------------------------------------


INHERITED_FROM_XM = (
    "fe_coefficients", "normalize_coefficients", "fitted_coefficients",
    "mean_removal_factor", "mains_df_derivation", "mains_budget",
    "full_budget", "cluster_bootstrap_mains", "mains_gate", "score_recovery",
    "ceiling_power", "score_predictions", "evaluate_leans", "synthetic_design",
    "Design", "gate_status", "anchor_gate", "scan_for_cohort_ids",
    "new_hits_only", "baseline_hit_keys", "load_cell_cache",
    "build_chain_design", "law_vocabulary",
)


def test_the_machinery_is_imported_by_file_and_not_copied():
    assert Path(MOD.XM.__file__).resolve() == XM_SCRIPT.resolve()
    assert Path(MOD.X1C.__file__).resolve() == X1C_SCRIPT.resolve()
    assert Path(MOD.X1B.__file__).resolve() == X1B_SCRIPT.resolve()
    assert MOD.X1C is MOD.XM.X1C
    assert MOD.X1B is MOD.XM.X1B
    source = SCRIPT.read_text(encoding="utf-8")
    for name in INHERITED_FROM_XM:
        target = getattr(MOD, name)
        assert getattr(MOD.XM, name, None) is target, name
        assert f"\ndef {name}(" not in source, name
        assert f"\nclass {name}" not in source, name


def test_the_estimator_itself_is_untouched():
    """X-Mb changes GATE SCORING ONLY: the estimating functions are X-M's."""

    design = _skeleton(n_authors=60, n_comms=10, k=4, seed=6)
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(19))
    assert MOD.mains_budget is MOD.XM.mains_budget
    assert MOD.full_budget is MOD.XM.full_budget
    mine = MOD.full_budget(world)
    theirs = MOD.XM.full_budget(world)
    for key in ("author", "community", "community_unweighted", "interaction",
                "var_y"):
        assert mine[key] == theirs[key], key


def test_the_registration_pins_are_xms():
    assert MOD.SEED == MOD.XM.SEED == 20260819
    assert MOD.N_SYNTH_REPLICATES == MOD.XM.N_SYNTH_REPLICATES == 8
    assert MOD.B_BOOT == 1000
    assert MOD.WORLDS == MOD.XM.WORLDS
    assert MOD.WORLD_SEED_OFFSET == MOD.XM.WORLD_SEED_OFFSET
    assert MOD.WORLD_SEED_OFFSET["a_only"] == 13
    assert MOD.WORLD_SEED_OFFSET["b_only"] == 19
    assert MOD.WORLD_SEED_OFFSET["g_only"] == 23
    assert MOD.WORLD_SEED_OFFSET["null"] == 7
    assert MOD.WORLD_SEED_OFFSET["full"] == 0
    assert MOD.RECOVERY_CLAUSES == (("a_only", "author"),
                                    ("b_only", "community"),
                                    ("full", "author"),
                                    ("full", "community"))
    assert MOD.LEAK_MAX == 0.005
    assert MOD.CELL_CERTIFIED == "MAINS_CERTIFIED"
    assert MOD.CELL_DEFECT == "INSTRUMENT_DEFECT"


def test_the_paired_ceilings_are_the_registered_ones():
    """#93a: both ceilings are the #92 resolution in share units."""

    assert MOD.CEILING_PAIRED_SD == 0.01
    assert MOD.CEILING_PAIRED_MEAN == 0.01
    assert MOD.CEILING_PAIRED_SD == MOD.RESOLUTION_SHARE
    assert MOD.CEILING_PAIRED_MEAN == MOD.RESOLUTION_SHARE


# ---------------------------------------------------------------------------
# 2. the REALIZED component — the reconstruction is the builder's own draw
# ---------------------------------------------------------------------------


def test_the_realized_components_are_the_vectors_the_builder_used():
    """A noiseless world: the cell means ARE ``a[sa] + b[sc] + g``.

    The three shares sum to one, so the builder's residual sigma is exactly
    zero and every cell mean equals the planted sum to a rounding of the
    sum/count round trip.  A reconstruction that consumed the stream in the
    wrong order would be wrong by order 1, not by 1e-16.
    """

    design = _skeleton(n_authors=80, n_comms=12, k=4, seed=17)
    shares = {"author": 0.5, "community": 0.3, "interaction": 0.2}
    world = MOD.synthetic_design(design, shares, np.random.default_rng(4242))
    a, b, g = MOD.realized_component_draws(design, shares, 4242, 0)
    planted = a[design.slot_author] + b[design.slot_comm] + g
    assert np.abs(world.mean_e - planted).max() < 1e-12
    assert np.abs(world.mean_l - planted).max() < 1e-12
    # and the test is not vacuous: the planted vector is not a constant
    assert planted.std() > 0.5


def test_a_wrong_stream_order_is_visibly_wrong():
    """The guard the previous test needs: a shuffled order breaks it loudly."""

    design = _skeleton(n_authors=80, n_comms=12, k=4, seed=17)
    shares = {"author": 0.5, "community": 0.3, "interaction": 0.2}
    world = MOD.synthetic_design(design, shares, np.random.default_rng(4242))
    rng = np.random.default_rng(4242)
    # community FIRST, which is not the builder's order
    b = rng.normal(0.0, np.sqrt(0.3), design.n_comms)
    a = rng.normal(0.0, np.sqrt(0.5), design.n_authors)
    g = rng.normal(0.0, np.sqrt(0.2), design.n_slots)
    wrong = a[design.slot_author] + b[design.slot_comm] + g
    assert np.abs(world.mean_e - wrong).max() > 0.1


def test_a_zero_share_consumes_nothing_from_the_stream():
    """The builder short-circuits a zero share; the reconstruction must too."""

    design = _skeleton(n_authors=40, n_comms=8, k=3, seed=21)
    a, b, g = MOD.realized_component_draws(design, MOD.WORLDS["b_only"],
                                           1234, 0)
    assert np.array_equal(a, np.zeros(design.n_authors))
    assert np.array_equal(g, np.zeros(design.n_slots))
    assert b.std() > 0
    # the b vector must be the FIRST draw of the stream, since a was skipped
    first = np.random.default_rng(1234).normal(
        0.0, np.sqrt(MOD.WORLDS["b_only"]["community"]), design.n_comms)
    assert np.array_equal(b, first)


def test_the_replicate_offset_is_the_builders():
    """Replicate r is seeded ``seed + 1000 * r``, as X1's block seeds it."""

    design = _skeleton(n_authors=40, n_comms=8, k=3, seed=21)
    shares = MOD.WORLDS["a_only"]
    a0, _, _ = MOD.realized_component_draws(design, shares, 500, 0)
    a3, _, _ = MOD.realized_component_draws(design, shares, 500, 3)
    direct, _, _ = MOD.realized_component_draws(design, shares, 500 + 3000, 0)
    assert np.array_equal(a3, direct)
    assert not np.array_equal(a0, a3)


def test_the_realized_target_is_the_estimators_own_functional_on_a_toy():
    """A toy where the answer is computable by hand, both scales."""

    design = _skeleton(n_authors=50, n_comms=9, k=4, seed=33)
    shares = MOD.WORLDS["full"]
    var_y = 2.0
    row = MOD.realized_targets(design, shares, 777, 2, var_y)
    a, b, _ = MOD.realized_component_draws(design, shares, 777, 2)
    weights = MOD.skeleton_weights(design)

    p = np.ones(design.n_authors) / design.n_authors
    want_a = float((p * a * a).sum() - ((p * a).sum()) ** 2) / var_y
    assert row["author_raw"] == pytest.approx(want_a)

    q = weights["community"] / weights["community"].sum()
    want_b = float((q * b * b).sum() - ((q * b).sum()) ** 2) / var_y
    assert row["community_raw"] == pytest.approx(want_b)

    f_a = MOD.mean_removal_factor(weights["author"])["factor"]
    f_c = MOD.mean_removal_factor(weights["community"])["factor"]
    assert row["author"] == pytest.approx(want_a * f_a)
    assert row["community"] == pytest.approx(want_b * f_c)
    # the size weighting is not the uniform one on a ragged skeleton
    assert row["community_raw"] != pytest.approx(
        row["community_unweighted_raw"])


def test_the_realized_target_scales_with_the_variance_denominator():
    design = _skeleton(n_authors=50, n_comms=9, k=4, seed=33)
    one = MOD.realized_targets(design, MOD.WORLDS["a_only"], 8, 0, 1.0)
    two = MOD.realized_targets(design, MOD.WORLDS["a_only"], 8, 0, 2.0)
    assert two["author_raw"] == pytest.approx(one["author_raw"] / 2.0)


def test_the_weighted_popvar_is_the_population_variance_it_claims():
    values = np.array([1.0, 2.0, 5.0, 8.0])
    assert MOD.weighted_popvar(values) == pytest.approx(float(np.var(values)))
    weights = np.array([1.0, 1.0, 2.0, 4.0])
    p = weights / weights.sum()
    want = float((p * values * values).sum() - ((p * values).sum()) ** 2)
    assert MOD.weighted_popvar(values, weights) == pytest.approx(want)


# ---------------------------------------------------------------------------
# 3. PAIRED vs NOMINAL scoring — both directions (#93a)
# ---------------------------------------------------------------------------


def test_a_tight_paired_clause_passes():
    row = MOD.score_paired({"mean_error": 0.0004, "sd_error": 0.0006})
    assert row["informative"] is True
    assert row["unbiased"] is True
    assert row["status"] == "PASS"
    assert row["sd_headroom"] > 0
    assert row["mean_headroom"] > 0


def test_a_biased_paired_clause_fails():
    """Direction one: the estimator is precise and wrong."""

    row = MOD.score_paired({"mean_error": 0.03, "sd_error": 0.0006})
    assert row["informative"] is True
    assert row["unbiased"] is False
    assert row["status"] == "FAIL"


def test_a_scattered_paired_clause_is_uninformative():
    """Direction two: the ESTIMATOR itself cannot resolve what it claims."""

    row = MOD.score_paired({"mean_error": 0.0001, "sd_error": 0.05})
    assert row["informative"] is False
    assert row["status"] == "UNINFORMATIVE"
    assert row["sd_headroom"] < 0


def test_the_paired_ceilings_sit_exactly_at_the_resolution():
    at = MOD.score_paired({"mean_error": MOD.CEILING_PAIRED_MEAN,
                           "sd_error": MOD.CEILING_PAIRED_SD})
    over_sd = MOD.score_paired({"mean_error": 0.0,
                                "sd_error": MOD.CEILING_PAIRED_SD * 1.001})
    over_mean = MOD.score_paired({"mean_error": MOD.CEILING_PAIRED_MEAN * 1.001,
                                  "sd_error": 0.0})
    assert at["status"] == "PASS"
    assert over_sd["status"] == "UNINFORMATIVE"
    assert over_mean["status"] == "FAIL"


def test_the_sd_ceiling_outranks_the_mean_ceiling():
    """An unmeasured clause reads UNINFORMATIVE, never FAIL."""

    row = MOD.score_paired({"mean_error": 0.5, "sd_error": 0.5})
    assert row["status"] == "UNINFORMATIVE"


def test_paired_scoring_rescues_a_world_limited_clause_the_nominal_one_stops():
    """The #93a case, built end to end on a toy that reproduces the shape.

    A size-skewed community side makes the NOMINAL replicate spread large
    while the estimator tracks each drawn world closely; the paired clause
    must see the estimator and the nominal one must not.
    """

    design = _skeleton(n_authors=200, n_comms=14, k=5, seed=44)
    log = MOD.RunLog(Path(_tmp()) / "block.jsonl")
    block = MOD.XM.synthetic_world_block_mains(
        design, MOD.WORLDS["b_only"], "b_only",
        MOD.SEED_PART0 + MOD.WORLD_SEED_OFFSET["b_only"], 6, log)
    paired = MOD.paired_recovery(design, "b_only", "community", block)
    nominal = MOD.score_recovery(block["stats"]["community"],
                                 MOD.WORLDS["b_only"]["community"])
    assert paired["sd_error"] < nominal["replicate_sd"]
    assert paired["realized_target_sd"] > paired["sd_error"]
    assert MOD.score_paired(paired)["status"] == "PASS"


def test_paired_scoring_does_not_forgive_an_estimator_that_is_wrong():
    """The other direction: pairing must not become a rubber stamp.

    The block's per-replicate community estimates are shifted by a constant
    well above the resolution; the paired clause has to FAIL, because the
    realized targets did not move with them.
    """

    design = _skeleton(n_authors=120, n_comms=12, k=4, seed=55)
    log = MOD.RunLog(Path(_tmp()) / "block2.jsonl")
    block = MOD.XM.synthetic_world_block_mains(
        design, MOD.WORLDS["b_only"], "b_only",
        MOD.SEED_PART0 + MOD.WORLD_SEED_OFFSET["b_only"], 5, log)
    for key in ("community", "community_raw"):
        block["stats"][key]["values"] = [v + 0.05 for v in
                                         block["stats"][key]["values"]]
    paired = MOD.paired_recovery(design, "b_only", "community", block)
    assert paired["mean_error"] > 0.04
    assert MOD.score_paired(paired)["status"] == "FAIL"


def test_the_paired_error_is_the_estimate_minus_the_realized_target():
    """The definition itself, replicate by replicate."""

    design = _skeleton(n_authors=90, n_comms=10, k=4, seed=66)
    log = MOD.RunLog(Path(_tmp()) / "block3.jsonl")
    block = MOD.XM.synthetic_world_block_mains(
        design, MOD.WORLDS["a_only"], "a_only",
        MOD.SEED_PART0 + MOD.WORLD_SEED_OFFSET["a_only"], 4, log)
    paired = MOD.paired_recovery(design, "a_only", "author", block)
    for rep in range(paired["replicates"]):
        assert paired["errors"][rep] == pytest.approx(
            paired["estimates"][rep] - paired["realized_targets"][rep])
        assert paired["estimates"][rep] == pytest.approx(
            block["stats"]["author"]["values"][rep])
    assert paired["mean_error"] == pytest.approx(
        float(np.mean(paired["errors"])))


def test_the_corrected_paired_error_is_the_raw_one_times_the_gauge_factor():
    """A fixed skeleton gives both sides the same constant factor."""

    design = _skeleton(n_authors=90, n_comms=10, k=4, seed=66)
    log = MOD.RunLog(Path(_tmp()) / "block4.jsonl")
    block = MOD.XM.synthetic_world_block_mains(
        design, MOD.WORLDS["b_only"], "b_only",
        MOD.SEED_PART0 + MOD.WORLD_SEED_OFFSET["b_only"], 4, log)
    paired = MOD.paired_recovery(design, "b_only", "community", block)
    factor = MOD.mean_removal_factor(
        MOD.skeleton_weights(design)["community"])["factor"]
    assert factor > 1.0
    assert paired["mean_error"] == pytest.approx(
        paired["raw"]["mean_error"] * factor, rel=1e-12)
    assert paired["sd_error"] == pytest.approx(
        paired["raw"]["sd_error"] * factor, rel=1e-12)


def test_the_paired_block_pairs_against_the_worlds_that_were_scored():
    """The realized target must come from the SAME replicate, not another."""

    design = _skeleton(n_authors=90, n_comms=10, k=4, seed=66)
    log = MOD.RunLog(Path(_tmp()) / "block5.jsonl")
    block = MOD.XM.synthetic_world_block_mains(
        design, MOD.WORLDS["a_only"], "a_only",
        MOD.SEED_PART0 + MOD.WORLD_SEED_OFFSET["a_only"], 4, log)
    paired = MOD.paired_recovery(design, "a_only", "author", block)
    shuffled = list(reversed(paired["realized_targets"]))
    mis_paired = np.array(paired["estimates"]) - np.array(shuffled)
    assert float(np.std(mis_paired, ddof=1)) > paired["sd_error"]


# ---------------------------------------------------------------------------
# 4. effective samples (#93c)
# ---------------------------------------------------------------------------


def test_the_effective_sample_is_one_over_the_sum_of_squared_weights():
    weights = np.array([1.0, 1.0, 1.0, 1.0])
    row = MOD.mean_removal_factor(weights)
    assert row["effective_members"] == pytest.approx(4.0)
    skewed = np.array([100.0, 1.0, 1.0, 1.0])
    p = skewed / skewed.sum()
    assert MOD.mean_removal_factor(skewed)["effective_members"] == \
        pytest.approx(1.0 / float((p * p).sum()))
    assert MOD.mean_removal_factor(skewed)["effective_members"] < 2.0


def test_the_effective_sample_rows_publish_nominal_beside_effective():
    design = _skeleton(n_authors=140, n_comms=18, k=5, seed=11)
    rows = MOD.effective_sample_rows(MOD.mains_df_derivation(design))
    assert rows[0]["row"].startswith("R02 / R04")     # the registered first
    for row in rows:
        assert row["nominal_members"] > 0
        assert row["effective_members"] > 0
        assert 0.0 < row["effective_fraction"] <= 1.0 + 1e-12
    weighted = rows[0]
    assert weighted["effective_members"] == pytest.approx(
        1.0 / weighted["sum_p_squared"])
    assert weighted["mean_removal_factor"] == pytest.approx(
        1.0 / (1.0 - weighted["sum_p_squared"]))


def test_the_effective_sample_of_a_uniform_weighting_is_its_nominal_count():
    design = _skeleton(n_authors=140, n_comms=18, k=5, seed=11)
    rows = {row["row"]: row
            for row in MOD.effective_sample_rows(
                MOD.mains_df_derivation(design))}
    author = rows["R01 / R03 — author main"]
    assert author["effective_members"] == pytest.approx(
        author["nominal_members"])


# ---------------------------------------------------------------------------
# 5. the replicate budget (#93b)
# ---------------------------------------------------------------------------


def test_the_chi_square_bound_is_a_bound_and_it_bites():
    """Chernoff on the upper tail: tiny where it should be, 0 where it is not."""

    assert MOD.chi_square_upper_tail_log10(7, 7.0) == 0.0
    small = MOD.chi_square_upper_tail_log10(7, 7 * 400.0)
    assert small < -500
    looser = MOD.chi_square_upper_tail_log10(7, 7 * 25.0)
    assert -60 < looser < -10
    assert looser > small                            # monotone in the argument


def test_the_paired_budget_derivation_uses_the_registered_replicates():
    design = _skeleton(n_authors=140, n_comms=18, k=5, seed=11)
    log = MOD.RunLog(Path(_tmp()) / "budget.jsonl")
    saved = MOD.BUDGET_SWEEP_REPLICATES, MOD.BUDGET_SWEEP_TRIALS
    MOD.BUDGET_SWEEP_REPLICATES, MOD.BUDGET_SWEEP_TRIALS = (8, 30), 40
    try:
        out = MOD.replicate_budget_derivation(design, log)
    finally:
        MOD.BUDGET_SWEEP_REPLICATES, MOD.BUDGET_SWEEP_TRIALS = saved
    paired = out["paired"]
    assert paired["replicates"] == MOD.N_SYNTH_REPLICATES == 8
    assert paired["ceiling"] == MOD.CEILING_PAIRED_SD
    assert paired["ceiling_over_sd"] == pytest.approx(
        MOD.CEILING_PAIRED_SD / paired["paired_sd_prior"])
    assert paired["chi_square_df"] == 7
    assert paired["chi_square_threshold"] == pytest.approx(
        7 * paired["ceiling_over_sd"] ** 2)
    assert paired["log10_upper_bound_p_breach"] < -5
    assert paired["se_of_paired_mean"] == pytest.approx(
        paired["paired_sd_prior"] / np.sqrt(8))


def test_the_prior_paired_sd_agrees_with_the_registration_pin():
    prior = MOD.prior_paired_sd()
    assert prior["registered_pin"] == MOD.XM_PRIOR_PAIRED_SD == 0.000496
    if prior["available"]:
        assert prior["pin_agrees"] is True
        assert set(prior["per_clause"]) == {
            f"{w}:{c}" for w, c in MOD.RECOVERY_CLAUSES}
        assert prior["worst_clause_sd"] >= prior["stopping_clause_sd"]
    assert prior["worst_clause_sd"] < MOD.CEILING_PAIRED_SD


# ---------------------------------------------------------------------------
# 6. the gate's re-scoring, the verdict, and the A1 stop
# ---------------------------------------------------------------------------


def test_the_a1_stop_reads_the_routing_family_only():
    assert MOD.a1_stop_fires({"routing_status": "FAIL",
                              "descriptive_status": "PASS"}) is True
    assert MOD.a1_stop_fires({"routing_status": "PASS",
                              "descriptive_status": "ANNOTATED"}) is False


def _gate_stub(routing_status="PASS", failing=None):
    return {"routing_status": routing_status, "descriptive_status": "PASS",
            "n_routing": 10,
            "n_routing_passed": 10 if failing is None else 10 - len(failing),
            "routing_clauses": dict(failing or {})}


def test_a_routing_failure_forbids_the_real_arm():
    verdict = MOD.build_verdict(
        _gate_stub("FAIL", {"(R02) something": "UNINFORMATIVE"}), None)
    assert verdict["cell"] == MOD.CELL_DEFECT
    assert verdict["certified"] is False
    assert verdict["real_arm_run"] is False


def test_a_clean_battery_certifies():
    verdict = MOD.build_verdict(_gate_stub("PASS"), {"budget": {}})
    assert verdict["cell"] == MOD.CELL_CERTIFIED
    assert verdict["certified"] is True
    assert verdict["real_arm_run"] is True


def test_the_gate_runs_end_to_end_on_a_toy_and_keeps_x_ms_shape(tmp_path):
    design = _skeleton(n_authors=300, n_comms=25, k=5, seed=12)
    log = MOD.RunLog(tmp_path / "gate.jsonl")
    gate = MOD.paired_gate(design, 40, log)
    assert gate["n_routing"] == 10
    assert gate["n_descriptive"] == 3
    assert set(gate["paired_recovery"]) == {f"{w}:{c}"
                                            for w, c in MOD.RECOVERY_CLAUSES}
    # R01-R04 are the paired clauses; R05-R10 are X-M's, character for character
    names = list(gate["routing_clauses"])
    assert all("PAIRED (#93a)" in name for name in names[:4])
    inherited = list(gate["inherited_gate"]["routing_clauses"])
    assert names[4:] == inherited[4:]
    assert gate["descriptive_clauses"] == {
        k: v for k, v in gate["descriptive_clauses"].items()}
    assert set(gate["effective_samples"][0]) >= {"nominal_members",
                                                 "effective_members"}
    assert gate["delta_from_xm"]["routing_before"] in {"PASS", "FAIL"}


def test_the_rescoring_only_touches_the_four_recovery_clauses(tmp_path):
    design = _skeleton(n_authors=300, n_comms=25, k=5, seed=12)
    log = MOD.RunLog(tmp_path / "gate2.jsonl")
    gate = MOD.paired_gate(design, 30, log)
    base = gate["inherited_gate"]
    for name, status in gate["routing_clauses"].items():
        if "PAIRED (#93a)" in name:
            continue
        assert base["routing_clauses"][name] == status, name
    assert len(gate["delta_from_xm"]["rows"]) == 4


# ---------------------------------------------------------------------------
# 7. the certification stamp and the gated real arm (#93 note)
# ---------------------------------------------------------------------------


def test_an_uncertified_certificate_cannot_reach_the_real_arm(tmp_path):
    design = _skeleton(n_authors=40, n_comms=8, k=3, seed=3)
    certificate = {"cell": MOD.CELL_DEFECT, "certified": False,
                   "stamped_monotonic_ns": 1}
    with pytest.raises(MOD.UncertifiedRealArm):
        MOD.run_real_arm(design, 5, certificate, tmp_path)
    assert not (tmp_path / "real_arm.json").exists()


def test_an_unstamped_certificate_cannot_reach_the_real_arm(tmp_path):
    design = _skeleton(n_authors=40, n_comms=8, k=3, seed=3)
    certificate = {"cell": MOD.CELL_CERTIFIED, "certified": True}
    with pytest.raises(MOD.UncertifiedRealArm):
        MOD.run_real_arm(design, 5, certificate, tmp_path)
    assert not (tmp_path / "real_arm.json").exists()


def test_a_certificate_that_is_not_on_disk_cannot_reach_the_real_arm(tmp_path):
    """The stamp must be auditable, not merely believed."""

    design = _skeleton(n_authors=40, n_comms=8, k=3, seed=3)
    certificate = {"cell": MOD.CELL_CERTIFIED, "certified": True,
                   "stamped_monotonic_ns": 7, "stamped_utc": MOD.utc_now()}
    with pytest.raises(MOD.UncertifiedRealArm):
        MOD.run_real_arm(design, 5, certificate, tmp_path)
    assert not (tmp_path / "real_arm.json").exists()


def test_a_stamped_certificate_runs_the_real_arm_and_the_order_holds(tmp_path):
    design = _skeleton(n_authors=60, n_comms=10, k=4, seed=9)
    world = MOD.synthetic_design(design, MOD.WORLDS["full"],
                                 np.random.default_rng(5))
    certificate = MOD.stamp_certification(
        MOD.build_verdict(_gate_stub("PASS"), None), tmp_path)
    assert certificate["cell"] == MOD.CELL_CERTIFIED
    assert (tmp_path / "certification.json").exists()
    real = MOD.run_real_arm(world, 12, certificate, tmp_path)
    assert (tmp_path / "real_arm.json").exists()
    order = MOD.certification_order(certificate, real)
    assert order["status"] == "PASS"
    assert order["ordered"] is True
    assert order["monotonic_delta_ns"] > 0
    assert MOD.parse_utc(real["started_utc"]) >= MOD.parse_utc(
        certificate["stamped_utc"])
    assert set(real["gauge_factors"]) >= {"author", "community_size_weighted",
                                          "community_unweighted"}
    assert real["effective_samples"]["communities_effective"] <= \
        real["effective_samples"]["communities_nominal"]


def test_the_order_assertion_catches_a_real_arm_that_ran_first():
    """The clause must be able to FAIL, or it is decoration."""

    certificate = {"cell": MOD.CELL_CERTIFIED, "certified": True,
                   "stamped_utc": "2026-08-19T12:00:01Z",
                   "stamped_monotonic_ns": 2_000}
    real = {"started_utc": "2026-08-19T12:00:00Z",
            "started_monotonic_ns": 1_000}
    order = MOD.certification_order(certificate, real)
    assert order["status"] == "FAIL"
    assert order["ordered"] is False


def test_the_order_assertion_is_vacuous_when_the_real_arm_did_not_run():
    certificate = {"cell": MOD.CELL_DEFECT, "certified": False,
                   "stamped_utc": "2026-08-19T12:00:00Z",
                   "stamped_monotonic_ns": 1}
    order = MOD.certification_order(certificate, None)
    assert order["status"] == "PASS"
    assert order["real_arm_started_utc"] is None


def test_the_real_arm_has_exactly_one_call_site_in_the_runner():
    """#93's dev-prototype note, enforced by construction and not by habit."""

    source = SCRIPT.read_text(encoding="utf-8")
    assert source.count("run_real_arm(") == 2        # the def and the call
    body = source.split("def main(")[1]
    assert "full_budget(" not in body
    assert "cluster_bootstrap_mains(" not in body
    assert "real = run_real_arm(" in body


def test_the_utc_parser_reads_the_artifacts_own_format():
    assert MOD.parse_utc("2026-08-19T12:00:00Z") < MOD.parse_utc(
        "2026-08-19T12:00:00.000001Z")
    assert MOD.parse_utc("2026-08-19T12:00:00.999999Z") < MOD.parse_utc(
        "2026-08-19T12:00:01Z")


# ---------------------------------------------------------------------------
# 8. the #83 ID-leak helper and the commit hygiene
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
    assert names == {"SUICA_M4_XMB_MAINS_PAIRED_REPORT.md",
                     "run_suica_m4_xmb_mains_paired.py",
                     "test_m4_xmb_mains_paired.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_results_stay_out_of_the_commit():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore


# ---------------------------------------------------------------------------
# 9. the anchors (#78, BLOCKING) as this leg pins them
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
# 10. the committed run (skipped where the artifacts were not produced)
# ---------------------------------------------------------------------------


def test_committed_run_reproduced_the_inherited_anchors():
    census = _artifact("census.json")
    assert census["status"] == "PASS"
    for key, pin in census["pins"].items():
        assert pin["status"] == "PASS", key
        assert pin["registered"] == pin["observed"], key


def test_committed_run_reproduced_the_predicate_chain_census():
    anchor = _artifact("chain_anchor.json")
    assert anchor["status"] == "PASS"
    chain = _artifact("chain_census.json")
    primary = chain[str(MOD.S_PRIMARY)]
    assert primary["authors"] == 3_665
    assert primary["communities"] == 1_000
    assert primary["shared_pairs"] == 31_899
    assert primary["singleton_communities"] == 0
    assert primary["lcc_author_coverage"] == 1.0


def test_committed_gate_scored_ten_routing_and_three_descriptive_clauses():
    gate = _artifact("part0_mains_gate_paired.json")
    assert gate["n_routing"] == 10
    assert gate["n_descriptive"] == 3
    assert set(gate["routing_clauses"]).isdisjoint(gate["descriptive_clauses"])
    assert gate["n_routing_passed"] == sum(
        1 for v in gate["routing_clauses"].values() if v == "PASS")
    assert gate["routing_status"] == (
        "PASS" if gate["n_routing_passed"] == gate["n_routing"] else "FAIL")


def test_committed_paired_rows_are_scored_by_the_registered_rule():
    gate = _artifact("part0_mains_gate_paired.json")
    assert set(gate["paired_recovery"]) == {f"{w}:{c}"
                                            for w, c in MOD.RECOVERY_CLAUSES}
    for key, row in gate["paired_recovery"].items():
        assert row["replicates"] == MOD.N_SYNTH_REPLICATES
        assert len(row["errors"]) == MOD.N_SYNTH_REPLICATES
        assert row["score"]["status"] == MOD.score_paired(row)["status"]
        assert row["score"]["ceiling_sd"] == MOD.CEILING_PAIRED_SD
        assert row["score"]["ceiling_mean"] == MOD.CEILING_PAIRED_MEAN
        assert row["mean_error"] == pytest.approx(
            float(np.mean(row["errors"])))
        for rep, err in enumerate(row["errors"]):
            assert err == pytest.approx(row["estimates"][rep]
                                        - row["realized_targets"][rep])
        assert "nominal" in row and "p_informative" in row[
            "nominal_reliability"]


def test_committed_run_reproduced_the_registered_effective_sample():
    """#93c: R02's 1,000 nominal against 43.3 effective, the first entry."""

    gate = _artifact("part0_mains_gate_paired.json")
    first = gate["effective_samples"][0]
    assert first["row"].startswith("R02 / R04")
    assert first["nominal_members"] == 1_000
    assert first["effective_members"] == pytest.approx(43.3, abs=0.1)
    assert first["effective_members"] == pytest.approx(
        1.0 / first["sum_p_squared"])
    dfd = gate["df_derivation"]
    assert dfd["community_size_weighted"]["effective_members"] == \
        pytest.approx(first["effective_members"])


def test_committed_run_shows_the_nominal_clause_getting_worse_with_budget():
    """#93b's worked example, checked in-leg rather than repeated."""

    budget = _artifact("replicate_budget.json")
    curve = budget["nominal"]["p_under_ceiling_by_replicates"]
    values = [curve[str(r)] for r in MOD.BUDGET_SWEEP_REPLICATES]
    assert budget["nominal"]["decreases_with_budget"] is True
    assert values[0] > values[-1]
    assert values[0] == pytest.approx(0.267, abs=0.05)
    paired = budget["paired"]
    assert paired["log10_upper_bound_p_breach"] < -20
    assert paired["ceiling_over_sd"] > 3.0


def test_committed_run_honoured_the_certification_order():
    order = _artifact("certification_order.json")
    certificate = _artifact("certification.json")
    verdict = _artifact("verdict.json")
    assert order["status"] == "PASS"
    assert certificate["cell"] == verdict["cell"]
    if verdict["certified"]:
        real = _artifact("real_arm.json")
        assert order["monotonic_delta_ns"] > 0
        assert real["started_monotonic_ns"] > certificate[
            "stamped_monotonic_ns"]
        assert MOD.parse_utc(real["started_utc"]) >= MOD.parse_utc(
            certificate["stamped_utc"])
        assert real["certificate"]["cell"] == MOD.CELL_CERTIFIED
    else:                                            # pragma: no cover
        assert not (ARTIFACTS / "real_arm.json").exists()
        assert order["real_arm_started_utc"] is None


def test_committed_run_kept_the_verdict_and_the_real_arm_consistent():
    gate = _artifact("part0_mains_gate_paired.json")
    verdict = _artifact("verdict.json")
    if gate["routing_status"] == "PASS":
        assert verdict["cell"] == MOD.CELL_CERTIFIED
        assert (ARTIFACTS / "real_arm.json").exists()
        assert verdict["real_arm_run"] is True
        assert _artifact("predictions.json")["scored"] is True
    else:                                            # pragma: no cover
        assert verdict["cell"] == MOD.CELL_DEFECT
        assert not (ARTIFACTS / "real_arm.json").exists()
        assert _artifact("predictions.json")["scored"] is False


def test_committed_real_budget_carries_both_scales_and_its_gauge_factors():
    verdict = _artifact("verdict.json")
    if not verdict["certified"]:                     # pragma: no cover
        pytest.skip("the instrument did not certify in this checkout")
    real = _artifact("real_arm.json")
    budget = real["budget"]
    for comp in ("author", "community", "community_unweighted"):
        assert budget[comp] == pytest.approx(
            budget[f"{comp}_raw"] * budget[f"{comp}_factor"])
        lo, hi = real["bootstrap"]["ci"][comp]
        assert lo < budget[comp] < hi, comp
    assert real["bootstrap"]["b_boot"] == 1000
    assert budget["residual"] == pytest.approx(
        1.0 - budget["author"] - budget["community"] - budget["interaction"])
    assert real["gauge_factors"]["author"]["factor"] == pytest.approx(
        budget["author_factor"])
    assert real["effective_samples"]["communities_effective"] == \
        pytest.approx(43.3, abs=0.1)


def test_committed_run_cleared_the_id_leak_gate():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS


def test_committed_report_matches_the_committed_verdict():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-Mb report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**VERDICT — {verdict['cell']}.**" in text
    for heading in ("## The reading", "## Leg lineage", "## Preconditions",
                    "## What X-Mb changes, and what it does not",
                    "## The gate — PAIRED and NOMINAL, side by side",
                    "## Effective samples (#93c)",
                    "## The replicate budget, derived (#93b)",
                    "## The inherited clauses (X-M verbatim)",
                    "## The certification stamp and the gated real arm "
                    "(#93 note)",
                    "## The corpus main budget", "## Registered leans",
                    "## Boundaries", "## Configuration"):
        assert heading in text, heading
    for boundary_head in ("Metadata only", "INSTRUMENT LEG, R1-class",
                          "No psychological naming", "EXPLORATORY",
                          "Incomplete design", "Cohort composition",
                          "The gate was repaired, not relaxed"):
        assert boundary_head in text, boundary_head


def test_committed_report_carries_the_numbers_from_the_artifacts():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-Mb report has not been produced in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    gate = _artifact("part0_mains_gate_paired.json")
    for name in gate["routing_clauses"]:
        assert name in text, name
    for name in gate["descriptive_clauses"]:
        assert name in text, name
    for row in gate["paired_recovery"].values():
        assert f"{row['mean_error']:.6f}" in text
        assert f"{row['sd_error']:.6f}" in text
        assert f"{row['nominal']['replicate_sd']:.4f}" in text
        assert f"{row['nominal_reliability']['p_informative']:.3f}" in text
    for row in gate["effective_samples"]:
        assert f"{row['effective_members']:.1f}" in text


def test_committed_report_prints_both_scorings_side_by_side():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-Mb report has not been produced in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    header = ("| clause | world | component | PAIRED mean error | PAIRED sd | "
              "PAIRED status | NOMINAL gap | NOMINAL sd | NOMINAL status | "
              "NOMINAL P(informative) |")
    assert header in text
    assert "EFFECTIVE members" in text


def test_committed_report_prints_the_real_budget_when_certified():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X-Mb report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    if not verdict["certified"]:                     # pragma: no cover
        assert "**NOT COMPUTED.**" in text
        return
    real = _artifact("real_arm.json")
    predictions = _artifact("predictions.json")
    for comp in ("author", "community", "community_unweighted"):
        assert f"{real['budget'][comp]:.4f}" in text
    for row in predictions["rows"].values():
        assert f"**{row['status']}**" in text


def test_committed_outcome_was_appended_to_the_registration():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X-Mb outcome (executor, 2026-08-19)" in text
    verdict = _artifact("verdict.json")
    assert verdict["cell"] in text


def test_the_claims_ledger_carries_exactly_one_xmb_row():
    text = LEDGER.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| M4-X-Mb ")]
    assert len(rows) == 1
    for token in ("EXPLORATORY", "label-free", "metadata-only", "X3",
                  "#93", "instrument"):
        assert token in rows[0], token


# ---------------------------------------------------------------------------
# a tmp_path shim for the module-level helpers that need a scratch directory
# ---------------------------------------------------------------------------


_TMP: list[Path] = []


def _tmp() -> Path:
    """A per-session scratch directory owned by pytest, never /tmp."""

    if not _TMP:                                     # pragma: no cover
        raise RuntimeError("the scratch directory fixture did not run")
    return _TMP[0]


@pytest.fixture(autouse=True, scope="session")
def _scratch(tmp_path_factory):
    _TMP.append(tmp_path_factory.mktemp("m4_xmb"))
    yield
    _TMP.clear()
