from __future__ import annotations

import numpy as np

from suica_core.v7_crossview_spectrum import (
    broken_correspondence_spectra,
    excess_spectral_profile,
    off_diagonal_cross_view_operator,
    ordered_spectrum,
    profile_cosine,
    simultaneous_null_upper,
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


def test_default_profile_output_is_unchanged_without_null_spectra() -> None:
    blocks, names = _shared_blocks()
    null = broken_correspondence_spectra(blocks, view_names=names, iterations=19, seed=11)
    profile = excess_spectral_profile(blocks, view_names=names, null_upper=np.quantile(null, 0.95, axis=0))
    # Stored W4b artifacts remain valid: no new keys appear on the default path.
    assert set(profile) == {
        "observed_eigenvalues", "null_upper_eigenvalues", "excess_eigenvalues",
        "n_positive_excess", "entropy_effective_rank",
        "participation_effective_rank", "excess_energy_90_rank",
    }


def test_simultaneous_envelope_removes_pointwise_positive_bias_under_global_null() -> None:
    """Under a true global null, pointwise 95% envelopes still pass positions by
    chance (positively biased count), while the max-T style simultaneous
    envelope yields ~0 positive excess positions."""
    names = ("left", "middle", "right")
    pointwise_total = 0
    simultaneous_total = 0
    n_datasets = 25
    for seed in range(n_datasets):
        rng = np.random.default_rng(100 + seed)
        blocks = {name: rng.normal(size=(24, 16)) for name in names}  # independent: no shared structure
        null = broken_correspondence_spectra(blocks, view_names=names, iterations=60, seed=500 + seed)
        profile = excess_spectral_profile(
            blocks,
            view_names=names,
            null_upper=np.quantile(null, 0.95, axis=0),
            null_spectra=null,
        )
        # Pointwise columns are byte-identical to the null_spectra=None path.
        reference = excess_spectral_profile(blocks, view_names=names, null_upper=np.quantile(null, 0.95, axis=0))
        assert profile["n_positive_excess"] == reference["n_positive_excess"]
        assert np.array_equal(profile["excess_eigenvalues"], reference["excess_eigenvalues"])
        assert profile["null_upper_simultaneous"] >= float(np.quantile(null, 0.95, axis=0).max()) - 1e-12
        pointwise_total += int(profile["n_positive_excess"])
        simultaneous_total += int(profile["n_positive_excess_simultaneous"])
    # Pointwise counting passes chance positions on average (positive bias:
    # here 12 spurious positions across 25 null datasets)...
    assert pointwise_total / n_datasets > 0.25
    # ...while the simultaneous bound keeps the per-dataset family-wise
    # exceedance near its nominal 5% (~0 excess positions on average).
    assert simultaneous_total / n_datasets <= 0.1
    assert simultaneous_total < pointwise_total


def test_simultaneous_envelope_retains_power_for_real_shared_structure() -> None:
    blocks, names = _shared_blocks()
    null = broken_correspondence_spectra(blocks, view_names=names, iterations=99, seed=13)
    profile = excess_spectral_profile(
        blocks, view_names=names, null_upper=np.quantile(null, 0.95, axis=0), null_spectra=null
    )
    assert profile["n_positive_excess_simultaneous"] >= 1
    assert profile["n_positive_excess_simultaneous"] <= profile["n_positive_excess"]


def test_simultaneous_null_upper_validates_input_shape() -> None:
    try:
        simultaneous_null_upper(np.zeros(5))
    except ValueError as error:
        assert "draw, position" in str(error)
    else:
        raise AssertionError("one-dimensional null spectra were accepted")


def test_negative_observed_modes_do_not_count_as_shared_excess() -> None:
    blocks, names = _shared_blocks()
    profile = excess_spectral_profile(
        blocks,
        view_names=names,
        null_upper=np.full(12, -10.0),
    )
    assert np.all(profile["excess_eigenvalues"][profile["observed_eigenvalues"] <= 0.0] == 0.0)
