"""M4-U3 -- the Who x When trait join: contract tests.

U3 is the When line's FIRST LABEL LEG, so the properties that must hold are
the ones that make a stamped label join mean anything at all.

**The stamp chain must be provable, and must fail when violated.**  The whole
claim of this leg's discipline is that the config was fixed and the
coordinates frozen BEFORE the label table was opened.  ``prove_stamp_order``
is driven directly on synthetic artifacts, in the good order and in every bad
one, including the two ways the order can be right while the stamp is a lie
(a joint quantity before the stamp, a label opened before the stamp).

**The reliability gate must exclude, and must stop.**  A coordinate below the
registered 0.5 is excluded LABEL-FREE; if the PRIMARY coordinate falls, the
leg must stop before any join and name ``COORDINATE_UNRELIABLE``.

**The Mantel machinery must detect planted structure and must not invent it.**
A positive control, a null world, and -- the leg's actual question -- a
REDUNDANT world (the coordinate reads the bag's trait channel) against an
INCREMENTAL one (the coordinate carries trait information the bag does not).
The vectorised permutation is also checked against its own justification: a
row/column permutation of a symmetric matrix is a bijection on unordered
pairs, so the null denominator is constant.

**The state map must be label-free.**  Not by inspection of the prose but by
construction: the map builder's signature carries no label parameter, the
module reads a CSV in exactly one function, and the coordinate machinery runs
to completion with that function replaced by a landmine.

The rest pins the exact eligibility predicates (including RD-U3-1's
disclosed tightening), coordinate determinism, the projection arithmetic, the
disattenuation formula and the blocking ID-leak scan.
"""
from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_u3_when_trait_join.py"
U1_SCRIPT = ROOT / "scripts" / "run_suica_m4_u1_order_identity.py"
U2_SCRIPT = ROOT / "scripts" / "run_suica_m4_u2_persistence_curve.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_u3_when_trait_join", SCRIPT)
DAY = MOD.DAY


# ---------------------------------------------------------------------------
# 1.  The stamp chain (G-U3).
# ---------------------------------------------------------------------------
def _log(stamp: str, freeze: str, join: str, *, joint_before: int = 0,
         labels_before: bool = False) -> list[dict]:
    return [
        {"utc": "2026-08-18T00:00:00+00:00", "event": "part0_start"},
        {"utc": stamp, "event": "config_stamped", "sha256": "a" * 64,
         "joint_quantities_before_stamp": joint_before,
         "labels_opened_before_stamp": labels_before},
        {"utc": freeze, "event": "coordinates_frozen", "sha256": "b" * 64},
        {"utc": join, "event": "first_join"},
    ]


def test_stamp_order_proof_passes_in_the_registered_order():
    proof = MOD.prove_stamp_order(_log("2026-08-18T01:00:00+00:00",
                                       "2026-08-18T02:00:00+00:00",
                                       "2026-08-18T03:00:00+00:00"))
    assert proof["PASS"] is True
    assert proof["stamp_precedes_freeze_precedes_first_join"] is True
    assert proof["seconds_between"]["stamp_to_freeze"] == 3600.0
    assert proof["seconds_between"]["freeze_to_first_join"] == 3600.0


@pytest.mark.parametrize("stamp,freeze,join", [
    # the join precedes the freeze
    ("2026-08-18T01:00:00+00:00", "2026-08-18T03:00:00+00:00",
     "2026-08-18T02:00:00+00:00"),
    # the freeze precedes the stamp
    ("2026-08-18T02:00:00+00:00", "2026-08-18T01:00:00+00:00",
     "2026-08-18T03:00:00+00:00"),
    # the join precedes everything -- the violation the leg exists to exclude
    ("2026-08-18T02:00:00+00:00", "2026-08-18T03:00:00+00:00",
     "2026-08-18T01:00:00+00:00"),
    # simultaneous is not "before"
    ("2026-08-18T01:00:00+00:00", "2026-08-18T01:00:00+00:00",
     "2026-08-18T03:00:00+00:00"),
])
def test_stamp_order_proof_fails_when_order_is_violated(stamp, freeze, join):
    proof = MOD.prove_stamp_order(_log(stamp, freeze, join))
    assert proof["stamp_precedes_freeze_precedes_first_join"] is False
    assert proof["PASS"] is False


