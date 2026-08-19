"""Contract tests for SUICA M4-X1c — the venue response, clause-separated gate.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X1c", commit 8fffaad) names four objects that are NEW here and therefore
have to be pinned by contract rather than inherited:

1. the CLAUSE-SEPARATED gate (#86a) — a ROUTING failure stops the leg, a
   DESCRIPTIVE failure annotates it, and both directions are exercised on
   synthetic fixtures;
2. the DF correction (#86c) — the formula on a toy, its invariances, and the
   fact that the routing statistic is the corrected one;
3. the MARGINAL-TARGET derivation (#86b) — checked against a SIMULATED
   design by running the estimator many times and comparing its mean to the
   pinned formula;
4. the inheritance itself — X1c must be bound to the committed X1b objects,
   not to copies of them.

Everything else (the predicate chain, the exact FE, the permutation null, the
cluster bootstrap) is X1b's and is covered by ``test_m4_x1b_venue_response_fe``;
it is re-checked here only where X1c's wrapper could break the binding.
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
SCRIPT = ROOT / "scripts" / "run_suica_m4_x1c_venue_response.py"
X1B_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
ARTIFACTS = ROOT / "results" / "m4_x1c_venue_response"
REPORT = ROOT / "reports" / "SUICA_M4_X1C_VENUE_RESPONSE_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"

BASELINE_PRE_EXISTING_HITS = 4          # #83: the HEAD collisions X1b recorded


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x1c_venue_response", SCRIPT)


# ---------------------------------------------------------------------------
# helpers — small synthetic designs, no corpus needed
# ---------------------------------------------------------------------------


def _skeleton(n_authors=180, n_comms=24, k=6, seed=3, ragged=True):
    """A connected author x community skeleton with UNEQUAL cell sizes.

    The cell sizes matter twice over. The marginal targets are size-weighted,
    so a skeleton with equal cells would let a wrong (1/k) formula pass; and
    the two halves of a cell must be CORRELATED in size the way real cells
    are (a busy venue is busy in both halves), because that correlation is
    what makes the exact composition weight exceed 1/k.
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
    return MOD.Design(slot_author=sa, slot_comm=sc, n_e=n_e, n_l=n_l,
                      s_e=zeros.copy(), s_l=zeros.copy(),
                      q_e=zeros.copy(), q_l=zeros.copy(),
                      n_authors=n_authors, n_comms=n_comms,
                      author_codes=np.arange(n_authors, dtype=np.int64))


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                            # pragma: no cover
        pytest.skip("the X1c run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. inheritance — X1c is BOUND to the committed X1b objects (#56/#81)
# ---------------------------------------------------------------------------


INHERITED = ("Design", "build_chain_design", "fe_residual", "fe_pair",
             "fe_exactness", "permutation_null_fe", "cluster_bootstrap_fe",
             "analyse_design_fe", "recover_shares_fe", "synthetic_design",
             "synthetic_world_block", "composition_diagnostics",
             "load_cell_cache", "law_vocabulary", "bipartite_lcc",
             "variance_budget", "per_author_correlations", "headroom_report",
             "magnitude_cells", "point_cell", "anchor_gate",
             "scan_for_cohort_ids", "new_hits_only", "baseline_hit_keys")


def test_the_machinery_is_imported_by_file_and_not_copied():
    """Provenance: every inherited name IS X1b's object, not a lookalike."""

    assert Path(MOD.X1B.__file__).resolve() == X1B_SCRIPT.resolve()
    assert Path(MOD.X1.__file__).resolve() == (
        ROOT / "scripts" / "run_suica_m4_x1_venue_response.py").resolve()
    assert MOD.X1 is MOD.X1B.X1
    source = SCRIPT.read_text(encoding="utf-8")
    for name in INHERITED:
        assert getattr(MOD, name) is getattr(MOD.X1B, name), name
        assert f"\ndef {name}(" not in source, name
        assert f"\nclass {name}" not in source, name


def test_the_registration_pins_are_the_inherited_ones():
    x1b = MOD.X1B
    for name in ("SEED", "B_PERM", "B_BOOT", "SEED_PART0", "SEED_PERM",
                 "SEED_BOOT", "N_MIN_PRIMARY", "N_MIN_SENSITIVITY", "K_MIN",
                 "S_PRIMARY", "S_SENSITIVITY", "S_CENSUS", "FE_TOL",
                 "BIG5_POWER_FLOOR", "TRACE_MAX", "IDIOSYNCRATIC_MAX",
                 "LEAN_R", "LEAN_INTERACTION", "LEAN_AUTHOR_MAIN",
                 "LEAN_COMMUNITY_MAIN", "PLANTED_SHARES", "NULL_SHARES",
                 "ABLATION_WORLDS", "N_SYNTH_REPLICATES", "TOL_SD_MULT",
                 "TOL_FLOOR", "ABLATION_LEAK_MAX", "CHAIN_ANCHORS",
                 "ANCHOR_ROWS_PARSEABLE", "ANCHOR_AUTHORS",
                 "ANCHOR_LAW_VOCAB", "ARM_LABELS"):
        assert getattr(MOD, name) == getattr(x1b, name), name
    # the values the registration writes out in words
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499 and MOD.B_BOOT == 1000
    assert MOD.TRACE_MAX == 0.02 and MOD.IDIOSYNCRATIC_MAX == 0.10
    assert MOD.BIG5_POWER_FLOOR == 300


def test_the_seeds_were_not_re_chosen_after_the_two_stops():
    """#76: gate-shopping is refused; the seeds come from X1's derivation."""

    assert MOD.SEED_PART0 == MOD.SEED + 1
    assert MOD.SEED_PERM == MOD.SEED + 2
    assert MOD.SEED_BOOT == MOD.SEED + 3


def test_x1c_inherits_the_registered_boundaries_and_adds_exactly_one():
    """Six inherited boundaries plus X1c's own; two restored to X1's tense.

    X1b wrote the first two in the subjunctive because its A1 stop made no
    claim. X1c reaches a cell, so the registration's own indicative wording is
    the correct inheritance — and the leg must not describe a claim it made as
    a claim it would have made.
    """

    x1b, x1 = MOD.X1B, MOD.X1
    assert len(MOD.BOUNDARIES) == len(x1b.BOUNDARIES) + 1
    assert MOD.BOUNDARIES[0] == x1.BOUNDARIES[0]
    assert MOD.BOUNDARIES[1] == x1.BOUNDARIES[1]
    assert MOD.BOUNDARIES[2:6] == tuple(x1b.BOUNDARIES[2:6])
    assert "would have been" not in MOD.BOUNDARIES[0]
    assert "a detection is a lower bound" in MOD.BOUNDARIES[1]
    assert "WELL-SHARED VENUES" in MOD.BOUNDARIES[5]
    assert "DF-CORRECTED" in MOD.BOUNDARIES[-1]
    assert "MARGINAL" in MOD.BOUNDARIES[-1]


# ---------------------------------------------------------------------------
# 2. the df correction (#86c)
# ---------------------------------------------------------------------------


def test_the_df_formula_on_a_toy():
    """P = 20, A = 4, C = 5 → rank 8, residual df 12, factor 20/12."""

    sa = np.repeat(np.arange(4), 5).astype(np.int64)
    sc = np.tile(np.arange(5), 4).astype(np.int64)
    zeros = np.zeros(20)
    design = MOD.Design(slot_author=sa, slot_comm=sc,
                        n_e=np.full(20, 7.0), n_l=np.full(20, 7.0),
                        s_e=zeros.copy(), s_l=zeros.copy(),
                        q_e=zeros.copy(), q_l=zeros.copy(),
                        n_authors=4, n_comms=5,
                        author_codes=np.arange(4, dtype=np.int64))
    dfc = MOD.df_correction(design)
    assert dfc["P_shared_pairs"] == 20
    assert dfc["A_authors"] == 4 and dfc["C_communities"] == 5
    assert dfc["rank_removed"] == 8
    assert dfc["residual_df"] == 12
    assert dfc["retained_fraction"] == pytest.approx(12 / 20)
    assert dfc["factor"] == pytest.approx(20 / 12)
    assert dfc["factor"] * dfc["retained_fraction"] == pytest.approx(1.0)


def test_the_df_factor_matches_x1bs_measured_retained_fraction():
    """X1b's composition diagnostic and X1c's correction are one object."""

    skeleton = _skeleton()
    dfc = MOD.df_correction(skeleton)
    old = MOD.composition_diagnostics(skeleton)
    assert dfc["retained_fraction"] == pytest.approx(
        old["fe_retained_fraction"])
    assert dfc["rank_removed"] == old["fe_rank_removed"]


def test_the_df_correction_undoes_the_projection_loss_on_a_planted_world():
    """The clause the registration promotes to ROUTING, on a small world."""

    skeleton = _skeleton(n_authors=250, n_comms=30, k=7, seed=17)
    factor = MOD.df_correction(skeleton)["factor"]
    raw = []
    for rep in range(12):
        rng = np.random.default_rng(400 + rep)
        world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES, rng)
        raw.append(MOD.recover_shares_fe(world)["interaction"])
    raw_mean = float(np.mean(raw))
    corrected = raw_mean * factor
    assert raw_mean < MOD.PLANTED_SHARES["interaction"]        # conservative
    assert corrected == pytest.approx(MOD.PLANTED_SHARES["interaction"],
                                      abs=0.002)


