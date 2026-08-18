"""Contract tests for M4-W2 — fast-time and branch-code transport.

The leg carries two sealed-prediction families onto a disjoint cohort using
machinery it does not own: U1's order pipeline and T1's hierarchical selection
identity.  These tests therefore check CONTRACTS rather than results —

* the seeded, size-matched subpool draws are deterministic and their ORDER is
  the documented one (swapping the draws changes both);
* the exact-bag within-half shuffle is bit-exact on THIS cohort's fold layout;
* rho is U1's formula, agreeing on a toy where the answer is known by hand;
* ``cross_fitted_hierarchical_identity`` is imported, not reimplemented, and
  behaves on a planted toy world;
* the census predicates are reproduced by the helpers the run actually calls;
* the four-class transport scheme (including RESOLVES) behaves on synthetic
  interval fixtures;
* the ID-leak helper implements the #83 HEAD-identical policy.

Nothing here reads a personality label.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_w2_fast_branch_transport.py"
U1_SCRIPT = ROOT / "scripts" / "run_suica_m4_u1_order_identity.py"
T1_ARTIFACTS = ROOT / "results" / "m4_t1_hierarchical_selection_identity"
ARTIFACTS = ROOT / "results" / "m4_w2_fast_branch_transport"
CACHE = ROOT / "results" / "m4_w1_slow_transport" / "disjoint_events_cache.npz"
REPORT = ROOT / "reports" / "SUICA_M4_W2_FAST_BRANCH_TRANSPORT_REPORT.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_w2_fast_branch_transport", SCRIPT)


def _log(tmp_path: Path):
    return MOD.RunLog(tmp_path / "run_log.jsonl")


def _cache():
    if not CACHE.exists():                            # pragma: no cover
        pytest.skip("W1's disjoint cache is absent in this checkout")
    return MOD.load_scaffold(CACHE)


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                             # pragma: no cover
        pytest.skip("the W2 run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Registration pins
# ---------------------------------------------------------------------------


def test_registered_pins_are_the_registered_numbers():
    assert MOD.SEED == 20260818
    assert MOD.N_FOLDS == 5
    assert MOD.C_PRIMARY == 24
    assert MOD.B_SHUFFLE == 499
    assert MOD.B_BOOTSTRAP == 1000
    assert MOD.N_ORDER_SUBPOOL == 984
    assert MOD.N_BRANCH_SUBPOOL == 1304
    assert MOD.ORDER_POOL_MIN_PER_HALF == 50
    assert MOD.BRANCH_MIN_EVENTS == 40
    assert (MOD.BRANCH_MAX_DEPTH, MOD.BRANCH_MIN_LEAF) == (6, 30)
    assert MOD.BRANCH_PERMUTATIONS == 499
    assert MOD.BRANCH_BOOTSTRAP == 1000
    assert MOD.CENSUS_LAW_VOCAB == 1443
    assert MOD.CENSUS_ORDER_POOL == 7247
    assert MOD.CENSUS_BRANCH_POOL == 8625
    assert MOD.CENSUS_VOCAB_FLOOR_USERS == math.ceil(0.01 * 8895) == 89
    assert (MOD.ORDER_CELL_LOW, MOD.ORDER_CELL_HIGH) == (0.10, 0.33)


def test_sealed_source_values_are_the_registered_ones():
    assert MOD.SEALED_ORDER["primary"]["point"] == 0.2893
    assert MOD.SEALED_ORDER["primary"]["ci"] == [0.2695, 0.3114]
    assert MOD.SEALED_ORDER["stay_rate"]["point"] == 0.1803
    assert MOD.SEALED_ORDER["stay_rate"]["ci"] == [0.1375, 0.2234]
    assert MOD.SEALED_ORDER["cross_thread"]["point"] == 0.1626
    assert MOD.SEALED_ORDER["cross_thread"]["ci"] == [0.1373, 0.1895]
    assert MOD.SEALED_DWELL_SHARE == 0.7122
    assert MOD.SEALED_BRANCH["full.flat_auc"]["point"] == 0.9837
    assert MOD.SEALED_BRANCH["full.hierarchical_path_auc"]["point"] == 0.7461
    assert MOD.SEALED_BRANCH["full.terminal_residual_auc"]["point"] == 0.9552
    assert MOD.SEALED_BRANCH["clean.flat_auc"]["point"] == 0.9661
    assert MOD.SEALED_BRANCH["clean.hierarchical_path_auc"]["point"] == 0.7317
    assert MOD.SEALED_BRANCH["clean.terminal_residual_auc"]["point"] == 0.9417
    assert MOD.SEALED_DEPTHS == {"full": [1, 2, 3, 4, 5], "clean": [1, 2, 3, 4]}


def test_the_sealed_order_values_match_u1s_committed_artifacts():
    """The seal is a QUOTE of U1's artifacts, not a retyped memory."""

    path = ROOT / "results/m4_u1_order_identity/arms.json"
    if not path.exists():                             # pragma: no cover
        pytest.skip("U1's artifacts are absent in this checkout")
    arms = {row["arm"]: row for row in
            json.loads(path.read_text(encoding="utf-8"))}
    for key, sealed in MOD.SEALED_ORDER.items():
        assert round(arms[key]["rho"], 4) == sealed["point"], key
        assert [round(v, 4) for v in arms[key]["rho_ci"]] == sealed["ci"], key
        assert arms[key]["pool_size"] == sealed["gallery"] == 984, key


