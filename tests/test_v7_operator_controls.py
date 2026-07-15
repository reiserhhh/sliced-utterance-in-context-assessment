from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v7_observations import (
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    prepare_source_panel,
)
from suica_core.v7_operator_controls import (
    bootstrap_source_comments,
    correspondence_permutation_test,
    score_operator_from_comments,
    source_cluster_bootstrap_z_sem,
    source_disjoint_partition,
    source_disjoint_score_consistency,
)
from suica_core.v7_psychometric import (
    RepresentationSpec,
    author_features_from_embeddings,
    fit_factor_bundle,
    fit_representation,
)


def _comments() -> pd.DataFrame:
    rows = []
    for user in range(36):
        for comment in range(12):
            rows.append({
                "author": f"u{user:02d}",
                "body": (
                    f"Author token {user} discusses route {comment % 4} with stable vocabulary. "
                    f"Repeated context {user % 5} supplies enough words for a source-level test."
                ),
                "created_utc": user * 100 + comment,
                "subreddit": f"s{comment % 3}",
            })
    return pd.DataFrame(rows)


def _fitted_components():
    comments = canonicalize_comments(_comments(), min_tokens=4)
    comments["split"] = np.where(
        comments["user_id"].str.extract(r"(\d+)")[0].astype(int) < 20,
        "discovery",
        np.where(comments["user_id"].str.extract(r"(\d+)")[0].astype(int) < 28, "calibration", "confirmation"),
    )
    spec = ObservationSpec(
        name="native", kind="native", min_tokens=4, max_units_per_user=16,
        max_source_comments_per_user=12,
    )
    panel = prepare_source_panel(comments, spec)
    representation = fit_representation(
        panel.loc[panel["split"].eq("discovery")],
        RepresentationSpec(max_features=300, svd_dimensions=6, factor_count=2, seed=3),
    )
    units = build_observations(panel, spec)
    features = author_features_from_embeddings(units, representation.transform(units["text"]))
    fitted = fit_factor_bundle(
        features,
        operator=spec.to_dict(),
        representation=representation.spec,
        runtime_artifact={"test": True},
        min_units_for_score=2,
        seed=3,
    )
    return panel, spec, representation, fitted.bundle


def test_source_disjoint_partition_has_no_source_comment_overlap() -> None:
    panel, _, _, _ = _fitted_components()
    left, right = source_disjoint_partition(panel, seed=9)
    assert set(left["source_row"]).isdisjoint(set(right["source_row"]))
    assert left.groupby("user_id").size().eq(6).all()
    assert right.groupby("user_id").size().eq(6).all()


def test_source_bootstrap_preserves_origin_and_assigns_unique_draw_ids() -> None:
    panel, _, _, _ = _fitted_components()
    sampled = bootstrap_source_comments(panel, seed=5)
    assert "source_origin" in sampled
    assert sampled["source_row"].is_unique
    assert sampled.groupby("user_id").size().eq(12).all()


def test_source_level_controls_score_frozen_operator_without_overlap() -> None:
    panel, spec, representation, bundle = _fitted_components()
    units, _, scores = score_operator_from_comments(panel, spec=spec, representation=representation, bundle=bundle)
    assert not units.empty
    assert scores["score_status"].eq("SCORED").all()
    consistency = source_disjoint_score_consistency(
        panel, spec=spec, representation=representation, bundle=bundle, seed=7, replicate=0
    )
    assert consistency["source_overlap_count"].eq(0).all()
    assert consistency["n_users"].min() >= 8
    bootstrap = source_cluster_bootstrap_z_sem(
        panel, spec=spec, representation=representation, bundle=bundle, repetitions=3, seed=11
    )
    assert bootstrap["sem_status"].eq("SOURCE_CLUSTER_BOOTSTRAP").all()
    permutation = correspondence_permutation_test(
        panel, spec=spec, representation=representation, bundle=bundle, seed=7, repetitions=20
    )
    assert permutation["permutations"].eq(20).all()
