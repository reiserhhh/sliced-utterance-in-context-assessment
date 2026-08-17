"""M4-U1 -- order-borne selection identity: contract tests.

The leg's whole claim rests on one property of the null: **the within-half
order shuffle destroys order and preserves the bag EXACTLY**. If the shuffle
leaked bag information, rho would be measuring the bag and not the order, and
every cell in the registration would be reading the wrong quantity. That
contract is tested first and hardest.

The rest pins the machinery the registration named as blocking gates: MH
stationarity and its acceptance formula (the W_transition world's guarantee),
fold purity (no test-author mass in any state map), the tie-stable sort,
the rho arithmetic on a hand-checked toy, OOV mapping, and the ID-leak
scanner.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_u1_order_identity.py"


def _load():
    spec = importlib.util.spec_from_file_location("m4_u1_order_identity",
                                                  SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["m4_u1_order_identity"] = module
    spec.loader.exec_module(module)
    return module


MOD = _load()


# ---------------------------------------------------------------------------
# The exact-bag contract
# ---------------------------------------------------------------------------


def _toy_halves(rng, n_halves=40, n_states=6, low=20, high=90):
    states = []
    halves = []
    for half in range(n_halves):
        length = int(rng.integers(low, high))
        states.append(rng.integers(0, n_states + 1, size=length))
        halves.append(np.full(length, half, dtype=np.int32))
    return (np.concatenate(states).astype(np.int32),
            np.concatenate(halves).astype(np.int32))


def test_shuffle_preserves_each_half_bag_exactly():
    """Blocking: per-half unigram bincounts are invariant under the shuffle."""

    rng = np.random.default_rng(11)
    states, halves = _toy_halves(rng)
    n_states = int(states.max())
    side = n_states + 1
    n_halves = int(halves.max()) + 1

    def bags(values):
        return np.bincount(halves.astype(np.int64) * side
                           + values.astype(np.int64),
                           minlength=n_halves * side).reshape(n_halves, side)

    reference = bags(states)
    shuffle_rng = np.random.default_rng(12)
    for _ in range(50):
        perm = MOD.within_half_permutation(halves, shuffle_rng)
        shuffled = states[perm]
        assert np.array_equal(bags(shuffled), reference)
        # and it must never move an event across a half boundary
        assert np.array_equal(halves[perm], halves)


def test_shuffle_actually_destroys_order():
    """The dual of the invariance contract: adjacency must genuinely change."""

    rng = np.random.default_rng(13)
    # a strongly ordered sequence: long runs of one state per half
    halves = np.repeat(np.arange(20, dtype=np.int32), 60)
    states = np.concatenate([np.repeat([h % 5, (h + 1) % 5], 30)
                             for h in range(20)]).astype(np.int32)
    same = halves[1:] == halves[:-1]
    pair_from = np.flatnonzero(same).astype(np.int64)
    pair_to = pair_from + 1
    pair_half = halves[pair_from]
    real = MOD.bigram_counts(states, pair_from, pair_to, pair_half, 20, 4)
    shuffle_rng = np.random.default_rng(14)
    perm = MOD.within_half_permutation(halves, shuffle_rng)
    shuffled = MOD.bigram_counts(states[perm], pair_from, pair_to, pair_half,
                                 20, 4)
    assert not np.array_equal(real, shuffled)
    # total pair mass per half is conserved (the same positions are counted)
    assert np.array_equal(real.sum(axis=1), shuffled.sum(axis=1))


def test_shuffle_is_a_permutation_of_positions():
    rng = np.random.default_rng(15)
    _, halves = _toy_halves(rng, n_halves=7)
    perm = MOD.within_half_permutation(halves, np.random.default_rng(16))
    assert np.array_equal(np.sort(perm), np.arange(halves.size))


# ---------------------------------------------------------------------------
# Metropolis-Hastings (the W_transition guarantee)
# ---------------------------------------------------------------------------


def test_mh_acceptance_formula_is_the_textbook_ratio():
    target = np.array([0.5, 0.25, 0.25])
    proposal = np.array([[0.0, 0.75, 0.25],
                         [0.5, 0.0, 0.5],
                         [0.1, 0.9, 0.0]])
    # min(1, pi_j q_ji / (pi_i q_ij))
    expected = min(1.0, (0.25 * 0.5) / (0.5 * 0.75))
    assert MOD.metropolis_hastings_acceptance(target, proposal, 0, 1) == \
        pytest.approx(expected)
    # a move that is favoured is always accepted
    assert MOD.metropolis_hastings_acceptance(target, proposal, 1, 0) == 1.0
    # symmetric-proposal special case reduces to min(1, pi_j / pi_i)
    symmetric = np.array([[0.0, 0.5, 0.5],
                          [0.5, 0.0, 0.5],
                          [0.5, 0.5, 0.0]])
    assert MOD.metropolis_hastings_acceptance(target, symmetric, 0, 1) == \
        pytest.approx(0.5)


def test_mh_kernel_is_stochastic_and_has_target_as_stationary():
    rng = np.random.default_rng(17)
    for beta in (0.0, 1.0, 9.0):
        target = rng.dirichlet(np.full(8, 0.7))
        blocks = rng.permutation(np.arange(8) % 3)
        proposal = MOD.block_proposal(8, blocks, beta)
        assert proposal.sum(axis=1) == pytest.approx(np.ones(8))
        assert np.allclose(np.diagonal(proposal), 0.0)
        kernel = MOD.metropolis_hastings_kernel(target, proposal)
        assert kernel.sum(axis=1) == pytest.approx(np.ones(8))
        assert (kernel >= -1e-12).all()
        # stationarity, exactly (this is what the registration promises)
        assert target @ kernel == pytest.approx(target, abs=1e-12)
        # and detailed balance, which is why
        flow = target[:, None] * kernel
        assert flow == pytest.approx(flow.T, abs=1e-12)


def test_mh_contract_helper_reports_machine_precision():
    report = MOD.mh_stationarity_check()
    assert report["max_stationary_drift"] < 1e-12
    assert report["max_detailed_balance_violation"] < 1e-12
    assert report["row_sum_error"] < 1e-12


def test_sticky_chain_stationary_is_exactly_pi():
    """The registration's in-line proof, checked numerically."""

    rng = np.random.default_rng(18)
    pi = rng.dirichlet(np.full(10, 0.5))
    for s in MOD.SYNTH_STICKY_S:
        kernel = s * np.eye(10) + (1.0 - s) * np.tile(pi, (10, 1))
        assert kernel.sum(axis=1) == pytest.approx(np.ones(10))
        assert pi @ kernel == pytest.approx(pi, abs=1e-12)