def test_the_sealed_branch_values_match_t1s_committed_artifacts():
    path = T1_ARTIFACTS / "summary.json"
    if not path.exists():                             # pragma: no cover
        pytest.skip("T1's artifacts are absent in this checkout")
    payload = json.loads(path.read_text(encoding="utf-8"))
    alias = {"full": "full", "clean": "clean_no_explicit_personality"}
    for key, sealed in MOD.SEALED_BRANCH.items():
        arm_key, metric = key.split(".", 1)
        assert round(payload["arms"][alias[arm_key]][metric], 4) == \
            sealed["point"], key


# ---------------------------------------------------------------------------
# The machinery is IMPORTED, never retyped (#81)
# ---------------------------------------------------------------------------


def test_order_machinery_is_u1s_object_not_a_reimplementation():
    """Every order-pipeline name W2 uses IS the function defined in U1's file."""

    assert Path(MOD.U1.__file__) == U1_SCRIPT
    for name in ("build_pool_context", "build_state_maps", "run_arm",
                 "assert_fold_purity", "compute_descriptives",
                 "split_halves", "scan_for_cohort_ids", "load_scaffold",
                 "is_explicit_personality_community"):
        bound = getattr(MOD, name)
        assert bound is getattr(MOD.U1, name), name
        assert Path(bound.__code__.co_filename) == U1_SCRIPT, name
    assert MOD.order_cell_of is MOD.U1._cell_of
    assert Path(MOD.order_cell_of.__code__.co_filename) == U1_SCRIPT
    # the three registered arms are U1's own ArmSpec rows, unedited
    assert {spec.key for spec in MOD.ORDER_ARMS} == {
        "primary", "stay_rate", "cross_thread"}
    by_key = {spec.key: spec for spec in MOD.U1.ARMS}
    for spec in MOD.ORDER_ARMS:
        assert spec is by_key[spec.key]
        assert spec.pool_min == MOD.ORDER_POOL_MIN_PER_HALF
        assert spec.vocab_variant == "full"
        assert spec.n_states == MOD.C_PRIMARY
    # W2 defines no order-pipeline function of its own
    own = {name for name, value in vars(MOD).items()
           if callable(value) and getattr(value, "__module__", None)
           == MOD.__name__}
    assert not own & {"bigram_counts", "features_from_counts", "stay_rates",
                      "similarity_matrix", "spherical_kmeans",
                      "within_half_permutation", "rho_from_auc",
                      "auc_from_matrix", "bootstrap_rho"}


def test_branch_machinery_is_the_suica_core_object():
    from suica_core.hierarchical_selection_identity import (
        cross_fitted_hierarchical_identity,
    )
    assert (MOD.cross_fitted_hierarchical_identity
            is cross_fitted_hierarchical_identity)


def test_suica_core_import_contract_on_a_planted_toy_world():
    """The imported object recovers a planted hierarchy and rejects a null."""

    from suica_core.hierarchical_selection_identity import (
        simulate_hierarchical_choices,
    )
    early, late, _paths = simulate_hierarchical_choices(
        n_authors=320, n_contexts=48, depth=3, events_per_half=400, seed=7)
    planted = MOD.cross_fitted_hierarchical_identity(
        early, late, n_splits=4, max_depth=4, min_leaf=20,
        random_state=MOD.SEED, n_permutations=19, n_bootstrap=50)
    assert set(planted) == {"summary", "metrics_by_depth", "per_user_depth"}
    for key in MOD.BRANCH_AUC_KEYS:
        assert key in planted["summary"]
    assert planted["summary"]["flat_auc"] > 0.75

    rng = np.random.default_rng(11)
    noise_early = rng.random((320, 48))
    noise_late = rng.random((320, 48))
    null = MOD.cross_fitted_hierarchical_identity(
        noise_early, noise_late, n_splits=4, max_depth=4, min_leaf=20,
        random_state=MOD.SEED, n_permutations=19, n_bootstrap=50)
    assert abs(null["summary"]["flat_auc"] - 0.5) < 0.10
    assert MOD.stable_depths_from_metrics(null["metrics_by_depth"]) == []


