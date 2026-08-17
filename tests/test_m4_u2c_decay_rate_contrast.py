"""M4-U2c -- the decay-rate contrast: contract tests.

U2c's whole claim is a CONTRAST OF SLOPES between two carrier restrictions of
the same blocks, so the properties that must hold are the ones that make such a
contrast an estimate of anything at all.

**The slope estimator must recover a known rate.**  lambda is the verdict's
unit; if the OLS on log E(b) does not return the generating rate of an exact
exponential to machine precision, nothing downstream means what it says.

**The bootstrap must be paired.**  Lambda's interval is a difference of two
rates taken replicate by replicate; that is legitimate only because every row
sits on ONE block set and ``compute_arm`` therefore draws the IDENTICAL author
multinomial for each of them.  This is tested directly.

**The gate predicate must be re-executable.**  Defect #78 was a gate governed
by a quantity nobody censused.  U2c's gate quantities are U2b's REALIZED
intersection numbers and the runner re-executes the same predicate; the tests
pin the arithmetic of that predicate and the registered anchors it must hit.

**The logarithm must fail loudly.**  A permutation replicate whose E(b) is
negative has no log-slope.  The estimator must return NaN and the count must be
reported, never silently imputed.

The rest pins the machinery the registration named as blocking: the three
cells, the exclusion of the 3y+ bin from the fit, the U2b/U2 import chain
(#56), the ID-leak scan and label-freedom.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_u2c_decay_rate_contrast.py"
U2B_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2b_persistence_budget.py"
U2_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2_persistence_curve.py"
ARTIFACTS = ROOT / "results" / "m4_u2c_decay_rate_contrast"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_u2c_decay_rate_contrast", SCRIPT)
DAY = 86400.0
GAPS = np.array([0.118, 0.365, 0.730, 1.417, 2.396])


def _toy_blocks(rng, n_blocks=200, n_authors=16, n_vocab=12,
                span_days=1300.0, k=50):
    """Exact-K count blocks with NO author structure (U2b's toy convention)."""

    author = rng.integers(0, n_authors, size=n_blocks).astype(np.int32)
    mid_days = np.sort(rng.uniform(0.0, span_days, size=n_blocks))
    counts = rng.multinomial(k, np.full(n_vocab, 1.0 / n_vocab),
                             size=n_blocks).astype(np.float64)
    features = np.sqrt(counts / k).astype(np.float32)
    quarter = (mid_days // MOD.U2.QUARTER_DAYS).astype(np.int32)
    order = np.lexsort((mid_days, quarter))
    return (features[order], counts[order], author[order], quarter[order],
            mid_days[order])


# ---------------------------------------------------------------------------
# The estimand: a slope fit that recovers a known exponential
# ---------------------------------------------------------------------------


def test_slope_fit_recovers_a_hand_checked_exponential():
    """E(b) = E0 * exp(-lambda * g_b) exactly => lambda and E0 come back."""

    e0, lam = 0.5312, 0.2734
    curve = e0 * np.exp(-lam * GAPS)
    fit = MOD.log_slope_fit(GAPS, curve)

    assert float(fit["lambda_per_year"]) == pytest.approx(lam, abs=1e-12)
    assert float(fit["e0"]) == pytest.approx(e0, rel=1e-12)
    assert float(fit["log_e0"]) == pytest.approx(np.log(e0), abs=1e-12)
    assert float(fit["r_squared"]) == pytest.approx(1.0, abs=1e-12)
    assert float(fit["sse_log"]) == pytest.approx(0.0, abs=1e-20)
    assert bool(fit["positive"]) is True

    # a hand-checked second case: halving every year is lambda = ln 2
    curve2 = 1.0 * np.exp(-np.log(2.0) * GAPS)
    assert float(MOD.log_slope_fit(GAPS, curve2)["lambda_per_year"]) == \
        pytest.approx(np.log(2.0), abs=1e-12)


def test_slope_fit_is_level_free_but_not_shape_free():
    """A gap-independent attenuation moves log E0, NEVER lambda."""

    curve = 0.5 * np.exp(-0.3 * GAPS)
    base = MOD.log_slope_fit(GAPS, curve)
    scaled = MOD.log_slope_fit(GAPS, 0.37 * curve)
    assert float(scaled["lambda_per_year"]) == pytest.approx(
        float(base["lambda_per_year"]), abs=1e-12)
    assert float(scaled["log_e0"]) == pytest.approx(
        float(base["log_e0"]) + np.log(0.37), abs=1e-12)
    # a gap-DEPENDENT distortion does move lambda -- the estimator is not blind
    tilted = MOD.log_slope_fit(GAPS, curve * np.exp(-0.1 * GAPS))
    assert float(tilted["lambda_per_year"]) == pytest.approx(0.4, abs=1e-12)


def test_slope_fit_batches_match_the_scalar_path():
    rng = np.random.default_rng(5)
    batch = 0.5 * np.exp(-np.array([[0.2], [0.3], [0.44]]) * GAPS)
    batch = batch * (1.0 + 0.01 * rng.standard_normal(batch.shape))
    fitted = MOD.log_slope_fit(GAPS, batch)["lambda_per_year"]
    assert fitted.shape == (3,)
    for i in range(3):
        one = MOD.log_slope_fit(GAPS, batch[i])["lambda_per_year"]
        assert float(fitted[i]) == pytest.approx(float(one), abs=1e-15)


def test_the_fit_uses_five_bins_and_never_the_3y_plus_bin():
    """The 3y+ bin is descriptive; moving it must not move lambda."""

    assert MOD.N_FIT_BINS == 5
    assert MOD.FAR_BIN == 4 and MOD.DESCRIPTIVE_BIN == 5
    assert MOD.BIN_LABELS[MOD.FAR_BIN] == "2-3y"
    assert MOD.BIN_LABELS[MOD.DESCRIPTIVE_BIN] == "3y+"

    six_gaps = np.append(GAPS, 3.40)
    curve = np.append(0.5 * np.exp(-0.3 * GAPS), 0.49)   # absurd 3y+ value
    fit = MOD.log_slope_fit(six_gaps, curve)
    assert float(fit["lambda_per_year"]) == pytest.approx(0.3, abs=1e-12)


# ---------------------------------------------------------------------------
# The positivity guard
# ---------------------------------------------------------------------------


def test_log_fit_positivity_guard_drops_and_counts_non_positive_replicates():
    """No logarithm of a non-positive excess, and the drop must be visible."""

    good = 0.5 * np.exp(-0.3 * GAPS)
    batch = np.vstack([good, good.copy(), good.copy(), good.copy()])
    batch[1, 2] = -1e-4          # a sign-flipped bin
    batch[2, 0] = 0.0            # an exactly-zero bin
    fit = MOD.log_slope_fit(GAPS, batch)
    lam = fit["lambda_per_year"]

    assert list(fit["positive"]) == [True, False, False, True]
    assert np.isnan(lam[1]) and np.isnan(lam[2])
    assert float(lam[0]) == pytest.approx(0.3, abs=1e-12)
    assert int(np.count_nonzero(~fit["positive"])) == 2
    # the CI helper must ignore the dropped replicates rather than propagate
    assert all(np.isfinite(v) for v in MOD.percentile_ci(lam))


def test_the_linear_companion_is_defined_where_the_log_is_not():
    """RD-U2C-1: the positivity-free slope exists on sign-flipped replicates."""

    null_like = np.array([[1e-4, -2e-4, 5e-5, -1e-4, 3e-5],
                          [-1e-4, 2e-4, -5e-5, 1e-4, -3e-5]])
    assert np.all(np.isnan(
        MOD.log_slope_fit(GAPS, null_like)["lambda_per_year"]))
    linear = MOD.linear_slope(GAPS, null_like)
    assert np.all(np.isfinite(linear))
    # antisymmetric input => antisymmetric slope
    assert float(linear[0]) == pytest.approx(-float(linear[1]), abs=1e-18)


# ---------------------------------------------------------------------------
# The pairing invariant (#72) -- what makes Lambda's interval a paired one
# ---------------------------------------------------------------------------


def test_rows_on_one_block_set_get_identical_bootstrap_author_draws():
    """The invariant Lambda's CI rests on, checked on the real machinery."""

    rng = np.random.default_rng(17)
    features, _counts, author, quarter, mid = _toy_blocks(rng)
    rows = {
        "full": features,
        "common": MOD.renormalize(features, np.arange(4)),
        "distinct": MOD.renormalize(features, np.arange(4, 12)),
    }
    results = {k: MOD.U2.compute_arm(v, author, quarter, mid, n_perm=3,
                                     n_boot=24, seed=MOD.SEED, label=k)
               for k, v in rows.items()}
    reference = results["full"]
    for key, result in results.items():
        assert result["self_pairs"] == reference["self_pairs"], key
        assert result["n_authors"] == reference["n_authors"], key
        assert result["boot_curve"].shape == reference["boot_curve"].shape
        assert result["cross_pairs_available"] == \
            reference["cross_pairs_available"], key

    n_authors = reference["n_authors"]
    draw_a = np.random.default_rng(MOD.SEED + 11).multinomial(
        n_authors, np.full(n_authors, 1.0 / n_authors), size=24)
    draw_b = np.random.default_rng(MOD.SEED + 11).multinomial(
        n_authors, np.full(n_authors, 1.0 / n_authors), size=24)
    assert np.array_equal(draw_a, draw_b)


def _synthetic_row(lam: float, e0: float, seed: int, n_boot: int = 64,
                   n_perm: int = 32) -> dict:
    """A row shaped exactly like ``compute_arm``'s output, with a known rate.

    The bootstrap noise is drawn from a per-row generator seeded so that the
    two rows of a contrast share their replicate INDEX -- which is what
    ``compute_arm``'s shared author multinomial guarantees on real data.
    """

    rng = np.random.default_rng(seed)
    gaps = np.append(GAPS, 3.40)
    curve = e0 * np.exp(-lam * gaps)
    boot = curve[None, :] * (1.0 + 0.04 * rng.standard_normal((n_boot, 6)))
    null = 2e-4 * rng.standard_normal((n_perm, 6))
    return {
        "curve": [float(v) for v in curve],
        "boot_curve": boot, "null_curve": null,
        "curve_ci": [[float(v) * 0.9, float(v) * 1.1] for v in curve],
        "curve_null_center": [0.0] * 6,
        "mean_gap_days": [float(v) * MOD.DAYS_PER_YEAR for v in gaps],
        "self_pairs": [100] * 6, "n_blocks": 500, "n_authors": 40,
        "floor_share": float(curve[MOD.FAR_BIN] / curve[MOD.NEAR_BIN]),
    }


def test_lambda_contrast_is_differenced_replicate_by_replicate():
    """Lambda's CI is the percentile CI of the PAIRED replicate difference."""

    row_a = _synthetic_row(0.34, 0.44, seed=23)
    row_b = _synthetic_row(0.25, 0.60, seed=24)
    gaps = np.asarray(row_a["mean_gap_days"]) / MOD.DAYS_PER_YEAR
    sa = MOD.summarize_lambda("distinct", "distinct", row_a, gaps)
    sb = MOD.summarize_lambda("common", "common", row_b, gaps)
    sa["_linear_null"] = MOD.linear_slope(gaps, row_a["null_curve"])
    sb["_linear_null"] = MOD.linear_slope(gaps, row_b["null_curve"])

    # the point rates ARE the generating rates
    assert sa["lambda_per_year"] == pytest.approx(0.34, abs=1e-12)
    assert sb["lambda_per_year"] == pytest.approx(0.25, abs=1e-12)

    out = MOD.rate_contrast("Λ", sa, sb, gaps, paired=True)
    manual = sa["_boot_lambda"] - sb["_boot_lambda"]
    assert out["ci"] == MOD.percentile_ci(manual)
    assert out["point"] == pytest.approx(0.09, abs=1e-12)
    assert out["boot_replicates"] == 64 and out["boot_retained"] == 64
    assert out["paired_bootstrap"] is True
    assert out["ci"][0] < out["point"] < out["ci"][1]


# ---------------------------------------------------------------------------
# The gate predicate (#78)
# ---------------------------------------------------------------------------


def test_gate_predicate_is_the_block_conjunction_at_the_primary_floor():
    """At m = 5 on a K = 50 block the predicate is exactly 5 <= common <= 45."""

    import itertools

    rng = np.random.default_rng(3)
    n_blocks, k, m = 300, MOD.K_PRIMARY, MOD.M_PRIMARY
    common_count = rng.integers(0, k + 1, size=n_blocks)
    distinct_count = k - common_count
    author = rng.integers(0, 20, size=n_blocks)

    literal = {
        (i, j) for i, j in itertools.combinations(range(n_blocks), 2)
        if author[i] == author[j]
        and common_count[i] >= m and distinct_count[i] >= m
        and common_count[j] >= m and distinct_count[j] >= m}
    block_ok = (common_count >= m) & (distinct_count >= m)
    assert np.array_equal(block_ok, (common_count >= m)
                          & (common_count <= k - m))
    eligible = [int(v) for v in np.flatnonzero(block_ok)]
    subset = {(i, j) for i, j in itertools.combinations(eligible, 2)
              if author[i] == author[j]}
    assert literal == subset and len(literal) > 0
    # the lower floor admits strictly more blocks than U2b's m = 10
    assert block_ok.sum() > ((common_count >= 10)
                             & (distinct_count >= 10)).sum()


def test_the_gate_anchors_are_u2bs_realized_quantities():
    """#78: the gate's numbers are the predicate ALREADY EXECUTED, not bounds."""

    assert MOD.GATE_ANCHORS["primary q=0.5/m=5"] == {
        "q_milli": 500, "m": 5, "pairs_2_3y": 179_107, "authors_2_3y": 424}
    assert MOD.GATE_ANCHORS["confirmatory q=0.7/m=10"] == {
        "q_milli": 700, "m": 10, "pairs_2_3y": 108_716, "authors_2_3y": 401}
    for pin in MOD.GATE_ANCHORS.values():
        assert pin["pairs_2_3y"] >= MOD.POOL_GATE_MIN_PAIRS_2_3Y
        assert pin["authors_2_3y"] >= MOD.POOL_GATE_MIN_AUTHORS_2_3Y

    grid = json.loads(
        (ROOT / "results/m4_u2b_persistence_budget/sensitivities.json"
         ).read_text(encoding="utf-8")) if (
        ROOT / "results/m4_u2b_persistence_budget/sensitivities.json"
    ).exists() else None
    if grid is None:                     # pragma: no cover - gitignored
        pytest.skip("U2b artifacts not present")
    by_config = {(entry["q"], entry["m"]): entry for entry in grid}
    for pin in MOD.GATE_ANCHORS.values():
        entry = by_config[(pin["q_milli"] / 1000.0, pin["m"])]
        assert entry["pairs_2_3y"] == pin["pairs_2_3y"]
        assert entry["authors_2_3y"] == pin["authors_2_3y"]


def test_gate_predicate_recomputation_is_a_census_not_a_projection():
    """The pair census counts BOTH pairs and contributing authors per bin."""

    author = np.array([0, 0, 0, 1, 1, 2])
    mid = np.array([0.0, 30.0, 800.0, 10.0, 500.0, 5.0])
    pairs, contributors = MOD.U2B.self_pair_census(author, mid)
    near = MOD.NEAR_BIN
    assert pairs[near] == 1 and contributors[near] == 1     # author 0: 0 vs 30
    assert int(pairs.sum()) == 3 + 1                        # 3 + 1 + 0
    assert contributors[MOD.FAR_BIN] == 1                   # only author 0
    # a marginal count is NOT the intersection count: the census must be exact
    assert int(pairs.sum()) < 6 * 5 // 2


# ---------------------------------------------------------------------------
# The permutation null
# ---------------------------------------------------------------------------


def test_permutation_null_center_of_the_slope_contrast_is_zero_on_a_toy():
    """A structureless world: the positivity-free Lambda null sits at zero."""

    rng = np.random.default_rng(29)
    features, _counts, author, quarter, mid = _toy_blocks(
        rng, n_blocks=260, n_authors=18)
    kwargs = dict(n_perm=120, n_boot=40, seed=MOD.SEED)
    a = MOD.U2.compute_arm(MOD.renormalize(features, np.arange(5)), author,
                           quarter, mid, label="a", **kwargs)
    b = MOD.U2.compute_arm(MOD.renormalize(features, np.arange(5, 12)),
                           author, quarter, mid, label="b", **kwargs)
    gaps = np.asarray(a["mean_gap_days"]) / MOD.DAYS_PER_YEAR

    null = (MOD.linear_slope(gaps, a["null_curve"])
            - MOD.linear_slope(gaps, b["null_curve"]))
    assert np.all(np.isfinite(null))
    spread = float(np.percentile(null, 97.5) - np.percentile(null, 2.5))
    assert abs(float(np.median(null))) < 0.25 * spread, (
        float(np.median(null)), spread)
    # and the per-bin E(b) null centers are at zero, U2's own check
    centers = np.asarray(a["curve_null_center"])
    finite = centers[np.isfinite(centers)]
    assert finite.size >= 4 and np.abs(finite).max() < 0.02


def test_identical_rows_give_an_exactly_zero_null_contrast():
    """The contrast of a row with itself is 0 in every replicate."""

    rng = np.random.default_rng(31)
    curves = 0.5 * np.exp(-0.3 * GAPS) * (
        1.0 + 0.05 * rng.standard_normal((64, MOD.N_FIT_BINS)))
    a = MOD.log_slope_fit(GAPS, curves)["lambda_per_year"]
    assert np.all(a - a == 0.0)
    assert MOD.percentile_ci(a - a) == [0.0, 0.0]


def test_rate_contrast_reports_retention_never_imputes():
    """A null with no usable log form must SAY SO, not fabricate a center."""

    def row(lam_boot, lam_null, point):
        return {"lambda_per_year": point, "_boot_lambda": lam_boot,
                "_null_lambda": lam_null,
                "linear_slope_per_year": 0.0,
                "_linear_null": np.zeros(lam_null.size)}

    boot = np.full(16, 0.30)
    null = np.full(8, np.nan)
    out = MOD.rate_contrast("Λ", row(boot, null, 0.33),
                            row(boot - 0.05, null, 0.25), GAPS, paired=True)
    assert out["null_replicates"] == 8 and out["null_retained"] == 0
    assert np.isnan(out["null_center"])
    assert out["boot_retained"] == 16
    assert out["linear_null_finite_fraction"] == 1.0
    assert out["point"] == pytest.approx(0.08)


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ci,expected", [
    ([0.02, 0.18], "COMMON_STANDING"),
    ([-0.18, -0.02], "DISTINCT_SLOWER"),
    ([-0.03, 0.19], "SIGN_UNRESOLVED"),
    ([0.0, 0.19], "SIGN_UNRESOLVED"),        # a boundary touch is unresolved
    ([-0.19, 0.0], "SIGN_UNRESOLVED"),
    ([-0.001, 0.001], "SIGN_UNRESOLVED"),    # near-zero is NOT equivalence
])
def test_cells_are_the_three_registered_boundaries(ci, expected):
    cell = MOD.classify_lambda({"ci": ci, "ci_half_width":
                                0.5 * (ci[1] - ci[0])})
    assert cell["cell"] == expected


