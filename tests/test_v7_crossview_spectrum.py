from __future__ import annotations

import numpy as np

from suica_core.v7_crossview_spectrum import (
    broken_correspondence_spectra,
    excess_spectral_profile,
    off_diagonal_cross_view_operator,
    ordered_spectrum,
    profile_cosine,
)


def _shared_blocks(seed: int = 4) -> tuple[dict[str, np.ndarray], tuple[str, ...]]:
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(80, 3))
    names = ("left", "middle", "right")
    return {name: latent @ rng.normal(size=(3, 12)) + rng.normal(scale=0.2, size=(80, 12)) for name in names}, names


def test_crossview_spectrum_has_expected_shape_and_null_adjusted_profile() -> None:
    blocks, names = _shared_blocks()
    spectrum = ordered_spectrum(off_diagonal_cross_view_operator(blocks, view_names=names))
    null = broken_correspondence_spectra(blocks, view_names=names, iterations=19, seed=11)
    profile = excess_spectral_profile(blocks, view_names=names, null_upper=np.quantile(null, 0.95, axis=0))
    assert spectrum.shape == (12,)
    assert null.shape == (19, 12)
    assert profile["n_positive_excess"] >= 1
    assert profile["entropy_effective_rank"] >= 1.0


def test_profile_cosine_is_one_for_identical_profiles() -> None:
    values = np.array([3.0, 1.0, 0.0])
    assert np.isclose(profile_cosine(values, values), 1.0)


def test_negative_observed_modes_do_not_count_as_shared_excess() -> None:
    blocks, names = _shared_blocks()
    profile = excess_spectral_profile(
        blocks,
        view_names=names,
        null_upper=np.full(12, -10.0),
    )
    assert np.all(profile["excess_eigenvalues"][profile["observed_eigenvalues"] <= 0.0] == 0.0)