def test_the_correction_is_a_positive_affine_map_so_zero_coverage_survives():
    """Cell 1's "the CI covers 0" is the same event on both scales."""

    dfc = MOD.df_correction(_skeleton())
    factor = dfc["factor"]
    assert factor > 1.0
    for lo, hi in ((-0.01, 0.01), (0.001, 0.02), (-0.05, -0.001)):
        raw_covers = lo <= 0.0 <= hi
        scaled = MOD._scale([lo, hi], factor)
        assert (scaled[0] <= 0.0 <= scaled[1]) == raw_covers
        assert scaled[0] < scaled[1]


def test_the_block_corrector_rescales_every_replicate_and_adds_no_draw(
        tmp_path):
    skeleton = _skeleton(n_authors=60, n_comms=10, k=4)
    log = MOD.RunLog(tmp_path / "block.jsonl")
    block = MOD.synthetic_world_block(skeleton, MOD.NULL_SHARES, "unit",
                                      101, 3, log)
    raw_values = list(block["stats"]["interaction"]["values"])
    factor = MOD.df_correction(skeleton)["factor"]
    MOD._block_corrected(block, factor)
    got = block["stats"]["interaction_corr"]["values"]
    assert got == pytest.approx([v * factor for v in raw_values])
    assert block["stats"]["interaction"]["values"] == raw_values


