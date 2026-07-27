"""Tests for the label-free V8 real-text pilot utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_realtext import (
    aggregate_half_features,
    cross_fitted_semantic_increment,
    deterministic_text_features,
    document_segments,
    load_pandora_source_disjoint_panels,
    require_local_reference,
    v8_author_split,
)


def test_document_segments_are_nonempty_and_deterministic() -> None:
    text = " ".join(f"token{index}" for index in range(400))
    first = document_segments(text, count=4)
    second = document_segments(text, count=4)
    assert first == second
    assert len(first) == 4
    assert all(segment for segment in first)


def test_text_features_are_finite_and_language_tolerant() -> None:
    english = deterministic_text_features("I think we should try a new route!")
    japanese = deterministic_text_features("私は別の方法を試すべきだと思います。")
    assert english.shape == japanese.shape
    assert np.isfinite(english).all()
    assert np.isfinite(japanese).all()


def test_half_aggregation_preserves_author_split() -> None:
    panel = pd.DataFrame([
        {
            "author_id": f"u{author}",
            "split": v8_author_split(f"u{author}"),
            "corpus": "fixture",
            "segment_id": f"u{author}-s{segment}",
            "unit_index": segment,
        }
        for author in range(8)
        for segment in range(4)
    ])
    vectors = {
        row.segment_id: np.array([float(author), float(segment)])
        for author in range(8)
        for segment, row in enumerate(
            panel.loc[panel["author_id"].eq(f"u{author}")].itertuples(index=False)
        )
    }
    metadata, left, right = aggregate_half_features(panel, vectors)
    assert len(metadata) == 8
    assert left.shape == right.shape == (8, 2)


def test_cross_fitted_increment_uses_confirmation_only_for_report() -> None:
    rng = np.random.default_rng(42)
    n = 90
    metadata = pd.DataFrame({
        "split": ["discovery"] * 45 + ["calibration"] * 22 + ["confirmation"] * 23,
    })
    identity = rng.normal(size=(n, 6))
    baseline_left = identity + rng.normal(scale=1.0, size=identity.shape)
    baseline_right = identity + rng.normal(scale=1.0, size=identity.shape)
    semantic_left = identity + rng.normal(scale=0.25, size=identity.shape)
    semantic_right = identity + rng.normal(scale=0.25, size=identity.shape)
    result = cross_fitted_semantic_increment(
        metadata,
        baseline_left,
        baseline_right,
        semantic_left,
        semantic_right,
        bootstrap_draws=200,
    )
    assert result["status"] == "TECHNICAL_INCREMENT_EVALUATED"
    assert result["n_confirmation"] == 23
    assert result["augmented_confirmation_auc"] >= result["baseline_confirmation_auc"]


def test_cross_corpus_reference_is_refused() -> None:
    require_local_reference(corpus="pandora", reference_corpus="pandora")
    try:
        require_local_reference(corpus="essays", reference_corpus="pandora")
    except ValueError as exc:
        assert "REFUSE_NONLOCAL_REFERENCE" in str(exc)
    else:
        raise AssertionError("cross-corpus norm must be refused")


def test_pandora_semantic_panel_respects_geometry_sides(tmp_path) -> None:
    rows = []
    for author in ("alpha", "beta"):
        for index in range(12):
            rows.append({
                "author": author,
                "body": f"{author} marker{index} " + "word " * 30,
                "created_utc": index,
                "subreddit": "fixture",
            })
    path = tmp_path / "pandora.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)
    eligible = pd.DataFrame({
        "user_id": ["alpha", "beta"],
        "split": ["discovery", "discovery"],
    })
    semantic, geometry = load_pandora_source_disjoint_panels(
        path,
        eligible_authors=eligible,
        max_by_split={"discovery": 2},
        semantic_segments_per_author=4,
        geometry_units_per_half=4,
        seed=17,
    )
    assert semantic.groupby("author_id").size().eq(4).all()
    assert geometry.groupby(["user_id", "split"]).size().eq(4).all()
    assert set(geometry["split"]) == {"left", "right"}
    assert semantic.loc[semantic["unit_index"] % 2 == 0, "unit_index"].nunique() == 2
    assert semantic.loc[semantic["unit_index"] % 2 == 1, "unit_index"].nunique() == 2
