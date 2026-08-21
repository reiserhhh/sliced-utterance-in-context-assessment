"""M4-X3 -- the trait join of expression coordinates: contract tests.

X3 is the X line's ONLY label leg, so the properties that must hold are the
ones that make a stamped label join mean anything at all.

**The stamp chain must be provable, and must fail when violated.**  The whole
claim of this leg's discipline is that the config was fixed and the four
coordinates frozen BEFORE the label table was opened.  ``prove_stamp_order``
is driven directly on synthetic artifacts, in the good order and in every bad
one, including the two ways the order can be right while the stamp is a lie
(a joint quantity before the stamp, a label opened before the stamp).

**The gate must exclude, and must stop only on X3's rule.**  A coordinate
below the registered 0.50 is excluded LABEL-FREE and reported; unlike U3's
primary-keyed gate, X3 stops the leg ONLY if every coordinate falls.  Both
halves of that difference are pinned.

**The Mantel machinery must detect planted structure and must not invent it.**
A positive control, a null world, a REDUNDANT world (the coordinate reads the
bag's trait channel) against an INCREMENTAL one, and the author-cluster
bootstrap's own honesty in both worlds.

**The coordinate builder must be label-free BY CONSTRUCTION.**  Not by
inspection of the prose: the builder's only argument is a ``Sources`` whose
fields cannot carry a trait value, the module reads a CSV in exactly one
function, the inherited label reader is referenced in exactly one function,
and the whole builder runs to completion on a synthetic corpus with every
label reader in the process replaced by a landmine -- twice, bit-identically.

The rest pins the cell structure, the registered constants, the #83 helper
(baseline 4), the projection arithmetic and the report table's pipe safety.
"""
from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suica_m4_x3_trait_join.py"
U3_SCRIPT = ROOT / "scripts" / "run_suica_m4_u3_when_trait_join.py"
X2_SCRIPT = ROOT / "scripts" / "run_suica_m4_x2_volume_path.py"
X5_SCRIPT = ROOT / "scripts" / "run_suica_m4_x5_ergodicity_atlas.py"
X4_SCRIPT = ROOT / "scripts" / "run_suica_m4_x4_three_levels.py"
X1_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1_venue_response.py"
X1B_SCRIPT = ROOT / "scripts" / "run_suica_m4_x1b_venue_response_fe.py"
XM_SCRIPT = ROOT / "scripts" / "run_suica_m4_xm_mains_estimator.py"

# The #83 baseline: the pre-existing dictionary collisions the widened
# 10,296-name universe finds in the two APPEND-ONLY documents at HEAD.
BASELINE_HITS_EXPECTED = 4


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MOD = _load("m4_x3_trait_join", SCRIPT)
SOURCE = SCRIPT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def _functions_referencing(name: str) -> set[str]:
    """Every top-level function whose body mentions the bare name ``name``."""

    out: set[str] = set()
    for node in ast.walk(TREE):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Name) and inner.id == name:
                out.add(node.name)
            if (isinstance(inner, ast.Attribute) and inner.attr == name
                    and isinstance(inner.value, ast.Name)):
                out.add(node.name)
    return out


# ---------------------------------------------------------------------------
# 1.  The stamp chain (G-X3).
# ---------------------------------------------------------------------------
def _log(stamp: str, freeze: str, join: str, *, joint_before: int = 0,
         labels_before: bool = False) -> list[dict]:
    return [
        {"utc": "2026-08-19T00:00:00+00:00", "event": "part0_start"},
        {"utc": stamp, "event": "config_stamped", "sha256": "a" * 64,
         "joint_quantities_before_stamp": joint_before,
         "labels_opened_before_stamp": labels_before},
        {"utc": freeze, "event": "coordinates_frozen", "sha256": "b" * 64},
        {"utc": join, "event": "first_join"},
    ]


T1 = "2026-08-19T01:00:00+00:00"
T2 = "2026-08-19T02:00:00+00:00"
T3 = "2026-08-19T03:00:00+00:00"


def test_stamp_order_proof_passes_in_the_registered_order():
    proof = MOD.prove_stamp_order(_log(T1, T2, T3))
    assert proof["PASS"] is True
    assert proof["stamp_precedes_freeze_precedes_first_join"] is True
    assert proof["all_three_events_present"] is True
    assert proof["seconds_between"]["stamp_to_freeze"] == 3600.0
    assert proof["seconds_between"]["freeze_to_first_join"] == 3600.0


@pytest.mark.parametrize("stamp,freeze,join", [
    (T2, T1, T3),          # the freeze predates the stamp
    (T1, T3, T2),          # the join predates the freeze
    (T3, T2, T1),          # fully reversed
    (T2, T3, T1),          # the join predates the stamp
    (T1, T1, T3),          # the freeze is not strictly after the stamp
    (T1, T2, T2),          # the join is not strictly after the freeze
])
def test_stamp_order_proof_fails_when_the_order_is_violated(stamp, freeze,
                                                            join):
    proof = MOD.prove_stamp_order(_log(stamp, freeze, join))
    assert proof["stamp_precedes_freeze_precedes_first_join"] is False
    assert proof["PASS"] is False


