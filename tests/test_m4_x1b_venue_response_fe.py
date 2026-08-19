"""Contract tests for SUICA M4-X1b — the venue response, exact estimator.

The registration (``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X1b", commit 0f8e43e) names the objects these tests pin: exactness of the
alternating-projection two-way fixed effects on a hand toy AND on the realized
skeleton, the full Part 0 gate battery, reproduction of the planner's
predicate-chain census at s = 3 / 5 / 8, the largest-connected-component
assertion the exactness argument rests on, the correctness of the bootstrap's
weighted FE against an explicitly duplicated design, and the #83 ID-leak
helper over the widened 10,296-name universe.
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
SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
ARTIFACTS = ROOT / "results" / "m4_x1b_venue_response_fe"
REPORT = ROOT / "reports" / "SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs" / "CLAIMS_LEDGER.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x1b_venue_response_fe", SCRIPT)

EXACT = 1e-10


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _group_means(values, index, size):
    counts = np.maximum(np.bincount(index, None, size).astype(float), 1.0)
    return np.bincount(index, values, size) / counts


def _incomplete_toy():
    """A deliberately incomplete, connected author x community grid.

    Six authors, four communities, three or four communities each — the shape
    that makes a single double-centering wrong and an alternating projection
    right.
    """

    pairs = [(0, 0), (0, 1), (0, 2),
             (1, 0), (1, 1), (1, 3),
             (2, 1), (2, 2), (2, 3),
             (3, 0), (3, 2), (3, 3),
             (4, 0), (4, 1), (4, 2), (4, 3),
             (5, 1), (5, 2), (5, 3)]
    slot_author = np.array([p[0] for p in pairs], dtype=np.int64)
    slot_comm = np.array([p[1] for p in pairs], dtype=np.int64)
    return slot_author, slot_comm, 6, 4


def _design(slot_author, slot_comm, n_authors, n_comms, mean_e, mean_l,
            n_per_cell=12.0):
    m = slot_author.size
    n = np.full(m, float(n_per_cell))
    return MOD.Design(
        slot_author=slot_author.astype(np.int64),
        slot_comm=slot_comm.astype(np.int64),
        n_e=n, n_l=n.copy(),
        s_e=np.asarray(mean_e, float) * n,
        s_l=np.asarray(mean_l, float) * n,
        q_e=n * np.asarray(mean_e, float) ** 2 + n,
        q_l=n * np.asarray(mean_l, float) ** 2 + n,
        n_authors=int(n_authors), n_comms=int(n_comms),
        author_codes=np.arange(n_authors, dtype=np.int64))


def _toy_table(rows, n_subs=8):
    """A hand cell table in the cache's own layout.

    ``rows`` are (author, community, half, n, mean) tuples; the sufficient
    statistics are built so the cell mean is exactly ``mean``.
    """

    author = np.array([r[0] for r in rows], dtype=np.int32)
    comm = np.array([r[1] for r in rows], dtype=np.int32)
    half = np.array([r[2] for r in rows], dtype=np.int8)
    n = np.array([r[3] for r in rows], dtype=np.int64)
    mean = np.array([r[4] for r in rows], dtype=float)
    return {
        "cell_author": author, "cell_comm": comm, "cell_half": half,
        "cell_n": n, "s_wcq": mean * n, "q_wcq": n * mean ** 2 + n,
        "s_wc": mean * n * 2.0, "q_wc": n * (mean * 2.0) ** 2 + n,
        "n_subs": n_subs,
    }


_REALIZED: dict[str, object] = {}


def _realized_primary():
    """The PRIMARY X1b design, rebuilt from X1's committed cell cache."""

    if "design" in _REALIZED:
        return _REALIZED["design"], _REALIZED["chain"]
    cache = MOD.DEFAULT_X1_CACHE
    meta = cache.with_suffix(".meta.json")
    if not (cache.exists() and meta.exists() and MOD.DEFAULT_COHORT.exists()):
        pytest.skip("X1's cell cache is not present in this checkout")
    blob = np.load(cache)
    info = json.loads(meta.read_text(encoding="utf-8"))
    table = {k: blob[k] for k in blob.files}
    table["n_subs"] = len(info["subreddits"])
    table["n_authors"] = len(info["authors"])
    names = info["authors"]
    code = {name: i for i, name in enumerate(names)}
    cohort = pd.read_csv(MOD.DEFAULT_COHORT, usecols=["author"])
    big5 = np.zeros(len(names), dtype=bool)
    for name in {str(x) for x in cohort["author"]}:
        if name in code:
            big5[code[name]] = True
    disjoint = ~big5
    users = np.bincount(
        table["pair_comm"][disjoint[table["pair_author"]]].astype(np.int64),
        minlength=table["n_subs"])
    seen = int(np.unique(
        table["pair_author"][disjoint[table["pair_author"]]]).size)
    floor = max(1, int(math.ceil(MOD.VOCAB_FLOOR_FRACTION * seen)))
    vocab = users >= floor
    design, chain = MOD.build_chain_design(
        table, disjoint, n_min=MOD.N_MIN_PRIMARY, support=MOD.S_PRIMARY,
        vocab_mask=vocab)
    _REALIZED["table"] = table
    _REALIZED["disjoint"] = disjoint
    _REALIZED["big5"] = big5
    _REALIZED["vocab"] = vocab
    _REALIZED["floor"] = floor
    _REALIZED["design"] = design
    _REALIZED["chain"] = chain
    return design, chain