def test_reducing_the_inner_counts_does_not_move_the_three_aucs():
    """Justifies RD-W2-2: permutations/bootstrap do not enter the AUCs.

    The AUC bootstrap re-runs the pinned function with its permutation and
    bootstrap counts set to the minimum.  That is only legitimate if those
    counts leave the AUCs bit-identical.
    """

    from suica_core.hierarchical_selection_identity import (
        simulate_hierarchical_choices,
    )
    early, late, _ = simulate_hierarchical_choices(
        n_authors=200, n_contexts=32, depth=3, events_per_half=300, seed=5)
    kwargs = dict(n_splits=4, max_depth=4, min_leaf=20,
                  random_state=MOD.SEED)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rich = MOD.cross_fitted_hierarchical_identity(
            early, late, n_permutations=97, n_bootstrap=200, **kwargs)
        lean = MOD.cross_fitted_hierarchical_identity(
            early, late,
            n_permutations=MOD.BRANCH_AUC_BOOT_PERMUTATIONS,
            n_bootstrap=MOD.BRANCH_AUC_BOOT_INNER, **kwargs)
    for key in MOD.BRANCH_AUC_KEYS:
        assert rich["summary"][key] == lean["summary"][key], key


def test_stable_depth_gate_reproduces_t1s_committed_depths():
    """T1's triple gate, replayed on T1's own committed per-depth table."""

    path = T1_ARTIFACTS / "metrics_by_depth.csv"
    summary_path = T1_ARTIFACTS / "summary.json"
    if not (path.exists() and summary_path.exists()):  # pragma: no cover
        pytest.skip("T1's artifacts are absent in this checkout")
    import pandas as pd
    frame = pd.read_csv(path)
    for arm, expected in (("full", [1, 2, 3, 4, 5]),
                          ("clean_no_explicit_personality", [1, 2, 3, 4])):
        rows = frame[frame["arm"] == arm].to_dict("records")
        assert MOD.stable_depths_from_metrics(rows) == expected, arm
    # and the sealed depth sets are exactly those
    assert MOD.SEALED_DEPTHS["full"] == [1, 2, 3, 4, 5]
    assert MOD.SEALED_DEPTHS["clean"] == [1, 2, 3, 4]


# ---------------------------------------------------------------------------
# The seeded, size-matched draws
# ---------------------------------------------------------------------------


def test_seeded_subpools_are_deterministic_and_size_matched():
    order_pool = np.arange(7247, dtype=np.int32)
    branch_pool = np.arange(8625, dtype=np.int32)
    first = MOD.seeded_subpools(order_pool, branch_pool)
    second = MOD.seeded_subpools(order_pool, branch_pool)
    assert np.array_equal(first["order_subpool"], second["order_subpool"])
    assert np.array_equal(first["branch_subpool"], second["branch_subpool"])
    assert first["order_digest"] == second["order_digest"]
    assert first["branch_digest"] == second["branch_digest"]
    assert first["order_n"] == MOD.N_ORDER_SUBPOOL == 984
    assert first["branch_n"] == MOD.N_BRANCH_SUBPOOL == 1304
    # uniform WITHOUT replacement, sorted ascending, drawn from the pools
    for key, pool in (("order_subpool", order_pool),
                      ("branch_subpool", branch_pool)):
        drawn = first[key]
        assert np.unique(drawn).size == drawn.size
        assert np.all(np.diff(drawn) > 0)
        assert set(int(v) for v in drawn) <= set(int(v) for v in pool)


def test_the_draw_order_is_documented_and_load_bearing():
    """Order first, branch second, one stream: swapping changes BOTH draws."""

    order_pool = np.arange(7247, dtype=np.int32)
    branch_pool = np.arange(8625, dtype=np.int32)
    registered = MOD.seeded_subpools(order_pool, branch_pool)
    assert registered["draw_order"] == ["order_subpool", "branch_subpool"]
    assert registered["seed"] == MOD.SEED == 20260818

    # the documented stream, replayed by hand
    rng = np.random.default_rng(MOD.SEED)
    by_hand_order = np.sort(rng.choice(order_pool, size=984, replace=False))
    by_hand_branch = np.sort(rng.choice(branch_pool, size=1304, replace=False))
    assert np.array_equal(registered["order_subpool"], by_hand_order)
    assert np.array_equal(registered["branch_subpool"], by_hand_branch)

    # the SWAPPED stream agrees with neither
    swapped = np.random.default_rng(MOD.SEED)
    swapped_branch = np.sort(swapped.choice(branch_pool, size=1304,
                                            replace=False))
    swapped_order = np.sort(swapped.choice(order_pool, size=984,
                                           replace=False))
    assert not np.array_equal(swapped_branch, by_hand_branch)
    assert not np.array_equal(swapped_order, by_hand_order)


def test_size_matching_is_refused_when_the_pool_is_too_small():
    with pytest.raises(SystemExit):
        MOD.seeded_subpools(np.arange(10, dtype=np.int32),
                            np.arange(8625, dtype=np.int32))