# ---------------------------------------------------------------------------
# rho, AUC and the ceiling-aware arithmetic
# ---------------------------------------------------------------------------


def test_rho_on_a_hand_checked_toy():
    # rho = (real - null) / (1 - null)
    assert MOD.rho_from_auc(0.96, 0.92) == pytest.approx(0.5)
    assert MOD.rho_from_auc(0.92, 0.92) == pytest.approx(0.0)
    assert MOD.rho_from_auc(1.0, 0.92) == pytest.approx(1.0)
    assert MOD.rho_from_auc(0.90, 0.92) == pytest.approx(-0.25)
    # the null is NOT 0.5: the same raw excess buys very different rho
    assert MOD.rho_from_auc(0.55, 0.50) == pytest.approx(0.10)
    assert MOD.rho_from_auc(0.99, 0.94) == pytest.approx(0.8333333, abs=1e-6)


def test_auc_from_matrix_hand_checked():
    # 2 authors. diagonal (same-author) scores 0.9, 0.8; off-diagonal 0.1, 0.7
    matrix = np.array([[0.9, 0.1],
                       [0.7, 0.8]])
    # positives {0.9, 0.8}; negatives {0.1, 0.7}: all four comparisons won
    assert MOD.auc_from_matrix(matrix) == pytest.approx(1.0)
    matrix = np.array([[0.5, 0.6],
                       [0.4, 0.5]])
    # positives {0.5, 0.5}; negatives {0.6, 0.4}: 2 wins, 2 losses
    assert MOD.auc_from_matrix(matrix) == pytest.approx(0.5)
    # exact tie handling: half credit
    matrix = np.array([[0.5, 0.5],
                       [0.5, 0.5]])
    assert MOD.auc_from_matrix(matrix) == pytest.approx(0.5)


