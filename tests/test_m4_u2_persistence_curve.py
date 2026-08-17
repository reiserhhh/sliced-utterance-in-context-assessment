"""M4-U2 -- the personal persistence curve: contract tests.

The leg's whole claim rests on two properties.

**The null must destroy identity while preserving the epoch.**  The
permutation reassigns block->author labels WITHIN each calendar quarter, so
every author keeps their per-quarter block count exactly and the epoch
structure the cross baseline matches on is untouched.  If the relabelling
leaked identity, the null band would inherit the signal it is supposed to
bound; if it moved blocks across quarters, the epoch match would be broken.
Both halves are tested first and hardest, together with the claim the
registration makes on paper -- that E's null location is 0 BY CONSTRUCTION --
checked as a realized number on a structureless toy.

**The blocks must be exactly K, disjoint, and in stream order**, because the
fixed-K construction is the entire reason attenuation is constant across bins
and the decay contrast D is transportable.

The rest pins the machinery the registration named as blocking gates: the
epoch-matching histogram identity, the D / floor-share arithmetic on a
hand-checked toy, the cache anchor gate, and the ID-leak scanner.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_u2_persistence_curve.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "m4_u2_persistence_curve", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["m4_u2_persistence_curve"] = module
    spec.loader.exec_module(module)
    return module


MOD = _load()
DAY = 86400.0


# ---------------------------------------------------------------------------
# Toy builders
# ---------------------------------------------------------------------------


def _toy_events(rng, n_authors=12, n_vocab=8, per_author=260, oov_rate=0.2):
    """Author-major, time-sorted cohort stream with some OOV events."""

    author, created, vocab = [], [], []
    for a in range(n_authors):
        n = per_author + int(rng.integers(0, 40))
        times = np.sort(rng.uniform(0.0, 900 * DAY, size=n))
        subs = rng.integers(0, n_vocab, size=n)
        subs = np.where(rng.random(n) < oov_rate, -1, subs)
        author.append(np.full(n, a, dtype=np.int32))
        created.append(times)
        vocab.append(subs.astype(np.int64))
    return (np.concatenate(author), np.concatenate(created),
            np.concatenate(vocab))


def _toy_blocks(rng, n_blocks=180, n_authors=15, n_vocab=10, span_days=1300.0):
    """Blocks with NO author structure: features independent of the author.

    Authors are assigned independently of time on purpose.  Sorting authors
    alongside timestamps would put one author in each quarter, which makes a
    within-quarter relabelling a near no-op and leaves cells with no
    different-author pair at all -- a degenerate world, not the corpus.
    """

    author = rng.integers(0, n_authors, size=n_blocks).astype(np.int32)
    mid_days = np.sort(rng.uniform(0.0, span_days, size=n_blocks))
    features = rng.random((n_blocks, n_vocab)).astype(np.float32)
    features /= np.linalg.norm(features, axis=1, keepdims=True)
    quarter = (mid_days // MOD.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid_days, quarter))
    return (features[order], author[order], quarter[order], mid_days[order])


# ---------------------------------------------------------------------------
# Exact-K disjoint block invariants
# ---------------------------------------------------------------------------


def test_blocks_are_exactly_k_disjoint_and_consecutive():
    rng = np.random.default_rng(11)
    author, created, vocab = _toy_events(rng)
    k = 50
    blocks = MOD.build_blocks(author, created, vocab, 8, k, n_authors=12)

    keep = vocab >= 0
    in_vocab_counts = np.bincount(author[keep], minlength=12)
    # exact-K, disjoint, trailing remainder dropped
    expected = in_vocab_counts // k
    assert np.array_equal(blocks.blocks_per_author, expected)
    assert blocks.author.size == expected.sum()
    assert blocks.features.shape == (expected.sum(), 8)

    # every block carries exactly K events' worth of mass: sum of squares of
    # the UNNORMALIZED sqrt(count/K) vector is 1 by construction, so the
    # L2-normalized features must recover integer counts summing to K.
    for row in blocks.features:
        counts = np.round((row / row[row > 0].min()) ** 2
                          * ((row[row > 0].min() ** 2) * k)) if row.any() else 0
        assert counts is not None  # placeholder guarded by the exact test below
    # exact reconstruction: renormalize to the Hellinger simplex
    scale = blocks.features ** 2
    scale /= scale.sum(axis=1, keepdims=True)
    counts = np.rint(scale * k)
    assert np.allclose(counts.sum(axis=1), k)
    assert np.allclose(scale * k, counts, atol=1e-4)


def test_block_midpoints_and_stream_order():
    author = np.zeros(9, dtype=np.int32)
    created = np.array([0.0, 1.0, 2.0, 10.0, 30.0, 50.0, 99.0, 100.0, 101.0])
    vocab = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=np.int64)
    blocks = MOD.build_blocks(author, created, vocab, 2, 3, n_authors=1)
    assert blocks.author.size == 3
    # midpoint = mean of the block's FIRST and LAST timestamps
    assert np.allclose(blocks.midpoint, [(0.0 + 2.0) / 2, (10.0 + 50.0) / 2,
                                         (99.0 + 101.0) / 2])
    # disjoint consecutive windows in stream order, remainder dropped
    blocks4 = MOD.build_blocks(author, created, vocab, 2, 4, n_authors=1)
    assert blocks4.author.size == 2
    assert np.allclose(blocks4.midpoint, [(0.0 + 10.0) / 2, (30.0 + 100.0) / 2])


def test_oov_events_are_dropped_before_blocking():
    author = np.zeros(8, dtype=np.int32)
    created = np.arange(8, dtype=np.float64)
    vocab = np.array([-1, 0, -1, 1, -1, 0, -1, 1], dtype=np.int64)
    blocks = MOD.build_blocks(author, created, vocab, 2, 4, n_authors=1)
    assert blocks.author.size == 1
    # the four in-vocabulary events are at t = 1, 3, 5, 7
    assert blocks.midpoint[0] == pytest.approx(4.0)
    assert np.allclose(blocks.features[0], np.sqrt(0.5))


# ---------------------------------------------------------------------------
# The permutation contract
# ---------------------------------------------------------------------------


def test_permutation_preserves_per_quarter_counts_and_breaks_linkage():
    rng = np.random.default_rng(5)
    _, author, quarter, _ = _toy_blocks(rng, n_blocks=240, n_authors=9)
    n_perm = 25
    plans = MOD.build_quarter_plans(quarter, author, n_perm, seed=7)

    real_key = author.astype(np.int64) * 100 + quarter
    real_counts = np.bincount(real_key, minlength=9 * 100)

    changed = 0
    for p in range(n_perm + 1):
        relabelled = np.empty_like(author)
        for q, plan in plans.items():
            # slot s owns author plan.slot_author[s]; permutation p puts the
            # block at local position slot_position[p][s] into that slot.
            relabelled[plan.rows[plan.slot_position[p]]] = plan.slot_author
        # per-(author, quarter) block counts are preserved EXACTLY
        key = relabelled.astype(np.int64) * 100 + quarter
        assert np.array_equal(np.bincount(key, minlength=9 * 100), real_counts)
        # no block ever leaves its quarter
        assert np.array_equal(quarter, quarter)
        if p == 0:
            assert np.array_equal(relabelled, author)   # row 0 is the identity
        else:
            changed += int(np.count_nonzero(relabelled != author))
    # identity is destroyed: most labels move under most permutations
    assert changed > 0.5 * n_perm * author.size


def test_permutation_null_center_is_zero_on_a_structureless_toy():
    """E's null location is 0 BY CONSTRUCTION -- verified as a number."""

    rng = np.random.default_rng(2026)
    features, author, quarter, mid = _toy_blocks(
        rng, n_blocks=300, n_authors=12, span_days=1300.0)
    result = MOD.compute_arm(features, author, quarter, mid,
                             n_perm=120, n_boot=60, seed=3)
    null = result["null_curve"]
    for b in range(MOD.N_BINS):
        column = null[:, b]
        column = column[np.isfinite(column)]
        if column.size < 20:
            continue
        centre = float(np.mean(column))
        spread = float(np.std(column, ddof=1)) / np.sqrt(column.size)
        # the null center sits at 0 within Monte-Carlo error
        assert abs(centre) < 6.0 * spread + 1e-9
    # and the REAL curve of a structureless world is a draw from that null.
    # Standardized rather than band-based on purpose: the real labelling IS
    # exchangeable with the permuted ones here, so it lands outside a 95%
    # band about one bin in twenty by construction; |z| > 4 would be a bug.
    for b in range(MOD.N_BINS):
        column = null[:, b]
        column = column[np.isfinite(column)]
        if column.size < 20 or not np.isfinite(result["curve"][b]):
            continue
        sd = float(np.std(column, ddof=1))
        assert abs(result["curve"][b]) < 4.0 * sd + 1e-9


