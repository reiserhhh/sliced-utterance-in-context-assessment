"""M4-U2b -- the persistence budget by carrier: contract tests.

The leg's whole claim is a CONTRAST of floor shares between two carrier
restrictions of the SAME blocks, so the properties that must hold are the ones
that make such a contrast meaningful at all.

**The pair set must be identical across rows** (#72).  If the common row and
the distinctive row were computed on even slightly different pair sets, their
floor-share difference would confound the carrier with the sample, and the
paired bootstrap that carries the CI would be paired in name only.  This is
tested first and hardest: identical pair indices, identical cross reservoir,
identical permutation plans, identical bootstrap author draws.

**The split must BE the registered object.**  The verdict's whole meaning
depends on Common(0.5) being the 32 communities the registration censused at a
realized share of 0.5036, computed on the pinned universe with the pinned
ranking (#77).

**The restriction must be a renormalization, not a projection.**  A restricted
block vector is sqrt(counts) over the sub-vocabulary, L2-normalized; taking the
full Hellinger vector's columns and renormalizing must give exactly that.

**The taste row must never see its own test authors.**  Its embeddings are
fitted per fold, and the fold purity gate is a mass identity, not a promise.

The rest pins the machinery the registration named as blocking: the U2 anchor
comparison (#56), the ID-leak scan, the pool-gate arithmetic, the cell
boundaries, and the permutation null's location on a structureless toy.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_u2b_persistence_budget.py"
U2_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2_persistence_curve.py"
T2_SCRIPT = ROOT / "scripts" / "run_suica_m4_t2_matched_residual.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_u2b_persistence_budget", SCRIPT)
DAY = 86400.0


# ---------------------------------------------------------------------------
# Toy builders
# ---------------------------------------------------------------------------


def _toy_blocks(rng, n_blocks=200, n_authors=16, n_vocab=12,
                span_days=1300.0, k=50):
    """Exact-K count blocks with NO author structure, plus their features.

    Authors are assigned independently of time (U2's toy convention) so a
    within-quarter relabelling is not a near no-op.
    """

    author = rng.integers(0, n_authors, size=n_blocks).astype(np.int32)
    mid_days = np.sort(rng.uniform(0.0, span_days, size=n_blocks))
    counts = rng.multinomial(k, np.full(n_vocab, 1.0 / n_vocab),
                             size=n_blocks).astype(np.float64)
    features = np.sqrt(counts / k).astype(np.float32)
    quarter = (mid_days // MOD.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid_days, quarter))
    return (features[order], counts[order], author[order], quarter[order],
            mid_days[order])


# ---------------------------------------------------------------------------
# #72 -- ONE pair set for all rows
# ---------------------------------------------------------------------------


def test_eligibility_is_a_block_property_so_the_pair_set_is_shared():
    """The registration's pair-level rule reduces to a per-block predicate.

    "both blocks hold >= m events in BOTH sub-vocabularies" is a conjunction of
    two per-block conditions, so the eligible PAIR set is exactly the
    same-author pair set of the eligible BLOCK set -- the property the whole
    leg's pairing rests on.
    """

    rng = np.random.default_rng(3)
    n_blocks, k = 300, 50
    common_count = rng.integers(0, k + 1, size=n_blocks)
    distinct_count = k - common_count
    author = rng.integers(0, 20, size=n_blocks)
    m = 10

    import itertools

    # the literal pair-level rule, applied pair by pair
    literal = {
        (i, j) for i, j in itertools.combinations(range(n_blocks), 2)
        if author[i] == author[j]
        and common_count[i] >= m and distinct_count[i] >= m
        and common_count[j] >= m and distinct_count[j] >= m}
    # the block-subset rule the runner actually uses
    block_ok = (common_count >= m) & (distinct_count >= m)
    eligible = [int(v) for v in np.flatnonzero(block_ok)]
    subset = {(i, j) for i, j in itertools.combinations(eligible, 2)
              if author[i] == author[j]}
    assert literal == subset
    assert len(literal) > 0


def test_rows_share_pair_indices_permutations_and_bootstrap_draws():
    """All rows on one block set => identical pairs, plans and author draws."""

    rng = np.random.default_rng(17)
    features, counts, author, quarter, mid = _toy_blocks(rng)
    common_cols = np.arange(4)
    distinct_cols = np.arange(4, features.shape[1])

    rows = {
        "full": features,
        "common": MOD.renormalize(features, common_cols),
        "distinct": MOD.renormalize(features, distinct_cols),
    }
    results = {key: MOD.U2.compute_arm(value, author, quarter, mid,
                                       n_perm=5, n_boot=7, seed=MOD.SEED,
                                       label=key)
               for key, value in rows.items()}

    reference = results["full"]
    assert sum(reference["self_pairs"]) > 0
    for key, result in results.items():
        assert result["self_pairs"] == reference["self_pairs"], key
        assert result["n_blocks"] == reference["n_blocks"], key
        assert result["n_authors"] == reference["n_authors"], key
        assert result["n_cells"] == reference["n_cells"], key
        assert result["cross_pairs_available"] == \
            reference["cross_pairs_available"], key

    # the permutation scaffold depends only on (quarter, author, seed)
    plan_a = MOD.U2.build_quarter_plans(quarter, author, 5, MOD.SEED)
    plan_b = MOD.U2.build_quarter_plans(quarter, author, 5, MOD.SEED)
    for q in plan_a:
        assert np.array_equal(plan_a[q].slot_position, plan_b[q].slot_position)
        assert np.array_equal(plan_a[q].slot_author, plan_b[q].slot_author)

    # the bootstrap multinomial depends only on (seed, n_authors, n_boot)
    n_authors = results["full"]["n_authors"]
    draw_a = np.random.default_rng(MOD.SEED + 11).multinomial(
        n_authors, np.full(n_authors, 1.0 / n_authors), size=7)
    draw_b = np.random.default_rng(MOD.SEED + 11).multinomial(
        n_authors, np.full(n_authors, 1.0 / n_authors), size=7)
    assert np.array_equal(draw_a, draw_b)


def test_a_shared_pair_set_makes_the_contrast_bootstrap_paired():
    """Δ's bootstrap is the difference of replicate-aligned floor shares."""

    rng = np.random.default_rng(23)
    features, counts, author, quarter, mid = _toy_blocks(rng)
    a = MOD.U2.compute_arm(MOD.renormalize(features, np.arange(4)), author,
                           quarter, mid, n_perm=3, n_boot=32, seed=MOD.SEED,
                           label="a")
    b = MOD.U2.compute_arm(MOD.renormalize(features, np.arange(4, 12)),
                           author, quarter, mid, n_perm=3, n_boot=32,
                           seed=MOD.SEED, label="b")
    delta = MOD.contrast("Δ", a, b, paired=True)

    manual = (MOD.floor_share(a["boot_curve"])
              - MOD.floor_share(b["boot_curve"]))
    assert delta["ci"] == MOD.percentile_ci(manual)
    assert delta["point"] == pytest.approx(a["floor_share"] - b["floor_share"])
    assert a["boot_curve"].shape == b["boot_curve"].shape


# ---------------------------------------------------------------------------
# The split (#77: the registered object, with its exact computation)
# ---------------------------------------------------------------------------


def test_common_prefix_is_the_smallest_prefix_reaching_q():
    counts = np.array([50, 30, 12, 5, 3], dtype=np.int64)
    vocab_index = np.repeat(np.arange(counts.size), counts)
    order, cumulative, universe = MOD.community_ranking(vocab_index,
                                                        counts.size)
    assert universe == int(counts.sum())
    assert list(order) == [0, 1, 2, 3, 4]
    columns, share = MOD.common_prefix(order, cumulative, 0.5)
    assert list(columns) == [0]              # 0.50 reached at the first rank
    assert share == pytest.approx(0.5)
    columns, share = MOD.common_prefix(order, cumulative, 0.51)
    assert list(columns) == [0, 1]
    assert share == pytest.approx(0.8)


def test_community_ranking_tie_break_is_deterministic():
    counts = np.array([10, 10, 10, 1], dtype=np.int64)
    vocab_index = np.repeat(np.arange(counts.size), counts)
    order, _cumulative, _universe = MOD.community_ranking(vocab_index,
                                                          counts.size)
    assert list(order) == [0, 1, 2, 3]       # ties by ascending vocab index


def test_oov_events_are_excluded_from_the_universe():
    vocab_index = np.array([0, 0, 1, -1, -1, -1, 2], dtype=np.int64)
    _order, _cumulative, universe = MOD.community_ranking(vocab_index, 3)
    assert universe == 4


def test_registered_split_reproduces_32_communities_at_0_5036():
    """BLOCKING census pin: the primary split IS the registered object."""

    cache_path = ROOT / "results/m4_u1_order_identity/events_cache.npz"
    if not cache_path.exists():          # pragma: no cover - gitignored
        pytest.skip("events cache not present")
    cache = MOD.U2.load_event_cache(cache_path)
    assert MOD.U2.verify_cache_anchors(cache)["status"] == "PASS"

    vocab_index = cache.vocab_of_subreddit[cache.subreddit_code]
    order, cumulative, universe = MOD.community_ranking(
        vocab_index, len(cache.vocabulary))
    assert universe == MOD.CENSUS_PINS["universe_in_vocab_events"]
    columns, share = MOD.common_prefix(order, cumulative, MOD.Q_PRIMARY)
    assert columns.size == MOD.CENSUS_PINS["common_size_q50"] == 32
    assert round(share, 4) == MOD.CENSUS_PINS["common_share_q50"] == 0.5036
    for q, size_key, share_key in ((0.3, "common_size_q30",
                                    "common_share_q30"),
                                   (0.7, "common_size_q70",
                                    "common_share_q70")):
        cols, sh = MOD.common_prefix(order, cumulative, q)
        assert cols.size == MOD.CENSUS_PINS[size_key]
        assert round(sh, 4) == MOD.CENSUS_PINS[share_key]


# ---------------------------------------------------------------------------
# Renormalization
# ---------------------------------------------------------------------------


def test_renormalization_equals_sqrt_counts_over_the_sub_vocabulary():
    """Restricting the Hellinger vector and renormalizing IS the sub-vector."""

    counts = np.array([[9.0, 16.0, 0.0, 25.0, 0.0],
                       [1.0, 1.0, 1.0, 1.0, 46.0]])
    k = counts.sum(axis=1)[0]
    features = np.sqrt(counts / k).astype(np.float32)
    columns = np.array([0, 1, 2])

    restricted = MOD.renormalize(features, columns)
    direct = np.sqrt(counts[:, columns])
    direct = direct / np.linalg.norm(direct, axis=1, keepdims=True)
    assert np.allclose(restricted, direct, atol=1e-6)
    assert np.allclose(np.linalg.norm(restricted, axis=1), 1.0, atol=1e-6)

    # a hand-checked row: sqrt(9),sqrt(16),0 -> (3,4,0)/5
    assert restricted[0] == pytest.approx([0.6, 0.8, 0.0], abs=1e-6)


def test_renormalization_leaves_an_all_zero_row_at_zero():
    features = np.array([[0.0, 0.0, 1.0]], dtype=np.float32)
    out = MOD.renormalize(features, np.array([0, 1]))
    assert np.all(out == 0.0)


def test_sub_vocabulary_counts_are_recovered_exactly_from_the_features():
    """K * f^2 recovers the count because a block's counts sum to K."""

    rng = np.random.default_rng(5)
    k = 50
    counts = rng.multinomial(k, np.full(9, 1.0 / 9), size=64)
    features = np.sqrt(counts / k).astype(np.float32)
    columns = np.array([0, 2, 5])
    recovered = MOD.block_counts_over(features, columns, k)
    assert np.abs(recovered - np.rint(recovered)).max() < 1e-3
    assert np.array_equal(np.rint(recovered).astype(np.int64),
                          counts[:, columns].sum(axis=1))
    # the feature is already unit-norm, so the full-vocabulary recovery is K
    everything = MOD.block_counts_over(features, np.arange(9), k)
    assert np.allclose(everything, k, atol=1e-3)


# ---------------------------------------------------------------------------
# The permutation null's own location (#68)
# ---------------------------------------------------------------------------


def test_permutation_null_center_is_zero_on_a_structureless_toy():
    """E's null location is 0 BY CONSTRUCTION; here it is a realized number."""

    rng = np.random.default_rng(29)
    features, _counts, author, quarter, mid = _toy_blocks(
        rng, n_blocks=260, n_authors=18)
    result = MOD.U2.compute_arm(MOD.renormalize(features, np.arange(5)),
                                author, quarter, mid, n_perm=120, n_boot=40,
                                seed=MOD.SEED, label="toy")
    centers = np.asarray(result["curve_null_center"])
    finite = centers[np.isfinite(centers)]
    assert finite.size >= 4
    assert np.abs(finite).max() < 0.02, centers
    # the real curve of a structureless world sits inside its own null band
    for b in range(MOD.N_BINS):
        lo, hi = result["curve_null_band"][b]
        value = result["curve"][b]
        if not np.isfinite(value) or not np.isfinite(lo):
            continue
        assert lo - 0.02 <= value <= hi + 0.02, (b, value, lo, hi)


def test_floor_share_null_is_reported_as_a_location_not_a_bound():
    """The Δfloor null is a ratio of near-zero quantities: heavy-tailed.

    The contract is that the runner reports the null's CENTER and IQR (the
    registration's claim is about location) and records what fraction of
    replicates is even finite -- never that the 95% band is narrow.
    """

    a = {"floor_share": 0.4,
         "boot_curve": np.tile([0.5, 0, 0, 0, 0.2, 0], (16, 1)).astype(float),
         "null_curve": np.tile([1e-4, 0, 0, 0, -1e-4, 0],
                               (16, 1)).astype(float)}
    b = {"floor_share": 0.6,
         "boot_curve": np.tile([0.5, 0, 0, 0, 0.3, 0], (16, 1)).astype(float),
         "null_curve": np.tile([1e-4, 0, 0, 0, 1e-4, 0],
                               (16, 1)).astype(float)}
    out = MOD.contrast("Δ", a, b, paired=True)
    assert out["point"] == pytest.approx(-0.2)
    assert set(("null_center", "null_iqr", "null_finite_fraction")) <= \
        set(out)
    assert out["null_finite_fraction"] == 1.0
    assert out["null_center"] == pytest.approx(-2.0)


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("point,ci,expected", [
    (0.02, [-0.05, 0.09], "NO_LAYER_SPLIT"),
    (0.14, [0.06, 0.22], "DISTINCTIVE_STANDING"),
    (-0.14, [-0.22, -0.06], "COMMON_STANDING"),
    (0.14, [-0.03, 0.31], "UNRESOLVED_SPLIT"),
    (-0.14, [-0.31, 0.03], "UNRESOLVED_SPLIT"),
    (0.001, [0.0005, 0.02], "DISTINCTIVE_STANDING"),
])
def test_cells_are_the_registered_boundaries(point, ci, expected):
    delta = {"point": point, "ci": ci,
             "ci_half_width": 0.5 * (ci[1] - ci[0])}
    assert MOD.classify_delta(delta)["cell"] == expected


def test_no_layer_split_requires_both_clauses():
    """CI including 0 is not enough: |Δ| must also sit inside the band."""

    wide_point = {"point": 0.30, "ci": [-0.02, 0.62], "ci_half_width": 0.32}
    assert MOD.classify_delta(wide_point)["cell"] == "UNRESOLVED_SPLIT"
    assert MOD.classify_delta(wide_point)["ci_includes_zero"] is True
    assert MOD.classify_delta(wide_point)["abs_point_below_band"] is False


def test_equivalence_band_reachability_is_reported():
    narrow = MOD.classify_delta({"point": 0.0, "ci": [-0.04, 0.04],
                                 "ci_half_width": 0.04})
    wide = MOD.classify_delta({"point": 0.0, "ci": [-0.30, 0.30],
                               "ci_half_width": 0.30})
    assert narrow["band_reachable"] is True
    assert wide["band_reachable"] is False
    assert wide["half_width_over_band"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# The pool gate (#69)
# ---------------------------------------------------------------------------


def test_self_pair_census_counts_pairs_and_contributors_by_bin():
    author = np.array([0, 0, 0, 1, 1, 2])
    # author 0: gaps 30 d, 400 d, 370 d ; author 1: gap 800 d ; author 2: none
    mid = np.array([0.0, 30.0, 400.0, 0.0, 800.0, 10.0])
    pairs, contributors = MOD.self_pair_census(author, mid)
    assert list(pairs) == [1, 0, 0, 2, 1, 0]
    assert pairs.sum() == 4                    # the lone block contributes 0
    assert contributors == [1, 0, 0, 1, 1, 0]
    # authors are grouped regardless of input order
    order = np.array([5, 1, 4, 0, 3, 2])
    shuffled = MOD.self_pair_census(author[order], mid[order])
    assert list(shuffled[0]) == list(pairs) and shuffled[1] == contributors


def test_pool_gate_arithmetic_is_a_conjunction_on_the_2_3y_bin():
    """Both clauses must hold; either one short is UNMET."""

    def status(pairs, authors):
        return ("PASS" if pairs >= MOD.POOL_GATE_MIN_PAIRS_2_3Y
                and authors >= MOD.POOL_GATE_MIN_AUTHORS_2_3Y else "UNMET")

    assert status(100_000, 400) == "PASS"
    assert status(99_999, 400) == "UNMET"
    assert status(100_000, 399) == "UNMET"
    assert status(99_714, 348) == "UNMET"       # the realized primary pool
    assert MOD.POOL_GATE_MIN_PAIRS_2_3Y == 100_000
    assert MOD.POOL_GATE_MIN_AUTHORS_2_3Y == 400


# ---------------------------------------------------------------------------
# Taste row
# ---------------------------------------------------------------------------


def test_ppmi_svd_is_the_frozen_t2_recipe_bit_for_bit():
    """RN-SR3-1 pattern: the replication must BE the recipe, not resemble it."""

    if not T2_SCRIPT.exists():           # pragma: no cover
        pytest.skip("T2 harness not present")
    t2 = _load("m4_t2_matched_residual_for_u2b", T2_SCRIPT)
    rng = np.random.default_rng(101)
    counts = rng.integers(0, 40, size=(23, 17)).astype(np.float64)
    mine = MOD.ppmi_svd(counts, 64, MOD.SEED)
    theirs = t2.ppmi_svd(counts, 64, MOD.SEED)
    assert np.array_equal(mine, theirs)
    assert mine.shape == (17, min(64, 17))


def test_ppmi_svd_handles_an_empty_count_matrix():
    out = MOD.ppmi_svd(np.zeros((4, 6)), 64, MOD.SEED)
    assert out.shape == (6, 64)
    assert np.all(out == 0.0)


def test_taste_folds_partition_the_pool_and_are_deterministic():
    pool = np.arange(849)
    folds_a = MOD.taste_folds(pool, MOD.SEED, MOD.TASTE_FOLDS)
    folds_b = MOD.taste_folds(pool, MOD.SEED, MOD.TASTE_FOLDS)
    seen: set[int] = set()
    for (train_a, test_a), (train_b, test_b) in zip(folds_a, folds_b):
        assert np.array_equal(train_a, train_b)
        assert np.array_equal(test_a, test_b)
        assert not (set(train_a.tolist()) & set(test_a.tolist()))
        assert train_a.size + test_a.size == pool.size
        assert not (seen & set(test_a.tolist()))
        seen |= set(test_a.tolist())
    assert seen == set(pool.tolist())


def test_taste_fold_purity_is_a_mass_identity_the_run_asserts():
    """The fitted matrix's mass must be the TRAINING mass, exactly."""

    rng = np.random.default_rng(7)
    n_authors, n_vocab = 40, 9
    first_half = rng.integers(0, 30, size=(n_authors, n_vocab)
                              ).astype(np.float64)
    mass = first_half.sum(axis=1)
    for train_idx, test_idx in MOD.taste_folds(np.arange(n_authors),
                                               MOD.SEED, MOD.TASTE_FOLDS):
        counts = first_half[train_idx]
        assert counts.shape[0] == train_idx.size
        assert abs(counts.sum() - mass[train_idx].sum()) < 1e-6
        # every test author's mass is entirely absent from the fitted object
        assert abs((mass.sum() - counts.sum())
                   - mass[test_idx].sum()) < 1e-6
        # and an embedding fitted on it cannot depend on a test row
        perturbed = first_half.copy()
        perturbed[test_idx] += 1000.0
        assert np.array_equal(MOD.ppmi_svd(counts, 8, MOD.SEED),
                              MOD.ppmi_svd(perturbed[train_idx], 8, MOD.SEED))


def test_taste_block_vector_is_the_hellinger_weighted_embedding_mean():
    features = np.array([[0.6, 0.8, 0.0]], dtype=np.float32)
    embedding = np.array([[1.0, 0.0], [0.0, 2.0], [5.0, 5.0]])
    taste = np.asarray(features, dtype=np.float64) @ embedding
    assert taste[0] == pytest.approx([0.6, 1.6])
    normalized = taste / np.linalg.norm(taste, axis=1, keepdims=True)
    assert np.linalg.norm(normalized[0]) == pytest.approx(1.0)


def test_fold_pooling_is_the_unweighted_mean_of_fold_curves():
    def fake(curve, boot, null):
        return {"curve": curve, "boot_curve": np.asarray(boot),
                "null_curve": np.asarray(null),
                "self_pairs": [10] * MOD.N_BINS,
                "self_mean": [0.5] * MOD.N_BINS,
                "cross_mean_matched": [0.1] * MOD.N_BINS,
                "mean_gap_days": [1.0] * MOD.N_BINS,
                "n_blocks": 5, "n_authors": 2, "n_quarters": 3,
                "b_perm": 1, "b_boot": 2, "floor_share": curve[4] / curve[0],
                "perm_p_existence": 0.5, "perm_p_decay": 0.5}

    a = fake([0.8, 0.7, 0.6, 0.5, 0.4, 0.3], [[0.8] * 6] * 2, [[0.0] * 6])
    b = fake([0.4, 0.3, 0.3, 0.2, 0.2, 0.1], [[0.4] * 6] * 2, [[0.0] * 6])
    pooled = MOD.pool_fold_results([a, b])
    assert pooled["curve"][0] == pytest.approx(0.6)
    assert pooled["curve"][4] == pytest.approx(0.3)
    assert pooled["floor_share"] == pytest.approx(0.5)
    assert pooled["self_pairs"] == [20] * MOD.N_BINS
    assert pooled["boot_curve"].shape == (2, 6)


# ---------------------------------------------------------------------------
# G0 -- the U2 anchor comparison (#56)
# ---------------------------------------------------------------------------


def test_g0_helper_detects_a_perturbed_anchor():
    committed = {name: ([0.1] * 6 if name.startswith("curve")
                        and "ci" not in name and "band" not in name
                        else ([[0.0, 0.2]] * 6 if ("ci" in name
                                                   or "band" in name)
                              else 0.5))
                 for name in MOD.G0_FIELDS}
    committed["self_pairs"] = [1, 2, 3, 4, 5, 6]
    committed["n_blocks"] = 10
    committed["n_authors"] = 3
    committed["n_quarters"] = 2
    identical = MOD.g0_compare(dict(committed), committed)
    assert identical["status"] == "PASS"
    assert identical["bitwise_identical"] is True
    assert identical["max_abs_difference"] == 0.0

    perturbed = dict(committed)
    perturbed["d"] = 0.5 + 1e-3
    out = MOD.g0_compare(perturbed, committed)
    assert out["status"] == "FAIL"
    assert out["max_abs_difference"] == pytest.approx(1e-3)

    missing = {k: v for k, v in committed.items() if k != "floor_share"}
    assert MOD.g0_compare(dict(committed), missing)["status"] != "PASS"


def test_g0_recomputation_matches_u2_on_a_toy_end_to_end():
    """The imported estimator is deterministic: same inputs, same numbers."""

    rng = np.random.default_rng(41)
    features, _counts, author, quarter, mid = _toy_blocks(rng, n_blocks=150)
    kwargs = dict(n_perm=4, n_boot=16, seed=MOD.U2.SEED,
                  cross_sampler_check=False, label="anchor")
    first = MOD.U2.compute_arm(features, author, quarter, mid, **kwargs)
    second = MOD.U2.compute_arm(features, author, quarter, mid, **kwargs)
    comparison = MOD.g0_compare(first, {k: second[k] for k in MOD.G0_FIELDS})
    assert comparison["status"] == "PASS"
    assert comparison["bitwise_identical"] is True


def test_committed_run_reproduced_u2s_anchor_bitwise():
    """The realized G0 gate, read from the run's own artifact."""

    path = (ROOT / "results/m4_u2b_persistence_budget"
            / "g0_anchor_comparison.json")
    if not path.exists():                # pragma: no cover - gitignored
        pytest.skip("U2b artifacts not present")
    g0 = json.loads(path.read_text(encoding="utf-8"))
    assert g0["status"] == "PASS", g0
    assert g0["bitwise_identical"] is True
    assert g0["max_abs_difference"] == 0.0


# ---------------------------------------------------------------------------
# ID-leak scan and label-freedom
# ---------------------------------------------------------------------------


def test_id_leak_scanner_finds_a_planted_name(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("only carriers, blocks and floor shares here\n")
    dirty = tmp_path / "dirty.md"
    dirty.write_text("the distinctive row for sample_user_9 is thin\n")
    cohort = ["sample_user_9", "another_person"]

    ok = MOD.U2.scan_for_cohort_ids([clean], cohort)
    assert ok["status"] == "PASS" and ok["n_hits"] == 0

    bad = MOD.U2.scan_for_cohort_ids([dirty], cohort)
    assert bad["status"] == "FAIL" and bad["n_hits"] == 1
    assert bad["hits"][0]["line"] == 1

    embedded = tmp_path / "embedded.md"
    embedded.write_text("sample_user_90 is a different token entirely\n")
    assert MOD.U2.scan_for_cohort_ids([embedded], cohort)["status"] == "PASS"


def test_committed_files_carry_no_cohort_identity():
    """The blocking ID-leak gate, run over U2b's exact committed set."""

    meta = ROOT / "results/m4_u1_order_identity/events_cache.meta.json"
    if not meta.exists():                # pragma: no cover - gitignored
        pytest.skip("events cache metadata not present")
    authors = json.loads(meta.read_text(encoding="utf-8"))["authors"]
    assert len(authors) == MOD.ANCHOR_AUTHORS
    targets = [
        SCRIPT,
        Path(__file__),
        ROOT / "reports/SUICA_M4_U2B_PERSISTENCE_BUDGET_REPORT.md",
        ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
        ROOT / "docs/CLAIMS_LEDGER.md",
    ]
    scan = MOD.U2.scan_for_cohort_ids(targets, authors)
    assert scan["status"] == "PASS", scan["hits"]


def test_no_personality_label_is_read_anywhere():
    """Label-free leg: the runner may not touch a Big5 or MBTI value."""

    import ast

    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = [node.value.casefold() for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)]
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc.casefold())

    banned = ("author_profiles", "pandora_official", ".csv", "prepared/",
              "big5/", "mbti_axes", "agreeableness", "conscientiousness",
              "neuroticism", "openness", "extraversion", "introversion")
    for literal in literals:
        if literal in docstrings:
            continue
        for word in banned:
            assert word not in literal, (word, literal[:120])

    assert MOD.DEFAULT_CACHE.name == "events_cache.npz"
    opened = {node.func.attr for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)}
    assert "read_csv" not in opened