def test_auc_ties_get_half_credit():
    positive = np.array([1.0, 2.0])
    negative = np.array([2.0, 3.0])
    # 1.0 loses twice; 2.0 ties once (0.5) and loses once
    assert MOD.auc_from_scores(positive, negative) == pytest.approx(0.125)


def test_binned_weighted_auc_matches_exact_auc_at_unit_weights():
    rng = np.random.default_rng(19)
    matrix = rng.random((60, 60))
    matrix[np.arange(60), np.arange(60)] += 0.35
    codes = MOD.bin_matrix(matrix)
    ones = np.ones(60)
    binned = MOD.weighted_auc_from_codes(codes, ones, MOD.BOOT_BINS)
    assert binned == pytest.approx(MOD.auc_from_matrix(matrix), abs=1e-4)


def test_weighted_auc_stack_matches_the_scalar_route():
    rng = np.random.default_rng(20)
    stack = np.stack([MOD.bin_matrix(rng.random((40, 40))) for _ in range(6)])
    counts = rng.integers(0, 4, size=40).astype(np.float64)
    if counts.sum() < 2:  # pragma: no cover - defensive
        counts[:2] = 1.0
    batched = MOD.weighted_auc_stack(stack, counts, MOD.BOOT_BINS)
    scalar = [MOD.weighted_auc_from_codes(codes, counts, MOD.BOOT_BINS)
              for codes in stack]
    assert batched == pytest.approx(np.array(scalar), abs=1e-12)


def test_bootstrap_negative_set_excludes_duplicate_copies_of_one_author():
    """Weighting by c_u * c_v off the diagonal is what enforces this."""

    # author 0 drawn twice, author 1 once, author 2 zero times
    codes = np.array([[3, 0, 0],
                      [0, 3, 0],
                      [0, 0, 3]], dtype=np.int32)
    counts = np.array([2.0, 1.0, 0.0])
    # negatives: only the (0,1) and (1,0) pairs, weight 2 each -> 4 total.
    # A duplicate-copy pair would have added weight on the diagonal.
    weights = np.outer(counts, counts)
    np.fill_diagonal(weights, 0.0)
    assert weights.sum() == pytest.approx(4.0)
    # all positives beat all negatives here
    assert MOD.weighted_auc_from_codes(codes, counts, 8) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Features, states and OOV
# ---------------------------------------------------------------------------


def test_bigram_counts_are_the_realized_adjacencies():
    states = np.array([0, 1, 1, 2, 0], dtype=np.int32)
    halves = np.zeros(5, dtype=np.int32)
    pair_from = np.arange(4, dtype=np.int64)
    counts = MOD.bigram_counts(states, pair_from, pair_from + 1,
                               halves[pair_from], 1, 2)
    square = counts.reshape(3, 3)
    assert square[0, 1] == 1   # 0 -> 1
    assert square[1, 1] == 1   # 1 -> 1
    assert square[1, 2] == 1   # 1 -> 2
    assert square[2, 0] == 1   # 2 -> 0
    assert square.sum() == 4