def test_restricting_the_scaffold_preserves_every_authors_own_geometry():
    """Halves and eligibility are per-author-local, so restriction is exact."""

    rng = np.random.default_rng(4)
    n_authors, n_subs = 12, 6
    author_code, subreddit_code, created, link = [], [], [], []
    for author in range(n_authors):
        n_events = int(rng.integers(8, 20))
        author_code.extend([author] * n_events)
        subreddit_code.extend(rng.integers(0, n_subs, n_events).tolist())
        created.extend(np.sort(rng.random(n_events) * 1e6).tolist())
        link.extend(rng.integers(0, 5, n_events).tolist())
    scaffold = MOD.EventScaffold(
        authors=[f"a{i}" for i in range(n_authors)],
        author_code=np.asarray(author_code, dtype=np.int32),
        subreddit_code=np.asarray(subreddit_code, dtype=np.int32),
        created_utc=np.asarray(created, dtype=np.float64),
        link_code=np.asarray(link, dtype=np.int32),
        subreddits=[f"s{i}" for i in range(n_subs)],
        vocabulary=[f"s{i}" for i in range(n_subs)],
        vocab_of_subreddit=np.arange(n_subs, dtype=np.int32),
        stream_stats={},
    )
    keep = np.array([1, 3, 4, 9], dtype=np.int32)
    restricted = MOD.restrict_scaffold(scaffold, keep)
    assert restricted.author_code.size == sum(
        int((scaffold.author_code == a).sum()) for a in keep)
    assert np.array_equal(np.unique(restricted.author_code),
                          np.arange(keep.size))
    for new_code, old_code in enumerate(keep):
        old = scaffold.author_code == old_code
        new = restricted.author_code == new_code
        assert np.array_equal(scaffold.created_utc[old],
                              restricted.created_utc[new])
        assert np.array_equal(MOD.split_halves(scaffold.created_utc[old]),
                              MOD.split_halves(restricted.created_utc[new]))
        assert np.array_equal(scaffold.link_code[old],
                              restricted.link_code[new])
    assert restricted.vocabulary == scaffold.vocabulary


# ---------------------------------------------------------------------------
# Census predicates, reproduced by the helpers the run calls
# ---------------------------------------------------------------------------


def test_census_predicates_reproduce_on_a_hand_built_toy():
    """>= 50 law-vocab events in EACH half; >= 40 events TOTAL."""

    saved = (MOD.ORDER_POOL_MIN_PER_HALF, MOD.BRANCH_MIN_EVENTS)
    MOD.ORDER_POOL_MIN_PER_HALF, MOD.BRANCH_MIN_EVENTS = 3, 5
    try:
        # author 0: 8 in-vocab events -> 4/4 halves -> both pools
        # author 1: 8 events but only 4 in vocab -> branch pool only
        # author 2: 4 events -> neither pool
        author_code, subreddit_code, created = [], [], []
        plan = [(0, 8, True), (1, 8, False), (2, 4, True)]
        for author, n_events, in_vocab in plan:
            author_code.extend([author] * n_events)
            subreddit_code.extend([0 if in_vocab or i % 2 == 0 else 1
                                   for i in range(n_events)])
            created.extend([float(t) for t in range(n_events)])
        scaffold = MOD.EventScaffold(
            authors=["a", "b", "c"],
            author_code=np.asarray(author_code, dtype=np.int32),
            subreddit_code=np.asarray(subreddit_code, dtype=np.int32),
            created_utc=np.asarray(created, dtype=np.float64),
            link_code=np.zeros(len(author_code), dtype=np.int32),
            subreddits=["in", "out"], vocabulary=["in"],
            vocab_of_subreddit=np.array([0, -1], dtype=np.int32),
            stream_stats={})
        segments = MOD.author_segments(scaffold)
        assert list(segments["order_pool"]) == [0]
        assert list(segments["branch_pool"]) == [0, 1]
        # the half rule sends the boundary event to EARLY
        assert int(segments["is_early"][:8].sum()) == 4
        assert segments["total_counts"].tolist() == [8, 8, 4]
    finally:
        MOD.ORDER_POOL_MIN_PER_HALF, MOD.BRANCH_MIN_EVENTS = saved


def test_adjacency_rates_are_within_author_only():
    author = np.array([0, 0, 0, 1, 1], dtype=np.int32)
    created = np.array([0.0, 0.0, 10.0, 99999.0, 100000.0])
    link = np.array([1, 1, 2, 3, 3], dtype=np.int32)
    rates = MOD.adjacency_rates(author, created, link)
    assert rates["adjacencies"] == 3           # the 0->1 boundary is excluded
    assert rates["tie_rate"] == pytest.approx(1 / 3)
    assert rates["session_share"] == pytest.approx(1.0)
    assert rates["cross_thread_share"] == pytest.approx(1 / 3)


