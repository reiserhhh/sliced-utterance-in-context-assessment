from __future__ import annotations

import numpy as np

from scripts.run_suica_v6_crossblock_geometry import _even_subsample


def test_even_subsample_is_reproducible_and_has_requested_size() -> None:
    index = _even_subsample(100, 24)
    assert len(index) == 24
    assert np.all(np.diff(index) > 0)
    assert index[0] == 0
    assert index[-1] == 99


def test_even_subsample_preserves_all_small_numeric_rows() -> None:
    assert np.array_equal(_even_subsample(15, 20), np.arange(15))