# ---------------------------------------------------------------------------
# 1. the repair: alternating-projection FE exactness
# ---------------------------------------------------------------------------


def test_fe_matches_double_centering_on_a_complete_grid():
    """On a COMPLETE grid the two estimators are the same object."""

    slot_author = np.repeat(np.arange(4), 5).astype(np.int64)
    slot_comm = np.tile(np.arange(5), 4).astype(np.int64)
    values = np.arange(20, dtype=float) ** 1.3 + 7.0
    v, sweeps, change = MOD.fe_residual(values, slot_author, slot_comm, 4, 5)
    old = MOD.double_center(values, slot_author, slot_comm, 4, 5)
    assert sweeps <= 3
    assert change <= MOD.FE_TOL
    assert np.abs(v - old).max() < 1e-12


def test_fe_is_exact_on_an_incomplete_hand_toy():
    """The registered exactness clause: both residual group means are zero."""

    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(11)
    values = (rng.normal(0, 2.0, A)[sa] + rng.normal(0, 1.0, C)[sc]
              + rng.normal(0, 0.3, sa.size))
    v, _, change = MOD.fe_residual(values, sa, sc, A, C)
    assert change <= EXACT
    assert np.abs(_group_means(v, sa, A)).max() <= EXACT
    assert np.abs(_group_means(v, sc, C)).max() <= EXACT


def test_double_centering_is_NOT_exact_on_the_same_toy():
    """The defect X1b repairs, pinned so it cannot silently come back."""

    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(11)
    values = (rng.normal(0, 2.0, A)[sa] + rng.normal(0, 1.0, C)[sc]
              + rng.normal(0, 0.3, sa.size))
    old = MOD.double_center(values, sa, sc, A, C)
    # a SINGLE simultaneous double-centering leaves both group means alive on
    # an incomplete grid; the alternating projection drives both to zero
    assert np.abs(_group_means(old, sa, A)).max() > 1e-3
    assert np.abs(_group_means(old, sc, C)).max() > 1e-3
    new, _, _ = MOD.fe_residual(values, sa, sc, A, C)
    assert np.abs(_group_means(new, sa, A)).max() <= EXACT
    assert np.abs(_group_means(new, sc, C)).max() <= EXACT


def test_fe_annihilates_pure_mains_on_an_incomplete_grid():
    """A world that is ONLY mains must project to exactly zero."""

    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(3)
    a = rng.normal(0, 3.0, A)
    b = rng.normal(0, 2.0, C)
    values = a[sa] + b[sc]
    v, _, _ = MOD.fe_residual(values, sa, sc, A, C)
    assert np.abs(v).max() <= 1e-9
    old = MOD.double_center(values, sa, sc, A, C)
    assert np.abs(old).max() > 1e-3        # the leak, in one number


def test_fe_leaves_a_pure_interaction_in_the_column_space_it_should():
    """The projection is idempotent: re-projecting the residual changes it not."""

    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(5)
    values = rng.normal(0, 1.0, sa.size)
    v1, _, _ = MOD.fe_residual(values, sa, sc, A, C)
    v2, sweeps, _ = MOD.fe_residual(v1, sa, sc, A, C)
    assert np.abs(v1 - v2).max() <= 1e-9
    assert sweeps <= 2


def test_fe_is_linear_in_its_argument():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(7)
    x = rng.normal(size=sa.size)
    y = rng.normal(size=sa.size)
    vx, _, _ = MOD.fe_residual(x, sa, sc, A, C)
    vy, _, _ = MOD.fe_residual(y, sa, sc, A, C)
    vxy, _, _ = MOD.fe_residual(3.0 * x - 2.0 * y, sa, sc, A, C)
    assert np.abs(vxy - (3.0 * vx - 2.0 * vy)).max() <= 1e-9


