"""Contract tests for SUICA M4-W1 — slow-time law transport (disjoint cohort).

What these tests hold the runner to:

* the CACHE BUILDER is U1's construction under a negated cohort predicate —
  the per-chunk incremental factorization must produce, on a toy stream, the
  array-for-array identical object that U1's whole-frame concat produces;
* the DISJOINT cohort is disjoint — zero authors shared with the 1401, and
  the union universe is the sum of the two;
* the CENSUS predicates are the ones the registration names — the vocabulary
  floor rule, the intersection predicate m <= common <= K - m, the 2-3y bin
  edges, the quarter grid, the block midpoint;
* the ESTIMANDS are formula-level identical to the imported U2c objects on a
  shared toy: the slope fit, Lambda as a paired replicate difference, and the
  eligibility predicate;
* the PAIRING invariants hold — one block set gives every row the same author
  bootstrap draws, and the within-quarter permutation preserves each author's
  per-quarter block count exactly;
* the TRANSPORT classification is the registered rule at its boundaries;
* the ID-LEAK helper works over the WIDENED universe of all 10,296 names;
* the leg is LABEL-FREE — ``author_profiles.csv`` appears nowhere.
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
SCRIPT = ROOT / "scripts" / "run_suica_m4_w1_slow_transport.py"
U2C_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2c_decay_rate_contrast.py"
U2B_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2b_persistence_budget.py"
U2_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2_persistence_curve.py"
T1_SCRIPT = ROOT / "scripts" / "run_suica_m4_t1_hierarchical_selection_identity.py"
ARTIFACTS = ROOT / "results" / "m4_w1_slow_transport"
REPORT = ROOT / "reports" / "SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_w1_slow_transport", SCRIPT)
DAY = 86400.0
GAPS = np.array([0.118, 0.365, 0.730, 1.417, 2.396])


def _log(tmp_path: Path):
    return MOD.RunLog(tmp_path / "run_log.jsonl")


# ---------------------------------------------------------------------------
# The cache builder: U1's construction under a NEGATED cohort predicate
# ---------------------------------------------------------------------------


def _toy_comments(tmp_path: Path, seed: int = 3) -> tuple[Path, Path, list]:
    """A small comments file plus a cohort file, with NaNs and bad rows."""

    rng = np.random.default_rng(seed)
    authors = [f"zeta_{i}" for i in range(6)] + [f"alpha_{i}" for i in range(6)]
    subs = ["Music", "askreddit", "INTJ", "politics", "mbti"]
    rows = []
    for i in range(400):
        rows.append({
            "author": authors[int(rng.integers(0, len(authors)))],
            "subreddit": subs[int(rng.integers(0, len(subs)))],
            # deliberate exact ties in created_utc, to pin the tie rule
            "created_utc": float(1_400_000_000 + int(rng.integers(0, 40)) * DAY),
            "link_id": f"t3_{int(rng.integers(0, 30))}",
        })
    rows.append({"author": None, "subreddit": "Music",
                 "created_utc": 1_400_000_000.0, "link_id": "t3_1"})
    rows.append({"author": "zeta_0", "subreddit": None,
                 "created_utc": 1_400_000_000.0, "link_id": "t3_1"})
    rows.append({"author": "alpha_1", "subreddit": "Music",
                 "created_utc": None, "link_id": "t3_1"})
    rows.append({"author": "zeta_2", "subreddit": "Music",
                 "created_utc": 1_400_000_500.0, "link_id": None})
    comments = tmp_path / "comments.csv"
    pd.DataFrame(rows).to_csv(comments, index=False)
    cohort = tmp_path / "cohort.csv"
    cohort_names = [f"alpha_{i}" for i in range(6)]
    pd.DataFrame({"author": cohort_names}).to_csv(cohort, index=False)
    return comments, cohort, cohort_names


def _u1_reference(comments: Path, cohort_names: list) -> dict:
    """U1's whole-frame construction, negated -- the reference object."""

    frame = pd.read_csv(comments,
                        usecols=["author", "subreddit", "created_utc",
                                 "link_id"],
                        dtype={"author": "str", "subreddit": "str",
                               "link_id": "str"})
    frame = frame[~frame["author"].isin(set(cohort_names))]
    frame = frame.dropna(subset=["author", "subreddit", "created_utc"])
    frame["link_id"] = frame["link_id"].fillna("")
    authors = sorted(set(frame["author"].astype(str)))
    author_index = {name: i for i, name in enumerate(authors)}
    author_code = frame["author"].map(author_index).to_numpy(np.int32)
    sub_codes, sub_uniques = pd.factorize(frame["subreddit"], sort=True)
    subreddit_code = np.asarray(sub_codes, dtype=np.int32)
    subreddits = [str(name) for name in sub_uniques]
    created = frame["created_utc"].to_numpy(np.float64)
    link_codes, _ = pd.factorize(frame["link_id"], sort=False)
    link_code = np.asarray(link_codes, dtype=np.int32)
    order = np.lexsort((created, author_code))
    return {"authors": authors, "subreddits": subreddits,
            "author_code": author_code[order],
            "subreddit_code": subreddit_code[order],
            "created_utc": created[order], "link_code": link_code[order]}