def test_oov_maps_to_the_extra_state_and_keeps_adjacency_real():
    """OOV events occupy state index C -- they are never spliced out."""

    n_vocab, n_states = 5, 3
    state_of_vocab = np.array([0, 1, 2, n_states, n_states, n_states],
                              dtype=np.int32)  # last entry is the OOV slot
    # vocab ids 3 and 4 have zero training mass -> mapped to OOV (index 3)
    event_vocab = np.array([0, 3, 1, n_vocab, 2], dtype=np.int32)
    states = state_of_vocab[event_vocab]
    assert states.tolist() == [0, n_states, 1, n_states, 2]
    pair_from = np.arange(4, dtype=np.int64)
    counts = MOD.bigram_counts(states, pair_from, pair_from + 1,
                               np.zeros(4, dtype=np.int32), 1, n_states)
    # four adjacencies survive: none was dropped for being OOV
    assert counts.sum() == 4
    square = counts.reshape(n_states + 1, n_states + 1)
    assert square[0, n_states] == 1
    assert square[n_states, 1] == 1


def test_hellinger_features_are_unit_norm_and_smoothed():
    counts = np.array([[4, 0, 0, 0, 2, 0, 0, 0, 1]], dtype=np.int64)
    features = MOD.features_from_counts(counts, 2, "hellinger_joint")
    assert np.linalg.norm(features[0]) == pytest.approx(1.0)
    assert (features > 0).all()          # alpha = 0.5 leaves no exact zero
    total = counts.sum() + MOD.ALPHA * counts.shape[1]
    assert features[0, 0] == pytest.approx(np.sqrt((4 + MOD.ALPHA) / total))


def test_conditional_rows_lens_is_row_normalised_and_unweighted():
    counts = np.array([[10, 0, 0, 0, 0, 0, 0, 0, 4]], dtype=np.int64)
    features = MOD.features_from_counts(counts, 2, "conditional_rows")
    assert np.linalg.norm(features[0]) == pytest.approx(1.0)
    rows = features[0].reshape(3, 3)
    # each row carried equal weight before the global normalisation
    norms = np.linalg.norm(rows, axis=1)
    assert norms == pytest.approx(np.full(3, norms[0]))


def test_stay_rate_is_the_diagonal_share():
    counts = np.zeros((1, 9), dtype=np.int64)
    square = counts.reshape(1, 3, 3)
    square[0, 0, 0] = 3
    square[0, 1, 1] = 1
    square[0, 0, 1] = 4
    assert MOD.stay_rates(counts, 2)[0] == pytest.approx(4 / 8)


def test_stay_rate_similarity_is_negative_absolute_difference():
    counts = np.zeros((4, 9), dtype=np.int64)
    square = counts.reshape(4, 3, 3)
    square[0, 0, 0] = 8; square[0, 0, 1] = 2      # early A, stay 0.8
    square[1, 0, 0] = 6; square[1, 0, 1] = 4      # late  A, stay 0.6
    square[2, 0, 0] = 1; square[2, 0, 1] = 9      # early B, stay 0.1
    square[3, 0, 0] = 2; square[3, 0, 1] = 8      # late  B, stay 0.2
    matrix = MOD.similarity_matrix(counts, 2, "stay_rate")
    assert matrix[0, 0] == pytest.approx(-0.2)
    assert matrix[0, 1] == pytest.approx(-0.6)
    assert matrix[1, 1] == pytest.approx(-0.1)
    # same-author pairs win -> AUC 1
    assert MOD.auc_from_matrix(matrix) == pytest.approx(1.0)


def test_shuffled_bigram_cosine_is_the_squared_bag_cosine_for_product_form():
    """Why the null walks near the bag ceiling (#68), as an identity."""

    rng = np.random.default_rng(21)
    p = rng.dirichlet(np.full(5, 1.2))
    q = rng.dirichlet(np.full(5, 1.2))
    bag_cosine = float(np.sqrt(p) @ np.sqrt(q))
    joint_p = np.outer(p, p).ravel()
    joint_q = np.outer(q, q).ravel()
    bigram_cosine = float(np.sqrt(joint_p) @ np.sqrt(joint_q))
    assert bigram_cosine == pytest.approx(bag_cosine ** 2)


# ---------------------------------------------------------------------------
# Halves, ties and the stable sort
# ---------------------------------------------------------------------------