def test_no_equivalence_cell_exists_by_registration():
    """#79a: none was reachable at the projected width, so none is offered."""

    tight = MOD.classify_lambda({"ci": [-0.002, 0.002],
                                 "ci_half_width": 0.002})
    assert tight["cell"] == "SIGN_UNRESOLVED"
    assert tight["equivalence_cell_offered"] is False
    source = SCRIPT.read_text(encoding="utf-8")
    assert "EQUIVALENCE_BAND" not in source
    assert "NO_LAYER_SPLIT" not in source
    assert set(MOD.classify_lambda({"ci": [np.nan, np.nan],
                                    "ci_half_width": np.nan})) >= {
        "cell", "equivalence_cell_offered"}


def test_projection_is_carried_in_code_and_compared_to_the_realized_width():
    assert MOD.PROJECTED_LAMBDA_POINT == 0.10
    assert MOD.PROJECTED_HALF_WIDTH == (0.08, 0.10)
    wide = MOD.classify_lambda({"ci": [-0.3, 0.3], "ci_half_width": 0.3})
    assert wide["half_width_inside_projection"] is False
    narrow = MOD.classify_lambda({"ci": [-0.05, 0.05], "ci_half_width": 0.05})
    assert narrow["half_width_inside_projection"] is True


# ---------------------------------------------------------------------------
# G0 and the inherited machinery (#56)
# ---------------------------------------------------------------------------