# ---------------------------------------------------------------------------
# 3. the MARGINAL-TARGET derivation (#86b), against a simulated design
# ---------------------------------------------------------------------------


def test_the_marginal_targets_reduce_to_the_planted_values_when_nothing_mixes():
    """With only one component planted there is nothing to compose."""

    skeleton = _skeleton()
    only_author = {"author": 0.30, "community": 0.0, "interaction": 0.0}
    tg = MOD.marginal_targets(skeleton, only_author)
    assert tg["author"]["composition_term"] == 0.0
    assert tg["author"]["target"] == pytest.approx(0.30 * (1 - 1 / 180))
    # the community marginal is PURE contamination in that world
    assert tg["community"]["planted_component"] == 0.0
    assert tg["community"]["target"] > 0.0


def test_kappa_equals_one_over_k_when_the_cells_are_equally_sized():
    """The X1b heuristic is the equal-size special case of the exact term."""

    flat = _skeleton(n_authors=100, n_comms=20, k=5, ragged=False)
    tg = MOD.marginal_targets(flat, MOD.PLANTED_SHARES)
    assert tg["author"]["mean_kappa"] == pytest.approx(1.0 / 5)
    assert tg["author"]["mean_inverse_k"] == pytest.approx(1.0 / 5)
    ragged = _skeleton(n_authors=100, n_comms=20, k=5, ragged=True)
    tr = MOD.marginal_targets(ragged, MOD.PLANTED_SHARES)
    # with unequal cells the composition weight is STRICTLY larger than 1/k,
    # which is exactly why the X1b heuristic under-predicted the bias
    assert tr["author"]["mean_kappa"] > tr["author"]["mean_inverse_k"]