def test_median_split_sends_boundary_events_to_early():
    created = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    early = MOD.split_halves(created)
    assert early.tolist() == [True, True, True, False, False]
    # a tie ON the median goes early
    created = np.array([10.0, 30.0, 30.0, 30.0, 90.0])
    assert MOD.split_halves(created).tolist() == [True, True, True, True,
                                                  False]


def test_tie_stable_sort_keeps_stream_order_and_is_deterministic():
    author = np.array([1, 1, 1, 0, 0], dtype=np.int32)
    created = np.array([5.0, 5.0, 1.0, 9.0, 9.0])
    order = np.lexsort((created, author))
    # author 0 first; its two tied events keep stream order (3 before 4)
    assert order.tolist() == [3, 4, 2, 0, 1]
    for _ in range(5):
        assert np.array_equal(np.lexsort((created, author)), order)


def test_spherical_kmeans_is_deterministic_and_covers_every_point():
    rng = np.random.default_rng(22)
    points = np.abs(rng.normal(size=(60, 12)))
    first = MOD.spherical_kmeans(points, 4, seed=7, n_init=3)
    second = MOD.spherical_kmeans(points, 4, seed=7, n_init=3)
    assert np.array_equal(first, second)
    assert first.min() >= 0 and first.max() < 4
    assert first.size == 60
    # a different seed is allowed to differ, but must stay a valid labelling
    other = MOD.spherical_kmeans(points, 4, seed=8, n_init=3)
    assert other.min() >= 0 and other.max() < 4


def test_spherical_kmeans_recovers_planted_cosine_groups():
    rng = np.random.default_rng(23)
    anchors = np.eye(3)
    points = np.vstack([anchors[i] * 5.0 + 0.01 * np.abs(rng.normal(size=3))
                        for i in range(3) for _ in range(15)])
    labels = MOD.spherical_kmeans(points, 3, seed=5, n_init=5)
    for group in range(3):
        block = labels[group * 15:(group + 1) * 15]
        assert len(set(block.tolist())) == 1


# ---------------------------------------------------------------------------
# Fold purity
# ---------------------------------------------------------------------------


def _fake_pool(n_authors=40, n_vocab=9, n_folds=None):
    n_folds = n_folds or MOD.N_FOLDS
    rng = np.random.default_rng(24)
    early_counts = rng.integers(50, 200, size=n_authors).astype(np.float64)
    fold_of = np.arange(n_authors) % n_folds
    folds = []
    train_counts = []
    for fold in range(n_folds):
        test_idx = np.flatnonzero(fold_of == fold).astype(np.int32)
        train_idx = np.flatnonzero(fold_of != fold).astype(np.int32)
        counts = np.zeros((n_vocab, train_idx.size))
        # put each training author's whole early mass in one community
        for column, author in enumerate(train_idx):
            counts[column % n_vocab, column] = early_counts[author]
        train_counts.append(counts)
        folds.append(MOD.FoldData(
            fold=fold, test_authors=test_idx, train_authors=train_idx,
            event_vocab=np.zeros(0, dtype=np.int32),
            event_half=np.zeros(0, dtype=np.int32),
            pair_from=np.zeros(0, dtype=np.int64),
            pair_to=np.zeros(0, dtype=np.int64),
            pair_half=np.zeros(0, dtype=np.int32),
            pair_session=np.zeros(0, dtype=bool),
            pair_cross_thread=np.zeros(0, dtype=bool),
            pair_same_thread=np.zeros(0, dtype=bool),
            n_halves=0))
    return MOD.PoolContext(
        key="fake", vocab_variant="full", pool_min=50, n_vocab=n_vocab,
        pool_authors=np.arange(n_authors, dtype=np.int32), folds=folds,
        train_early_counts=train_counts, early_vocab_counts=early_counts,
        census={})


def test_fold_purity_passes_when_maps_use_training_authors_only():
    pool = _fake_pool()
    report = MOD.assert_fold_purity(pool)
    assert report["status"] == "PASS"
    for fold in report["folds"]:
        assert fold["train_test_overlap"] == 0
        assert fold["map_mass"] == pytest.approx(fold["train_early_mass"])
        assert fold["test_early_mass_excluded"] > 0