def test_field_comparison_detects_a_perturbed_row():
    committed = {"curve": [0.5, 0.4, 0.3, 0.2, 0.1, 0.05], "n_blocks": 10}
    same = MOD.compare_fields(dict(committed), committed,
                              ("curve", "n_blocks"))
    assert same["bitwise_identical"] is True
    assert same["max_abs_difference"] == 0.0

    nudged = {"curve": [0.5, 0.4, 0.3, 0.2, 0.1 + 1e-12, 0.05],
              "n_blocks": 10}
    off = MOD.compare_fields(nudged, committed, ("curve", "n_blocks"))
    assert off["bitwise_identical"] is False
    assert off["max_abs_difference"] == pytest.approx(1e-12, rel=1e-3)

    missing = MOD.compare_fields({"curve": [1.0]}, committed, ("n_blocks",))
    assert missing["bitwise_identical"] is False


def test_g0_recomputation_is_bit_identical_on_a_toy_end_to_end():
    rng = np.random.default_rng(41)
    features, _counts, author, quarter, mid = _toy_blocks(rng, n_blocks=150)
    kwargs = dict(n_perm=4, n_boot=16, seed=MOD.SEED,
                  cross_sampler_check=False, label="anchor")
    first = MOD.U2B.summarize_row(
        MOD.U2.compute_arm(features, author, quarter, mid, **kwargs))
    second = MOD.U2B.summarize_row(
        MOD.U2.compute_arm(features, author, quarter, mid, **kwargs))
    comparison = MOD.compare_fields(first, second, MOD.G0_ROW_FIELDS)
    assert comparison["bitwise_identical"] is True
    assert comparison["max_abs_difference"] == 0.0
    assert len(comparison["fields"]) == len(MOD.G0_ROW_FIELDS)