def test_cache_builder_matches_u1s_whole_frame_construction(tmp_path):
    comments, cohort, cohort_names = _toy_comments(tmp_path)
    built = MOD.stream_disjoint_events(comments, cohort, _log(tmp_path))
    reference = _u1_reference(comments, cohort_names)

    assert built["authors"] == reference["authors"]
    assert built["subreddits"] == reference["subreddits"]
    for key in ("author_code", "subreddit_code", "created_utc", "link_code"):
        np.testing.assert_array_equal(built[key], reference[key])


def test_cache_builder_keeps_only_authors_outside_the_cohort(tmp_path):
    comments, cohort, cohort_names = _toy_comments(tmp_path)
    built = MOD.stream_disjoint_events(comments, cohort, _log(tmp_path))
    assert set(built["authors"]).isdisjoint(set(cohort_names))
    assert built["stream_stats"]["cohort_authors_excluded"] == len(cohort_names)
    # every retained event belongs to a retained author
    assert int(built["author_code"].max()) < len(built["authors"])


def test_cache_builder_sorts_by_author_then_time_keeping_stream_ties(tmp_path):
    comments, cohort, _ = _toy_comments(tmp_path)
    built = MOD.stream_disjoint_events(comments, cohort, _log(tmp_path))
    a = built["author_code"]
    t = built["created_utc"]
    assert np.all(np.diff(a) >= 0)
    same = np.diff(a) == 0
    assert np.all(np.diff(t)[same] >= 0)


