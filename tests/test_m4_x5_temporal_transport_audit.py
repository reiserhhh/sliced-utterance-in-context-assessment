"""Contract tests for the post-closure X5 temporal transport audit."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_suica_m4_x5_temporal_transport_audit.py"
SPEC = importlib.util.spec_from_file_location("x5_temporal_audit_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def toy_cache(n_authors: int = 2, events_per_author: int = 16):
    """A cache with equal early/late event counts and two numeric channels."""

    total = n_authors * events_per_author
    offsets = np.arange(n_authors + 1, dtype=np.int64) * events_per_author
    x = np.tile(np.arange(events_per_author, dtype=float), n_authors)
    y = 2.0 * x + np.repeat(np.arange(n_authors, dtype=float), events_per_author)
    return {
        "offsets": offsets,
        "n_early": np.full(n_authors, events_per_author // 2, dtype=np.int64),
        "n_total": np.full(n_authors, events_per_author, dtype=np.int64),
        "ev_x": x,
        "ev_y": y,
    }


def test_segment_requirements_scale_the_original_half_floor():
    assert MOD.segment_requirements(2) == (50, 1.0)
    assert MOD.segment_requirements(4) == (25, 0.5)
    assert MOD.segment_requirements(8) == (13, 0.25)


def test_master_segments_are_nested_and_preserve_the_original_halves():
    cache = toy_cache(n_authors=1)
    usable = np.ones(16, dtype=bool)
    segments = MOD.assign_master_segments(cache, usable)
    assert segments.tolist() == [0, 0, 1, 1, 2, 2, 3, 3,
                                 4, 4, 5, 5, 6, 6, 7, 7]
    assert np.all(segments[:8] < 4)
    assert np.all(segments[8:] >= 4)


def test_master_segments_ignore_unusable_events_without_reordering():
    cache = toy_cache(n_authors=1)
    usable = np.ones(16, dtype=bool)
    usable[[1, 6, 9, 14]] = False
    segments = MOD.assign_master_segments(cache, usable)
    assert np.all(segments[~usable] == -1)
    assert np.all(np.diff(segments[usable][:6]) >= 0)
    assert np.all(np.diff(segments[usable][6:]) >= 0)


def test_segment_moments_match_direct_two_pass_calculation():
    cache = toy_cache()
    who = np.repeat(np.arange(2, dtype=np.int32), 16)
    usable = np.ones(32, dtype=bool)
    segments = MOD.assign_master_segments(cache, usable)
    relation = SimpleNamespace(x="x", y="y")
    moments = MOD.segment_moments(cache, relation, who, usable, segments, 8)
    assert moments["n"].shape == (2, 8)
    assert np.all(moments["n"] == 2)
    for author in range(2):
        for segment in range(8):
            start = author * 16 + segment * 2
            stop = start + 2
            x = cache["ev_x"][start:stop]
            y = cache["ev_y"][start:stop]
            assert np.isclose(moments["den"][author, segment],
                              np.sum((x - x.mean()) ** 2))
            assert np.isclose(moments["num"][author, segment],
                              np.sum((x - x.mean()) * (y - y.mean())))


def test_point_estimates_separate_between_and_within_slopes():
    authors, k = 6, 4
    n = np.full((authors, k), 10.0)
    xbar = np.arange(authors, dtype=float)[:, None] + np.arange(k)[None, :]
    ybar = 2.0 * xbar + 3.0
    moments = {
        "n": n,
        "sx": xbar * n,
        "sy": ybar * n,
        "den": np.full((authors, k), 5.0),
        "num": np.full((authors, k), 15.0),
    }
    result = MOD.point_estimates(moments, np.ones(authors, dtype=bool))
    assert np.allclose(result["between"], 2.0)
    assert np.allclose(result["within"], 3.0)
    assert np.allclose(result["delta"], -1.0)


def test_r1_original_pool_refuses_an_approximate_reconstruction():
    moments = {
        "n": np.full((2, 2), 50.0),
        "den": np.full((2, 2), 1.0),
    }
    try:
        MOD.original_pool(moments, "R1")
    except ValueError as exc:
        assert "frozen X4 cache mask" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("R1 must not silently use den > 0")


def test_bootstrap_is_paired_deterministic_and_has_expected_shape():
    authors, k = 20, 2
    xbar = np.arange(authors, dtype=float)[:, None] + np.array([[0.0, 1.0]])
    ybar = 1.5 * xbar + np.linspace(-0.2, 0.2, authors)[:, None]
    estimates = {
        "xbar": xbar,
        "ybar": ybar,
        "num": np.full((authors, k), 2.0),
        "den": np.full((authors, k), 1.0),
    }
    first = MOD.bootstrap_estimates(estimates, 25, 77)
    second = MOD.bootstrap_estimates(estimates, 25, 77)
    for key in ("between", "within", "delta"):
        assert first[key].shape == (25, k)
        assert np.array_equal(first[key], second[key])
    assert np.allclose(first["delta"], first["between"] - first["within"])


def test_temporal_classification_uses_simultaneous_intervals_and_margin():
    equivalent = {
        "contrast": np.array([0.004, -0.004]),
        "intervals": np.array([[-0.010, 0.018], [-0.018, 0.010]]),
    }
    detected = {
        "contrast": np.array([0.031, -0.031]),
        "intervals": np.array([[0.021, 0.041], [-0.041, -0.021]]),
    }
    unresolved = {
        "contrast": np.array([0.025, -0.025]),
        "intervals": np.array([[-0.005, 0.050], [-0.050, 0.005]]),
    }
    assert MOD.temporal_classification(equivalent) == MOD.CLASS_EQUIV
    assert MOD.temporal_classification(detected) == MOD.CLASS_HET
    assert MOD.temporal_classification(unresolved) == MOD.CLASS_UNRESOLVED


def test_transport_family_requires_gap_and_detected_slope_signs():
    positive = (0.1, 0.2)
    negative = (-0.2, -0.1)
    crossing = (-0.1, 0.1)
    assert MOD.transport_family(0.2, -0.1, positive, negative, positive) == MOD.FAMILY_SIGN_FLIP
    assert MOD.transport_family(0.2, 0.1, positive, positive, positive) == MOD.FAMILY_SAME_SIGN
    assert MOD.transport_family(0.2, 0.0, positive, crossing, positive) == MOD.FAMILY_SIGN_UNRESOLVED
    assert MOD.transport_family(0.2, -0.1, positive, negative, crossing) == MOD.FAMILY_GAP_UNRESOLVED


def test_historical_labels_map_to_the_registered_four_families():
    assert MOD.historical_family("NONERGODIC_SIGN_FLIP") == MOD.FAMILY_SIGN_FLIP
    assert MOD.historical_family("NONERGODIC_SAME_SIGN") == MOD.FAMILY_SAME_SIGN
    assert MOD.historical_family("NONERGODIC_SIGN_UNRESOLVED") == MOD.FAMILY_SIGN_UNRESOLVED
    assert MOD.historical_family("LEVELS_INDISTINGUISHABLE") == MOD.FAMILY_GAP_UNRESOLVED


def test_trend_uses_the_registered_floor_in_its_normalization():
    raw, normalized = MOD.trend_statistics(np.array([-0.01, 0.01]))
    assert np.isclose(raw, 0.01)
    assert np.isclose(normalized, 0.5)


def test_drift_energy_decomposition_is_exact_and_reports_cancellation():
    between = np.array([0.0, 1.0, 2.0])
    within = np.array([0.0, 0.5, 1.0])
    result = MOD.drift_energy_decomposition(between, within)
    assert result["identity_error"] < 1e-12
    assert np.isclose(
        result["between_energy_ratio"]
        + result["within_energy_ratio"]
        + result["cross_energy_ratio"],
        1.0,
    )
    assert result["cross_energy"] < 0.0
    assert np.isclose(result["between_within_path_correlation"], 1.0)


def test_drift_energy_decomposition_rejects_mismatched_paths():
    try:
        MOD.drift_energy_decomposition([0.0, 1.0], [0.0])
    except ValueError as exc:
        assert "equal-length" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("mismatched paths must not be silently broadcast")


def test_protocol_commit_and_governance_are_pinned():
    source = SCRIPT.read_text(encoding="utf-8")
    protocol = MOD.PROTOCOL.read_text(encoding="utf-8")
    assert MOD.PROTOCOL_COMMIT == "b0b38c2"
    assert "REGISTERED_NOT_RUN" in protocol
    assert "K\\in\\{2,4,8\\}" in protocol
    assert "author_profiles.csv" not in source
    assert "usecols" not in source
    assert "event_cache.npz" in source