def test_stamp_order_proof_fails_when_a_joint_quantity_preceded_the_stamp():
    proof = MOD.prove_stamp_order(_log(T1, T2, T3, joint_before=1))
    assert proof["stamp_precedes_freeze_precedes_first_join"] is True
    assert proof["PASS"] is False


def test_stamp_order_proof_fails_when_a_label_was_opened_before_the_stamp():
    proof = MOD.prove_stamp_order(_log(T1, T2, T3, labels_before=True))
    assert proof["stamp_precedes_freeze_precedes_first_join"] is True
    assert proof["PASS"] is False


@pytest.mark.parametrize("missing", ["config_stamped", "coordinates_frozen",
                                     "first_join"])
def test_stamp_order_proof_fails_when_an_event_is_missing(missing):
    records = [r for r in _log(T1, T2, T3) if r["event"] != missing]
    proof = MOD.prove_stamp_order(records)
    assert proof["all_three_events_present"] is False
    assert proof["PASS"] is False


def test_stamp_order_proof_reads_the_first_occurrence_of_each_event():
    records = _log(T1, T2, T3)
    records.append({"utc": "2026-08-19T00:30:00+00:00",
                    "event": "first_join"})
    assert MOD.prove_stamp_order(records)["first_join_utc"] == T3


def test_the_runner_truncates_the_log_so_a_prior_run_cannot_be_reused():
    src = inspect.getsource(MOD.stage_part0)
    assert 'run_log.jsonl").write_text("", encoding="utf-8")' in src


# ---------------------------------------------------------------------------
# 2.  The reliability gate -- U3's rows, X3's ALL-FAIL stop rule.
# ---------------------------------------------------------------------------
def test_reliability_gate_admits_above_and_excludes_below_the_threshold():
    gate = MOD.apply_reliability_gate({"raw_level": 0.90, "adj_level": 0.31,
                                       "rhythm": 0.64, "r2_slope": 0.54})
    assert gate["admitted"] == ["raw_level", "rhythm", "r2_slope"]
    assert gate["excluded"] == ["adj_level"]
    assert gate["rows"]["adj_level"]["gate"] == "EXCLUDE"
    assert gate["rows"]["raw_level"]["gate"] == "ADMIT"
    assert gate["STOP_before_join"] is False
    assert gate["stop_verdict"] is None


def test_reliability_gate_boundary_is_inclusive_and_nan_excludes():
    gate = MOD.apply_reliability_gate({"a": 0.50, "b": float("nan"),
                                       "c": 0.4999999})
    assert gate["rows"]["a"]["gate"] == "ADMIT"
    assert gate["rows"]["b"]["gate"] == "EXCLUDE"
    assert gate["rows"]["c"]["gate"] == "EXCLUDE"


def test_reliability_gate_stops_only_when_every_coordinate_fails():
    partial = MOD.apply_reliability_gate({"a": 0.10, "b": 0.51})
    assert partial["STOP_before_join"] is False
    every = MOD.apply_reliability_gate({"a": 0.10, "b": 0.49,
                                        "c": float("nan")})
    assert every["STOP_before_join"] is True
    assert every["stop_verdict"] == MOD.CELL_UNRELIABLE == \
        "COORDINATES_UNRELIABLE"
    assert every["admitted"] == []


def test_the_all_fail_stop_happens_before_the_stamp_is_written():
    """A1: the clean stop must be reachable with NO stamp on disk."""

    src = inspect.getsource(MOD.stage_part0)
    stop = src.index("RELIABILITY GATE: ALL COORDINATES FAILED")
    stamp = src.index('log.event("config_stamped"')
    assert stop < stamp, "the clean stop must precede the stamp write"
    assert "A1: no stamp written" in src


def test_the_gate_reports_the_registered_expectations_without_gating_on_them():
    gate = MOD.apply_reliability_gate({"rhythm": 0.10})
    assert gate["expectation"]["rhythm"] == MOD.RELIABILITY_EXPECTATION[
        "rhythm"] == 0.637
    assert gate["rows"]["rhythm"]["threshold"] == 0.50


def test_spearman_brown_is_the_inherited_full_length_formula():
    assert MOD.spearman_brown(0.5) == pytest.approx(2 / 3)
    assert MOD.spearman_brown(0.0) == 0.0
    assert np.isnan(MOD.spearman_brown(float("nan")))


# ---------------------------------------------------------------------------
# 3.  Mantel and the SLS partial on toy worlds.
# ---------------------------------------------------------------------------
def _world(n, rng, *, planted=0.0, bag_channel=0.0):
    """A toy world: traits, a coordinate, and a bag signature.

    ``planted`` couples the coordinate to trait 0 directly (an INCREMENTAL
    world); ``bag_channel`` couples the coordinate to a bag that is itself a
    function of trait 0 (a REDUNDANT world).
    """

    traits = rng.normal(size=(n, 5))
    bag_axis = traits[:, 0] + 0.3 * rng.normal(size=n)
    coord = (planted * traits[:, 0] + bag_channel * bag_axis
             + rng.normal(size=n))
    rows, cols = MOD.condensed_indices(n)
    diff = traits[rows] - traits[cols]
    trait_dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
    trait_square = MOD.square_from_condensed(trait_dist, rows, cols, n)
    x = np.abs(coord[rows] - coord[cols])
    bag = np.abs(bag_axis[rows] - bag_axis[cols])
    return rows, cols, x, trait_dist, trait_square, bag