def test_the_marginal_targets_are_recovered_on_a_simulated_design():
    """The derivation, checked the only way that counts: by simulation.

    Forty replicates of the planted world on a ragged simulated skeleton; the
    MEAN of the estimator must land on the pinned target inside a few
    standard errors, and — the part that matters — much closer to the target
    than to the planted variance component it is so often mistaken for.
    """

    skeleton = _skeleton(n_authors=400, n_comms=40, k=7, seed=29)
    tg = MOD.marginal_targets(skeleton, MOD.PLANTED_SHARES)
    author, community = [], []
    for rep in range(40):
        rng = np.random.default_rng(9_000 + rep)
        world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES, rng)
        got = MOD.recover_shares_fe(world)
        author.append(got["author"])
        community.append(got["community"])
    for values, key in ((author, "author"), (community, "community")):
        mean = float(np.mean(values))
        se = float(np.std(values, ddof=1)) / math.sqrt(len(values))
        target = tg[key]["target"]
        planted = MOD.PLANTED_SHARES[key]
        assert abs(mean - target) < 4.0 * se, (key, mean, target, se)
        assert abs(mean - target) < abs(mean - planted), key


def test_the_marginal_targets_use_only_the_design():
    """No y, planted or real, may enter a target — swap the y and re-check."""

    skeleton = _skeleton()
    before = MOD.marginal_targets(skeleton, MOD.PLANTED_SHARES)
    rng = np.random.default_rng(5)
    world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES, rng)
    after = MOD.marginal_targets(world, MOD.PLANTED_SHARES)
    assert after["author"]["target"] == pytest.approx(
        before["author"]["target"])
    assert after["community"]["target"] == pytest.approx(
        before["community"]["target"])


def test_the_printed_formula_matches_the_computed_target():
    """Rule 24 in miniature: the report prints a formula that is the code."""

    skeleton = _skeleton(n_authors=150, n_comms=20, k=5, seed=7)
    shares = MOD.PLANTED_SHARES
    tg = MOD.marginal_targets(skeleton, shares)
    sa, sc = skeleton.slot_author, skeleton.slot_comm
    A, C = skeleton.n_authors, skeleton.n_comms
    v_a, v_c, v_g = shares["author"], shares["community"], shares["interaction"]
    a_ne = np.bincount(sa, skeleton.n_e, A)
    a_nl = np.bincount(sa, skeleton.n_l, A)
    w_e = skeleton.n_e / a_ne[sa]
    w_l = skeleton.n_l / a_nl[sa]
    kappa = np.bincount(sa, w_e * w_l, A)
    wbar_e = np.bincount(sc, w_e, C) / A
    wbar_l = np.bincount(sc, w_l, C) / A
    hand_a = (v_a * (1 - 1 / A) + (v_c + v_g) * kappa.mean()
              - v_c * float((wbar_e * wbar_l).sum())
              - v_g * float(kappa.mean()) / A)
    assert tg["author"]["target"] == pytest.approx(hand_a)
    c_ne = np.bincount(sc, skeleton.n_e, C)
    c_nl = np.bincount(sc, skeleton.n_l, C)
    t_e = skeleton.n_e / c_ne[sc]
    t_l = skeleton.n_l / c_nl[sc]
    lam = np.bincount(sc, t_e * t_l, C)
    what = (c_ne + c_nl) / (c_ne + c_nl).sum()
    phi_e = np.bincount(sa, what[sc] * t_e, A)
    phi_l = np.bincount(sa, what[sc] * t_l, A)
    hand_c = (v_c * (1 - float((what ** 2).sum()))
              + v_a * (float((what * lam).sum()) - float((phi_e * phi_l).sum()))
              + v_g * (float((what * lam).sum())
                       - float((what ** 2 * lam).sum())))
    assert tg["community"]["target"] == pytest.approx(hand_c)


def test_the_decontamination_annotation_inverts_its_own_mixing():
    """Annotation arithmetic: plant the mixing, recover the components."""

    kappa, lam = 0.29, 0.094
    v_a, v_c, v_g = 0.31, 0.06, 0.019
    marginal_a = v_a + kappa * (v_c + v_g)
    marginal_c = v_c + lam * (v_a + v_g)
    got = MOD.decontaminate(marginal_a, marginal_c, v_g, kappa, lam)
    assert got["solvable"] is True
    assert got["implied_author_main"] == pytest.approx(v_a)
    assert got["implied_community_main"] == pytest.approx(v_c)


# ---------------------------------------------------------------------------
# 4. the CLAUSE-SEPARATED gate (#86a) — both directions
# ---------------------------------------------------------------------------


