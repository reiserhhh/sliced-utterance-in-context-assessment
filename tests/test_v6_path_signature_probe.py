from __future__ import annotations

import numpy as np

from scripts.run_suica_v6_path_signature_probe import paired_auc_delta


def test_paired_auc_delta_detects_ordered_advantage() -> None:
    rng = np.random.default_rng(31)
    n = 80
    # Ordered distances discriminate own authors; null distances do not.
    own = rng.normal(0.2, 0.03, n)
    stranger = rng.normal(0.8, 0.03, (n, 5))
    null_own = rng.normal(0.5, 0.03, n)
    null_stranger = rng.normal(0.5, 0.03, (n, 5))
    result = paired_auc_delta(own, stranger, null_own, null_stranger, seed=32, iterations=100)
    assert result["order_delta_auc"] > 0.4
    assert result["order_delta_ci_lo"] > 0.3