def test_mantel_detects_planted_structure_positive_control():
    rng = np.random.default_rng(11)
    rows, cols, x, _, tsq, _ = _world(160, rng, planted=1.6)
    res = MOD.mantel_permutation(x, tsq, rows, cols, 160, 199, MOD.SEED)
    assert res["r"] > 0.10
    assert res["outside_band"] is True
    assert res["p_two_sided"] < 0.01


def test_mantel_does_not_detect_in_a_null_world():
    rng = np.random.default_rng(12)
    rows, cols, x, _, tsq, _ = _world(160, rng)
    res = MOD.mantel_permutation(x, tsq, rows, cols, 160, 199, MOD.SEED)
    assert abs(res["r"]) < 0.05
    assert res["outside_band"] is False
    assert res["p_two_sided"] > 0.05


def test_the_mantel_null_is_centred_and_its_band_brackets_the_null_mean():
    rng = np.random.default_rng(13)
    rows, cols, x, _, tsq, _ = _world(120, rng)
    res = MOD.mantel_permutation(x, tsq, rows, cols, 120, 399, MOD.SEED)
    assert abs(res["null_mean"]) < 0.02
    assert res["band_lo"] < res["null_mean"] < res["band_hi"]
    assert res["band_halfwidth"] > 0
    assert res["realized_mdr_1p96sd"] == pytest.approx(1.96 * res["null_sd"])


def test_the_row_permutation_preserves_the_moments_the_shortcut_assumes():
    """A row/column permutation is a bijection on unordered pairs."""

    rng = np.random.default_rng(14)
    n = 40
    rows, cols = MOD.condensed_indices(n)
    values = rng.normal(size=rows.size)
    square = MOD.square_from_condensed(values, rows, cols, n)
    for _ in range(20):
        perm = rng.permutation(n)
        permuted = square[perm[rows], perm[cols]]
        assert permuted.sum() == pytest.approx(values.sum())
        assert (permuted ** 2).sum() == pytest.approx((values ** 2).sum())


def test_mantel_r_equals_a_brute_force_pearson_on_the_same_pairs():
    rng = np.random.default_rng(15)
    rows, cols, x, trait_dist, tsq, _ = _world(50, rng, planted=0.8)
    res = MOD.mantel_permutation(x, tsq, rows, cols, 50, 9, MOD.SEED)
    assert res["r"] == pytest.approx(float(np.corrcoef(x, trait_dist)[0, 1]))
    assert res["n_pairs"] == rows.size == 50 * 49 // 2


def test_partial_mantel_kills_a_redundant_coupling():
    rng = np.random.default_rng(16)
    rows, cols, x, td, tsq, bag = _world(180, rng, bag_channel=1.8)
    raw = MOD.mantel_permutation(x, tsq, rows, cols, 180, 199, MOD.SEED)
    partial = MOD.partial_mantel_sls(x, td, bag[:, None], rows, cols, 180,
                                     199, MOD.SEED + 1)
    assert raw["outside_band"] is True
    assert abs(partial["r"]) < abs(raw["r"])
    assert partial["outside_band"] is False
    assert partial["method"].startswith("Smouse-Long-Sokal")


def test_partial_mantel_keeps_an_incremental_coupling():
    rng = np.random.default_rng(17)
    rows, cols, x, td, tsq, bag = _world(180, rng, planted=1.8)
    partial = MOD.partial_mantel_sls(x, td, bag[:, None], rows, cols, 180,
                                     199, MOD.SEED + 1)
    assert partial["outside_band"] is True
    assert partial["p_two_sided"] < 0.05


def test_partial_mantel_finds_nothing_in_a_null_world():
    rng = np.random.default_rng(18)
    rows, cols, x, td, _, bag = _world(180, rng)
    partial = MOD.partial_mantel_sls(x, td, bag[:, None], rows, cols, 180,
                                     199, MOD.SEED + 1)
    assert partial["outside_band"] is False


def test_partial_mantel_accepts_two_covariates_for_the_activity_row():
    rng = np.random.default_rng(19)
    rows, cols, x, td, _, bag = _world(120, rng)
    act = np.abs(rng.normal(size=rows.size))
    two = MOD.partial_mantel_sls(x, td, np.column_stack([bag, act]), rows,
                                 cols, 120, 99, MOD.SEED + 2)
    assert two["n_covariates"] == 2
    assert two["outside_band"] is False


def test_ols_residual_removes_exactly_the_linear_part():
    rng = np.random.default_rng(20)
    cov = rng.normal(size=(200, 2))
    y = 3.0 + 2.0 * cov[:, 0] - 1.5 * cov[:, 1] + 1e-9 * rng.normal(size=200)
    assert np.max(np.abs(MOD.ols_residual(y, cov))) < 1e-6


def test_square_from_condensed_round_trips_and_is_symmetric():
    rng = np.random.default_rng(21)
    n = 25
    rows, cols = MOD.condensed_indices(n)
    values = rng.normal(size=rows.size)
    square = MOD.square_from_condensed(values, rows, cols, n)
    assert np.array_equal(square, square.T)
    assert np.allclose(np.diag(square), 0.0)
    assert np.allclose(square[rows, cols], values)