def test_stamp_order_proof_fails_when_a_joint_quantity_preceded_the_stamp():
    proof = MOD.prove_stamp_order(_log("2026-08-18T01:00:00+00:00",
                                       "2026-08-18T02:00:00+00:00",
                                       "2026-08-18T03:00:00+00:00",
                                       joint_before=1))
    assert proof["stamp_precedes_freeze_precedes_first_join"] is True
    assert proof["PASS"] is False


def test_stamp_order_proof_fails_when_a_label_was_opened_before_the_stamp():
    proof = MOD.prove_stamp_order(_log("2026-08-18T01:00:00+00:00",
                                       "2026-08-18T02:00:00+00:00",
                                       "2026-08-18T03:00:00+00:00",
                                       labels_before=True))
    assert proof["PASS"] is False


@pytest.mark.parametrize("missing", ["config_stamped", "coordinates_frozen",
                                     "first_join"])
def test_stamp_order_proof_fails_when_an_event_is_missing(missing):
    records = [r for r in _log("2026-08-18T01:00:00+00:00",
                               "2026-08-18T02:00:00+00:00",
                               "2026-08-18T03:00:00+00:00")
               if r["event"] != missing]
    proof = MOD.prove_stamp_order(records)
    assert proof["all_three_events_present"] is False
    assert proof["PASS"] is False


def test_stamp_order_proof_reads_the_first_occurrence_of_each_event():
    doubled = (_log("2026-08-18T01:00:00+00:00", "2026-08-18T02:00:00+00:00",
                    "2026-08-18T03:00:00+00:00")
               + _log("2026-08-18T09:00:00+00:00", "2026-08-18T08:00:00+00:00",
                      "2026-08-18T07:00:00+00:00"))
    proof = MOD.prove_stamp_order(doubled)
    assert proof["config_stamped_utc"] == "2026-08-18T01:00:00+00:00"
    assert proof["PASS"] is True


# ---------------------------------------------------------------------------
# 2.  The reliability gate.
# ---------------------------------------------------------------------------
def test_reliability_gate_admits_above_and_excludes_below_the_threshold():
    gate = MOD.apply_reliability_gate(
        {"stay_ct": 0.77, "tight": 0.89, "drift_pa": 0.42})
    assert gate["admitted"] == ["stay_ct", "tight"]
    assert gate["excluded"] == ["drift_pa"]
    assert gate["rows"]["drift_pa"]["gate"] == "EXCLUDE"
    assert gate["STOP_before_join"] is False
    assert gate["stop_verdict"] is None


def test_reliability_gate_stops_the_leg_when_the_primary_fails():
    gate = MOD.apply_reliability_gate(
        {"stay_ct": 0.31, "tight": 0.89, "drift_pa": 0.94})
    assert gate["primary_admitted"] is False
    assert gate["STOP_before_join"] is True
    assert gate["stop_verdict"] == "COORDINATE_UNRELIABLE"


def test_reliability_gate_boundary_is_inclusive_and_nan_excludes():
    gate = MOD.apply_reliability_gate(
        {"stay_ct": MOD.RELIABILITY_GATE, "tight": float("nan")})
    assert gate["rows"]["stay_ct"]["gate"] == "ADMIT"
    assert gate["rows"]["tight"]["gate"] == "EXCLUDE"


def test_spearman_brown_and_the_disattenuation_denominator():
    assert MOD.spearman_brown(0.5) == pytest.approx(2 / 3)
    assert MOD.spearman_brown(1.0) == pytest.approx(1.0)
    rel_sb = MOD.spearman_brown(0.7685)
    denom = float(np.sqrt(rel_sb * MOD.REL_LABEL_DECLARED))
    assert 0.1 / denom > 0.1               # disattenuation only inflates
    assert MOD.REL_LABEL_DECLARED == 0.80  # DECLARED, never measured