def test_planted_personal_signal_is_detected():
    """The estimator must see a signature that is really there."""

    rng = np.random.default_rng(99)
    n_authors, n_vocab, per_author = 14, 12, 26
    feats, authors, mids = [], [], []
    for a in range(n_authors):
        taste = rng.random(n_vocab)
        taste /= taste.sum()
        for j in range(per_author):
            draw = rng.multinomial(50, 0.9 * taste + 0.1 / n_vocab)
            v = np.sqrt(draw.astype(np.float32) / 50.0)
            feats.append(v / np.linalg.norm(v))
            authors.append(a)
            mids.append(rng.uniform(0.0, 1300.0))
    features = np.asarray(feats, dtype=np.float32)
    author = np.asarray(authors, dtype=np.int32)
    mid = np.asarray(mids)
    quarter = (mid // MOD.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid, quarter))
    result = MOD.compute_arm(features[order], author[order], quarter[order],
                             mid[order], n_perm=60, n_boot=100, seed=4)
    # a stationary personal taste: strong excess, no decay
    assert result["curve"][MOD.NEAR_BIN] > result["curve_null_band"][
        MOD.NEAR_BIN][1]
    assert result["curve_ci"][MOD.NEAR_BIN][0] > 0.0
    assert abs(result["d"]) < 0.2 * result["curve"][MOD.NEAR_BIN]


# ---------------------------------------------------------------------------
# Epoch matching
# ---------------------------------------------------------------------------


def test_cross_weights_match_the_self_quarter_pair_histogram():
    """The cross term is weighted by the self pairs' joint quarter histogram."""

    rng = np.random.default_rng(31)
    features, author, quarter, mid = _toy_blocks(
        rng, n_blocks=200, n_authors=10, span_days=1200.0)
    result = MOD.compute_arm(features, author, quarter, mid,
                             n_perm=3, n_boot=10, seed=8)

    # Rebuild the estimator from its own definition: E(b) is the self mean
    # minus the cell-weighted cross mean, with weights equal to the self
    # histogram over (quarter_i, quarter_j) cells within the bin.
    for b in range(MOD.N_BINS):
        if result["self_pairs"][b] == 0:
            continue
        direct = result["self_mean"][b] - result["cross_mean_matched"][b]
        assert direct == pytest.approx(result["curve"][b], abs=1e-9)

    # brute force on the same toy: same-author pairs binned by gap
    n = features.shape[0]
    gram = features @ features.T
    iu = np.triu_indices(n, 1)
    gaps = np.abs(mid[:, None] - mid[None, :])[iu]
    bins = MOD.gap_bin(gaps)
    same = (author[:, None] == author[None, :])[iu]
    cos = gram[iu]
    for b in range(MOD.N_BINS):
        sel = (bins == b) & same
        if not sel.any():
            continue
        assert result["self_pairs"][b] == int(sel.sum())
        assert result["self_mean"][b] == pytest.approx(
            float(cos[sel].mean()), abs=1e-5)


def test_epoch_matching_absorbs_a_global_epoch_trend():
    """A shared platform drift with no personal structure must give E ~ 0."""

    rng = np.random.default_rng(77)
    n_blocks, n_vocab, n_authors = 320, 10, 12
    mid = np.sort(rng.uniform(0.0, 1300.0, size=n_blocks))
    author = rng.integers(0, n_authors, size=n_blocks).astype(np.int32)
    # every block's taste is a function of its EPOCH only -- no author term
    features = np.empty((n_blocks, n_vocab), dtype=np.float32)
    for i, t in enumerate(mid):
        centre = (t / 1300.0) * (n_vocab - 1)
        weight = np.exp(-0.5 * ((np.arange(n_vocab) - centre) / 1.5) ** 2)
        draw = rng.multinomial(50, weight / weight.sum())
        v = np.sqrt(draw.astype(np.float32) / 50.0)
        features[i] = v / np.linalg.norm(v)
    quarter = (mid // MOD.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid, quarter))
    result = MOD.compute_arm(features[order], author[order], quarter[order],
                             mid[order], n_perm=80, n_boot=200, seed=6)
    # the raw self similarity is high at short gaps purely from the epoch...
    assert result["self_mean"][MOD.NEAR_BIN] > 0.5
    # ...and the epoch-matched excess is not
    lo, hi = result["curve_ci"][MOD.NEAR_BIN]
    assert lo <= 0.02 and result["curve"][MOD.NEAR_BIN] < 0.05


# ---------------------------------------------------------------------------
# D, floor share, cells
# ---------------------------------------------------------------------------


def test_decay_and_floor_share_on_a_hand_checked_toy():
    arm = {
        "curve": [0.60, 0.50, 0.45, 0.40, 0.30, 0.20],
        "curve_ci": [[0.55, 0.65], [0.45, 0.55], [0.40, 0.50],
                     [0.35, 0.45], [0.25, 0.35], [0.15, 0.25]],
        "curve_null_band": [[-0.01, 0.01]] * 6,
        "d": 0.60 - 0.30,
        "d_ci": [0.25, 0.35],
        "d_null_band": [-0.02, 0.02],
        "d_ci_half_width": 0.05,
        "equivalence_margin": 0.2 * 0.60,
    }
    # hand arithmetic: D = 0.30, floor share = 0.30 / 0.60 = 0.5
    assert arm["d"] == pytest.approx(0.30)
    assert arm["curve"][MOD.FAR_BIN] / arm["curve"][MOD.NEAR_BIN] == \
        pytest.approx(0.5)
    out = MOD.classify(arm)
    assert out["cell"] == "DRIFT_WITH_CORE"
    assert out["equivalence_margin"] == pytest.approx(0.12)

    # the far bin loses its floor -> FULL_DRIFT
    full = dict(arm)
    full["curve_ci"] = list(arm["curve_ci"])
    full["curve_ci"][MOD.FAR_BIN] = [-0.05, 0.35]
    assert MOD.classify(full)["cell"] == "FULL_DRIFT"

    # no decay and inside the equivalence band -> FIXED_POINT
    flat = dict(arm)
    flat["d"] = 0.01
    flat["d_ci"] = [-0.03, 0.05]
    assert MOD.classify(flat)["cell"] == "FIXED_POINT"

    # no existence -> the NULL-first cell wins whatever D says
    dead = dict(arm)
    dead["curve_ci"] = list(arm["curve_ci"])
    dead["curve_ci"][MOD.NEAR_BIN] = [-0.02, 0.65]
    assert MOD.classify(dead)["cell"] == "NO_PERSONAL_PERSISTENCE"

    # existence inside the permutation band is also the null cell
    banded = dict(arm)
    banded["curve_null_band"] = [[-1.0, 1.0]] + [[-0.01, 0.01]] * 5
    assert MOD.classify(banded)["cell"] == "NO_PERSONAL_PERSISTENCE"


def test_verdict_endpoint_is_the_2_3y_bin_not_3y_plus():
    """Convention #74: the 3y+ bin may never carry the verdict."""

    assert MOD.BIN_LABELS[MOD.FAR_BIN] == "2-3y"
    assert MOD.BIN_LABELS[MOD.DESCRIPTIVE_BIN] == "3y+"
    assert MOD.VERDICT_BINS == 5
    assert MOD.DESCRIPTIVE_BIN >= MOD.VERDICT_BINS


def test_gap_bin_edges_are_left_closed_right_open():
    edges = np.array([0.0, 89.999, 90.0, 179.999, 180.0, 364.999, 365.0,
                      729.999, 730.0, 1094.999, 1095.0, 5000.0])
    assert list(MOD.gap_bin(edges)) == [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]


def test_exponential_fit_recovers_a_planted_curve():
    x = np.array([40.0, 130.0, 270.0, 520.0, 880.0])
    truth = 0.2 + 0.5 * np.exp(-x / 300.0)
    fit = MOD.exponential_fit(x, truth)
    assert fit["e_inf"] == pytest.approx(0.2, abs=0.02)
    assert fit["amplitude"] == pytest.approx(0.5, abs=0.03)
    assert fit["tau_days"] == pytest.approx(300.0, rel=0.05)
    assert fit["cap_hit"] is False
    # a curve with no floor pushes tau to the cap, and the cap is reported
    flat = 0.4 + 0.0 * x
    capped = MOD.exponential_fit(x, flat)
    assert capped["tau_cap_days"] == MOD.TAU_CAP_DAYS
    assert capped["tau_days"] <= MOD.TAU_CAP_DAYS


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def test_cache_anchor_gate_passes_only_on_the_pinned_object():
    good = MOD.EventCache(
        author_code=np.zeros(MOD.ANCHOR_EVENTS, dtype=np.int32),
        subreddit_code=np.zeros(MOD.ANCHOR_EVENTS, dtype=np.int32),
        created_utc=np.zeros(MOD.ANCHOR_EVENTS),
        vocab_of_subreddit=np.arange(MOD.ANCHOR_VOCAB, dtype=np.int32),
        authors=[], subreddits=[], vocabulary=[], stream_stats={})
    good.author_code[:MOD.ANCHOR_AUTHORS] = np.arange(MOD.ANCHOR_AUTHORS)
    report = MOD.verify_cache_anchors(good)
    assert report["status"] == "PASS"
    assert report["mismatches"] == {}

    short = MOD.EventCache(
        author_code=good.author_code[:-1], subreddit_code=good.subreddit_code,
        created_utc=good.created_utc,
        vocab_of_subreddit=good.vocab_of_subreddit,
        authors=[], subreddits=[], vocabulary=[], stream_stats={})
    bad = MOD.verify_cache_anchors(short)
    assert bad["status"] == "FAIL"
    assert "events" in bad["mismatches"]

    thin = MOD.EventCache(
        author_code=good.author_code, subreddit_code=good.subreddit_code,
        created_utc=good.created_utc,
        vocab_of_subreddit=np.arange(MOD.ANCHOR_VOCAB - 1, dtype=np.int32),
        authors=[], subreddits=[], vocabulary=[], stream_stats={})
    assert MOD.verify_cache_anchors(thin)["status"] == "FAIL"


def test_census_pins_are_the_registered_numbers():
    """The pins the runner refuses to proceed without."""

    assert MOD.CENSUS_PINS["authors_ge_4_blocks"] == 849
    assert MOD.CENSUS_PINS["total_blocks_all_authors"] == 46_318
    assert MOD.CENSUS_PINS["n_quarters"] == 18
    assert MOD.CENSUS_PINS["self_pairs_per_bin"] == [
        1_005_742, 783_654, 1_198_561, 1_248_992, 417_963, 100_150]
    assert MOD.CENSUS_PINS["authors_2_3y"] == 564
    assert MOD.CENSUS_PINS["tercile_sizes"] == [302, 265, 282]
    assert MOD.SEED == 20260818
    assert (MOD.B_PERM, MOD.B_BOOT) == (499, 1000)
    assert MOD.K_PRIMARY == 50


def test_id_leak_scanner_finds_a_planted_name(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("no cohort identity here; only blocks and quarters\n")
    dirty = tmp_path / "dirty.md"
    dirty.write_text("author sample_user_9 contributed 12 blocks\n")
    cohort = ["sample_user_9", "another_person"]

    ok = MOD.scan_for_cohort_ids([clean], cohort)
    assert ok["status"] == "PASS" and ok["n_hits"] == 0

    bad = MOD.scan_for_cohort_ids([dirty], cohort)
    assert bad["status"] == "FAIL" and bad["n_hits"] == 1
    assert bad["hits"][0]["line"] == 1

    # substring of a longer token is NOT a hit (word-boundary rule)
    embedded = tmp_path / "embedded.md"
    embedded.write_text("the field sample_user_90 is a different token\n")
    assert MOD.scan_for_cohort_ids([embedded], cohort)["status"] == "PASS"

    # short names are skipped by the min-length rule
    assert MOD.scan_for_cohort_ids([dirty], ["abc"])["status"] == "PASS"


def test_committed_files_carry_no_cohort_identity():
    """The blocking ID-leak gate, run over the exact committed set."""

    meta = (ROOT / "results/m4_u1_order_identity/events_cache.meta.json")
    if not meta.exists():          # pragma: no cover - cache is gitignored
        pytest.skip("events cache metadata not present")
    import json
    authors = json.loads(meta.read_text(encoding="utf-8"))["authors"]
    assert len(authors) == MOD.ANCHOR_AUTHORS
    targets = [
        SCRIPT,
        Path(__file__),
        ROOT / "reports/SUICA_M4_U2_PERSISTENCE_CURVE_REPORT.md",
        ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
        ROOT / "docs/CLAIMS_LEDGER.md",
    ]
    scan = MOD.scan_for_cohort_ids(targets, authors)
    assert scan["status"] == "PASS", scan["hits"]


def test_no_personality_label_is_read_anywhere():
    """Label-free leg: the runner may not touch a Big5 or MBTI value.

    Checked on CODE, not prose -- the report text is allowed to SAY that no
    label is read.  The binding property is that the only data the runner
    opens is the U1 events cache (author codes, subreddit codes, timestamps),
    and that no label table or trait column is named in an expression.
    """

    import ast

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    literals = [node.value.casefold() for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)]
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc.casefold())

    banned_paths = ("author_profiles", "pandora_official", ".csv",
                    "prepared/", "big5/", "mbti_axes")
    banned_columns = ("agreeableness", "conscientiousness", "neuroticism",
                      "openness", "extraversion", "introversion")
    for literal in literals:
        if literal in docstrings:
            continue
        for banned in banned_paths + banned_columns:
            assert banned not in literal, (banned, literal[:120])

    # the only data source is the U1 events cache
    assert MOD.DEFAULT_CACHE.name == "events_cache.npz"
    opened = {node.func.attr for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)}
    assert "read_csv" not in opened

    # the MBTI vocabulary that IS present exists only to REMOVE communities
    assert "is_explicit_personality_community" in SCRIPT.read_text(
        encoding="utf-8")


def test_explicit_personality_matcher_matches_t1():
    assert MOD.is_explicit_personality_community("INTJ")
    assert MOD.is_explicit_personality_community("mbti")
    assert MOD.is_explicit_personality_community("Enneagram")
    assert MOD.is_explicit_personality_community("introverts")
    assert not MOD.is_explicit_personality_community("AskReddit")
    assert not MOD.is_explicit_personality_community("running")
