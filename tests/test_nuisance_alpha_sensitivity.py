from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v6_nuisance_alpha_sensitivity import (
    _stable_subsample,
    _standardized_static_views,
)


def test_alpha_subsample_is_deterministic_without_exporting_users() -> None:
    users = [f"u{index:03d}" for index in range(80)]
    first = _stable_subsample(users, 24, 77)
    second = _stable_subsample(users, 24, 77)
    assert len(first) == 24
    assert np.array_equal(first, second)


def test_static_views_use_discovery_reference_only() -> None:
    rows = []
    for user_number in range(28):
        for half in ("early", "late"):
            rows.append({
                "user_id": f"u{user_number}", "half": half,
                "static::x": float(user_number), "static::y": float(user_number + (half == "late")),
            })
    early, late, users, diagnostics = _standardized_static_views(
        pd.DataFrame(rows), {f"u{index}" for index in range(14)}, {f"u{index}" for index in range(14, 28)},
    )
    assert early.shape == late.shape == (14, 2)
    assert len(users) == 14
    assert diagnostics["mean_norm_early"] > 0.0