def test_fe_does_not_mutate_its_input():
    sa, sc, A, C = _incomplete_toy()
    values = np.arange(sa.size, dtype=float)
    before = values.copy()
    MOD.fe_residual(values, sa, sc, A, C)
    assert np.array_equal(values, before)


def test_fe_exactness_helper_reports_both_residual_means():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(13)
    design = _design(sa, sc, A, C, rng.normal(size=sa.size),
                     rng.normal(size=sa.size))
    v_e, v_l, sweeps = MOD.fe_pair(design)
    report = MOD.fe_exactness(design, v_e, v_l)
    assert set(report) == {"max_abs_author_mean_early",
                           "max_abs_author_mean_late",
                           "max_abs_community_mean_early",
                           "max_abs_community_mean_late"}
    assert max(report.values()) <= EXACT
    assert sweeps["sweeps_early"] >= 1 and sweeps["sweeps_late"] >= 1


# ---------------------------------------------------------------------------
# 2. FE exactness on the REALIZED skeleton
# ---------------------------------------------------------------------------


def test_fe_is_exact_on_the_realized_primary_skeleton():
    design, _ = _realized_primary()
    v_e, v_l, sweeps = MOD.fe_pair(design)
    report = MOD.fe_exactness(design, v_e, v_l)
    assert max(report.values()) <= EXACT
    assert sweeps["change_early"] <= MOD.FE_TOL
    assert sweeps["change_late"] <= MOD.FE_TOL
    assert sweeps["sweeps_early"] < 1000


def test_the_realized_skeleton_is_one_connected_component():
    """The LCC assertion the exactness argument rests on."""

    design, chain = _realized_primary()
    lcc = MOD.bipartite_lcc(design.slot_author, design.slot_comm,
                            design.n_authors, design.n_comms)
    assert lcc["components"] == 1
    assert lcc["lcc_author_coverage"] == 1.0
    assert bool(lcc["slot_mask"].all())
    assert chain["lcc_author_coverage"] == 1.0


def test_the_realized_skeleton_kills_pure_mains_too():
    """Synthetic mains on the real incidence: the projection must zero them."""

    design, _ = _realized_primary()
    rng = np.random.default_rng(29)
    a = rng.normal(0, 1.0, design.n_authors)
    b = rng.normal(0, 1.0, design.n_comms)
    values = a[design.slot_author] + b[design.slot_comm]
    v, _, _ = MOD.fe_residual(values, design.slot_author, design.slot_comm,
                              design.n_authors, design.n_comms)
    assert np.abs(v).max() <= 1e-8
    old = MOD.double_center(values, design.slot_author, design.slot_comm,
                            design.n_authors, design.n_comms)
    assert np.abs(old).max() > 1e-2


# ---------------------------------------------------------------------------
# 3. the largest connected component
# ---------------------------------------------------------------------------


def test_lcc_finds_the_bigger_of_two_components():
    slot_author = np.array([0, 0, 1, 1, 2, 3, 4], dtype=np.int64)
    slot_comm = np.array([0, 1, 0, 1, 2, 2, 2], dtype=np.int64)
    lcc = MOD.bipartite_lcc(slot_author, slot_comm, 5, 3)
    assert lcc["components"] == 2
    assert lcc["lcc_authors"] == 3
    assert lcc["lcc_author_coverage"] == pytest.approx(3 / 5)
    assert list(lcc["slot_mask"]) == [False, False, False, False,
                                      True, True, True]


def test_lcc_on_a_connected_graph_keeps_everything():
    sa, sc, A, C = _incomplete_toy()
    lcc = MOD.bipartite_lcc(sa, sc, A, C)
    assert lcc["components"] == 1
    assert lcc["lcc_author_coverage"] == 1.0
    assert bool(lcc["slot_mask"].all())


# ---------------------------------------------------------------------------
# 4. the predicate chain
# ---------------------------------------------------------------------------


def _chain_toy():
    """Cells engineered so every step of the chain bites exactly once."""

    rows = []
    # community 0 and 1 carry five authors each in both halves -> they survive
    for author in range(5):
        for comm in (0, 1, 2):
            for half in (0, 1):
                rows.append((author, comm, half, 12, 1.0 + author + comm))
    # community 3 is supported by ONE author only -> dropped at step 3
    rows.append((0, 3, 0, 12, 2.0))
    rows.append((0, 3, 1, 12, 2.5))
    # author 5 has three communities but one is late-only -> only two shared
    rows.append((5, 0, 0, 12, 1.0))
    rows.append((5, 0, 1, 12, 1.5))
    rows.append((5, 1, 0, 12, 2.0))
    rows.append((5, 1, 1, 12, 2.5))
    rows.append((5, 2, 1, 12, 3.0))
    # community 4 is out of vocabulary -> dropped at step 1
    for author in range(5):
        for half in (0, 1):
            rows.append((author, 4, half, 12, 4.0))
    # a thin cell below n_min -> dropped at step 1
    rows.append((1, 5, 0, 4, 9.0))
    rows.append((1, 5, 1, 4, 9.0))
    return _toy_table(rows)