def test_the_law_vocabulary_rule_is_sr0s_rule():
    """Distinct users per community, floor ceil(0.01 * authors_seen)."""

    n_authors = 300
    rng = np.random.default_rng(2)
    author_code, subreddit_code = [], []
    # community 0 seen by 5 authors, community 1 by 60, community 2 by 3
    for community, n_users in ((0, 5), (1, 60), (2, 3)):
        for author in range(n_users):
            for _ in range(int(rng.integers(1, 4))):
                author_code.append(author)
                subreddit_code.append(community)
    # pad the author universe to 300 with a community nobody else uses
    for author in range(n_authors):
        author_code.append(author)
        subreddit_code.append(3 + (author % 200))
    order = np.argsort(np.asarray(author_code), kind="stable")
    scaffold = MOD.EventScaffold(
        authors=[f"a{i}" for i in range(n_authors)],
        author_code=np.asarray(author_code, dtype=np.int32)[order],
        subreddit_code=np.asarray(subreddit_code, dtype=np.int32)[order],
        created_utc=np.arange(len(author_code), dtype=np.float64),
        link_code=np.zeros(len(author_code), dtype=np.int32),
        subreddits=[f"c{i}" for i in range(203)],
        vocabulary=["c1"],
        vocab_of_subreddit=np.full(203, -1, dtype=np.int32),
        stream_stats={})
    info = MOD.law_vocabulary(scaffold)
    assert info["authors_seen"] == n_authors
    assert info["floor_users"] == math.ceil(0.01 * n_authors) == 3
    # communities 0 (5 users), 1 (60) and 2 (3) all clear a floor of 3
    assert info["vocabulary_size"] == 3
    assert info["identical_to_cache"] is False       # the toy cache lists one


# ---------------------------------------------------------------------------
# The exact-bag shuffle, asserted on THIS cohort
# ---------------------------------------------------------------------------


def test_exact_bag_shuffle_is_bit_exact_on_this_cohorts_fold_layout(tmp_path):
    """Per-half unigram bincounts must be EXACTLY invariant, not approximately.

    Run on a small author-restricted slice of the real disjoint cache, so the
    invariant is asserted on this cohort's own half boundaries rather than on
    a synthetic layout.
    """

    cache = _cache()
    segments = MOD.author_segments(cache)
    pool = segments["order_pool"]
    codes = np.sort(np.random.default_rng(1).choice(pool, size=40,
                                                    replace=False))
    scaffold = MOD.restrict_scaffold(cache, codes)
    context = MOD.build_pool_context(scaffold, "full",
                                     MOD.ORDER_POOL_MIN_PER_HALF,
                                     _log(tmp_path))
    maps, _info = MOD.build_state_maps(context, MOD.C_PRIMARY, _log(tmp_path))
    rng = np.random.default_rng(MOD.SEED)
    for fold_data, state_of_vocab in zip(context.folds, maps):
        states = state_of_vocab[fold_data.event_vocab]
        side = MOD.C_PRIMARY + 1
        reference = np.bincount(
            fold_data.event_half.astype(np.int64) * side
            + states.astype(np.int64),
            minlength=fold_data.n_halves * side)
        for _ in range(5):
            permutation = MOD.U1.within_half_permutation(
                fold_data.event_half, rng)
            shuffled = states[permutation]
            got = np.bincount(
                fold_data.event_half.astype(np.int64) * side
                + shuffled.astype(np.int64),
                minlength=fold_data.n_halves * side)
            assert np.array_equal(got, reference)
            # the shuffle never moves an event across a half boundary
            assert np.array_equal(fold_data.event_half[permutation],
                                  fold_data.event_half)
            # and it really does move things: order is not preserved
        assert not np.array_equal(permutation, np.arange(permutation.size))


def test_fold_purity_is_asserted_on_this_cohort(tmp_path):
    cache = _cache()
    segments = MOD.author_segments(cache)
    codes = np.sort(np.random.default_rng(2).choice(
        segments["order_pool"], size=40, replace=False))
    context = MOD.build_pool_context(MOD.restrict_scaffold(cache, codes),
                                     "full", MOD.ORDER_POOL_MIN_PER_HALF,
                                     _log(tmp_path))
    assert MOD.assert_fold_purity(context)["status"] == "PASS"


# ---------------------------------------------------------------------------
# rho: U1's formula, agreeing on a toy
# ---------------------------------------------------------------------------