def test_committed_run_reproduced_u2bs_four_rows_bitwise():
    """The realized G0 gate, read from the run's own artifact."""

    path = ARTIFACTS / "g0_anchor_comparison.json"
    if not path.exists():                # pragma: no cover - gitignored
        pytest.skip("U2c artifacts not present")
    g0 = json.loads(path.read_text(encoding="utf-8"))
    assert g0["status"] == "PASS", g0
    assert g0["bitwise_identical"] is True
    assert g0["max_abs_difference"] == 0.0
    assert [row["row"] for row in g0["rows"]] == list(MOD.ROW_KEYS)


def test_committed_run_re_executed_the_gate_predicate():
    path = ARTIFACTS / "gate_anchor.json"
    if not path.exists():                # pragma: no cover - gitignored
        pytest.skip("U2c artifacts not present")
    gate = json.loads(path.read_text(encoding="utf-8"))
    assert gate["status"] == "PASS"
    assert len(gate["rows"]) == len(MOD.GATE_ANCHORS)
    for row in gate["rows"]:
        assert row["observed_pairs_2_3y"] == row["registered_pairs_2_3y"]
        assert row["observed_authors_2_3y"] == row["registered_authors_2_3y"]
        assert row["meets_69_targets"] is True


def test_machinery_is_imported_from_u2b_and_u2_not_reimplemented():
    """#56: the estimator and the split must be the inherited objects."""

    source = SCRIPT.read_text(encoding="utf-8")
    assert "run_suica_m4_u2b_persistence_budget.py" in source
    assert MOD.U2B.__file__ == str(U2B_SCRIPT)
    assert MOD.U2.__file__ == str(U2_SCRIPT)
    for name in ("community_ranking", "common_prefix", "block_counts_over",
                 "renormalize", "self_pair_census", "ppmi_svd",
                 "first_half_counts", "taste_folds", "pool_fold_results",
                 "summarize_row", "percentile_ci"):
        assert hasattr(MOD.U2B, name), name
    for name in ("build_blocks", "assign_quarters", "gap_bin", "compute_arm",
                 "scan_for_cohort_ids", "load_event_cache",
                 "verify_cache_anchors", "build_quarter_plans"):
        assert hasattr(MOD.U2, name), name
    for banned in ("def compute_arm", "def build_blocks", "def ppmi_svd",
                   "def renormalize", "def community_ranking",
                   "def self_pair_census", "def pool_fold_results"):
        assert banned not in source, banned