# ---------------------------------------------------------------------------
# 3.  Mantel and the SLS partial.
# ---------------------------------------------------------------------------
def _pairs(n):
    return MOD.condensed_indices(n)


def _trait_square(z, rows, cols, n):
    diff = z[rows] - z[cols]
    dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
    return MOD.square_from_condensed(dist, rows, cols, n), dist


def test_mantel_detects_planted_structure_positive_control():
    rng = np.random.default_rng(11)
    n = 90
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    z = c[:, None] * np.ones((1, 5)) / np.sqrt(5) + 0.35 * rng.normal(
        size=(n, 5))
    square, _ = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    result = MOD.mantel_permutation(x, square, rows, cols, n, 199, 7)
    assert result["r"] > 0.3
    assert result["outside_band"] is True
    assert result["p_two_sided"] <= 0.01


def test_mantel_does_not_detect_in_a_null_world():
    rng = np.random.default_rng(23)
    n = 90
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    z = rng.normal(size=(n, 5))              # independent of c
    square, _ = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    result = MOD.mantel_permutation(x, square, rows, cols, n, 499, 7)
    assert result["outside_band"] is False
    assert result["p_two_sided"] > 0.05
    assert abs(result["null_mean"]) < 0.02


def test_mantel_null_is_centred_and_its_band_brackets_the_null_mean():
    rng = np.random.default_rng(5)
    n = 60
    rows, cols = _pairs(n)
    z = rng.normal(size=(n, 5))
    square, _ = _trait_square(z, rows, cols, n)
    x = np.abs(rng.normal(size=n)[rows] - rng.normal(size=n)[cols])
    result = MOD.mantel_permutation(x, square, rows, cols, n, 499, 3)
    assert result["band_lo"] < result["null_mean"] < result["band_hi"]
    assert result["band_halfwidth"] > 0
    # the Bonferroni band is strictly wider than the 95% band
    assert result["bonferroni_band_lo"] <= result["band_lo"]
    assert result["bonferroni_band_hi"] >= result["band_hi"]


def test_permutation_preserves_the_condensed_moments_the_shortcut_assumes():
    """The vectorisation's justification, checked directly."""

    rng = np.random.default_rng(31)
    n = 40
    rows, cols = _pairs(n)
    z = rng.normal(size=(n, 5))
    square, dist = _trait_square(z, rows, cols, n)
    for _ in range(20):
        perm = rng.permutation(n)
        permuted = square[perm[rows], perm[cols]]
        assert permuted.sum() == pytest.approx(dist.sum())
        assert (permuted ** 2).sum() == pytest.approx((dist ** 2).sum())
        assert sorted(permuted) == pytest.approx(sorted(dist))


def test_mantel_r_equals_a_brute_force_pearson_on_the_same_pairs():
    rng = np.random.default_rng(41)
    n = 35
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    z = rng.normal(size=(n, 5))
    square, dist = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    result = MOD.mantel_permutation(x, square, rows, cols, n, 49, 1)
    assert result["r"] == pytest.approx(np.corrcoef(x, dist)[0, 1])
    assert result["n_pairs"] == n * (n - 1) // 2


def test_ols_residual_removes_exactly_the_linear_part():
    rng = np.random.default_rng(51)
    z = rng.normal(size=200)
    y = 3.0 + 2.0 * z
    assert np.allclose(MOD.ols_residual(y, z[:, None]), 0.0, atol=1e-9)
    resid = MOD.ols_residual(y + rng.normal(size=200), z[:, None])
    assert abs(float(np.corrcoef(resid, z)[0, 1])) < 1e-9


def test_partial_mantel_kills_a_redundant_coupling():
    """The coordinate reads the bag's trait channel through a scalar."""

    rng = np.random.default_rng(61)
    n = 100
    rows, cols = _pairs(n)
    latent = rng.normal(size=n)
    c = latent + 0.02 * rng.normal(size=n)
    z = latent[:, None] * np.ones((1, 5)) + 0.05 * rng.normal(size=(n, 5))
    _, trait = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    bag = np.abs(latent[rows] - latent[cols])
    raw = MOD.mantel_permutation(x, MOD.square_from_condensed(trait, rows,
                                                              cols, n),
                                 rows, cols, n, 199, 2)
    partial = MOD.partial_mantel_sls(x, trait, bag[:, None], rows, cols, n,
                                     199, 2)
    assert raw["r"] > 0.8 and raw["outside_band"] is True
    assert abs(partial["r"]) < 0.10
    assert partial["outside_band"] is False
    assert partial["method"].startswith("Smouse-Long-Sokal")