def test_gate_status_routes_on_routing_and_annotates_on_descriptive():
    ok = {"a": "PASS", "b": "PASS"}
    bad = {"a": "PASS", "b": "FAIL"}
    assert MOD.gate_status(ok, ok) == ("PASS", "PASS")
    assert MOD.gate_status(ok, bad) == ("PASS", MOD.DESCRIPTIVE_ANNOTATED)
    assert MOD.gate_status(bad, ok) == ("FAIL", "PASS")
    assert MOD.gate_status(bad, bad) == ("FAIL", MOD.DESCRIPTIVE_ANNOTATED)


def test_the_a1_stop_reads_the_routing_family_only():
    assert MOD.a1_stop_fires({"routing_status": "FAIL",
                              "descriptive_status": "PASS"}) is True
    assert MOD.a1_stop_fires({"routing_status": "PASS",
                              "descriptive_status":
                                  MOD.DESCRIPTIVE_ANNOTATED}) is False


GATE_FIXTURE = dict(n_authors=300, n_comms=30, k=7, seed=23)
GATE_B = 32


def test_the_gate_runs_end_to_end_and_separates_its_two_families(tmp_path):
    skeleton = _skeleton(**GATE_FIXTURE)
    log = MOD.RunLog(tmp_path / "gate.jsonl")
    gate = MOD.clause_separated_gate(skeleton, b_perm=GATE_B, b_boot=GATE_B,
                                     log=log)
    assert gate["routing_status"] == "PASS"          # the honest fixture
    assert gate["descriptive_status"] == "PASS"
    assert gate["n_routing"] == 5
    assert gate["n_descriptive"] == 2
    assert set(gate["descriptives"]) == {"author", "community"}
    assert gate["status"] == gate["routing_status"]
    assert gate["routing_status"] == ("PASS" if gate["n_routing_passed"] == 5
                                      else "FAIL")
    # the recovery clause that ROUTES is the CORRECTED one
    rec = gate["recovery_interaction"]
    assert rec["target"] == MOD.PLANTED_SHARES["interaction"]
    assert rec["df_factor"] == pytest.approx(
        MOD.df_correction(skeleton)["factor"])
    assert rec["recovered_mean"] == pytest.approx(
        rec["raw_recovered_mean"] * rec["df_factor"])
    # both scales are on the record for the null world (#67)
    hon = gate["honesty"]
    assert hon["interaction_share_corr"] == pytest.approx(
        hon["interaction_share_raw"] * gate["df_correction"]["factor"])
    assert hon["interaction_ci_corr"] == pytest.approx(
        [v * gate["df_correction"]["factor"]
         for v in hon["interaction_ci_raw"]])


def test_a_DESCRIPTIVE_failure_annotates_and_does_NOT_stop(tmp_path,
                                                           monkeypatch):
    """Direction one: break the descriptives, the leg must still route."""

    skeleton = _skeleton(**GATE_FIXTURE)
    honest_targets = MOD.marginal_targets
    honest = MOD.clause_separated_gate(skeleton, b_perm=GATE_B,
                                       b_boot=GATE_B,
                                       log=MOD.RunLog(tmp_path / "ok.jsonl"))

    def absurd(design, shares):
        real = honest_targets(design, shares)
        for key in ("author", "community"):
            real[key]["target"] = -5.0
        return real

    monkeypatch.setattr(MOD, "marginal_targets", absurd)
    log = MOD.RunLog(tmp_path / "gate_desc.jsonl")
    gate = MOD.clause_separated_gate(skeleton, b_perm=GATE_B, b_boot=GATE_B,
                                     log=log)
    assert all(v == "FAIL" for v in gate["descriptive_clauses"].values())
    assert gate["descriptive_status"] == MOD.DESCRIPTIVE_ANNOTATED
    assert gate["routing_status"] == "PASS"
    assert gate["status"] == "PASS"
    assert MOD.a1_stop_fires(gate) is False
    assert len(gate["annotations"]) == 2
    for note in gate["annotations"]:
        assert note.startswith("#67 DUAL STAMP")
        assert "does not route" in note
    # the routing family is BIT-FOR-BIT what it was before the descriptives
    # were broken: a descriptive failure cannot move the verdict
    assert gate["routing_clauses"] == honest["routing_clauses"]
    assert gate["recovery_interaction"] == honest["recovery_interaction"]
    assert gate["honesty"] == honest["honesty"]


