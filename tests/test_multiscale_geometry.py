from __future__ import annotations

import numpy as np

from suica_core.multiscale_geometry import multiscale_neighbour_profile


def test_multiscale_profile_detects_stable_neighbourhoods() -> None:
    rng = np.random.default_rng(91)
    latent = rng.normal(size=(100, 4))
    early = latent + rng.normal(scale=0.04, size=latent.shape)
    late = latent + rng.normal(scale=0.04, size=latent.shape)
    rows, null = multiscale_neighbour_profile(
        early, late, scales=(5, 15), iterations=99, seed=92,
    )
    assert len(rows) == 2
    assert len(null) == 198
    assert all(row["permutation_p"] <= 0.02 for row in rows)
    assert all(row["absolute_excess"] > 0.1 for row in rows)


def test_multiscale_profile_rejects_invalid_scale() -> None:
    rng = np.random.default_rng(93)
    values = rng.normal(size=(20, 3))
    try:
        multiscale_neighbour_profile(values, values, scales=(20,), iterations=99)
    except ValueError as error:
        assert "valid neighbourhood scales" in str(error)
    else:
        raise AssertionError("invalid scale must be rejected")