def test_the_chain_applies_its_five_steps_in_the_pinned_order():
    table = _chain_toy()
    vocab = np.ones(table["n_subs"], dtype=bool)
    vocab[4] = False                                # out of vocabulary
    mask = np.ones(8, dtype=bool)
    design, chain = MOD.build_chain_design(
        table, mask, n_min=10, support=5, vocab_mask=vocab, k_min=3)
    # step 2 keeps the shared pairs of communities 0-3 for authors 0-4, the
    # two shared pairs of author 5, and the community-3 pair of author 0
    assert chain["step2_shared_pairs"] == 5 * 3 + 1 + 2
    # step 3 removes the single-author community 3
    assert chain["step3_shared_pairs"] == 5 * 3 + 2
    # step 4 removes author 5, who now holds only two shared communities
    assert chain["step4_shared_pairs"] == 15
    assert chain["step5_shared_pairs"] == 15
    assert design.n_authors == 5
    assert design.n_comms == 3
    assert chain["singleton_communities"] == 0


def test_the_chain_does_not_iterate_to_a_fixed_point():
    """A community that drops below the floor AFTER step 4 must survive."""

    rows = []
    for author in range(5):
        for comm in (0, 1, 2):
            for half in (0, 1):
                rows.append((author, comm, half, 12, 1.0 + comm))
    # community 3 is supported by exactly five authors, but four of them hold
    # only that one shared community and are removed at step 4.
    for author in range(5, 9):
        for half in (0, 1):
            rows.append((author, 3, half, 12, 5.0))
    for half in (0, 1):
        rows.append((0, 3, half, 12, 5.0))
    table = _toy_table(rows)
    vocab = np.ones(table["n_subs"], dtype=bool)
    design, chain = MOD.build_chain_design(
        table, np.ones(9, dtype=bool), n_min=10, support=5,
        vocab_mask=vocab, k_min=3)
    # a fixed-point rule would have removed community 3 on the second pass
    assert design.n_comms == 4
    assert chain["singleton_communities"] == 1
    assert design.n_authors == 5


def test_the_chain_reproduces_the_planner_census_at_every_support_floor():
    """BLOCKING anchor (#78): the s = 3 / 5 / 8 table, to the unit."""

    _realized_primary()
    table = _REALIZED["table"]
    for support, want in MOD.CHAIN_ANCHORS.items():
        _design_s, chain = MOD.build_chain_design(
            table, _REALIZED["disjoint"], n_min=MOD.N_MIN_PRIMARY,
            support=support, vocab_mask=_REALIZED["vocab"])
        for key, value in want.items():
            assert chain[key] == value, (support, key, chain[key])


def test_the_law_vocabulary_floor_reproduces():
    _realized_primary()
    assert _REALIZED["floor"] == MOD.ANCHOR_VOCAB_FLOOR_USERS
    assert int(_REALIZED["vocab"].sum()) == MOD.ANCHOR_LAW_VOCAB
    assert int(_REALIZED["disjoint"].sum()) == MOD.ANCHOR_DISJOINT_AUTHORS
    assert int(_REALIZED["big5"].sum()) == MOD.ANCHOR_BIG5_AUTHORS


def test_the_word_count_arm_shares_the_design_and_changes_only_y():
    _realized_primary()
    table = _REALIZED["table"]
    design_wc, chain_wc = MOD.build_chain_design(
        table, _REALIZED["disjoint"], n_min=MOD.N_MIN_PRIMARY,
        support=MOD.S_PRIMARY, vocab_mask=_REALIZED["vocab"], y_key="wc")
    design, chain = _realized_primary()
    assert chain_wc["shared_pairs"] == chain["shared_pairs"]
    assert np.array_equal(design_wc.slot_author, design.slot_author)
    assert not np.allclose(design_wc.mean_e, design.mean_e)


# ---------------------------------------------------------------------------
# 5. the bootstrap's weighted FE
# ---------------------------------------------------------------------------