# ---------------------------------------------------------------------------
# 4.  The author-cluster bootstrap on the Mantel r.
# ---------------------------------------------------------------------------
def test_the_cluster_bootstrap_excludes_zero_on_a_planted_world():
    rng = np.random.default_rng(22)
    rows, cols, x, _, tsq, _ = _world(150, rng, planted=2.0)
    xsq = MOD.square_from_condensed(x, rows, cols, 150)
    boot = MOD.cluster_bootstrap_mantel(xsq, tsq, 150, 200, MOD.SEED_BOOT)
    assert boot["ci_covers_zero"] is False
    assert boot["ci"][0] < boot["boot_mean"] < boot["ci"][1]
    assert boot["replicates_finite"] == 200


def test_the_cluster_bootstrap_covers_zero_in_a_null_world():
    rng = np.random.default_rng(23)
    rows, cols, x, _, tsq, _ = _world(150, rng)
    xsq = MOD.square_from_condensed(x, rows, cols, 150)
    boot = MOD.cluster_bootstrap_mantel(xsq, tsq, 150, 200, MOD.SEED_BOOT)
    assert boot["ci_covers_zero"] is True


def test_the_cluster_bootstrap_drops_the_self_pairs_it_says_it_drops():
    rng = np.random.default_rng(24)
    n = 60
    rows, cols, x, _, tsq, _ = _world(n, rng)
    xsq = MOD.square_from_condensed(x, rows, cols, n)
    boot = MOD.cluster_bootstrap_mantel(xsq, tsq, n, 50, MOD.SEED_BOOT)
    # a draw with replacement always repeats somebody, so every replicate must
    # carry strictly fewer pairs than the complete triangle
    assert boot["median_pairs_per_replicate"] < n * (n - 1) / 2
    assert boot["cluster"] == "author"


def test_the_cluster_bootstrap_is_deterministic_under_its_seed():
    rng = np.random.default_rng(25)
    rows, cols, x, _, tsq, _ = _world(80, rng, planted=1.0)
    xsq = MOD.square_from_condensed(x, rows, cols, 80)
    a = MOD.cluster_bootstrap_mantel(xsq, tsq, 80, 60, 7)
    b = MOD.cluster_bootstrap_mantel(xsq, tsq, 80, 60, 7)
    assert a["ci"] == b["ci"] and a["boot_mean"] == b["boot_mean"]


# ---------------------------------------------------------------------------
# 5.  The registered cell structure.
# ---------------------------------------------------------------------------
def _row(raw_hit: bool, partial_hit: bool = False) -> dict:
    return {"detected_raw": raw_hit,
            "partial_bag": {"outside_band": partial_hit}}


def test_cell_1_is_the_null_first_default():
    cells = MOD.classify({n: _row(False) for n in MOD.COORDINATES})
    assert cells["verdict"] == MOD.CELL_SILENT
    assert cells["cell"] == 1 and cells["suffix"] is None
    assert cells["verdict_with_suffix"] == "EXPRESSION_TRAIT_SILENT"


def test_cell_2_is_raw_level_only_with_the_dynamics_silent():
    cells = MOD.classify({"raw_level": _row(True), "adj_level": _row(False),
                          "rhythm": _row(False), "r2_slope": _row(False)})
    assert cells["verdict"] == MOD.CELL_LEVEL_ONLY and cells["cell"] == 2
    assert cells["suffix"] == "REDUNDANT"


def test_cell_3_is_both_levels_detecting():
    cells = MOD.classify({"raw_level": _row(True, True),
                          "adj_level": _row(True), "rhythm": _row(False),
                          "r2_slope": _row(False)})
    assert cells["verdict"] == MOD.CELL_LEVEL_INTRINSIC and cells["cell"] == 3
    assert cells["suffix"] == "INCREMENTAL"
    assert cells["off_menu_note"] is None


def test_cell_4_takes_precedence_over_any_level_pattern():
    for levels in ((False, False), (True, False), (True, True)):
        cells = MOD.classify({
            "raw_level": _row(levels[0]), "adj_level": _row(levels[1]),
            "rhythm": _row(False), "r2_slope": _row(True)})
        assert cells["verdict"] == MOD.CELL_DYNAMICS and cells["cell"] == 4


def test_the_adjusted_only_pattern_is_routed_and_disclosed():
    cells = MOD.classify({"raw_level": _row(False), "adj_level": _row(True),
                          "rhythm": _row(False), "r2_slope": _row(False)})
    assert cells["verdict"] == MOD.CELL_LEVEL_INTRINSIC
    assert cells["off_menu_note"] and "DISCLOSED" in cells["off_menu_note"]


def test_the_suffix_is_incremental_if_any_detecting_partial_is_outside():
    cells = MOD.classify({"raw_level": _row(True), "adj_level": _row(False),
                          "rhythm": _row(True, True), "r2_slope": _row(False)})
    assert cells["suffix"] == "INCREMENTAL"
    assert "(INCREMENTAL)" in cells["verdict_with_suffix"]