def test_rho_is_u1s_formula_on_a_toy_with_a_known_answer():
    U1 = _load("u1_for_rho_test", U1_SCRIPT)
    # rho = (real - null) / (1 - null): a hand-checkable identity
    assert U1.rho_from_auc(0.95, 0.90) == pytest.approx(0.5)
    assert U1.rho_from_auc(0.90, 0.90) == pytest.approx(0.0)
    assert U1.rho_from_auc(1.00, 0.90) == pytest.approx(1.0)
    assert U1.rho_from_auc(0.85, 0.90) == pytest.approx(-0.5)
    assert math.isnan(U1.rho_from_auc(0.99, 1.0))
    # and the sealed source row is reproduced from its own published AUCs
    path = ROOT / "results/m4_u1_order_identity/arms.json"
    if not path.exists():                             # pragma: no cover
        pytest.skip("U1's artifacts are absent in this checkout")
    primary = next(row for row in json.loads(path.read_text(encoding="utf-8"))
                   if row["arm"] == "primary")
    assert U1.rho_from_auc(primary["auc_real"],
                           primary["auc_null_mean"]) == pytest.approx(
                               primary["rho"])
    assert round(primary["rho"], 4) == MOD.SEALED_ORDER["primary"]["point"]


def test_auc_from_matrix_is_the_exact_rank_auc_on_a_toy():
    U1 = _load("u1_for_auc_test", U1_SCRIPT)
    # a 2x2 gallery where the diagonal wins outright
    matrix = np.array([[0.9, 0.1], [0.2, 0.8]])
    assert U1.auc_from_matrix(matrix) == pytest.approx(1.0)
    # ties get half credit
    assert U1.auc_from_matrix(np.ones((3, 3))) == pytest.approx(0.5)
    # and the diagonal losing outright is AUC 0
    assert U1.auc_from_matrix(np.array([[0.1, 0.9], [0.8, 0.2]])) == \
        pytest.approx(0.0)


# ---------------------------------------------------------------------------
# The four-class transport scheme (#75 + RESOLVES)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("source_ci,target_ci,source_point,target_point,expected", [
    # overlapping intervals inside one cell
    ([0.25, 0.31], [0.28, 0.32], 0.28, 0.31, "REPRODUCES"),
    # touching endpoints still count as met
    ([0.20, 0.28], [0.28, 0.32], 0.24, 0.30, "REPRODUCES"),
    # same cell, disjoint intervals
    ([0.27, 0.31], [0.20, 0.24], 0.29, 0.22, "SHIFTS"),
    # a different cell is a break
    ([0.27, 0.31], [0.02, 0.06], 0.29, 0.04, "BREAKS"),
    # W2's own realised primary row: same cell, disjoint intervals
    ([0.2695, 0.3114], [0.2023, 0.2401], 0.2893, 0.2207, "SHIFTS"),
    # a target interval that itself straddles a boundary resolves nothing
    ([0.25, 0.31], [0.28, 0.34], 0.28, 0.31, "BREAKS"),
])
def test_four_class_scheme_on_order_cell_fixtures(source_ci, target_ci,
                                                  source_point, target_point,
                                                  expected):
    got = MOD.classify_four_class(source_ci, target_ci, source_point,
                                  target_point, MOD.order_cell_of_rho)
    assert got["classification"] == expected


def test_resolves_is_a_precision_gain_not_a_contradiction():
    """W1's Lambda row, replayed: the source straddled zero, the target does not.

    Source +0.0741 [-0.0558, 0.1854] (sign unresolved); target +0.0911
    [+0.0628, +0.1490] (strictly positive) with the source point inside the
    target interval.  Under the three-class rule this was BREAKS; the
    adjudicated fourth class calls it RESOLVES.
    """

    got = MOD.classify_four_class([-0.0558, 0.1854], [0.0628, 0.1490],
                                  0.0741, 0.0911, MOD.sign_cell_of)
    assert got["classification"] == "RESOLVES"
    assert got["source_point_inside_target_ci"] is True
    # the same row under the OLD three-class reading would have been a break
    assert got["source_cell"] != got["target_cell"]


def test_resolves_needs_the_source_point_inside_the_target_interval():
    # source point OUTSIDE the target CI: a genuine break, not a precision gain
    got = MOD.classify_four_class([-0.20, 0.05], [0.30, 0.50],
                                  -0.05, 0.40, MOD.sign_cell_of)
    assert got["classification"] == "BREAKS"
    # ... and a straddling TARGET is never a resolution
    got = MOD.classify_four_class([0.27, 0.31], [-0.05, 0.30],
                                  0.29, 0.10, MOD.sign_cell_of)
    assert got["classification"] == "BREAKS"


def test_resolves_works_at_an_order_cell_boundary_too():
    """A source interval straddling 0.33 that the target excludes."""

    got = MOD.classify_four_class([0.30, 0.36], [0.25, 0.32],
                                  0.32, 0.29, MOD.order_cell_of_rho)
    assert got["classification"] == "RESOLVES"


def test_missing_source_interval_falls_back_to_point_in_target_ci():
    inside = MOD.classify_four_class(None, [0.96, 0.99], 0.9837, 0.9817,
                                     MOD.auc_cell_of)
    assert inside["classification"] == "REPRODUCES"
    assert inside["source_ci_missing"] is True
    outside = MOD.classify_four_class(None, [0.70, 0.73], 0.7461, 0.7154,
                                      MOD.auc_cell_of)
    assert outside["classification"] == "SHIFTS"
    assert outside["source_ci_missing"] is True
    # a collapse to chance is a BREAK even with no source interval
    collapsed = MOD.classify_four_class(None, [0.40, 0.48], 0.9837, 0.44,
                                        MOD.auc_cell_of)
    assert collapsed["classification"] == "BREAKS"