def test_weighted_fe_equals_an_explicitly_duplicated_design():
    """Bootstrap-FE correctness: weight m == m physical copies of an author."""

    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(17)
    values = rng.normal(size=sa.size)
    mult = np.array([2.0, 1.0, 0.0, 3.0, 1.0, 1.0])

    # (a) the weighted projection the bootstrap actually runs
    keep = mult[sa] > 0
    ua, a_idx = np.unique(sa[keep], return_inverse=True)
    uc, c_idx = np.unique(sc[keep], return_inverse=True)
    a_idx = a_idx.reshape(-1)
    c_idx = c_idx.reshape(-1)
    weighted, _, _ = MOD.fe_residual(values[keep], a_idx, c_idx,
                                     int(ua.size), int(uc.size),
                                     weights=mult[ua][a_idx])

    # (b) the same design with each drawn author physically duplicated
    rows_a, rows_c, rows_v, origin = [], [], [], []
    next_author = 0
    for author in ua:
        for _copy in range(int(mult[author])):
            sel = np.flatnonzero(sa == author)
            for slot in sel:
                rows_a.append(next_author)
                rows_c.append(sc[slot])
                rows_v.append(values[slot])
                origin.append(slot)
            next_author += 1
    exp_a = np.array(rows_a, dtype=np.int64)
    exp_c = np.array(rows_c, dtype=np.int64)
    uc2, exp_c = np.unique(exp_c, return_inverse=True)
    exp_c = exp_c.reshape(-1)
    expanded, _, _ = MOD.fe_residual(np.array(rows_v), exp_a, exp_c,
                                     next_author, int(uc2.size))

    # every copy of a slot must carry the weighted projection's value
    lookup = dict(zip(np.flatnonzero(keep).tolist(), weighted.tolist()))
    for value, slot in zip(expanded.tolist(), origin):
        assert value == pytest.approx(lookup[int(slot)], abs=1e-8)


def test_bootstrap_replicate_returns_full_length_vectors_and_a_weighted_R():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(19)
    design = _design(sa, sc, A, C, rng.normal(size=sa.size),
                     rng.normal(size=sa.size))
    mult = np.array([2.0, 0.0, 1.0, 1.0, 1.0, 1.0])
    v_e, v_l, r_boot = MOD._bootstrap_replicate(design, mult)
    assert v_e.size == design.n_slots and v_l.size == design.n_slots
    assert np.all(v_e[mult[sa] == 0] == 0.0)
    assert np.isfinite(r_boot)


def test_the_full_bootstrap_recomputes_the_projection_every_replicate():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(23)
    design = _design(sa, sc, A, C, rng.normal(size=sa.size),
                     rng.normal(size=sa.size))
    out = MOD.cluster_bootstrap_fe(design, 16, seed=1)
    assert out["b_boot"] == 16
    assert set(out["shares_ci"]) >= {"author", "community", "interaction",
                                     "residual"}
    lo, hi = out["shares_ci"]["interaction"]
    assert lo <= hi
    assert np.isfinite(out["r_ci"]).all()


def test_the_bootstrap_is_deterministic_under_its_seed():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(31)
    design = _design(sa, sc, A, C, rng.normal(size=sa.size),
                     rng.normal(size=sa.size))
    first = MOD.cluster_bootstrap_fe(design, 8, seed=5)
    second = MOD.cluster_bootstrap_fe(design, 8, seed=5)
    assert first["shares_ci"] == second["shares_ci"]
    assert first["r_ci"] == second["r_ci"]


# ---------------------------------------------------------------------------
# 6. the permutation null preserves the design exactly
# ---------------------------------------------------------------------------


def test_the_permutation_preserves_the_design():
    sa, _sc, _A, _C = _incomplete_toy()
    rng = np.random.default_rng(37)
    batch = MOD.permutation_batch(sa, rng, 8)
    for row in batch:
        assert np.array_equal(np.sort(row), np.arange(sa.size))
        assert np.array_equal(sa[row], sa)     # values stay inside the author


def test_the_permutation_null_is_deterministic_and_brackets_zero():
    sa, sc, A, C = _incomplete_toy()
    rng = np.random.default_rng(41)
    design = _design(sa, sc, A, C, rng.normal(size=sa.size),
                     rng.normal(size=sa.size))
    first = MOD.permutation_null_fe(design, 32, seed=9)
    second = MOD.permutation_null_fe(design, 32, seed=9)
    assert first["interaction_band"] == second["interaction_band"]
    lo, hi = first["interaction_band"]
    assert lo <= 0.0 <= hi


# ---------------------------------------------------------------------------
# 7. the Part 0 gate battery
# ---------------------------------------------------------------------------