def test_a_ROUTING_failure_stops_regardless_of_the_descriptives(tmp_path,
                                                                monkeypatch):
    """Direction two: break a routing clause, the A1 stop must fire."""

    skeleton = _skeleton(**GATE_FIXTURE)
    honest = MOD.df_correction(skeleton)

    def inflated(design):
        out = dict(honest)
        out["factor"] = honest["factor"] * 6.0
        return out

    monkeypatch.setattr(MOD, "df_correction", inflated)
    log = MOD.RunLog(tmp_path / "gate_route.jsonl")
    gate = MOD.clause_separated_gate(skeleton, b_perm=GATE_B, b_boot=GATE_B,
                                     log=log)
    assert gate["routing_clauses"][
        "(i) recovery — DF-CORRECTED interaction share within "
        "max(0.01, 3 x replicate sd)"] == "FAIL"
    assert gate["routing_status"] == "FAIL"
    assert gate["status"] == "FAIL"
    assert MOD.a1_stop_fires(gate) is True
    # the descriptives are untouched by a routing failure
    assert gate["descriptive_status"] in {"PASS", MOD.DESCRIPTIVE_ANNOTATED}


def test_the_a1_stop_verdict_names_only_routing_clauses():
    part0 = {"routing_status": "FAIL", "n_routing": 5, "n_routing_passed": 4,
             "routing_clauses": {"(iii) null world — R inside its permutation "
                                 "band": "FAIL", "other": "PASS"},
             "descriptive_clauses": {"x": "FAIL"}}
    verdict = MOD.build_verdict({}, {}, False, part0)
    assert verdict["cell"] == MOD.CELL_A1_STOP
    assert verdict["clauses_failed"] == ["(iii) null world — R inside its "
                                         "permutation band"]
    assert "no corpus value" in verdict["sentence"]


# ---------------------------------------------------------------------------
# 5. the cell rule and the leans, now keyed on the corrected share
# ---------------------------------------------------------------------------


def _arm(raw, ci_raw, r, band, factor=1.1712502294841196):
    return {"budget": {"interaction": raw, "author": 0.3, "community": 0.08,
                       "residual": 0.6},
            "bootstrap": {"shares_ci": {"interaction": list(ci_raw)},
                          "r_ci": [r - 0.01, r + 0.01]},
            "null": {"r_band": list(band), "interaction_band": [-0.001, 0.001]},
            "R": r,
            "df": {"factor": factor},
            "share_raw": raw, "share_corr": raw * factor,
            "share_ci_raw": list(ci_raw),
            "share_ci_corr": [v * factor for v in ci_raw]}


def test_the_cell_reads_the_corrected_share_not_the_raw_one():
    """A raw share below 0.02 whose CORRECTED value is above it must move."""

    raw = 0.019                                       # corrected ≈ 0.02225
    arm = _arm(raw, (0.018, 0.020), 0.4, (-0.02, 0.02))
    cell = MOD.classify(arm)
    assert cell["share_raw"] == pytest.approx(raw)
    assert cell["share_corr"] > MOD.TRACE_MAX
    assert cell["cell"] == MOD.CELL_IDIOSYNCRATIC
    assert MOD.point_cell(raw) == MOD.CELL_TRACE      # the raw scale disagrees


def test_the_null_cell_still_needs_both_of_its_conditions():
    inside = _arm(0.0, (-0.01, 0.01), 0.01, (-0.02, 0.02))
    assert MOD.classify(inside)["cell"] == MOD.CELL_NO_RESPONSE
    r_outside = _arm(0.0, (-0.01, 0.01), 0.5, (-0.02, 0.02))
    assert MOD.classify(r_outside)["cell"] != MOD.CELL_NO_RESPONSE
    ci_excludes = _arm(0.03, (0.025, 0.035), 0.01, (-0.02, 0.02))
    assert MOD.classify(ci_excludes)["cell"] == MOD.CELL_IDIOSYNCRATIC


def test_straddles_are_reported_as_straddles():
    straddle = MOD.classify(_arm(0.016, (0.010, 0.030), 0.4, (-0.02, 0.02)))
    assert straddle["straddle"] is True
    assert MOD.CELL_TRACE in straddle["touched"]
    assert MOD.CELL_IDIOSYNCRATIC in straddle["touched"]
    major = MOD.classify(_arm(0.20, (0.15, 0.25), 0.4, (-0.02, 0.02)))
    assert major["cell"] == MOD.CELL_MAJOR