def test_auc_and_order_cells_partition_their_lines():
    assert MOD.auc_cell_of(0.98) == "ABOVE_CHANCE"
    assert MOD.auc_cell_of(0.50) == "AT_CHANCE"
    assert MOD.auc_cell_of(0.42) == "BELOW_CHANCE"
    assert MOD.order_cell_of_rho(-0.01) == "NO_ORDER_CHANNEL"
    assert MOD.order_cell_of_rho(0.0) == "NO_ORDER_CHANNEL"
    assert MOD.order_cell_of_rho(0.05) == "ORDER_TRACE"
    assert MOD.order_cell_of_rho(0.10) == "ORDER_CHANNEL"
    assert MOD.order_cell_of_rho(0.33) == "ORDER_CHANNEL"
    assert MOD.order_cell_of_rho(0.34) == "ORDER_MAJOR"


def test_depth_set_classes_are_the_registered_rule():
    def classify(source, target):
        branch = {"arms": {"full": {"stable_depths": target},
                           "clean_no_explicit_personality":
                               {"stable_depths": target}}}
        saved = dict(MOD.SEALED_DEPTHS)
        MOD.SEALED_DEPTHS.update({"full": source, "clean": source})
        try:
            return MOD.depth_transport_rows(branch)[0]["classification"]
        finally:
            MOD.SEALED_DEPTHS.clear()
            MOD.SEALED_DEPTHS.update(saved)

    assert classify([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == "DEPTHS_REPRODUCE"
    assert classify([1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6]) == "DEPTHS_SHIFT"
    assert classify([1, 2, 3, 4, 5], [1, 2, 3, 4]) == "DEPTHS_SHIFT"
    assert classify([1, 2, 3, 4, 5], [1, 2, 3]) == "DEPTHS_BREAK"
    assert classify([1, 2, 3, 4, 5], []) == "DEPTHS_BREAK"


def test_the_verdict_is_routed_by_the_primary_rho_row_only():
    def route(rho, ci, classification):
        row = {"key": "primary", "target_point": rho, "target_ci": ci,
               "classification": classification, "source_cell": "ORDER_CHANNEL",
               "arm_cell_with_ci_support":
                   MOD.order_cell_of({"rho": rho, "rho_ci": ci})}
        return MOD.route_verdict([row], {"gallery_n": 984})["verdict"]

    assert route(0.29, [0.27, 0.31], "REPRODUCES") == "ORDER_TRANSPORTS"
    assert route(0.29, [0.27, 0.31], "RESOLVES") == "ORDER_TRANSPORTS"
    assert route(0.22, [0.20, 0.24], "SHIFTS") == "ORDER_SHIFTS"
    assert route(0.05, [0.03, 0.07], "BREAKS") == "ORDER_BREAKS"
    assert route(0.40, [0.36, 0.44], "BREAKS") == "ORDER_BREAKS"
    # NULL-first: a CI touching zero is the no-channel case
    assert route(0.08, [-0.01, 0.17], "BREAKS") == "ORDER_BREAKS"


# ---------------------------------------------------------------------------
# The ID-leak helper under the #83 HEAD-identical policy
# ---------------------------------------------------------------------------


def test_new_hits_are_separated_from_pre_existing_ones_mechanically():
    hits = [{"path": "/repo/docs/CLAIMS_LEDGER.md", "line": 58},
            {"path": "/repo/docs/CLAIMS_LEDGER.md", "line": 903},
            {"path": "/repo/reports/W2.md", "line": 7}]
    assert [h["line"] for h in
            MOD.new_hits_only(hits, {("CLAIMS_LEDGER.md", 58)})] == [903, 7]
    # a leg-authored file has no HEAD version, so its baseline is empty
    assert len(MOD.new_hits_only(hits, set())) == 3
    # a hit on a DIFFERENT line of a pre-existing file is still NEW
    assert len(MOD.new_hits_only(hits, {("CLAIMS_LEDGER.md", 59)})) == 3
    # and a fully pre-existing hit set clears the gate
    assert MOD.new_hits_only(hits, {("CLAIMS_LEDGER.md", 58),
                                    ("CLAIMS_LEDGER.md", 903),
                                    ("W2.md", 7)}) == []


def test_the_scanner_finds_a_planted_name_and_respects_word_boundaries(tmp_path):
    planted = tmp_path / "planted.md"
    planted.write_text("a line about zzqqxx-user here\n"
                       "and embeddedzzqqxxinside is not a hit\n",
                       encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([planted], ["zzqqxx-user", "zzqqxx"])
    assert scan["status"] == "FAIL"
    assert {h["line"] for h in scan["hits"]} == {1}
    clean = tmp_path / "clean.md"
    clean.write_text("nothing to see\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([clean], ["zzqqxx-user"])["status"] == "PASS"


def test_baseline_recovery_marks_leg_authored_files_as_zero_tolerance(tmp_path):
    """Files with no HEAD version get an empty baseline, hence no tolerance."""

    absent = ROOT / "reports" / "SUICA_M4_W2_FAST_BRANCH_TRANSPORT_REPORT.md"
    present = ROOT / "docs" / "CLAIMS_LEDGER.md"
    keys, detail = MOD.baseline_hit_keys([absent, present], ["zzqqxx-user"],
                                         tmp_path / "head")
    assert detail["files"][present.relative_to(ROOT).as_posix()] == \
        "recovered from HEAD"
    # the report is authored by THIS leg, so it has no HEAD version yet; once
    # it is committed the entry flips to "recovered from HEAD" and its own
    # content becomes its baseline -- which is why the gate is re-run
    assert detail["files"][absent.relative_to(ROOT).as_posix()] in (
        "absent at HEAD (authored by this leg)", "recovered from HEAD")
    assert isinstance(keys, set)


def test_committed_files_are_the_five_this_leg_touches():
    names = {path.name for path in MOD.COMMITTED_FILES}
    assert names == {"SUICA_M4_W2_FAST_BRANCH_TRANSPORT_REPORT.md",
                     "run_suica_m4_w2_fast_branch_transport.py",
                     "test_m4_w2_fast_branch_transport.py",
                     "SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md",
                     "CLAIMS_LEDGER.md"}


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------


def test_no_personality_label_is_read_anywhere():
    """`author_profiles.csv` may be NAMED in governance prose, never opened."""

    text = SCRIPT.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "author_profiles" not in line:
            continue
        assert "never" in line.casefold(), line
        for access in ("read_csv", "open(", "np.load", "loadtxt"):
            assert access not in line, line
    for banned in ("author_profiles.csv", "profiles.csv", "labels.csv",
                   "big5_prepared", "mbti_axes"):
        offenders = [ln for ln in text.splitlines()
                     if banned in ln and "never" not in ln.casefold()]
        assert offenders == [], (banned, offenders)
    for trait in ("openness", "conscientiousness", "neuroticism",
                  "agreeableness", "extraversion"):
        assert trait not in text.casefold(), trait


def test_artifacts_live_only_in_gitignored_results():
    assert str(MOD.DEFAULT_OUTPUT).endswith("results/m4_w2_fast_branch_transport")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore.splitlines()


# ---------------------------------------------------------------------------
# Committed-run consistency (skipped in a fresh checkout)
# ---------------------------------------------------------------------------


def test_committed_run_reproduced_every_anchor():
    anchors = _artifact("anchors.json")
    assert anchors["status"] == "PASS"
    assert anchors["mismatches"] == {}
    assert anchors["vocabulary_identical_to_cache"] is True
    assert anchors["observed"]["law_vocabulary"] == 1443
    assert anchors["observed"]["order_pool"] == 7247
    assert anchors["observed"]["branch_pool"] == 8625


def test_committed_run_was_size_matched_on_both_families():
    order = _artifact("order_arms.json")
    branch = _artifact("branch_arms.json")
    assert order["gallery_n"] == 984
    assert branch["gallery_n_input"] == 1304
    for arm in order["arms"].values():
        assert arm["pool_size"] == 984
        assert arm["bag_invariance_exact"] is True
        assert arm["b_shuffle"] == MOD.B_SHUFFLE


def test_committed_run_id_gate_passed_over_the_full_universe():
    scan = _artifact("id_leak_scan.json")
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == 10_296
    authored = {"SUICA_M4_W2_FAST_BRANCH_TRANSPORT_REPORT.md",
                "run_suica_m4_w2_fast_branch_transport.py",
                "test_m4_w2_fast_branch_transport.py"}
    assert not (authored & {Path(h["path"]).name
                            for h in scan.get("new_hits", [])})
    assert {"SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md", "CLAIMS_LEDGER.md"} <= \
        {Path(p).name for p in scan["files_scanned"]}


def test_the_committed_report_is_generated_from_the_committed_artifacts():
    if not REPORT.exists():                           # pragma: no cover
        pytest.skip("the W2 run has not been executed in this checkout")
    verdict = _artifact("verdict.json")
    text = REPORT.read_text(encoding="utf-8")
    assert verdict["verdict"] in text
    assert f"{verdict['primary_rho']:.4f}" in text
    transport = _artifact("transport_table.json")
    for row in transport["order"]:
        assert f"{row['target_point']:.4f}" in text, row["key"]
    for row in transport["branch"]:
        assert f"{row['target_point']:.4f}" in text, row["key"]
