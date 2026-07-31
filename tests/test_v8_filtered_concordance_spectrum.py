"""Tests for the opportunity-filtered concordance spectrum."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_filtered_concordance_spectrum import (
    FilteredSpectrumSpec,
    evaluate_filtered_spectrum,
)


def _panel(seed: int, *, signal: bool) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(seed)
    authors = 180
    metadata = pd.DataFrame(
        {
            "author_id": [f"u{index}" for index in range(authors)],
            "context": np.resize(["a", "b", "c"], authors),
            "split": np.resize(["D0"] * 80 + ["D1"] * 50 + ["D2"] * 50, authors),
        }
    )
    latent = rng.normal(size=(authors, 2))
    left = rng.normal(scale=0.7, size=(authors, 10))
    right = rng.normal(scale=0.7, size=(authors, 10))
    if signal:
        loading = rng.normal(size=(2, 10))
        left += latent @ loading
        right += latent @ loading
    return metadata, np.stack([left, right], axis=1)


def test_filtered_spectrum_resolves_planted_low_rank_signal() -> None:
    result = evaluate_filtered_spectrum(
        {"synthetic": _panel(5, signal=True)},
        gamma_by_corpus={"synthetic": 0.1},
        spec=FilteredSpectrumSpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
            maximum_rank=4,
            seed=41,
        ),
    )
    assert result["discovery"].iloc[0]["candidate_rank"] >= 1
    assert result["status"] == "FILTERED_LOW_DIMENSIONAL_SPECTRUM_REPLICATED"


def test_filtered_spectrum_refuses_null_panel() -> None:
    result = evaluate_filtered_spectrum(
        {"synthetic": _panel(7, signal=False)},
        gamma_by_corpus={"synthetic": 0.1},
        spec=FilteredSpectrumSpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
            maximum_rank=4,
            seed=43,
        ),
    )
    assert result["status"] == (
        "FILTERED_CONCORDANCE_HIGH_DIMENSIONAL_OR_UNDERRESOLVED"
    )
