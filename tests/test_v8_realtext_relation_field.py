"""Tests for V8-REALTEXT-RELATION-FIELD-1."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import (
    _macro_decomposition,
    CorpusFeaturePanel,
    RealTextRelationSpec,
    approximate_gromov_wasserstein,
    evaluate_corpus_local,
    family_features,
    fit_corpus_calibration,
    frozen_event_vector,
    frozen_random_directions,
    support_overlap,
)


def test_frozen_event_vector_is_deterministic_and_finite() -> None:
    first = frozen_event_vector("The market moved, but I kept my plan.", dimensions=16)
    second = frozen_event_vector("The market moved, but I kept my plan.", dimensions=16)
    japanese = frozen_event_vector("市場は動いたが、私は計画を維持した。", dimensions=16)
    assert first.shape == second.shape == japanese.shape == (32,)
    assert np.array_equal(first, second)
    assert np.isfinite(japanese).all()


def test_marginal_family_is_order_free_but_transition_family_is_not() -> None:
    rng = np.random.default_rng(3)
    events = rng.normal(size=(12, 10))
    directions = frozen_random_directions(
        event_dimensions=10,
        count=4,
        seed=9,
    )
    forward = family_features(
        events,
        marginal_directions=directions[0],
        transition_directions=directions[1],
        current_directions=directions[2],
    )
    reverse = family_features(
        events[::-1],
        marginal_directions=directions[0],
        transition_directions=directions[1],
        current_directions=directions[2],
    )
    assert np.allclose(forward["M"], reverse["M"], atol=1e-12)
    assert not np.allclose(forward["K"], reverse["K"], atol=1e-6)


def test_support_overlap_accepts_internal_gauge_rotation() -> None:
    rng = np.random.default_rng(4)
    basis, _ = np.linalg.qr(rng.normal(size=(12, 3)))
    rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    overlap = support_overlap(basis, basis @ rotation)
    assert overlap["omega"] > 0.999999
    assert overlap["worst_alignment"] > 0.999999


def test_approximate_gw_is_invariant_to_rotation_and_permutation() -> None:
    rng = np.random.default_rng(5)
    values = rng.normal(size=(28, 4))
    rotation, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    permuted = values[rng.permutation(len(values))] @ rotation
    result = approximate_gromov_wasserstein(
        values,
        permuted,
        maximum_authors=28,
        iterations=20,
        seed=7,
    )
    assert result["status"] == "GW_APPROXIMATED"
    assert result["distance"] < 0.05


def test_local_pipeline_recovers_distinct_related_families() -> None:
    rng = np.random.default_rng(11)
    authors = 240
    dimensions = 12
    shared = rng.normal(size=(authors, 2))
    private_m = rng.normal(size=(authors, 1))
    private_k = rng.normal(size=(authors, 1))
    latent_m = np.column_stack([shared, private_m])
    latent_k = np.column_stack([shared, private_k])
    loading_m, _ = np.linalg.qr(rng.normal(size=(dimensions, 3)))
    loading_k, _ = np.linalg.qr(rng.normal(size=(dimensions, 3)))
    raw_m = np.stack(
        [
            latent_m @ loading_m.T + rng.normal(scale=0.20, size=(authors, dimensions)),
            latent_m @ loading_m.T + rng.normal(scale=0.20, size=(authors, dimensions)),
        ],
        axis=1,
    )
    raw_k = np.stack(
        [
            latent_k @ loading_k.T + rng.normal(scale=0.20, size=(authors, dimensions)),
            latent_k @ loading_k.T + rng.normal(scale=0.20, size=(authors, dimensions)),
        ],
        axis=1,
    )
    splits = np.asarray(["D0"] * 96 + ["D1"] * 72 + ["D2"] * 72)
    contexts = np.asarray(["a", "b"] * (authors // 2))
    metadata = pd.DataFrame(
        {
            "corpus": "fixture",
            "author_id": [f"u{index}" for index in range(authors)],
            "context": contexts,
            "split": splits,
            "event_count": 8,
        }
    )
    panel = CorpusFeaturePanel(
        metadata=metadata,
        raw={"M": raw_m, "K": raw_k},
        context_role="FIXTURE",
        replicate_type="FIXTURE",
    )
    spec = RealTextRelationSpec(
        maximum_rank=4,
        minimum_rank=2,
        support_permutations=19,
        relation_permutations=39,
        support_subsamples=9,
        minimum_split_authors=20,
        minimum_context_authors=12,
        alignment_floor=0.20,
        relation_agreement_floor=0.40,
        gw_authors=16,
        gw_iterations=8,
    )
    calibration = fit_corpus_calibration("fixture", panel, spec=spec)
    assert all(
        support.status == "SOFT_SUPPORT_CALIBRATED"
        for support in calibration.supports.values()
    )
    assert calibration.alias["status"] == "FAMILIES_DISTINCT"
    result = evaluate_corpus_local(panel, calibration)
    assert result["relation"]
    assert any(row["relation_license"] == 1 for row in result["relation"])


def test_macro_decomposition_is_exact_in_covariance_space() -> None:
    rng = np.random.default_rng(17)
    authors = 90
    left = rng.normal(size=(authors, 2, 7))
    right = 0.6 * left + rng.normal(scale=0.5, size=(authors, 2, 7))
    contexts = np.repeat(np.asarray(["a", "b", "c"]), authors // 3)
    result = _macro_decomposition(left, right, contexts)
    assert result["decomposition_error"] < 1e-12
    assert np.allclose(
        result["total"],
        result["within"] + result["between"],
        atol=1e-12,
    )