def test_the_share_lean_is_reported_on_both_scales_with_its_scale_named():
    arm = _arm(0.016, (0.010, 0.022), 0.20, (-0.02, 0.02))
    arm["budget"]["author"] = 0.30
    arm["budget"]["community"] = 0.08
    rows = MOD.evaluate_leans(arm, MOD.CELL_TRACE, MOD.CELL_TRACE)
    share_rows = [r for r in rows if "interaction share" in r["lean"]]
    assert len(share_rows) == 2
    assert "RAW" in share_rows[0]["scale"]
    assert "registered" in share_rows[0]["scale"]
    assert "DF-CORRECTED" in share_rows[1]["scale"]
    assert share_rows[0]["observed"] == pytest.approx(arm["share_raw"])
    assert share_rows[1]["observed"] == pytest.approx(arm["share_corr"])
    names = [r["lean"] for r in rows]
    assert any("marginal author share" in n for n in names)
    assert any("marginal community share" in n for n in names)
    assert not any("author main share" in n for n in names)


def test_augment_arm_attaches_the_correction_and_the_annotation():
    skeleton = _skeleton(n_authors=90, n_comms=12, k=4, seed=31)
    arm = _arm(0.02, (0.01, 0.03), 0.2, (-0.02, 0.02))
    arm.pop("df")
    arm.pop("share_raw")
    arm.pop("share_corr")
    arm.pop("share_ci_raw")
    arm.pop("share_ci_corr")
    out = MOD.augment_arm(arm, skeleton)
    factor = MOD.df_correction(skeleton)["factor"]
    assert out["share_corr"] == pytest.approx(0.02 * factor)
    assert out["share_band_corr"] == pytest.approx(
        [v * factor for v in out["share_band_raw"]])
    assert out["composition"]["mean_kappa"] > 0
    assert out["decontamination_annotation"]["solvable"] is True


