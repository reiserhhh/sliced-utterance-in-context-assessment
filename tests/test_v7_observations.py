from __future__ import annotations

import pandas as pd

from suica_core.v7_observations import (
    ObservationSpec,
    build_observations,
    cap_author_source_comments,
    canonicalize_comments,
    deterministic_author_split,
    observation_manifest,
    prepare_source_panel,
    select_reference_authors,
)


def _raw_comments() -> pd.DataFrame:
    rows = []
    for user in range(30):
        for comment in range(12):
            rows.append({
                "author": f"u{user:02d}",
                "body": (
                    f"This is comment {comment} from author {user}. "
                    "It contains enough ordinary words to create a valid observation. "
                    "Another sentence gives the semantic operator a natural boundary."
                ),
                "created_utc": float(comment + user * 100),
                "subreddit": "alpha" if comment % 2 else "beta",
            })
    return pd.DataFrame(rows)


def test_canonicalization_and_reference_selection_preserve_author_grouping() -> None:
    canonical = canonicalize_comments(_raw_comments(), min_tokens=8)
    selected = select_reference_authors(canonical, min_comments_per_user=12, max_users=20, seed=9)
    assert selected["user_id"].nunique() == 20
    assert set(selected["split"]).issubset({"discovery", "calibration", "confirmation"})
    assert deterministic_author_split("u01", seed=9) == deterministic_author_split("u01", seed=9)
    assert selected.groupby("user_id")["order"].apply(lambda values: values.is_monotonic_increasing).all()
    fresh = select_reference_authors(
        canonical, min_comments_per_user=12, max_users=20, seed=9,
        exclude_user_ids={"u00", "u01"}, cohort_salt="fresh",
    )
    assert not {"u00", "u01"}.intersection(set(fresh["user_id"]))


def test_observation_operators_build_distinct_repeated_units() -> None:
    canonical = canonicalize_comments(_raw_comments(), min_tokens=8)
    selected = select_reference_authors(canonical, min_comments_per_user=12, max_users=20, seed=2)
    specs = [
        ObservationSpec(name="whole", kind="whole", min_tokens=8, max_units_per_user=12),
        ObservationSpec(name="native", kind="native", min_tokens=8, max_units_per_user=12),
        ObservationSpec(name="fixed", kind="fixed", min_tokens=8, max_units_per_user=12, window_tokens=32, stride_tokens=32),
        ObservationSpec(name="semantic", kind="semantic", min_tokens=8, max_units_per_user=12, max_tokens=40),
    ]
    outputs = {spec.name: build_observations(selected, spec) for spec in specs}
    assert outputs["whole"].groupby("user_id").size().eq(1).all()
    assert outputs["native"].groupby("user_id").size().min() >= 2
    assert outputs["fixed"].groupby("user_id").size().min() >= 2
    assert outputs["semantic"].groupby("user_id").size().min() >= 2
    manifest = observation_manifest(selected, outputs["native"], specs[1])
    assert manifest["n_users"] == 20
    assert manifest["support_summary"]["median_units_per_user"] >= 2


def test_nested_operator_is_not_misrepresented_as_raw_slicing() -> None:
    canonical = canonicalize_comments(_raw_comments(), min_tokens=8)
    selected = select_reference_authors(canonical, min_comments_per_user=12, max_users=20, seed=2)
    nested = ObservationSpec(name="nested", kind="nested", members=("native", "fixed"))
    try:
        build_observations(selected, nested)
    except ValueError as error:
        assert "Nested operators" in str(error)
    else:
        raise AssertionError("Nested operator must be constructed from base author features.")


def test_source_comment_cap_is_distinct_from_output_unit_cap() -> None:
    canonical = canonicalize_comments(_raw_comments(), min_tokens=8)
    canonical["split"] = "discovery"
    capped = cap_author_source_comments(canonical, max_comments_per_user=3)
    assert capped.groupby("user_id").size().eq(3).all()
    spec = ObservationSpec(
        name="native", kind="native", min_tokens=8, max_units_per_user=12,
        max_source_comments_per_user=3,
    )
    panel = prepare_source_panel(canonical, spec)
    units = build_observations(panel, spec)
    assert panel.groupby("user_id").size().eq(3).all()
    assert units.groupby("user_id").size().eq(3).all()


def test_fixed_windows_keep_exact_source_provenance_and_boundary_modes() -> None:
    raw = pd.DataFrame([
        {"author": "u", "body": "one two three four five six", "created_utc": 1, "subreddit": "a"},
        {"author": "u", "body": "seven eight nine ten eleven twelve", "created_utc": 2, "subreddit": "b"},
        {"author": "u", "body": "thirteen fourteen fifteen sixteen seventeen eighteen", "created_utc": 3, "subreddit": "c"},
        {"author": "u", "body": "nineteen twenty twentyone twentytwo twentythree twentyfour", "created_utc": 4, "subreddit": "d"},
    ])
    canonical = canonicalize_comments(raw, min_tokens=1)
    canonical["split"] = "discovery"
    cross = ObservationSpec(
        name="cross", kind="fixed", window_tokens=8, stride_tokens=8, min_tokens=1,
        max_units_per_user=12, max_source_comments_per_user=4, source_boundary_mode="cross",
    )
    within = ObservationSpec(
        name="within", kind="fixed", window_tokens=8, stride_tokens=8, min_tokens=1,
        max_units_per_user=12, max_source_comments_per_user=4, source_boundary_mode="within",
    )
    marker = ObservationSpec(
        name="marker", kind="fixed", window_tokens=8, stride_tokens=8, min_tokens=1,
        max_units_per_user=12, max_source_comments_per_user=4, source_boundary_mode="cross_marker",
    )
    cross_units = build_observations(canonical, cross)
    within_units = build_observations(canonical, within)
    marker_units = build_observations(canonical, marker)
    all_sources = set(canonical["source_row"].astype(str))
    assert all(set(value.split(",")) != all_sources for value in cross_units["source_rows"])
    assert within_units["source_count"].eq(1).all()
    assert marker_units["source_rows"].map(lambda value: set(value.split(",")).issubset(all_sources)).all()
    assert marker_units["text"].str.contains("SUICA_BOUNDARY", regex=False).any()


def test_fixed_window_offsets_are_deterministic_and_cover_source_rows() -> None:
    canonical = canonicalize_comments(_raw_comments().query("author == 'u00'"), min_tokens=8)
    canonical["split"] = "discovery"
    spec = ObservationSpec(
        name="hashed", kind="fixed", window_tokens=32, stride_tokens=32, min_tokens=8,
        max_units_per_user=40, max_source_comments_per_user=12, source_boundary_mode="cross",
        offset_strategy="author_hash",
    )
    first = build_observations(canonical, spec)
    second = build_observations(canonical, spec)
    assert first[["text", "source_rows"]].equals(second[["text", "source_rows"]])
    covered = set()
    for value in first["source_rows"]:
        covered.update(int(token) for token in value.split(",") if token)
    assert covered == set(canonical["source_row"].astype(int))