def test_the_sls_partial_controls_linearly_and_a_quadratic_row_exists():
    """A SHARED NON-LINEAR dependence on the covariate survives a linear
    control.  This is a property of the registered estimator, not a bug, so
    the runner also carries a quadratic second reading that routes nothing.

    The uniform-latent version of the redundant world above is exactly such a
    case: both distances hit the same noise floor at small covariate values.
    """

    rng = np.random.default_rng(61)
    n = 100
    rows, cols = _pairs(n)
    latent = rng.uniform(size=n)
    c = latent + 0.02 * rng.normal(size=n)
    z = latent[:, None] * np.ones((1, 5)) + 0.05 * rng.normal(size=(n, 5))
    _, trait = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    bag = np.abs(latent[rows] - latent[cols])
    linear = MOD.partial_mantel_sls(x, trait, bag[:, None], rows, cols, n,
                                    199, 2)
    quadratic = MOD.partial_mantel_sls(
        x, trait, np.column_stack([bag, bag ** 2]), rows, cols, n, 199, 2)
    assert linear["r"] > 0.2                    # the linear control leaks
    assert abs(quadratic["r"]) < abs(linear["r"])   # the quadratic row absorbs


def test_partial_mantel_keeps_an_incremental_coupling():
    """The coordinate carries trait information the bag does not."""

    rng = np.random.default_rng(71)
    n = 100
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    bag_latent = rng.normal(size=n)              # independent channel
    z = c[:, None] * np.ones((1, 5)) / np.sqrt(5) + 0.3 * rng.normal(
        size=(n, 5))
    _, trait = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    bag = np.abs(bag_latent[rows] - bag_latent[cols])
    partial = MOD.partial_mantel_sls(x, trait, bag[:, None], rows, cols, n,
                                     199, 2)
    assert partial["r"] > 0.3
    assert partial["outside_band"] is True
    assert partial["outside_bonferroni_band"] is True


def test_partial_mantel_finds_nothing_in_a_null_world():
    rng = np.random.default_rng(81)
    n = 90
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    z = rng.normal(size=(n, 5))
    _, trait = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    bag = np.abs(rng.normal(size=n)[rows] - rng.normal(size=n)[cols])
    partial = MOD.partial_mantel_sls(x, trait, bag[:, None], rows, cols, n,
                                     499, 2)
    assert partial["outside_band"] is False
    assert partial["p_two_sided"] > 0.05


def test_partial_mantel_accepts_two_covariates_for_the_activity_sensitivity():
    rng = np.random.default_rng(91)
    n = 70
    rows, cols = _pairs(n)
    c = rng.normal(size=n)
    z = rng.normal(size=(n, 5))
    _, trait = _trait_square(z, rows, cols, n)
    x = np.abs(c[rows] - c[cols])
    activity = np.log(rng.integers(50, 5000, size=n))
    covariates = np.column_stack([
        np.abs(rng.normal(size=n)[rows] - rng.normal(size=n)[cols]),
        np.abs(activity[rows] - activity[cols])])
    result = MOD.partial_mantel_sls(x, trait, covariates, rows, cols, n, 99, 2)
    assert result["n_covariates"] == 2
    assert np.isfinite(result["r"])


def test_square_from_condensed_round_trips_and_is_symmetric():
    rng = np.random.default_rng(101)
    n = 12
    rows, cols = _pairs(n)
    values = rng.normal(size=rows.size)
    square = MOD.square_from_condensed(values, rows, cols, n)
    assert np.allclose(square, square.T)
    assert np.allclose(np.diag(square), 0.0)
    assert np.allclose(square[rows, cols], values)