# ---------------------------------------------------------------------------
# 6. the #83 ID-leak helper and the commit hygiene
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
    assert names == {"SUICA_M4_X1C_VENUE_RESPONSE_REPORT.md",
                     "run_suica_m4_x1c_venue_response.py",
                     "test_m4_x1c_venue_response.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_results_stay_out_of_the_commit():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore


# ---------------------------------------------------------------------------
# 7. the committed run (skipped where the artifacts were not produced)
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


def test_committed_run_scored_both_clause_families_separately():
    part0 = _artifact("part0_clause_separated_gate.json")
    assert part0["n_routing"] == 5
    assert part0["n_descriptive"] == 2
    assert set(part0["routing_clauses"]).isdisjoint(
        set(part0["descriptive_clauses"]))
    assert part0["routing_status"] == (
        "PASS" if part0["n_routing_passed"] == 5 else "FAIL")
    assert part0["null_block"]["planted"]["interaction"] == 0.0
    assert part0["planted_block"]["replicates"] == MOD.N_SYNTH_REPLICATES
    assert (len(part0["annotations"]) ==
            part0["n_descriptive"] - part0["n_descriptive_passed"])


def test_committed_run_pinned_the_realized_df_correction():
    part0 = _artifact("part0_clause_separated_gate.json")
    dfc = part0["df_correction"]
    assert dfc["P_shared_pairs"] == 31_899
    assert dfc["A_authors"] == 3_665
    assert dfc["C_communities"] == 1_000
    assert dfc["residual_df"] == 31_899 - 3_665 - 1_000 + 1
    assert dfc["factor"] == pytest.approx(31_899 / 27_235)


def test_committed_run_honoured_the_a1_stop():
    """Real estimands may exist only when every ROUTING clause passed."""

    part0 = _artifact("part0_clause_separated_gate.json")
    verdict = _artifact("verdict.json")
    if part0["routing_status"] == "PASS":
        assert verdict["cell"] != MOD.CELL_A1_STOP
        assert (ARTIFACTS / "arms.json").exists()
        assert (ARTIFACTS / "cells.json").exists()
        assert (ARTIFACTS / "leans.json").exists()
    else:                                            # pragma: no cover
        assert verdict["cell"] == MOD.CELL_A1_STOP
        assert not (ARTIFACTS / "arms.json").exists()


def test_committed_run_verified_the_projection_on_the_real_incidence():
    part0 = _artifact("part0_clause_separated_gate.json")
    exact = part0["honesty"]["fe_exactness"]
    assert max(exact.values()) <= 1e-10
    assert part0["honesty"]["fe"]["change_early"] <= MOD.FE_TOL
    assert part0["honesty"]["fe"]["change_late"] <= MOD.FE_TOL


def test_committed_arms_route_on_the_corrected_share():
    arms = _artifact("arms.json")
    cells = _artifact("cells.json")
    assert set(arms) == set(MOD.ARM_LABELS)
    for key, arm in arms.items():
        factor = arm["df"]["factor"]
        assert arm["share_corr"] == pytest.approx(arm["share_raw"] * factor)
        assert arm["share_ci_corr"] == pytest.approx(
            [v * factor for v in arm["share_ci_raw"]])
        assert cells[key]["share_corr"] == pytest.approx(arm["share_corr"])
        assert cells[key]["cell"] in {MOD.CELL_NO_RESPONSE, MOD.CELL_TRACE,
                                      MOD.CELL_IDIOSYNCRATIC, MOD.CELL_MAJOR}
        assert MOD.classify(arm)["cell"] == cells[key]["cell"]


def test_committed_run_censused_the_big5_arm_against_the_69_floor():
    power = _artifact("big5_power.json")
    assert power["floor"] == MOD.BIG5_POWER_FLOOR
    assert power["meets_floor"] == (power["authors"] >= power["floor"])
    designs = _artifact("arm_designs.json")
    assert designs["replication_big5"]["authors"] == power["authors"]
    assert set(designs) == set(MOD.ARM_LABELS)


def test_committed_flags_73_follow_the_cells():
    cells = _artifact("cells.json")
    flags = _artifact("flags_73.json")
    power = _artifact("big5_power.json")
    primary = cells["primary"]["cell"]
    for key, cell in cells.items():
        if key == "primary":
            assert key not in flags
            continue
        if key == "replication_big5" and not power["meets_floor"]:
            continue                                 # pragma: no cover
        if cell["cell"] != primary:
            assert key in flags and flags[key].startswith("#73")
        else:
            assert key not in flags


def test_committed_report_matches_the_committed_verdict():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X1c report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**VERDICT — {verdict['cell']}.**" in text
    for heading in ("## Leg lineage", "### ROUTING clauses (A1-stopping)",
                    "### DESCRIPTIVE clauses (report-gated",
                    "## The budget, per arm", "## Headroom",
                    "## Boundaries", "## Configuration"):
        assert heading in text
    for boundary_head in ("Metadata only", "projection caution",
                          "No psychological naming", "EXPLORATORY",
                          "Cohort composition", "WELL-SHARED VENUES",
                          "DF-CORRECTED"):
        assert boundary_head in text


def test_committed_report_carries_the_numbers_from_the_artifacts():
    if not REPORT.exists():                          # pragma: no cover
        pytest.skip("the X1c report has not been produced in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    part0 = _artifact("part0_clause_separated_gate.json")
    for name in part0["routing_clauses"]:
        assert name in text
    for name in part0["descriptive_clauses"]:
        assert name in text
    for key in ("author", "community"):
        row = part0["descriptives"][key]
        assert f"{row['target']:.4f}" in text
        assert f"{row['recovered_mean']:.4f}" in text
    arms = _artifact("arms.json")
    for arm in arms.values():
        assert f"{arm['share_corr']:.4f}" in text
        assert f"{arm['share_raw']:.4f}" in text
    chain = _artifact("chain_census.json")
    for row in chain.values():
        assert f"{row['shared_pairs']:,}" in text


def test_committed_run_cleared_the_id_leak_gate():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS
    assert scan["n_pre_existing_hits"] == BASELINE_PRE_EXISTING_HITS


def test_committed_outcome_was_appended_to_the_registration():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X1c outcome (executor, 2026-08-19)" in text
    verdict = _artifact("verdict.json")
    assert verdict["cell"] in text


def test_the_claims_ledger_carries_exactly_one_x1c_row():
    text = LEDGER.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| M4-X1c ")]
    assert len(rows) == 1
    for token in ("EXPLORATORY", "corpus-level", "label-free",
                  "metadata-only", "X1b", "X1c"):
        assert token in rows[0]