def test_a_missing_coordinate_row_never_invents_a_detection():
    cells = MOD.classify({"raw_level": _row(False)})
    assert cells["verdict"] == MOD.CELL_SILENT
    assert cells["dynamics_hits"] == [] and cells["level_hits"] == []


# ---------------------------------------------------------------------------
# 6.  LABEL-FREENESS BY CONSTRUCTION.
# ---------------------------------------------------------------------------
def test_the_module_reads_a_csv_in_exactly_one_function():
    readers = []
    for node in ast.walk(TREE):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "read_csv"):
                readers.append(node.name)
    assert readers == ["load_cohort_names"], readers
    assert "author" in inspect.getsource(MOD.load_cohort_names)
    for trait in MOD.BIG5:
        assert trait not in inspect.getsource(MOD.load_cohort_names)


def test_the_label_path_and_the_label_reader_live_in_one_place_each():
    # PROFILES is only OPENED by open_trait_table; the other mentions are
    # provenance strings, so the binding assertion is on the reader itself.
    # The label reader is named in exactly two places: its own delegating
    # wrapper, and the ONE stage that is allowed to call it.
    assert _functions_referencing("open_trait_table") == {
        "open_trait_table", "stage_stagee"}
    opener = inspect.getsource(MOD.open_trait_table)
    assert "U3.open_trait_table" in opener
    # and U3 itself is reached from exactly two functions: the label reader
    # and the gate wrapper -- everything else binds its symbols at import.
    assert _functions_referencing("U3") == {"open_trait_table",
                                            "apply_reliability_gate"}


def test_the_coordinate_builder_takes_no_label_argument():
    params = set(inspect.signature(MOD.build_coordinates).parameters)
    assert params == {"sources"}
    forbidden = set(MOD.BIG5) | {"traits", "trait", "labels", "label", "z",
                                 "big5", "profiles", "y_trait"}
    fields = set(MOD.Sources.__dataclass_fields__)
    assert not fields & forbidden
    for name in ("reproduction_checks", "source_agreement",
                 "apply_reliability_gate", "load_sources"):
        assert not set(inspect.signature(getattr(MOD, name)).parameters) \
            & forbidden


def _toy_sources(rng, n_authors=16, n_big5=10, per_author=140, n_subs=5):
    """A synthetic label-free corpus that exercises all four coordinates.

    ``n_big5`` is 10 so that every in-vocabulary community clears the largest
    censused support floor (s = 8) and the whole three-support census runs.
    """

    half = per_author // 2
    n_events = n_authors * per_author
    n_total = np.full(n_authors, per_author, dtype=np.int64)
    n_early = np.full(n_authors, half, dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(n_total))).astype(np.int64)
    who = np.repeat(np.arange(n_authors), per_author)
    level = rng.normal(0.0, 0.8, size=n_authors)
    volume = level[who] + rng.normal(size=n_events)
    gap = rng.normal(3.0, 1.2, size=n_events)
    volume += 0.25 * gap                       # a real R2 slope to recover
    x5 = {"pool_author_code": np.arange(n_authors, dtype=np.int64),
          "pool_is_big5": np.array([i < n_big5 for i in range(n_authors)]),
          "offsets": offsets, "n_early": n_early, "n_total": n_total,
          "ev_volume": volume, "ev_gap": gap}

    # the cell table the chain design reads: every Big5 author in every
    # in-vocabulary community, both halves
    cell_author, cell_comm, cell_half, cell_n, s_wcq, q_wcq = [], [], [], \
        [], [], []
    for a in range(n_big5):
        for c in range(n_subs - 1):            # the last community is OOV
            for h in (0, 1):
                mu = 3.0 + level[a] + 0.1 * c + 0.05 * h
                cell_author.append(a)
                cell_comm.append(c)
                cell_half.append(h)
                cell_n.append(20.0)
                s_wcq.append(20.0 * mu)
                q_wcq.append(20.0 * (mu * mu + 1.0))
    table = {"cell_author": np.array(cell_author, np.int64),
             "cell_comm": np.array(cell_comm, np.int64),
             "cell_half": np.array(cell_half, np.int64),
             "cell_n": np.array(cell_n, np.float64),
             "s_wcq": np.array(s_wcq, np.float64),
             "q_wcq": np.array(q_wcq, np.float64),
             "n_subs": n_subs}
    vocab_mask = np.array([True] * (n_subs - 1) + [False])
    names = [f"author_{i:03d}" for i in range(n_authors)]
    return MOD.Sources(
        x5=x5, x5_meta={"authors": names}, x2={}, x2_meta={"authors": names},
        table=table, scaffold={"authors": names}, cohort_names=names[:n_big5],
        big5_mask=np.array([i < n_big5 for i in range(n_authors)]),
        vocab={"mask": vocab_mask, "vocabulary_size": n_subs - 1,
               "floor_users": 0},
        author_names=names)