def test_fold_purity_fails_when_test_author_mass_leaks_into_a_map():
    pool = _fake_pool()
    # leak: add one test author's early mass into fold 0's state-map input
    leaked = int(pool.folds[0].test_authors[0])
    pool.train_early_counts[0][0, 0] += pool.early_vocab_counts[leaked]
    with pytest.raises(AssertionError, match="state-map mass"):
        MOD.assert_fold_purity(pool)


def test_fold_purity_fails_on_train_test_overlap():
    pool = _fake_pool()
    pool.folds[1].train_authors[0] = pool.folds[1].test_authors[0]
    with pytest.raises(AssertionError, match="train/test overlap"):
        MOD.assert_fold_purity(pool)


# ---------------------------------------------------------------------------
# Classification cells
# ---------------------------------------------------------------------------


def _arm(rho, lo, hi, key="x", n_states=24):
    return {"arm": key, "n_states": n_states, "rho": rho, "rho_ci": [lo, hi]}


def test_cells_are_null_first_and_effect_size_keyed():
    # NULL first, and the registration's quantifier is "at EVERY C": the null
    # cell needs CI lower <= 0 at all three resolutions, not just one.
    dead = [_arm(0.01, -0.02, 0.05, "c12", 12),
            _arm(0.01, -0.01, 0.04, "primary"),
            _arm(0.02, -0.03, 0.06, "c48", 48)]
    assert MOD.classify(dead[1], dead)["cell"] == "NO_ORDER_CHANNEL"

    # one dead resolution is NOT enough to null out a live primary
    primary = _arm(0.20, 0.10, 0.30, "primary")
    mixed = [_arm(0.01, -0.02, 0.05, "c12", 12), primary,
             _arm(0.19, 0.09, 0.29, "c48", 48)]
    assert MOD.classify(primary, mixed)["cell"] == "ORDER_CHANNEL"
    assert MOD.classify(primary, mixed)["every_C_ci_lower_le_zero"] is False

    resolutions = [_arm(0.15, 0.05, 0.25, "c12", 12), primary,
                   _arm(0.19, 0.09, 0.29, "c48", 48)]
    assert MOD.classify(primary, resolutions)["cell"] == "ORDER_CHANNEL"

    trace = _arm(0.05, 0.01, 0.09, "primary")
    assert MOD.classify(trace, [trace])["cell"] == "ORDER_TRACE"

    major = _arm(0.40, 0.35, 0.46, "primary")
    assert MOD.classify(major, [major])["cell"] == "ORDER_MAJOR"


def test_scoped_equivalence_attaches_only_inside_epsilon():
    tight = _arm(0.01, -0.01, 0.03, "primary")
    verdict = MOD.classify(tight, [tight])
    assert verdict["cell"] == "NO_ORDER_CHANNEL"
    assert verdict["scoped_equivalence_attaches"] is True
    wide = _arm(0.01, -0.01, 0.20, "primary")
    assert MOD.classify(wide, [wide])["scoped_equivalence_attaches"] is False


def test_straddles_are_reported_not_hidden():
    straddling = _arm(0.11, 0.06, 0.35, "primary")
    verdict = MOD.classify(straddling, [straddling])
    assert verdict["ci_straddles"] == ["0.10", "0.33"]
    assert verdict["cell"] == "ORDER_CHANNEL"


def test_arm_cell_helper_agrees_with_the_primary_classifier():
    for rho, lo, hi in ((0.02, -0.01, 0.05), (0.05, 0.01, 0.09),
                        (0.20, 0.10, 0.30), (0.50, 0.40, 0.60)):
        arm = _arm(rho, lo, hi, "primary")
        assert MOD._cell_of(arm) == MOD.classify(arm, [arm])["cell"]


# ---------------------------------------------------------------------------
# ID-leak scan
# ---------------------------------------------------------------------------


