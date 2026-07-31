"""Tests for the conditional concordance spectrum."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_conditional_concordance_spectrum import (
    ConcordanceSpectrumSpec,
    evaluate_conditional_concordance_spectrum,
    generalized_spectrum,
    projected_concordance,
    signed_operators,
    subspace_affinity,
)
from suica_core.v8_event_set_composition_knockout import EventTensor
from suica_core.v8_realtext_relation_field import RealTextRelationSpec


def test_generalized_spectrum_recovers_positive_and_negative_directions() -> None:
    rng = np.random.default_rng(3)
    latent = rng.normal(size=(300, 3))
    first = latent + rng.normal(scale=0.1, size=latent.shape)
    second = latent.copy()
    second[:, 1] *= -1.0
    second += rng.normal(scale=0.1, size=latent.shape)
    values = np.stack([first, second], axis=1)
    between, within = signed_operators(
        values,
        block_slices=[slice(0, 3)],
    )
    spectrum = generalized_spectrum(between, within, gamma=0.01)
    eigenvalues = spectrum["eigenvalues"]
    assert eigenvalues[0] > 0.9
    assert eigenvalues[-1] < -0.9
    assert np.max(np.abs(eigenvalues)) <= 1.0 + 1e-8


def test_projected_concordance_and_subspace_affinity() -> None:
    rng = np.random.default_rng(9)
    latent = rng.normal(size=(120, 4))
    values = np.stack(
        [
            latent + rng.normal(scale=0.2, size=latent.shape),
            latent + rng.normal(scale=0.2, size=latent.shape),
        ],
        axis=1,
    )
    between, within = signed_operators(
        values,
        block_slices=[slice(0, 2), slice(2, 4)],
    )
    spectrum = generalized_spectrum(between, within, gamma=0.03)
    vectors = spectrum["generalized"][:, :2]
    assert projected_concordance(between, within, vectors) > 0.5
    assert np.isclose(
        subspace_affinity(
            spectrum["loadings"][:, :2],
            spectrum["loadings"][:, :2],
        ),
        1.0,
    )


def test_underresolved_spectrum_returns_typed_empty_cells() -> None:
    rng = np.random.default_rng(17)
    authors = 60
    tensor = EventTensor(
        metadata=pd.DataFrame(
            {
                "author_id": [f"u{index}" for index in range(authors)],
                "context": ["c"] * authors,
                "split": ["D0"] * 20 + ["D1"] * 20 + ["D2"] * 20,
            }
        ),
        vectors=rng.normal(size=(authors, 8, 64)).astype(np.float32),
        lengths=np.full((authors, 8), 20, dtype=np.int32),
    )
    result = evaluate_conditional_concordance_spectrum(
        {"synthetic": tensor},
        feature_spec=RealTextRelationSpec(
            hash_dimensions=32,
            random_directions=8,
            support_permutations=19,
            relation_permutations=19,
            support_subsamples=5,
        ),
        spec=ConcordanceSpectrumSpec(
            background_draws=49,
            spectrum_null_draws=49,
            test_null_draws=99,
            bootstrap_draws=99,
            bootstrap_reference_worlds=8,
            minimum_half_authors=4,
            maximum_rank=2,
        ),
    )
    assert set(result["cells"].columns) >= {
        "corpus",
        "split",
        "view",
        "max_t_p",
    }