def test_the_builder_runs_with_every_label_reader_disarmed(monkeypatch):
    """A landmine in every label path must never be stepped on."""

    def landmine(*_a, **_k):                 # pragma: no cover - must not run
        raise AssertionError("a label column was opened in a label-free path")

    monkeypatch.setattr(MOD, "open_trait_table", landmine)
    monkeypatch.setattr(MOD.U3, "open_trait_table", landmine)
    monkeypatch.setattr(MOD.pd, "read_csv", landmine)
    monkeypatch.setattr(MOD.U3.pd, "read_csv", landmine)
    sources = _toy_sources(np.random.default_rng(101))
    coords = MOD.build_coordinates(sources)
    assert coords.label_data_in_inputs is False
    assert coords.pool_codes.size == 10
    assert set(coords.values) == set(MOD.COORDINATES)
    for name in MOD.COORDINATES:
        assert coords.values[name].size == 10
        assert coords.eligible[name].any(), name
    # the planted R2 slope comes back near 0.25 on the toy corpus
    assert coords.diagnostics["r2_slope"]["mean_beta"] == pytest.approx(
        0.25, abs=0.08)


def test_the_coordinates_are_deterministic():
    a = MOD.build_coordinates(_toy_sources(np.random.default_rng(102)))
    b = MOD.build_coordinates(_toy_sources(np.random.default_rng(102)))
    assert a.reliabilities == b.reliabilities
    for name in MOD.COORDINATES:
        assert np.array_equal(a.values[name], b.values[name],
                              equal_nan=True), name
        assert np.array_equal(a.eligible[name], b.eligible[name]), name
    assert a.chain_census == b.chain_census


def test_an_ineligible_author_is_nan_and_not_silently_zero():
    sources = _toy_sources(np.random.default_rng(103))
    # strip one Big5 author out of the chain entirely
    keep = sources.table["cell_author"] != 0
    for key in ("cell_author", "cell_comm", "cell_half", "cell_n", "s_wcq",
                "q_wcq"):
        sources.table[key] = sources.table[key][keep]
    coords = MOD.build_coordinates(sources)
    assert np.isnan(coords.values["adj_level"][0])
    assert coords.eligible["adj_level"][0] == np.False_
    assert coords.eligible["adj_level"].sum() == 9
    assert coords.eligible["raw_level"].all()


def test_the_chain_census_covers_the_three_registered_supports():
    coords = MOD.build_coordinates(_toy_sources(np.random.default_rng(104)))
    assert set(coords.chain_census) == {"3", "5", "8"}
    assert str(MOD.CHAIN_SUPPORT_PRIMARY) in coords.chain_census
    assert coords.diagnostics["adj_level"]["support_primary"] == 5


def test_the_reliability_of_a_reproducible_coordinate_is_high_on_the_toy():
    coords = MOD.build_coordinates(_toy_sources(np.random.default_rng(105)))
    assert coords.reliabilities["raw_level"] > 0.5
    assert coords.reliabilities["adj_level"] > 0.5


# ---------------------------------------------------------------------------
# 7.  Import provenance (#56/#81) -- the inherited object, not a copy.
# ---------------------------------------------------------------------------
def test_the_inherited_machinery_is_imported_not_copied():
    inherited = {
        "prove_stamp_order": U3_SCRIPT, "mantel_permutation": U3_SCRIPT,
        "partial_mantel_sls": U3_SCRIPT, "condensed_indices": U3_SCRIPT,
        "square_from_condensed": U3_SCRIPT, "full_signature": U3_SCRIPT,
        "projection_mdr": U3_SCRIPT, "pearson": U3_SCRIPT,
        "spearman_brown": U3_SCRIPT, "ols_residual": U3_SCRIPT,
        "arm_layout": X2_SCRIPT,
        "relation_stats": X5_SCRIPT, "event_author_and_half": X5_SCRIPT,
        "cell_moments": X4_SCRIPT, "per_cell_slopes": X4_SCRIPT,
        "build_chain_design": X1B_SCRIPT,
        "fitted_coefficients": XM_SCRIPT, "full_budget": XM_SCRIPT,
        "law_vocabulary": X1B_SCRIPT, "anchor_gate": X1_SCRIPT,
        "baseline_hit_keys": X1_SCRIPT, "new_hits_only": X1_SCRIPT,
    }
    for name, source in inherited.items():
        code = getattr(MOD, name).__code__
        assert Path(code.co_filename) == source, (name, code.co_filename)
    assert Path(MOD.Arm.__init__.__code__.co_filename) == X2_SCRIPT
    assert Path(MOD.RelationSkeleton.__init__.__code__.co_filename) \
        == X5_SCRIPT
    defined = {node.name for node in ast.walk(TREE)
               if isinstance(node, ast.FunctionDef)}
    assert not defined & set(inherited), defined & set(inherited)


def test_the_reliability_gate_wrapper_delegates_to_u3s_rows():
    src = inspect.getsource(MOD.apply_reliability_gate)
    assert "U3.apply_reliability_gate" in src


def test_the_r2_slope_uses_the_89_floor_the_registration_pins():
    assert MOD.X5.ESTIMABILITY_FLOOR_DEN == 1.0
    assert MOD.X5.POOL_FLOOR_EVENTS == 50
    assert MOD.X2.POOL_FLOOR_PRIMARY == 50