def test_id_leak_scan_finds_a_planted_cohort_id(tmp_path):
    target = tmp_path / "leaky_report.md"
    target.write_text("The author SomeRedditHandle had 12 events.\n",
                      encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target],
                                   ["SomeRedditHandle", "another_user"])
    assert scan["status"] == "FAIL"
    assert scan["n_hits"] == 1
    assert scan["hits"][0]["line"] == 1


def test_id_leak_scan_is_case_insensitive_and_boundary_aware(tmp_path):
    target = tmp_path / "report.md"
    target.write_text("prefixhandlesuffix and HANDLE-ish\n", encoding="utf-8")
    # embedded inside a longer identifier -> not a leak
    assert MOD.scan_for_cohort_ids([target], ["handle"])["n_hits"] == 0
    # standalone, different case -> a leak
    target.write_text("the word Handle appears alone\n", encoding="utf-8")
    assert MOD.scan_for_cohort_ids([target], ["handle"])["status"] == "FAIL"


def test_id_leak_scan_passes_on_clean_text(tmp_path):
    target = tmp_path / "clean.md"
    target.write_text("Aggregates only: 984 authors, rho 0.29.\n",
                      encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["someuser", "otheruser"])
    assert scan["status"] == "PASS"
    assert scan["files_scanned"] == [str(target)]


def test_id_leak_scan_skips_short_candidates(tmp_path):
    target = tmp_path / "short.md"
    target.write_text("the C=24 arm\n", encoding="utf-8")
    scan = MOD.scan_for_cohort_ids([target], ["C", "24", "the"])
    assert scan["candidates_checked"] == 0
    assert scan["status"] == "PASS"


# ---------------------------------------------------------------------------
# Determinism of the seeds themselves
# ---------------------------------------------------------------------------


def test_stable_seed_is_process_independent():
    assert MOD.stable_seed(20260818, "shuffle", "primary", 0) == \
        MOD.stable_seed(20260818, "shuffle", "primary", 0)
    assert MOD.stable_seed(20260818, "shuffle", "primary", 0) != \
        MOD.stable_seed(20260818, "shuffle", "primary", 1)
    # a literal, so a salted builtin hash() would break this test
    assert MOD.stable_seed("a", "b") == 246123018


def test_registration_pins_are_the_registered_values():
    assert MOD.SEED == 20260818
    assert MOD.N_FOLDS == 5
    assert MOD.ALPHA == 0.5
    assert MOD.B_SHUFFLE == 499
    assert MOD.B_BOOTSTRAP == 1000
    assert MOD.C_PRIMARY == 24
    assert MOD.C_SENSITIVITY == (12, 48)
    assert MOD.POOL_PRIMARY_MIN == 50
    assert MOD.POOL_SENSITIVITY_MIN == 100
    assert MOD.SESSION_GAP_SECONDS == 3600.0
    assert MOD.KMEANS_N_INIT == 10
    assert MOD.CENSUS_VOCABULARY == 1191
    assert MOD.CENSUS_POOL_PRIMARY == 984


def test_arm_table_matches_the_registration():
    keys = [arm.key for arm in MOD.ARMS]
    assert keys[0] == "primary"
    assert MOD.ARMS[0].role == "PRIMARY"
    assert {"cross_thread", "session", "c12", "c48", "conditional_rows",
            "stay_rate", "pool100", "clean"} <= set(keys)
    cross = next(a for a in MOD.ARMS if a.key == "cross_thread")
    assert cross.role == "CO_PRIMARY" and cross.pairs == "cross_thread"
    clean = next(a for a in MOD.ARMS if a.key == "clean")
    assert clean.vocab_variant == "clean"


def test_explicit_personality_matcher_reproduces_the_t1_rule():
    for name in ("mbti", "INTJ", "enfp", "Enneagram", "JungianTypology",
                 "introverts", "personality", "socionics", "MbtiTypeMe"):
        assert MOD.is_explicit_personality_community(name)
    for name in ("AskReddit", "politics", "science", "introversion_music",
                 "funny"):
        assert not MOD.is_explicit_personality_community(name)