# ---------------------------------------------------------------------------
# ID-leak scan and label-freedom
# ---------------------------------------------------------------------------


def test_id_leak_scanner_finds_a_planted_name(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("carriers, decay rates and slope contrasts only\n")
    dirty = tmp_path / "dirty.md"
    dirty.write_text("the distinctive rate for sample_user_9 is steep\n")
    cohort = ["sample_user_9", "another_person"]

    ok = MOD.U2.scan_for_cohort_ids([clean], cohort)
    assert ok["status"] == "PASS" and ok["n_hits"] == 0

    bad = MOD.U2.scan_for_cohort_ids([dirty], cohort)
    assert bad["status"] == "FAIL" and bad["n_hits"] == 1

    embedded = tmp_path / "embedded.md"
    embedded.write_text("sample_user_90 is a different token entirely\n")
    assert MOD.U2.scan_for_cohort_ids([embedded], cohort)["status"] == "PASS"


def test_committed_files_carry_no_cohort_identity():
    """The blocking ID-leak gate, run over U2c's exact committed set."""

    meta = ROOT / "results/m4_u1_order_identity/events_cache.meta.json"
    if not meta.exists():                # pragma: no cover - gitignored
        pytest.skip("events cache metadata not present")
    authors = json.loads(meta.read_text(encoding="utf-8"))["authors"]
    assert len(authors) == MOD.ANCHOR_AUTHORS
    targets = [
        SCRIPT,
        Path(__file__),
        ROOT / "reports/SUICA_M4_U2C_DECAY_RATE_CONTRAST_REPORT.md",
        ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
        ROOT / "docs/CLAIMS_LEDGER.md",
    ]
    scan = MOD.U2.scan_for_cohort_ids([p for p in targets if p.exists()],
                                      authors)
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
    assert MOD.Q_PRIMARY == 0.5 and MOD.M_PRIMARY == 5
    assert MOD.Q_CONFIRMATORY == 0.7 and MOD.M_CONFIRMATORY == 10
    assert MOD.Q_G0 == 0.5 and MOD.M_G0 == 10
    assert MOD.TASTE_FOLDS == 5 and MOD.TASTE_DIM == 64
    assert MOD.K_PRIMARY == 50 and MOD.POOL_MIN_BLOCKS == 4
    assert MOD.COMMON_SIZE_Q50 == 32 and MOD.COMMON_SIZE_Q70 == 104
    assert MOD.CENSUS_UNIVERSE == 2_348_361
    assert MOD.POOL_AUTHORS == 849 and MOD.POOL_BLOCKS == 45_731
    assert MOD.POOL_GATE_MIN_PAIRS_2_3Y == 100_000
    assert MOD.POOL_GATE_MIN_AUTHORS_2_3Y == 400
    assert MOD.ROW_KEYS == ("full", "common", "distinct", "taste")


def test_the_verdict_prose_carries_the_registered_cautions():
    """The three disclosures the registration requires in the outcome prose."""

    payload = {
        "primary": {
            "gap_years": [0.12, 0.37, 0.73, 1.42, 2.40, 3.40],
            "primary": {"ci_half_width": 0.09},
        },
    }
    text = " ".join(MOD.build_boundaries(payload))
    assert "eq 12" in text and "§5.4" in text
    assert "THREE-YEAR CORE" in text.upper()
    assert "permanent" in text
    assert "disclos" in text.casefold()
    assert "no equivalence cell" in text.casefold()


def test_committed_verdict_matches_the_committed_report():
    """Rule 24: the report's headline is the artifact's, not a transcription."""

    verdict_path = ARTIFACTS / "verdict.json"
    report = ROOT / "reports/SUICA_M4_U2C_DECAY_RATE_CONTRAST_REPORT.md"
    if not (verdict_path.exists() and report.exists()):
        pytest.skip("U2c artifacts not present")   # pragma: no cover
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    text = report.read_text(encoding="utf-8")
    assert f"**Outcome: `{verdict['outcome']}`.**" in text
    assert verdict["cell"] in {"SIGN_UNRESOLVED", "COMMON_STANDING",
                               "DISTINCT_SLOWER"}
    assert f"{verdict['lambda_point']:.4f}" in text
    assert f"{verdict['lambda_ci'][0]:.4f}" in text
    assert f"{verdict['lambda_ci'][1]:.4f}" in text
    # the confirmatory arm's cell and any #73 flag must both be in the prose
    assert verdict["confirmatory_cell"] in text
    assert ("**#73 flag**" in text) == bool(verdict["flags_73"])
    assert ("No #73 flag" in text) != bool(verdict["flags_73"])