# ---------------------------------------------------------------------------
# 4.  The state map is label-free BY CONSTRUCTION.
# ---------------------------------------------------------------------------
def test_the_module_reads_a_csv_in_exactly_one_function():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    readers = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "read_csv"):
                readers.append(node.name)
    assert readers == ["open_trait_table"], readers


def test_the_map_builder_takes_no_label_argument():
    params = set(inspect.signature(MOD.build_global_state_map).parameters)
    forbidden = set(MOD.BIG5) | {"traits", "trait", "labels", "label", "z",
                                 "big5", "profiles"}
    assert not params & forbidden
    for name in ("cross_thread_stay", "block_coordinates", "full_signature",
                 "assign_halves"):
        assert not set(inspect.signature(getattr(MOD, name)).parameters) \
            & forbidden


def _toy_stream(rng, n_authors=14, n_vocab=9, per_author=140):
    author, sub, ts, link = [], [], [], []
    clock = 1_500_000_000.0
    for a in range(n_authors):
        favourite = rng.integers(n_vocab)
        for i in range(per_author):
            author.append(a)
            sub.append(favourite if rng.random() < 0.55
                       else int(rng.integers(n_vocab)))
            clock += float(rng.integers(600, 90_000))
            ts.append(clock)
            link.append(int(rng.integers(0, per_author // 3 + 1)))
    return (np.array(author, np.int32), np.array(sub, np.int32),
            np.array(ts, float), np.array(link, np.int32))


def test_the_map_and_the_coordinates_run_with_the_label_reader_disarmed(
        monkeypatch):
    """A landmine in the one label reader must never be stepped on."""

    def landmine(*_args, **_kwargs):        # pragma: no cover - must not run
        raise AssertionError("a label column was opened in a label-free path")

    monkeypatch.setattr(MOD, "open_trait_table", landmine)
    monkeypatch.setattr(MOD.pd, "read_csv", landmine)
    rng = np.random.default_rng(202)
    author, sub, ts, link = _toy_stream(rng)
    n_authors = int(author.max()) + 1
    n_vocab = int(sub.max()) + 1
    event_vocab = sub.astype(np.int32)
    early = MOD.assign_halves(author, ts, n_authors)
    pool = np.arange(n_authors)
    state_of_vocab, info = MOD.build_global_state_map(
        event_vocab, author, early, pool, n_vocab, n_states=3, seed=MOD.SEED)
    assert info["label_data_in_inputs"] is False
    assert info["oov_state_index"] == 3
    assert state_of_vocab[-1] == 3            # the OOV slot
    states = state_of_vocab[np.where(event_vocab >= 0, event_vocab, n_vocab)]
    values, counts = MOD.cross_thread_stay(author, link, states, n_authors)
    assert counts.sum() > 0
    assert np.all((values[np.isfinite(values)] >= 0)
                  & (values[np.isfinite(values)] <= 1))
    sig = MOD.full_signature(event_vocab, author, pool, n_vocab)
    assert np.allclose(np.linalg.norm(sig, axis=1), 1.0)


def test_the_global_map_is_deterministic_under_the_registered_seed():
    rng = np.random.default_rng(303)
    author, sub, ts, link = _toy_stream(rng)
    n_authors = int(author.max()) + 1
    n_vocab = int(sub.max()) + 1
    early = MOD.assign_halves(author, ts, n_authors)
    pool = np.arange(n_authors)
    first, _ = MOD.build_global_state_map(sub, author, early, pool, n_vocab,
                                          n_states=4, seed=MOD.SEED)
    second, _ = MOD.build_global_state_map(sub, author, early, pool, n_vocab,
                                           n_states=4, seed=MOD.SEED)
    assert np.array_equal(first, second)
    other, _ = MOD.build_global_state_map(sub, author, early, pool, n_vocab,
                                          n_states=4, seed=MOD.SEED + 1)
    assert other.shape == first.shape


def test_the_coordinates_are_deterministic():
    rng = np.random.default_rng(404)
    author, sub, ts, link = _toy_stream(rng, per_author=260)
    n_authors = int(author.max()) + 1
    n_vocab = int(sub.max()) + 1
    early = MOD.assign_halves(author, ts, n_authors)
    pool = np.arange(n_authors)
    state_of_vocab, _ = MOD.build_global_state_map(
        sub, author, early, pool, n_vocab, n_states=4, seed=MOD.SEED)
    states = state_of_vocab[sub]
    a1, c1 = MOD.cross_thread_stay(author, link, states, n_authors)
    a2, c2 = MOD.cross_thread_stay(author, link, states, n_authors)
    assert np.array_equal(np.nan_to_num(a1, nan=-1),
                          np.nan_to_num(a2, nan=-1))
    assert np.array_equal(c1, c2)
    blocks = MOD.build_blocks(author, ts, sub.astype(np.int32), n_vocab, 20,
                              n_authors=n_authors)
    first = MOD.block_coordinates(blocks.features, blocks.midpoint,
                                  blocks.author, pool, n_authors)
    second = MOD.block_coordinates(blocks.features, blocks.midpoint,
                                   blocks.author, pool, n_authors)
    assert np.array_equal(np.nan_to_num(first.tight, nan=-9),
                          np.nan_to_num(second.tight, nan=-9))
    assert np.array_equal(np.nan_to_num(first.drift, nan=-9),
                          np.nan_to_num(second.drift, nan=-9))
    assert np.array_equal(first.tight_pairs, second.tight_pairs)


# ---------------------------------------------------------------------------
# 5.  stay_ct's exact definition.
# ---------------------------------------------------------------------------
def test_stay_counts_only_cross_thread_adjacencies():
    author = np.zeros(4, np.int32)
    states = np.array([1, 1, 2, 2], np.int32)
    same_thread = np.array([7, 7, 7, 7], np.int32)
    values, counts = MOD.cross_thread_stay(author, same_thread, states, 1)
    assert counts[0] == 0 and np.isnan(values[0])
    alternating = np.array([1, 2, 3, 4], np.int32)
    values, counts = MOD.cross_thread_stay(author, alternating, states, 1)
    assert counts[0] == 3                       # 1-1, 1-2, 2-2
    assert values[0] == pytest.approx(2 / 3)    # the middle pair changes state


def test_stay_never_splices_across_an_oov_event():
    """OOV is a STATE, not a hole: the chain keeps its length."""

    author = np.zeros(3, np.int32)
    link = np.array([1, 2, 3], np.int32)
    oov = MOD.C_STATES
    states = np.array([5, oov, 5], np.int32)
    values, counts = MOD.cross_thread_stay(author, link, states, 1)
    assert counts[0] == 2                       # two adjacencies, not one
    assert values[0] == pytest.approx(0.0)      # and neither of them stays


def test_stay_never_pairs_across_authors():
    author = np.array([0, 0, 1, 1], np.int32)
    link = np.array([1, 2, 3, 4], np.int32)
    states = np.array([3, 3, 3, 3], np.int32)
    _, counts = MOD.cross_thread_stay(author, link, states, 2)
    assert counts.tolist() == [1, 1]


def test_stay_restriction_selects_pairs_with_both_events_inside():
    author = np.zeros(4, np.int32)
    link = np.array([1, 2, 3, 4], np.int32)
    states = np.array([1, 1, 1, 1], np.int32)
    restrict = np.array([True, True, False, False])
    _, counts = MOD.cross_thread_stay(author, link, states, 1,
                                      restrict=restrict)
    assert counts[0] == 1                       # only the first pair survives


def test_halves_follow_the_full_stream_median_with_the_boundary_early():
    author = np.zeros(5, np.int32)
    ts = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    early = MOD.assign_halves(author, ts, 1)
    assert early.tolist() == [True, True, True, False, False]


# ---------------------------------------------------------------------------
# 6.  The block coordinates.
# ---------------------------------------------------------------------------
def test_block_coordinates_on_a_hand_built_case():
    features = np.array([[1.0, 0.0], [1.0, 0.0], [0.6, 0.8], [0.0, 1.0]])
    midpoint = np.array([0.0, 10.0, 20.0, 500.0]) * DAY
    block_author = np.zeros(4, np.int32)
    out = MOD.block_coordinates(features, midpoint, block_author, [0], 1)
    # consecutive gaps 10 d, 10 d, 480 d -> the first two qualify for tight
    assert out.tight_pairs[0] == 2
    assert out.tight[0] == pytest.approx((1.0 + 0.6) / 2)
    # all six pairs: gaps 10, 20, 500 / 10, 490 / 480
    assert out.near_pairs[0] == 3 and out.far_pairs[0] == 3
    near_mean = (1.0 + 0.6 + 0.6) / 3           # (0,1), (0,2), (1,2)
    far_mean = (0.0 + 0.0 + 0.8) / 3            # (0,3), (1,3), (2,3)
    assert out.drift[0] == pytest.approx(near_mean - far_mean)


def test_block_coordinate_odd_even_splits_partition_the_pair_lists():
    rng = np.random.default_rng(505)
    features = rng.normal(size=(9, 4))
    features /= np.linalg.norm(features, axis=1, keepdims=True)
    midpoint = np.arange(9) * 30.0 * DAY
    out = MOD.block_coordinates(features, midpoint, np.zeros(9, np.int32),
                                [0], 1)
    assert out.tight_pairs[0] == 8              # every consecutive gap is 30 d
    assert np.isfinite(out.tight_odd[0]) and np.isfinite(out.tight_even[0])
    # the two split means average back to the full mean when the split is even
    assert (out.tight_odd[0] + out.tight_even[0]) / 2 == pytest.approx(
        out.tight[0])


def test_drift_needs_both_cells_and_is_nan_otherwise():
    features = np.eye(3)[:, :3].astype(float)
    midpoint = np.array([0.0, 5.0, 10.0]) * DAY     # no far pairs at all
    out = MOD.block_coordinates(features, midpoint, np.zeros(3, np.int32),
                                [0], 1)
    assert out.far_pairs[0] == 0
    assert np.isnan(out.drift[0])


# ---------------------------------------------------------------------------
# 7.  The eligibility predicates (exact, #77/#78) and RD-U3-1.
# ---------------------------------------------------------------------------
def test_stay_predicate_is_the_disclosed_strict_form():
    early = np.array([29, 30, 31, 100])
    late = np.array([100, 100, 100, 30])
    pool = np.arange(4)
    strict = MOD.stay_eligible(early, late, pool)
    loose = MOD.stay_eligible(early, late, pool, strict=False)
    assert strict.tolist() == [2]               # only min > 30
    assert loose.tolist() == [1, 2, 3]          # min >= 30
    assert MOD.STAY_PREDICATE_STRICT is True
    assert MOD.STAY_MIN_ADJ_PER_HALF == 30


def test_tight_and_drift_predicates_use_the_registered_floors():
    assert MOD.TIGHT_MIN_PAIRS == 2 and MOD.TIGHT_GAP_DAYS == 90.0
    assert MOD.DRIFT_MIN_PAIRS == 3
    assert MOD.DRIFT_NEAR_DAYS == 180.0 and MOD.DRIFT_FAR_DAYS == 365.0
    pairs = np.array([0, 1, 2, 5])
    assert MOD.tight_eligible(pairs, np.arange(4)).tolist() == [2, 3]
    near = np.array([3, 3, 2, 9])
    far = np.array([3, 2, 3, 9])
    assert MOD.drift_eligible(near, far, np.arange(4)).tolist() == [0, 3]


def test_the_registered_census_pins_are_the_ones_the_runner_gates_on():
    assert MOD.CENSUS_PINS == {"block_pool_ge4_blocks": 849,
                               "stay_eligible": 847, "tight_eligible": 763,
                               "drift_eligible": 652}
    assert (MOD.ANCHOR_EVENTS, MOD.ANCHOR_AUTHORS, MOD.ANCHOR_VOCAB) == (
        3_005_360, 1401, 1191)


# ---------------------------------------------------------------------------
# 8.  The registered projection arithmetic.
# ---------------------------------------------------------------------------
def test_the_projection_reproduces_the_registrations_minimal_detectable_r():
    assert MOD.projection_mdr(849) == pytest.approx(MOD.REGISTERED_MDR,
                                                    abs=5e-4)
    assert MOD.projection_mdr(847) == pytest.approx(MOD.REGISTERED_MDR,
                                                    abs=5e-4)
    # z ~ r*sqrt(N): a four-fold pool halves the detectable r
    assert MOD.projection_mdr(4 * 849) == pytest.approx(
        MOD.projection_mdr(849) / 2)
    assert (MOD.SR1_R, MOD.SR1_Z, MOD.SR1_N) == (0.049, 5.42, 1306)


# ---------------------------------------------------------------------------
# 9.  Governance: the ID-leak helper and the inherited-machinery chain (#56).
# ---------------------------------------------------------------------------
def test_id_leak_helper_finds_a_planted_name_and_clears_a_clean_file(tmp_path):
    planted = tmp_path / "planted.md"
    planted.write_text("the author QuietSeedling posted twice\n",
                       encoding="utf-8")
    clean = tmp_path / "clean.md"
    clean.write_text("849 authors, 847 stay-eligible, no names\n",
                     encoding="utf-8")
    cohort = ["QuietSeedling", "OtherPerson"]
    assert MOD.scan_for_cohort_ids([planted], cohort)["status"] == "FAIL"
    assert MOD.scan_for_cohort_ids([clean], cohort)["status"] == "PASS"
    # a substring inside a longer token is NOT a leak
    embedded = tmp_path / "embedded.md"
    embedded.write_text("QuietSeedlingXYZ_is_a_different_token\n",
                        encoding="utf-8")
    assert MOD.scan_for_cohort_ids([embedded], cohort)["status"] == "PASS"


def test_the_committed_report_and_sources_carry_no_cohort_name():
    """Blocking: 0 of the 1401 cohort names may appear in a committed file."""

    cache = MOD.DEFAULT_CACHE
    if not cache.exists():
        pytest.skip("events cache absent")
    names = MOD.load_event_cache(cache).authors
    targets = [SCRIPT, Path(__file__), MOD.DEFAULT_REPORT, MOD.PLAN_DOC,
               MOD.LEDGER]
    scan = MOD.scan_for_cohort_ids([p for p in targets if p.exists()], names)
    assert scan["status"] == "PASS", scan["hits"]


def test_the_inherited_machinery_is_imported_not_copied():
    inherited = {"spherical_kmeans": U1_SCRIPT, "build_blocks": U2_SCRIPT,
                 "load_event_cache": U2_SCRIPT,
                 "verify_cache_anchors": U2_SCRIPT,
                 "scan_for_cohort_ids": U2_SCRIPT}
    for name, source in inherited.items():
        code = getattr(MOD, name).__code__
        assert Path(code.co_filename) == source, (name, code.co_filename)
    # and U3 does not shadow any of them with a local copy
    defined = {node.name for node in
               ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8")))
               if isinstance(node, ast.FunctionDef)}
    assert not defined & set(inherited)


def test_the_registration_constants_are_the_ones_the_plan_pins():
    assert MOD.SEED == 20260818
    assert MOD.B_PERM == 999
    assert MOD.C_STATES == 24 and MOD.KMEANS_N_INIT == 10
    assert MOD.K_BLOCK == 50 and MOD.POOL_MIN_BLOCKS == 4
    assert MOD.RELIABILITY_GATE == 0.50
    assert MOD.PRIMARY_COORDINATE == "stay_ct"
    assert MOD.N_SECONDARY_ROWS == 3
    assert MOD.LEAN_RAW_POINT == 0.03
    assert MOD.REGISTRATION_COMMIT == "921fe86"
    assert set(MOD.BIG5) == {"agreeableness", "openness", "conscientiousness",
                             "extraversion", "neuroticism"}


def test_section_5_4_and_the_drift_caution_are_carried_in_the_notes():
    joined = " ".join(MOD.RN_NOTES.values()).lower()
    assert "no psychological naming" in joined
    assert "moving targets" in joined
    assert "declared" in joined