# ---------------------------------------------------------------------------
# 8.  #83 -- the ID-leak helper and its baseline.
# ---------------------------------------------------------------------------
def test_id_leak_helper_finds_a_planted_name_and_clears_a_clean_file(tmp_path):
    planted = tmp_path / "planted.md"
    planted.write_text("the author Zzyzx_Placeholder posted twice\n",
                       encoding="utf-8")
    clean = tmp_path / "clean.md"
    clean.write_text("1,116 pool authors, 1,100 slope-eligible, no names\n",
                     encoding="utf-8")
    cohort = ["Zzyzx_Placeholder", "Qqqq_Other_Placeholder"]
    assert MOD.scan_for_cohort_ids([planted], cohort)["status"] == "FAIL"
    assert MOD.scan_for_cohort_ids([clean], cohort)["status"] == "PASS"
    embedded = tmp_path / "embedded.md"
    embedded.write_text("Zzyzx_PlaceholderXYZ_is_another_token\n",
                        encoding="utf-8")
    assert MOD.scan_for_cohort_ids([embedded], cohort)["status"] == "PASS"


def test_new_hits_only_separates_a_head_baseline_from_a_fresh_leak(tmp_path):
    hits = [{"path": str(tmp_path / "doc.md"), "line": 58},
            {"path": str(tmp_path / "doc.md"), "line": 999}]
    baseline = {("doc.md", 58)}
    fresh = MOD.new_hits_only(hits, baseline)
    assert [h["line"] for h in fresh] == [999]
    assert MOD.new_hits_only(hits, {("doc.md", 58), ("doc.md", 999)}) == []


def test_the_committed_files_carry_no_new_cohort_name():
    """Blocking: 0 NEW hits over the widened 10,296-name universe."""

    meta = ROOT / "results/m4_x2_volume_path/event_cache.meta.json"
    cohort = MOD.DEFAULT_COHORT
    if not meta.exists() or not cohort.exists():
        pytest.skip("gitignored caches absent")
    names = json.loads(meta.read_text(encoding="utf-8"))["authors"]
    universe = sorted({str(n) for n in MOD.load_cohort_names(cohort)}
                      | {str(n) for n in names})
    assert len(universe) == MOD.ANCHOR_AUTHORS
    targets = [p for p in MOD.COMMITTED_FILES if p.exists()]
    scan = MOD.scan_for_cohort_ids(targets, universe)
    keys, detail = MOD.baseline_hit_keys(targets, universe,
                                         ROOT / "results/m4_x3_trait_join"
                                         / "head_baseline_test")
    assert detail["n_baseline_hits"] == BASELINE_HITS_EXPECTED, detail
    assert MOD.new_hits_only(scan["hits"], keys) == []


# ---------------------------------------------------------------------------
# 9.  The registered constants, the projection and the report mechanics.
# ---------------------------------------------------------------------------
def test_the_registration_constants_are_the_ones_the_plan_pins():
    assert MOD.SEED == 20260819
    assert MOD.B_PERM == 999 and MOD.B_BOOT == 1000
    assert MOD.RELIABILITY_GATE == 0.50
    assert MOD.REL_LABEL_DECLARED == 0.80
    assert MOD.LEAN_DYNAMICS_ABS_R == 0.03
    assert MOD.REGISTERED_MDR == 0.019
    assert MOD.REGISTRATION_COMMIT == "8823b60"
    assert MOD.COORDINATES == ("raw_level", "adj_level", "rhythm", "r2_slope")
    assert MOD.LEVEL_COORDINATES == ("raw_level", "adj_level")
    assert MOD.DYNAMICS_COORDINATES == ("rhythm", "r2_slope")
    assert set(MOD.BIG5) == {"agreeableness", "openness", "conscientiousness",
                             "extraversion", "neuroticism"}
    assert (MOD.CHAIN_N_MIN, MOD.CHAIN_SUPPORT_PRIMARY, MOD.CHAIN_K_MIN) \
        == (10, 5, 3)


def test_the_inherited_anchors_are_the_ones_the_line_carries():
    assert MOD.ANCHOR_ROWS_PARSEABLE == 17_640_062
    assert MOD.ANCHOR_AUTHORS == 10_296
    assert MOD.ANCHOR_BIG5_AUTHORS + MOD.ANCHOR_DISJOINT_AUTHORS \
        == MOD.ANCHOR_AUTHORS
    assert MOD.ANCHOR_LAW_VOCAB == 1_443
    assert MOD.ANCHOR_POOL_BIG5 == 1_116
    assert MOD.ANCHOR_R2_POOL_BIG5 == 1_100
    assert MOD.ANCHOR_POOL_BIG5 + MOD.ANCHOR_POOL_DISJOINT \
        == MOD.ANCHOR_CANDIDATES


def test_the_projection_reproduces_the_registrations_minimal_detectable_r():
    assert MOD.projection_mdr(MOD.ANCHOR_POOL_BIG5) == pytest.approx(
        MOD.REGISTERED_MDR, abs=0.0005)
    # the adjusted level's smaller support must be strictly less powerful
    assert MOD.projection_mdr(408) > MOD.projection_mdr(MOD.ANCHOR_POOL_BIG5)