# ---------------------------------------------------------------------------
# Registration pins carried in code
# ---------------------------------------------------------------------------


def test_registration_pins_are_the_registered_numbers():
    assert MOD.SEED == 20260818
    assert MOD.B_PERM == 499
    assert MOD.B_BOOT == 1000
    assert MOD.Q_PRIMARY == 0.5
    assert MOD.Q_SENSITIVITIES == (0.3, 0.7)
    assert MOD.M_PRIMARY == 10
    assert MOD.M_SENSITIVITIES == (5, 15)
    assert MOD.TASTE_FOLDS == 5
    assert MOD.TASTE_DIM == 64
    assert MOD.EQUIVALENCE_BAND == 0.10
    assert MOD.LEAN_DELTA == (0.05, 0.25)
    assert MOD.K_PRIMARY == 50 and MOD.POOL_MIN_BLOCKS == 4
    assert MOD.CENSUS_PINS["common_size_q50"] == 32
    assert MOD.CENSUS_PINS["common_share_q50"] == 0.5036
    assert MOD.CENSUS_PINS["pool_authors"] == 849
    assert MOD.CENSUS_PINS["pool_blocks"] == 45_731


def test_verdict_endpoint_is_the_2_3y_bin_not_3y_plus():
    assert MOD.BIN_LABELS[MOD.FAR_BIN] == "2-3y"
    assert MOD.BIN_LABELS[MOD.NEAR_BIN] == "0-90d"
    assert MOD.BIN_LABELS[MOD.DESCRIPTIVE_BIN] == "3y+"
    curve = np.array([0.6, 0.5, 0.45, 0.4, 0.3, 0.1])
    assert MOD.floor_share(curve) == pytest.approx(0.5)


def test_machinery_is_imported_from_u2_not_reimplemented():
    """#56: the estimator must be U2's object, not a look-alike."""

    source = SCRIPT.read_text(encoding="utf-8")
    assert "run_suica_m4_u2_persistence_curve.py" in source
    assert MOD.U2.__file__ == str(U2_SCRIPT)
    for name in ("build_blocks", "assign_quarters", "gap_bin", "compute_arm",
                 "scan_for_cohort_ids", "load_event_cache",
                 "verify_cache_anchors", "build_quarter_plans"):
        assert hasattr(MOD.U2, name), name
    # U2b must not define its own copy of the estimator
    assert "def compute_arm" not in source
    assert "def build_blocks" not in source