def _dense_skeleton(n_authors=200, n_comms=25, k=8, seed=2):
    rng = np.random.default_rng(seed)
    author, comm = [], []
    for u in range(n_authors):
        picks = rng.choice(n_comms, size=k, replace=False)
        author.extend([u] * k)
        comm.extend(picks.tolist())
    sa = np.array(author, dtype=np.int64)
    sc = np.array(comm, dtype=np.int64)
    n = np.full(sa.size, 20.0)
    zeros = np.zeros(sa.size)
    return MOD.Design(slot_author=sa, slot_comm=sc, n_e=n, n_l=n.copy(),
                      s_e=zeros.copy(), s_l=zeros.copy(),
                      q_e=zeros.copy(), q_l=zeros.copy(),
                      n_authors=n_authors, n_comms=n_comms,
                      author_codes=np.arange(n_authors, dtype=np.int64))


def test_the_fe_estimator_recovers_a_planted_interaction():
    skeleton = _dense_skeleton()
    rng = np.random.default_rng(53)
    world = MOD.synthetic_design(skeleton, MOD.PLANTED_SHARES, rng)
    got = MOD.recover_shares_fe(world)
    rank = skeleton.n_authors + skeleton.n_comms - 1
    retained = (skeleton.n_slots - rank) / skeleton.n_slots
    assert got["interaction"] == pytest.approx(
        MOD.PLANTED_SHARES["interaction"] * retained, abs=0.004)
    assert got["R"] > 0.2


def test_the_fe_estimator_reads_zero_in_a_null_world():
    skeleton = _dense_skeleton()
    values = []
    for rep in range(4):
        rng = np.random.default_rng(59 + rep)
        world = MOD.synthetic_design(skeleton, MOD.NULL_SHARES, rng)
        values.append(MOD.recover_shares_fe(world)["interaction"])
    assert abs(float(np.mean(values))) < 0.002


def test_the_ablation_worlds_do_not_leak_into_the_interaction():
    skeleton = _dense_skeleton()
    for shares in MOD.ABLATION_WORLDS.values():
        leaks = []
        for rep in range(4):
            rng = np.random.default_rng(67 + rep)
            world = MOD.synthetic_design(skeleton, shares, rng)
            leaks.append(MOD.recover_shares_fe(world)["interaction"])
        assert abs(float(np.mean(leaks))) < MOD.ABLATION_LEAK_MAX


def test_the_synthetic_block_reports_mean_sd_and_every_replicate(tmp_path):
    skeleton = _dense_skeleton(n_authors=60, n_comms=10, k=5)
    log = MOD.RunLog(tmp_path / "block.jsonl")
    block = MOD.synthetic_world_block(skeleton, MOD.NULL_SHARES, "unit",
                                      101, 3, log)
    assert block["replicates"] == 3
    assert len(block["stats"]["interaction"]["values"]) == 3
    assert block["planted"]["interaction"] == 0.0
    assert set(block["stats"]) >= {"author", "community", "interaction", "R"}


def test_the_gate_battery_runs_end_to_end_and_scores_every_clause(tmp_path):
    skeleton = _dense_skeleton(n_authors=120, n_comms=15, k=6)
    log = MOD.RunLog(tmp_path / "gate.jsonl")
    gate = MOD.synthetic_gate(skeleton, b_perm=16, b_boot=16, log=log)
    assert gate["n_clauses"] == 9
    assert set(gate["recovery"]) == set(MOD.PLANTED_SHARES)
    assert gate["status"] in {"PASS", "FAIL"}
    assert gate["status"] == ("PASS" if gate["n_clauses_passed"] == 9
                              else "FAIL")
    for row in gate["recovery"].values():
        assert row["tolerance"] >= MOD.TOL_FLOOR
        expected = "PASS" if abs(row["bias"]) <= row["tolerance"] else "FAIL"
        assert row["status"] == expected
    for row in gate["ablation_clauses"].values():
        assert row["maximum"] == MOD.ABLATION_LEAK_MAX
        expected = ("PASS" if row["leakage"] < MOD.ABLATION_LEAK_MAX
                    else "FAIL")
        assert row["status"] == expected
    # the #85b clause and the CI clause read the same object
    assert (gate["clauses"]["null world — interaction share CI covers 0"]
            == gate["clauses"]["#85b bootstrap-zero — the null world's "
                               "cluster-bootstrap CI covers 0"])