def test_the_fisher_transform_is_two_sided_and_degrades_gracefully():
    assert MOD._fisher_two_sided_p(0.0, 1000) == pytest.approx(1.0)
    assert MOD._fisher_two_sided_p(0.5, 1000) < 1e-10
    assert MOD._fisher_two_sided_p(-0.5, 1000) == pytest.approx(
        MOD._fisher_two_sided_p(0.5, 1000))
    assert np.isnan(MOD._fisher_two_sided_p(0.5, 3))
    assert np.isnan(MOD._fisher_two_sided_p(float("nan"), 100))


def test_the_report_table_escapes_pipes_in_the_header_and_the_body():
    lines: list[str] = []
    MOD._table(lines.append, ["a | b", "c"], [["d | e", "f"]])
    assert lines[0] == "| a \\| b | c |"
    assert lines[2] == "| d \\| e | f |"
    assert lines[1] == "|---|---|"


def test_the_boundary_notes_carry_the_permanent_prohibitions():
    joined = " ".join(MOD.RN_NOTES.values()).lower()
    assert "no psychological naming" in joined
    assert "regardless of outcome" in joined
    assert "metadata only" in joined
    assert "cohort caveat" in joined
    assert "aggregates only" in " ".join(MOD.RN_NOTES.values()).lower() \
        or "no per-author trait value" in joined
    assert "no ratio null" in joined


def test_the_reproduction_anchors_are_the_committed_numbers():
    assert MOD.REPRO_X2_RHYTHM_RHO_OWN == 0.6366996180212687
    assert MOD.REPRO_X5_R2_RHO_OWN == 0.538039302428076
    assert MOD.REPRO_X5_R2_MEAN_BETA == 0.05203279700207156
    assert MOD.REPRO_XMB_AUTHOR_MAIN == 0.12858739914097542
    assert MOD.REPRO_XMB_CHAIN_S5 == {"authors": 3665, "communities": 1000,
                                      "shared_pairs": 31899}
    assert MOD.REPRO_TOL == 1e-9


def test_the_source_agreement_check_fails_when_the_universes_disagree():
    sources = _toy_sources(np.random.default_rng(106))
    sources.x5["pool_author_code"] = np.arange(16, dtype=np.int64)
    sources.x2 = {"pool_author_code": np.arange(15, dtype=np.int64),
                  "pool_is_big5": np.ones(15, bool)}
    sources.x5["pool_is_big5"] = np.ones(16, bool)
    assert MOD.source_agreement(sources)["status"] == "FAIL"
    sources.x2 = {"pool_author_code": np.arange(16, dtype=np.int64),
                  "pool_is_big5": np.ones(16, bool)}
    assert MOD.source_agreement(sources)["status"] == "PASS"


def test_the_stage_order_is_the_registered_one():
    assert MOD.STAGE_ORDER == ("part0", "stageb", "stagee", "gate",
                               "finalize", "report")
    assert set(MOD.STAGES) == set(MOD.STAGE_ORDER)


# ---------------------------------------------------------------------------
# 10.  The artifacts of the run (skipped in a fresh clone: results/ is ignored)
# ---------------------------------------------------------------------------
needs_run = pytest.mark.skipif(
    not (MOD.DEFAULT_OUTPUT / "verdict.json").exists(),
    reason="the leg has not been run in this working tree")


@needs_run
def test_the_run_proved_the_stamp_chain_from_its_own_artifacts():
    gate = json.loads((MOD.DEFAULT_OUTPUT / "gate.json").read_text("utf-8"))
    chain = gate["G-X3_stamp_chain"]
    assert chain["PASS"] is True
    assert chain["config_stamped_utc"] < chain["coordinate_freeze_utc"] \
        < chain["first_join_utc"]
    assert chain["joint_quantities_before_stamp"] == 0
    assert chain["labels_opened_before_stamp"] is False
    assert gate["hashes"]["config_hash_matches"] is True
    assert gate["hashes"]["coordinate_hash_matches"] is True
    assert gate["determinism"] == "PASS"
    assert gate["id_leak_scan"]["n_new_hits"] == 0
    assert gate["id_leak_scan"]["n_pre_existing"] == BASELINE_HITS_EXPECTED


@needs_run
def test_the_run_reproduced_every_inherited_value():
    part0 = json.loads((MOD.DEFAULT_OUTPUT / "part0.json").read_text("utf-8"))
    assert part0["G0"]["census"]["status"] == "PASS"
    assert part0["G0"]["reproductions"]["status"] == "PASS"
    assert part0["G0"]["source_agreement"]["status"] == "PASS"
    assert part0["G0"]["labels_opened_in_part0"] is False
    assert part0["G0"]["joint_quantities_in_part0"] == 0


@needs_run
def test_the_committed_artifacts_carry_no_per_author_trait_value():
    join = json.loads((MOD.DEFAULT_OUTPUT / "join.json").read_text("utf-8"))
    assert join["analysis_pool_label_completeness"]["n_pool"] == \
        MOD.ANCHOR_POOL_BIG5
    blob = MOD.DEFAULT_REPORT.read_text(encoding="utf-8")
    for trait in MOD.BIG5:
        # the trait NAMES may appear; a per-author row may not
        assert f"{trait}_of_" not in blob
    assert "author_profiles.csv" in blob          # the label event is named
    assert "AGGREGATES ONLY" in blob