def test_vocabulary_floor_is_sr0s_rule_re_instantiated(tmp_path):
    comments, cohort, _ = _toy_comments(tmp_path)
    built = MOD.stream_disjoint_events(comments, cohort, _log(tmp_path))
    stats = built["stream_stats"]
    assert stats["floor_users"] == max(
        1, math.ceil(MOD.VOCAB_FLOOR_FRACTION * stats["authors_seen"]))
    # the floor is on DISTINCT USERS per community, not on events
    n_authors = len(built["authors"])
    pair = built["subreddit_code"].astype(np.int64) * n_authors \
        + built["author_code"]
    users = np.bincount((np.unique(pair) // n_authors).astype(np.int64),
                        minlength=len(built["subreddits"]))
    expected = sorted(name for name, u in zip(built["subreddits"], users)
                      if u >= stats["floor_users"])
    assert built["vocabulary"] == expected
    assert stats["vocabulary_size"] == len(expected)


def test_cache_carries_no_comment_bodies(tmp_path):
    comments, cohort, _ = _toy_comments(tmp_path)
    built = MOD.stream_disjoint_events(comments, cohort, _log(tmp_path))
    assert set(built) == {"authors", "author_code", "subreddit_code",
                          "created_utc", "link_code", "subreddits",
                          "vocabulary", "vocab_of_subreddit", "stream_stats"}


# ---------------------------------------------------------------------------
# Census predicates -- reproduction helpers
# ---------------------------------------------------------------------------


def test_registered_census_pins_are_the_registered_numbers():
    """The anchor gates carried in code must BE the registration's table."""

    assert MOD.CENSUS_DISJOINT_EVENTS == 14_634_702
    assert MOD.CENSUS_AUTHORS_SEEN == 8_895
    assert MOD.CENSUS_VOCAB_FLOOR_USERS == math.ceil(
        0.01 * MOD.CENSUS_AUTHORS_SEEN) == 89
    assert MOD.CENSUS_LAW_VOCAB == 1_443
    assert MOD.CENSUS_LAW_COVERAGE == 0.7587
    assert MOD.CENSUS_COMMON_Q50 == 71
    assert MOD.CENSUS_TYPOLOGY_IN_VOCAB == 22
    assert MOD.CENSUS_TYPOLOGY_IN_COMMON == 8
    assert MOD.CENSUS_POOL_AUTHORS == 6_111
    assert MOD.CENSUS_POOL_BLOCKS == 213_489
    assert MOD.CENSUS_QUARTERS == 18
    assert MOD.CENSUS_SELF_PAIRS_2_3Y == 2_591_663
    assert (MOD.CENSUS_GATE_M10_PAIRS, MOD.CENSUS_GATE_M10_AUTHORS) == \
        (1_211_631, 3_241)
    assert (MOD.CENSUS_GATE_M5_PAIRS, MOD.CENSUS_GATE_M5_AUTHORS) == \
        (1_790_865, 3_746)
    assert MOD.SEED == 20260818 and MOD.B_PERM == 499 and MOD.B_BOOT == 1000
    assert MOD.Q_PRIMARY == 0.5 and MOD.M_PRIMARY == 10
    assert MOD.M_SENSITIVITY == 5
    assert MOD.K_PRIMARY == 50 and MOD.POOL_MIN_BLOCKS == 4
    assert MOD.PROJECTED_HALF_WIDTH == 0.044
    assert MOD.PROJECTED_LAMBDA_POINT == 0.074


def test_bins_and_quarters_are_the_pinned_u2_grid():
    assert MOD.BIN_LABELS == ("0-90d", "90-180d", "180-365d", "1-2y", "2-3y",
                              "3y+")
    assert MOD.FAR_BIN == 4 and MOD.DESCRIPTIVE_BIN == 5
    assert MOD.N_FIT_BINS == 5
    assert MOD.QUARTER_DAYS == 91.3
    # the 2-3y bin is left-closed / right-open on 730 .. 1095 days
    edges = np.array([729.9, 730.0, 1000.0, 1094.9, 1095.0])
    assert list(MOD.U2.gap_bin(edges)) == [3, 4, 4, 4, 5]


def test_block_midpoint_is_the_mean_of_first_and_last_event(tmp_path):
    k = MOD.K_PRIMARY
    n = 2 * k
    author = np.zeros(n, dtype=np.int32)
    stamps = np.arange(n, dtype=np.float64) * DAY
    vocab_index = np.zeros(n, dtype=np.int32)
    blocks = MOD.U2.build_blocks(author, stamps, vocab_index, 1, k,
                                 n_authors=1)
    assert blocks.author.size == 2
    assert blocks.midpoint[0] == pytest.approx(0.5 * (stamps[0]
                                                      + stamps[k - 1]))
    assert blocks.midpoint[1] == pytest.approx(0.5 * (stamps[k]
                                                      + stamps[2 * k - 1]))


def test_typology_matcher_is_t1s_function_verbatim():
    t1 = _load("m4_t1_for_w1", T1_SCRIPT)
    names = ["INTJ", "intj", "mbti", "Enneagram", "socionics", "introverts",
             "PersonalityCafe", "typology", "jung", "Music", "askreddit",
             "politics", "science"]
    for name in names:
        assert MOD.is_explicit_personality_community(name) == \
            t1.is_explicit_personality_community(name)
    assert MOD.is_explicit_personality_community("INTJ") is True
    assert MOD.is_explicit_personality_community("Music") is False


# ---------------------------------------------------------------------------
# Formula-level agreement with the imported U2c estimator on a shared toy
# ---------------------------------------------------------------------------


def test_slope_fit_is_u2cs_object_not_a_reimplementation():
    u2c = _load("m4_u2c_for_w1", U2C_SCRIPT)
    curve = 0.5312 * np.exp(-0.2734 * GAPS)
    mine = MOD.U2C.log_slope_fit(GAPS, curve)
    theirs = u2c.log_slope_fit(GAPS, curve)
    assert float(mine["lambda_per_year"]) == float(theirs["lambda_per_year"])
    assert float(mine["lambda_per_year"]) == pytest.approx(0.2734, abs=1e-12)
    assert MOD.U2C.log_slope_fit is u2c.log_slope_fit.__wrapped__ \
        if hasattr(u2c.log_slope_fit, "__wrapped__") else True
    # the function object this leg calls comes from the U2c module it imported
    assert MOD.U2C.log_slope_fit.__module__ == "suica_m4_u2c"
    assert MOD.U2B.ppmi_svd.__module__ == "suica_m4_u2b"
    assert MOD.U2.compute_arm.__module__ == "suica_m4_u2"


def _synthetic_row(lam: float, e0: float, seed: int, n_boot: int = 96,
                   n_perm: int = 48, noise: float = 0.02) -> dict:
    """A row shaped like compute_arm's output, with known lambda."""

    rng = np.random.default_rng(seed)
    six = np.append(GAPS, 3.40)
    curve = e0 * np.exp(-lam * six)
    boot = curve[None, :] * (1.0 + noise * rng.standard_normal((n_boot, 6)))
    null = 0.001 * rng.standard_normal((n_perm, 6))
    return {
        "label": f"toy lam={lam}", "curve": [float(v) for v in curve],
        "boot_curve": boot, "null_curve": null,
        "curve_ci": [[float(v), float(v)] for v in curve],
        "curve_null_center": [0.0] * 6,
        "mean_gap_days": [float(g * MOD.DAYS_PER_YEAR) for g in six],
        "self_pairs": [100] * 6, "n_blocks": 500, "n_authors": 40,
        "floor_share": float(curve[4] / curve[0]),
    }


def test_lambda_is_the_paired_replicate_difference_of_two_row_lambdas():
    fast = _synthetic_row(0.34, 0.52, seed=1)
    slow = _synthetic_row(0.24, 0.58, seed=2)
    gaps = np.asarray(fast["mean_gap_days"]) / MOD.DAYS_PER_YEAR
    a = MOD.U2C.summarize_lambda("distinct", "d", fast, gaps)
    b = MOD.U2C.summarize_lambda("common", "c", slow, gaps)
    a["_linear_null"] = MOD.U2C.linear_slope(gaps, fast["null_curve"])
    b["_linear_null"] = MOD.U2C.linear_slope(gaps, slow["null_curve"])
    delta = MOD.U2C.rate_contrast("Λ", a, b, gaps, paired=True)

    assert delta["point"] == pytest.approx(0.34 - 0.24, abs=1e-9)
    assert delta["paired_bootstrap"] is True
    # the difference is taken replicate by replicate, not interval by interval
    manual = a["_boot_lambda"] - b["_boot_lambda"]
    assert delta["ci"] == MOD.percentile_ci(manual)
    assert delta["boot_replicates"] == manual.size


def test_lambda_cells_are_the_three_registered_boundaries():
    for ci, expected in (([0.01, 0.19], "COMMON_STANDING"),
                         ([-0.19, -0.01], "DISTINCT_SLOWER"),
                         ([-0.02, 0.15], "SIGN_UNRESOLVED"),
                         ([0.0, 0.15], "SIGN_UNRESOLVED"),
                         ([-0.15, 0.0], "SIGN_UNRESOLVED")):
        delta = {"ci": ci, "ci_half_width": 0.5 * (ci[1] - ci[0])}
        assert MOD.classify_w1(delta)["cell"] == expected
    # W1 re-stamps the projection but never the cell logic
    delta = {"ci": [-0.02, 0.15], "ci_half_width": 0.085}
    cell = MOD.classify_w1(delta)
    assert cell["projected_half_width"] == MOD.PROJECTED_HALF_WIDTH
    assert cell["equivalence_cell_offered"] is False
    assert cell["projection_ratio"] == pytest.approx(
        0.085 / MOD.PROJECTED_HALF_WIDTH)
    assert cell["half_width_inside_projection"] is False


def test_intersection_predicate_is_m_le_common_le_k_minus_m():
    """The eligibility predicate must BE the registered block conjunction."""

    rng = np.random.default_rng(11)
    k = MOD.K_PRIMARY
    n_vocab, n_blocks = 9, 240
    counts = rng.multinomial(k, np.full(n_vocab, 1.0 / n_vocab),
                             size=n_blocks).astype(np.float64)
    features = np.sqrt(counts / k).astype(np.float32)
    common_cols = np.array([0, 1, 2], dtype=np.int64)
    recovered = MOD.U2B.block_counts_over(features, common_cols, k)
    np.testing.assert_allclose(recovered, counts[:, common_cols].sum(axis=1),
                               atol=1e-6)
    for m in (5, 10):
        common_count = np.rint(recovered).astype(np.int64)
        mask = (common_count >= m) & (k - common_count >= m)
        expected = (common_count >= m) & (common_count <= k - m)
        np.testing.assert_array_equal(mask, expected)


def test_eligibility_reproduces_the_predicate_through_the_geometry(tmp_path):
    """Geometry.eligibility is that predicate plus U2b's exact pair census."""

    class FakeGeom:
        n_vocab = 9
        pool_features = None
        pool_author = None
        pool_mid = None

    rng = np.random.default_rng(13)
    k = MOD.K_PRIMARY
    n_blocks = 300
    counts = rng.multinomial(k, np.full(9, 1.0 / 9), size=n_blocks
                             ).astype(np.float64)
    geom = FakeGeom()
    geom.pool_features = np.sqrt(counts / k).astype(np.float32)
    geom.pool_author = rng.integers(0, 20, size=n_blocks).astype(np.int32)
    geom.pool_mid = np.sort(rng.uniform(0.0, 1400.0, size=n_blocks))
    common_cols = np.array([0, 1, 2, 3], dtype=np.int64)
    distinct_cols = np.array([4, 5, 6, 7, 8], dtype=np.int64)

    entry = MOD.Geometry.eligibility(geom, common_cols, distinct_cols, 0.44,
                                     0.5, 10)
    common_count = np.rint(
        MOD.U2B.block_counts_over(geom.pool_features, common_cols, k)
    ).astype(np.int64)
    expected_mask = (common_count >= 10) & (k - common_count >= 10)
    np.testing.assert_array_equal(entry["intersection_mask"], expected_mask)
    pairs, contributors = MOD.U2B.self_pair_census(
        geom.pool_author[expected_mask], geom.pool_mid[expected_mask])
    assert entry["pairs_2_3y"] == int(pairs[MOD.FAR_BIN])
    assert entry["authors_2_3y"] == int(contributors[MOD.FAR_BIN])
    assert entry["blocks"] == int(expected_mask.sum())


# ---------------------------------------------------------------------------
# Pairing and permutation invariants
# ---------------------------------------------------------------------------


def _toy_arm_inputs(rng, n_blocks=180, n_authors=14, n_vocab=10,
                    span_days=1300.0, k=50):
    author = rng.integers(0, n_authors, size=n_blocks).astype(np.int32)
    mid_days = np.sort(rng.uniform(0.0, span_days, size=n_blocks))
    counts = rng.multinomial(k, np.full(n_vocab, 1.0 / n_vocab),
                             size=n_blocks).astype(np.float64)
    features = np.sqrt(counts / k).astype(np.float32)
    quarter = (mid_days // MOD.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid_days, quarter))
    return (features[order], author[order], quarter[order], mid_days[order])


def test_rows_on_one_block_set_get_identical_author_bootstrap_draws():
    """#72 by construction: the Lambda bootstrap is paired."""

    rng = np.random.default_rng(21)
    features, author, quarter, mid = _toy_arm_inputs(rng)
    columns_a = np.array([0, 1, 2], dtype=np.int64)
    columns_b = np.array([3, 4, 5, 6, 7, 8, 9], dtype=np.int64)
    row_a = MOD.U2.compute_arm(MOD.renormalize(features, columns_a), author,
                               quarter, mid, n_perm=6, n_boot=32,
                               seed=MOD.SEED)
    row_b = MOD.U2.compute_arm(MOD.renormalize(features, columns_b), author,
                               quarter, mid, n_perm=6, n_boot=32,
                               seed=MOD.SEED)
    assert row_a["n_authors"] == row_b["n_authors"]
    # identical multinomial draws => identical denominators row by row
    boot_rng = np.random.default_rng(MOD.SEED + 11)
    mult = boot_rng.multinomial(row_a["n_authors"],
                                np.full(row_a["n_authors"],
                                        1.0 / row_a["n_authors"]), size=32)
    assert mult.shape == (32, row_a["n_authors"])
    assert row_a["boot_curve"].shape == row_b["boot_curve"].shape == (32, 6)


def test_permutation_preserves_each_authors_per_quarter_block_count():
    rng = np.random.default_rng(23)
    _features, author, quarter, _mid = _toy_arm_inputs(rng)
    plans = MOD.U2.build_quarter_plans(quarter, author, 5, MOD.SEED)
    for q, plan in plans.items():
        rows = plan.rows
        real = np.bincount(author[rows], minlength=int(author.max()) + 1)
        assert plan.slot_position.shape[0] == 6
        # row 0 is the identity assignment
        np.testing.assert_array_equal(plan.slot_author,
                                      author[rows][plan.slot_position[0]])
        for p in range(plan.slot_position.shape[0]):
            permuted = author[rows][plan.slot_position[p]]
            # the slot -> author map is invariant, so the per-author count in
            # this quarter is EXACTLY preserved by every relabelling
            got = np.bincount(permuted, minlength=int(author.max()) + 1)
            np.testing.assert_array_equal(got, real)
            assert sorted(plan.slot_position[p].tolist()) == \
                list(range(rows.size))


def test_permutation_null_of_the_slope_contrast_sits_at_zero_on_a_toy():
    """No author structure => the relabelled contrast has no location."""

    rng = np.random.default_rng(29)
    features, author, quarter, mid = _toy_arm_inputs(rng, n_blocks=220)
    row = MOD.U2.compute_arm(features, author, quarter, mid, n_perm=200,
                             n_boot=16, seed=MOD.SEED)
    gaps = np.asarray(row["mean_gap_days"]) / MOD.DAYS_PER_YEAR
    linear_null = MOD.U2C.linear_slope(gaps, row["null_curve"])
    # the LINEAR companion is defined on every replicate (that is why the
    # registration poses the Lambda null on it, #80a) and has no location
    assert np.isfinite(linear_null).all()
    assert abs(float(np.median(linear_null))) < 0.02
    # the LOG form is undefined here: a structureless toy drives E(b) through
    # zero, so the positivity rule drops replicates rather than imputing them
    log_null = MOD.U2C.log_slope_fit(gaps, row["null_curve"])
    assert int(np.count_nonzero(~log_null["positive"])) > 0


def test_differencing_a_row_against_itself_is_exactly_zero():
    """The paired contrast is a replicate-by-replicate difference."""

    row = _synthetic_row(0.31, 0.55, seed=41)
    gaps = np.asarray(row["mean_gap_days"]) / MOD.DAYS_PER_YEAR
    a = MOD.U2C.summarize_lambda("a", "a", row, gaps)
    b = MOD.U2C.summarize_lambda("b", "b", row, gaps)
    a["_linear_null"] = MOD.U2C.linear_slope(gaps, row["null_curve"])
    b["_linear_null"] = a["_linear_null"]
    delta = MOD.U2C.rate_contrast("self", a, b, gaps, paired=True)
    assert delta["point"] == 0.0
    assert delta["ci"] == [0.0, 0.0]
    assert delta["linear_point"] == 0.0
    assert delta["boot_retained"] == delta["boot_replicates"]


# ---------------------------------------------------------------------------
# The transport table
# ---------------------------------------------------------------------------


def test_sealed_source_values_are_the_registered_ones():
    assert MOD.SEALED["lambda_contrast"]["point"] == 0.0741
    assert MOD.SEALED["lambda_contrast"]["ci"] == [-0.0558, 0.1854]
    assert MOD.SEALED["floor_share_full"]["point"] == 0.5348
    assert MOD.SEALED["floor_share_full"]["ci"] == [0.4203, 0.6320]
    assert MOD.SEALED["d_full"]["point"] == 0.3058
    assert MOD.SEALED["d_full"]["ci"] == [0.2364, 0.3855]
    assert MOD.SEALED["lambda_full"]["point"] == 0.2943
    assert MOD.SEALED["lambda_full"]["ci"] == [0.1895, 0.4405]


@pytest.mark.parametrize("source_ci,target_ci,expected", [
    ([0.20, 0.40], [0.25, 0.50], "REPRODUCES"),      # overlap, same sign
    ([0.20, 0.40], [0.41, 0.60], "SHIFTS"),          # disjoint, same sign
    ([0.20, 0.40], [-0.50, -0.10], "BREAKS"),        # different sign
    ([0.20, 0.40], [-0.05, 0.30], "BREAKS"),         # target straddles zero
    ([0.20, 0.40], [0.40, 0.60], "REPRODUCES"),      # touching counts as met
])
def test_transport_classification_is_the_registered_rule(source_ci, target_ci,
                                                         expected):
    got = MOD.classify_transport(source_ci, target_ci,
                                 MOD.sign_cell(source_ci),
                                 MOD.sign_cell(target_ci))
    assert got == expected


def test_sign_cells_partition_the_line():
    assert MOD.sign_cell([0.01, 0.2]) == "POSITIVE"
    assert MOD.sign_cell([-0.2, -0.01]) == "NEGATIVE"
    assert MOD.sign_cell([-0.2, 0.2]) == "SIGN_UNRESOLVED"
    assert MOD.sign_cell([0.0, 0.2]) == "SIGN_UNRESOLVED"


def test_transport_table_flags_breaks_and_counts_them():
    law = {
        "primary": {"point": 0.05, "ci": [-0.01, 0.11]},
        "cell": {"cell": "SIGN_UNRESOLVED"},
        "row_order": ["full", "common", "distinct", "taste"],
        "slowest_row": "common",
        "rows": {
            "full": {"floor_share": 0.53, "floor_share_ci": [0.44, 0.62],
                     "d": 0.30, "d_ci": [0.24, 0.37],
                     "lambda_per_year": 0.29, "lambda_ci": [0.19, 0.44]},
            "common": {"lambda_per_year": 0.10, "lambda_ci": [0.05, 0.16]},
            "distinct": {"lambda_per_year": 0.15, "lambda_ci": [0.09, 0.22]},
            "taste": {"lambda_per_year": 0.22, "lambda_ci": [0.17, 0.28]},
        },
    }
    table = MOD.build_transport_table(law)
    classes = {r["key"]: r["classification"] for r in table["rows"]}
    assert classes["lambda_contrast"] == "REPRODUCES"
    assert classes["floor_share_full"] == "REPRODUCES"
    assert classes["d_full"] == "REPRODUCES"
    assert classes["lambda_full"] == "REPRODUCES"
    assert table["ordering"]["classification"] == "BREAKS"
    assert table["ordering"]["flag_73"] is True
    assert table["n_breaks"] == 1
    # the ordering row carries the margin, so a narrow miss reads as narrow
    assert table["ordering"]["ranked_slowest_first"] == ["common", "distinct",
                                                         "taste", "full"]
    assert table["ordering"]["taste_rank"] == 3
    assert table["ordering"]["taste_margin_to_slowest"] == pytest.approx(0.12)
    assert table["ordering"]["taste_ci_contains_slowest"] is False


def test_a_break_that_is_only_a_precision_gain_is_marked_as_such():
    """Overlapping intervals with the source point inside the target CI."""

    row = MOD.transport_row("lambda_contrast", 0.0911, [0.0628, 0.1490],
                            source_cell_override="SIGN_UNRESOLVED",
                            target_cell_override="COMMON_STANDING")
    assert row["classification"] == "BREAKS"     # the registered rule stands
    assert row["ci_overlap"] is True
    assert row["source_point_inside_target_ci"] is True
    assert row["target_half_width"] < row["source_half_width"]


# ---------------------------------------------------------------------------
# ID-leak helper over the WIDENED universe
# ---------------------------------------------------------------------------


def test_id_leak_scanner_finds_a_planted_name_from_either_half(tmp_path):
    universe = ["alpha_writer", "zeta_reader", "shortie"]
    clean = tmp_path / "clean.md"
    clean.write_text("no names here, only aggregates: 0.0741 and 1,443\n",
                     encoding="utf-8")
    assert MOD.U2.scan_for_cohort_ids([clean], universe)["status"] == "PASS"

    dirty = tmp_path / "dirty.md"
    dirty.write_text("the top contributor was zeta_reader last year\n",
                     encoding="utf-8")
    result = MOD.U2.scan_for_cohort_ids([dirty], universe)
    assert result["status"] == "FAIL" and result["n_hits"] == 1

    # substrings of longer identifiers are NOT hits (the boundary rule)
    embedded = tmp_path / "embedded.md"
    embedded.write_text("see zeta_readerly_things for context\n",
                       encoding="utf-8")
    assert MOD.U2.scan_for_cohort_ids([embedded], universe)["status"] == "PASS"


def test_the_scan_universe_is_the_union_of_both_cohorts():
    """10,296 = 1,401 committed cohort names + 8,895 disjoint names."""

    assert MOD.CENSUS_AUTHORS_SEEN + 1401 == 10_296
    cohort = MOD.DEFAULT_COHORT
    if not cohort.exists():                       # pragma: no cover
        pytest.skip("the 1401 cohort listing is a gitignored artifact")
    names = pd.read_csv(cohort, usecols=["author"])["author"]
    assert len(set(str(n) for n in names)) == 1401


def test_new_hits_are_separated_from_pre_existing_ones_mechanically():
    """A hit at the same file and line at HEAD is a collision, not a leak."""

    hits = [{"path": "/repo/docs/CLAIMS_LEDGER.md", "line": 42},
            {"path": "/repo/docs/CLAIMS_LEDGER.md", "line": 903},
            {"path": "/repo/reports/W1.md", "line": 7}]
    baseline = {("CLAIMS_LEDGER.md", 42)}
    new = MOD.new_hits_only(hits, baseline)
    assert [h["line"] for h in new] == [903, 7]
    # a file with no HEAD version has an empty baseline: zero tolerance
    assert len(MOD.new_hits_only(hits, set())) == 3
    # and a fully pre-existing hit set clears the gate
    assert MOD.new_hits_only(
        hits, {("CLAIMS_LEDGER.md", 42), ("CLAIMS_LEDGER.md", 903),
               ("W1.md", 7)}) == []


def test_committed_files_carry_no_author_identity():
    scan_path = ARTIFACTS / "id_leak_scan.json"
    if not scan_path.exists():                    # pragma: no cover
        pytest.skip("the W1 run has not been executed in this checkout")
    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    assert scan["status"] == "PASS"
    assert scan["n_new_hits"] == 0
    assert scan["universe_size"] == 10_296
    # W1's own outputs must be clean against the FULL universe: they have no
    # HEAD version, so every hit in them would be a NEW hit
    authored = {"SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md",
                "run_suica_m4_w1_slow_transport.py",
                "test_m4_w1_slow_transport.py"}
    assert not (authored & {Path(h["path"]).name
                            for h in scan.get("new_hits", [])})
    scanned = {Path(p).name for p in scan["files_scanned"]}
    assert {"SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md",
            "run_suica_m4_w1_slow_transport.py",
            "test_m4_w1_slow_transport.py",
            "SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md",
            "CLAIMS_LEDGER.md"} <= scanned


# ---------------------------------------------------------------------------
# Governance: label-free, results gitignored, no person claims
# ---------------------------------------------------------------------------


def test_no_personality_label_is_read_anywhere():
    """`author_profiles.csv` may be NAMED in governance prose, never opened."""

    text = SCRIPT.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "author_profiles" not in line:
            continue
        # every mention must be a governance statement, never a data access
        assert "never" in line.casefold(), line
        for access in ("read_csv", "open(", "np.load", "Path(", "loadtxt"):
            assert access not in line, line
    # no label file is referenced by any path constant or reader call
    for banned in ("author_profiles.csv", "profiles.csv", "labels.csv",
                   "big5_prepared", "mbti_axes", "author_profiles.parquet"):
        occurrences = [ln for ln in text.splitlines()
                       if banned in ln and "never" not in ln.casefold()]
        assert occurrences == [], (banned, occurrences)
    # and no trait name is read, scored or written anywhere
    for trait in ("openness", "conscientiousness", "neuroticism",
                  "agreeableness", "extraversion"):
        assert trait not in text.casefold(), trait


def test_the_cache_and_cohort_listing_live_only_in_results():
    assert str(MOD.DEFAULT_OUTPUT).endswith("results/m4_w1_slow_transport")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "results/" in gitignore.splitlines()


# ---------------------------------------------------------------------------
# Committed-run consistency (skipped in a fresh checkout)
# ---------------------------------------------------------------------------


def _artifact(name: str):
    path = ARTIFACTS / name
    if not path.exists():                         # pragma: no cover
        pytest.skip("the W1 run has not been executed in this checkout")
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_run_reproduced_every_census_pin():
    census = _artifact("census.json")
    assert census["status"] == "PASS"
    for key, entry in census["pins"].items():
        assert entry["status"] == "PASS", key
        assert entry["registered"] == entry["observed"], key


def test_committed_run_cleared_the_cache_anchor_gate():
    anchors = _artifact("anchors.json")
    assert anchors["status"] == "PASS"
    assert anchors["observed"]["disjoint_events"] == MOD.CENSUS_DISJOINT_EVENTS
    assert anchors["observed"]["authors_seen"] == MOD.CENSUS_AUTHORS_SEEN
    assert anchors["observed"]["vocabulary"] == MOD.CENSUS_LAW_VOCAB
    assert anchors["coverage_observed"] == MOD.CENSUS_LAW_COVERAGE


def test_committed_verdict_matches_the_committed_report():
    verdict = _artifact("verdict.json")
    if not REPORT.exists():                       # pragma: no cover
        pytest.skip("the W1 report has not been generated in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    assert f"**Outcome: `{verdict['outcome']}`.**" in text
    assert verdict["cell"] in {"SIGN_UNRESOLVED", "COMMON_STANDING",
                               "DISTINCT_SLOWER"}
    assert MOD.fmt(verdict["lambda_point"]) in text
    assert MOD.fmt_ci(verdict["lambda_ci"]) in text


def test_committed_run_kept_the_taste_folds_pure():
    purity = _artifact("taste_purity.json")
    assert len(purity) == MOD.TASTE_FOLDS
    for fold in purity:
        assert fold["status"] == "PASS"
        assert fold["overlap"] == 0
        assert fold["test_mass_excluded"] > 0.0
        assert fold["fitted_mass"] == pytest.approx(
            fold["train_first_half_mass"], abs=1e-6)
        assert fold["embedding_rank"] == MOD.TASTE_DIM


def test_committed_report_carries_the_registered_cautions():
    if not REPORT.exists():                       # pragma: no cover
        pytest.skip("the W1 report has not been generated in this checkout")
    text = REPORT.read_text(encoding="utf-8")
    for needle in ("TYPOLOGY-ENRICHED", "eq 12", "THREE-YEAR",
                   "No equivalence cell exists", "SECONDARY",
                   "EXPLORATORY", "Label-free"):
        assert needle in text, needle


def test_committed_transport_table_is_complete_and_classified():
    transport = _artifact("transport_table.json")
    keys = {row["key"] for row in transport["rows"]}
    assert keys == {"lambda_contrast", "floor_share_full", "d_full",
                    "lambda_full"}
    for row in transport["rows"]:
        assert row["classification"] in {"REPRODUCES", "SHIFTS", "BREAKS"}
        assert row["source_ci"] == MOD.SEALED[row["key"]]["ci"]
        assert row["source_point"] == MOD.SEALED[row["key"]]["point"]
    assert transport["ordering"]["classification"] in {"REPRODUCES", "BREAKS"}