def test_the_composition_diagnostic_predicts_the_author_main_bias():
    skeleton = _dense_skeleton()
    diag = MOD.composition_diagnostics(skeleton)
    k = np.bincount(skeleton.slot_author, None, skeleton.n_authors)
    assert diag["mean_inverse_k"] == pytest.approx(float(np.mean(1.0 / k)))
    assert diag["predicted_author_bias"] == pytest.approx(
        diag["mean_inverse_k"] * (MOD.PLANTED_SHARES["community"]
                                  + MOD.PLANTED_SHARES["interaction"]))
    assert 0.0 < diag["fe_retained_fraction"] <= 1.0


# ---------------------------------------------------------------------------
# 8. cells, leans and flags (inherited from X1 verbatim)
# ---------------------------------------------------------------------------


def _arm(share, ci, r, band):
    return {"budget": {"interaction": share, "author": 0.3,
                       "community": 0.08, "residual": 0.6},
            "bootstrap": {"shares_ci": {"interaction": list(ci)},
                          "r_ci": [r - 0.01, r + 0.01]},
            "null": {"r_band": list(band),
                     "interaction_band": [-0.001, 0.001]},
            "R": r}


def test_the_null_cell_needs_both_of_its_conditions():
    inside = _arm(0.0, (-0.01, 0.01), 0.01, (-0.02, 0.02))
    assert MOD.classify(inside)["cell"] == MOD.CELL_NO_RESPONSE
    r_outside = _arm(0.0, (-0.01, 0.01), 0.5, (-0.02, 0.02))
    assert MOD.classify(r_outside)["cell"] != MOD.CELL_NO_RESPONSE
    ci_excludes = _arm(0.03, (0.02, 0.04), 0.01, (-0.02, 0.02))
    assert MOD.classify(ci_excludes)["cell"] == MOD.CELL_IDIOSYNCRATIC


def test_the_magnitude_cells_and_straddles():
    assert MOD.classify(_arm(0.01, (0.005, 0.015), 0.4,
                             (-0.02, 0.02)))["cell"] == MOD.CELL_TRACE
    straddle = MOD.classify(_arm(0.019, (0.010, 0.030), 0.4, (-0.02, 0.02)))
    assert straddle["straddle"] is True
    assert MOD.CELL_TRACE in straddle["touched"]
    assert MOD.CELL_IDIOSYNCRATIC in straddle["touched"]
    assert MOD.classify(_arm(0.20, (0.15, 0.25), 0.4,
                             (-0.02, 0.02)))["cell"] == MOD.CELL_MAJOR


def test_the_registered_boundaries_are_the_ones_x1_registered():
    assert MOD.TRACE_MAX == 0.02
    assert MOD.IDIOSYNCRATIC_MAX == 0.10
    assert MOD.LEAN_R == (0.05, 0.30)
    assert MOD.LEAN_INTERACTION == (0.005, 0.05)
    assert MOD.LEAN_AUTHOR_MAIN == (0.15, 0.45)
    assert MOD.LEAN_COMMUNITY_MAIN == (0.02, 0.15)
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 499 and MOD.B_BOOT == 1000
    assert MOD.S_PRIMARY == 5 and MOD.K_MIN == 3
    assert MOD.N_MIN_PRIMARY == 10 and MOD.N_MIN_SENSITIVITY == 5
    assert MOD.BIG5_POWER_FLOOR == 300


# ---------------------------------------------------------------------------
# 9. the #83 ID-leak helper over the widened universe
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
    baseline = {("CLAIMS_LEDGER.md", 58)}
    new = MOD.new_hits_only(hits, baseline)
    assert len(new) == 1
    assert new[0]["path"] == "reports/NEW.md"


def test_the_scanned_file_list_is_the_committed_one():
    names = {path.name for path in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md",
                     "run_suica_m4_x1b_venue_response_fe.py",
                     "test_m4_x1b_venue_response_fe.py",
                     "SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
                     "CLAIMS_LEDGER.md"}


def test_results_stay_out_of_the_commit():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore


# ---------------------------------------------------------------------------
# 10. the committed run (skipped where the artifacts were not produced)
# ---------------------------------------------------------------------------


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                          # pragma: no cover
        pytest.skip("the X1b run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_run_reproduced_the_inherited_anchors():
    census = _artifact("census.json")
    assert census["status"] == "PASS"
    for key, pin in census["pins"].items():
        assert pin["status"] == "PASS", key
        assert pin["registered"] == pin["observed"], key


def test_committed_run_reproduced_the_predicate_chain_census():
    anchor = _artifact("chain_anchor.json")
    assert anchor["status"] == "PASS"
    for key, row in anchor["pins_by_s"].items():
        assert row["status"] == "PASS", key
        for field, value in row["observed"].items():
            assert value == MOD.CHAIN_ANCHORS[int(key)][field], (key, field)


def test_committed_run_asserted_the_lcc_before_projecting():
    chain = _artifact("chain_census.json")
    for key, row in chain.items():
        assert row["lcc_author_coverage"] == 1.0, key
    assert chain[str(MOD.S_PRIMARY)]["singleton_communities"] == 0


def test_committed_run_scored_every_gate_clause():
    part0 = _artifact("part0_synthetic_gate.json")
    assert part0["n_clauses"] == 9
    assert part0["status"] in {"PASS", "FAIL"}
    assert part0["status"] == ("PASS" if part0["n_clauses_passed"] == 9
                               else "FAIL")
    assert part0["null_block"]["planted"]["interaction"] == 0.0
    assert part0["planted_block"]["replicates"] == MOD.N_SYNTH_REPLICATES


def test_committed_run_honoured_the_a1_stop():
    """No real estimand may exist unless every Part 0 clause passed."""

    part0 = _artifact("part0_synthetic_gate.json")
    verdict = _artifact("verdict.json")
    if part0["status"] == "PASS":                  # pragma: no cover
        assert verdict["cell"] != MOD.CELL_A1_STOP
        assert (ARTIFACTS / "arms.json").exists()
    else:
        assert verdict["cell"] == MOD.CELL_A1_STOP
        assert not (ARTIFACTS / "arms.json").exists()
        assert not (ARTIFACTS / "cells.json").exists()
        assert not (ARTIFACTS / "leans.json").exists()


def test_committed_run_verified_the_projection_on_the_real_incidence():
    part0 = _artifact("part0_synthetic_gate.json")
    exact = part0["honesty"]["fe_exactness"]
    assert max(exact.values()) <= EXACT
    assert part0["honesty"]["fe"]["change_early"] <= MOD.FE_TOL
    assert part0["honesty"]["fe"]["change_late"] <= MOD.FE_TOL


def test_committed_run_recorded_the_estimator_comparison():
    comp = _artifact("estimator_comparison.json")
    grid = comp["grid"]
    assert len(grid) == 4
    new = grid["x1b_repaired_skeleton|x1b_exact_fe"]["interaction_mean"]
    old = grid["x1b_repaired_skeleton|x1_double_centering"]["interaction_mean"]
    assert abs(new) < 0.001                 # the zero, now
    assert old > 0.005                      # the leak, then
    assert abs(grid["x1_registered_skeleton|x1b_exact_fe"][
        "interaction_mean"]) < 0.001


def test_committed_run_censused_the_big5_arm_against_the_69_floor():
    power = _artifact("big5_power.json")
    assert power["floor"] == MOD.BIG5_POWER_FLOOR
    assert power["meets_floor"] == (power["authors"] >= power["floor"])
    designs = _artifact("arm_designs.json")
    assert designs["replication_big5"]["authors"] == power["authors"]
    assert set(designs) == set(MOD.ARM_LABELS)


def test_committed_report_matches_the_committed_verdict():
    if not REPORT.exists():                        # pragma: no cover
        pytest.skip("the X1b report has not been produced in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**VERDICT — {verdict['cell']}.**" in text
    for boundary_head in ("Metadata only", "projection caution",
                          "No psychological naming", "EXPLORATORY",
                          "Cohort composition", "WELL-SHARED VENUES"):
        assert boundary_head in text


def test_committed_report_carries_the_gate_numbers_from_the_artifact():
    if not REPORT.exists():                        # pragma: no cover
        pytest.skip("the X1b report has not been produced in this checkout")
    part0 = _artifact("part0_synthetic_gate.json")
    text = REPORT.read_text(encoding="utf-8")
    for row in part0["recovery"].values():
        assert f"{row['recovered_mean']:.4f}" in text
        assert f"{row['tolerance']:.4f}" in text
    for name, status in part0["clauses"].items():
        assert name in text
    chain = _artifact("chain_census.json")
    for key, row in chain.items():
        assert f"{row['shared_pairs']:,}" in text


def test_committed_run_cleared_the_id_leak_gate():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == MOD.ANCHOR_AUTHORS


def test_committed_outcome_was_appended_to_the_registration():
    text = PLAN.read_text(encoding="utf-8")
    assert "## X1b outcome (executor, 2026-08-19)" in text
    verdict = _artifact("verdict.json")
    assert verdict["cell"] in text


def test_the_claims_ledger_carries_exactly_one_x1b_row():
    text = LEDGER.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| M4-X1b ")]
    assert len(rows) == 1
    assert "EXPLORATORY" in rows[0]
    assert "metadata-only" in rows[0]
